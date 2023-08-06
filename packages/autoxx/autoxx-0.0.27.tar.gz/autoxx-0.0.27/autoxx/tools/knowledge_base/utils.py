import pinecone
import os
from langchain.chat_models import ChatOpenAI
from autogpt.config import Config
from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index import (LLMPredictor,
                        ServiceContext,
                        StorageContext)
from llama_index.indices.loading import load_index_from_storage
from llama_index.storage.docstore import MongoDocumentStore
from llama_index.storage.index_store import MongoIndexStore
from llama_index.vector_stores import PineconeVectorStore
from llama_index.readers.schema.base import Document
from typing import List, Dict
from llama_index.node_parser import SimpleNodeParser
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.callbacks.base import CallbackManager

class knowleage_bot:

    def __init__(self, corpus:str, model:str = "gpt-3.5-turbo"):
        self.corpus = corpus
        self.model = model
        mongodb_dbname = self.corpus

        mongodb_password = os.getenv("MONGODB_PASSWORD")
        assert mongodb_password is not None, "Please set MONGODB_PASSWORD environment variable"
        mongodb_user = os.getenv("MONGODB_USER") or "raga"
        mongodb_url = f"mongodb+srv://{mongodb_user}:{mongodb_password}@cluster0.spj0g.mongodb.net/?retryWrites=true&w=majority"

        # create mongodb docstore, indexstore
        self.docstore = MongoDocumentStore.from_uri(uri=mongodb_url, db_name=mongodb_dbname)
        self.index_store = MongoIndexStore.from_uri(uri=mongodb_url, db_name=mongodb_dbname)
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        assert pinecone_api_key is not None, "Please set PINECONE_API_KEY environment variable"
        pinecone_environment =  os.getenv("PINECONE_ENVIRONMENT") or "us-central1-gcp"
        pinecone_index_name = f"{self.corpus}-index"

        pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        pinecone_index = pinecone.Index(pinecone_index_name)
        self.vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

        storage_context = StorageContext.from_defaults(
            docstore=self.docstore,
            index_store=self.index_store,
            vector_store=self.vector_store,
        )

        config = Config()
        if config.use_azure:
            llm = ChatOpenAI(model_name= config.fast_llm_model, model_kwargs={
                "api_key": config.openai_api_key,
                "api_base": config.openai_api_base,
                "api_type": config.openai_api_type,
                "api_version": config.openai_api_version,
                "deployment_id": config.get_azure_deployment_id_for_model(config.fast_llm_model),
            })
            llm_predictor_chatgpt = LLMPredictor(
                llm=llm
            )
            embed_model = OpenAIEmbedding(
                deployment_name=config.get_azure_deployment_id_for_model("text-embedding-ada-002"),
                api_key=config.openai_api_key,
                api_base=config.openai_api_base,
                api_type=config.openai_api_type,
                api_version=config.openai_api_version,
            )
        else:
            print(config.use_azure, config.openai_api_key)
            llm_predictor_chatgpt = LLMPredictor(
                llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
            )
            embed_model = OpenAIEmbedding()
        service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor_chatgpt, chunk_size_limit=1024, embed_model=embed_model,
            node_parser=SimpleNodeParser(
                text_splitter=TokenTextSplitter(
                    callback_manager=CallbackManager([]),
                    chunk_size = 2048,
            ))
        )
        self.index = load_index_from_storage(
            storage_context=storage_context, service_context=service_context
        )

    def query(self, query:str):
        try:
            engine = self.index.as_query_engine()
            return engine.query(query)
        except Exception as e:
            print("Error:", e)
            raise Exception(f"failed to finish query: {str(e)}")

    def similarity_search(self, query:str):
        try:
            retriever = self.index.as_retriever()
            nodes =  retriever.retrieve(query)
        except Exception as e:
            print("Error:", e)
            raise Exception(f"failed to retrieve nodes: {str(e)}")

        return nodes

    def upsert_document(self, documents: List[Document]) -> None:
        self.index.docstore.add_documents(documents, allow_update=True)
        for document in documents:
            nodes = self.index.service_context.node_parser.get_nodes_from_documents([document])
            self.index.insert_nodes(nodes)

    def delete_document(self, document_id: str) -> None:
        self.index.delete(document_id)
        self.index.docstore.delete_document(document_id)

    def retrieve_document(self, document_ids: List[str]) ->  List[Document]:
        if document_ids is None or len(document_ids) == 0:
            return [doc for _, doc in self.index.docstore.docs.items()]

        documents = []
        for document_id in document_ids:
            document = self.index.docstore.get_document(document_id)
            documents.append(document)
        return documents
