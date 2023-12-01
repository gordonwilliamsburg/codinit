import os
import re
from typing import List, Optional

import weaviate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.base import Document
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.utilities import ApifyWrapper

from codinit.config import client, secrets

os.environ["APIFY_API_TOKEN"] = secrets.apify_key


# from codinit.doc_schema import library_class, documentation_file_class
# client.schema.create({"classes": [library_class, documentation_file_class]})
def embed_documentation_recursiveloader(
    libname: str,
    links: List[str],
    weaviate_client: weaviate.Client,
    exclude_dirs: Optional[List[str]] = None,
    lib_desc: Optional[str] = None,
):
    lib_obj = {
        "name": libname,
        "links": links,
        "description": lib_desc,
    }
    print(lib_obj)
    lib_id = weaviate_client.data_object.create(
        data_object=lib_obj, class_name="Library"
    )
    for link in links:
        loader = RecursiveUrlLoader(url=link, exclude_dirs=exclude_dirs)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        docs = text_splitter.split_documents(docs)

        with weaviate_client.batch() as batch:
            for doc in docs:
                doc
                doc_obj = {**doc.metadata, "content": doc.page_content}
                print(doc_obj)
                doc_id = batch.add_data_object(
                    data_object=doc_obj, class_name="DocumentionFile"
                )
                # DocumentionFile -> Library relationship
                batch.add_reference(
                    from_object_class_name="DocumentionFile",
                    from_object_uuid=doc_id,
                    from_property_name="fromLibrary",
                    to_object_class_name="Library",
                    to_object_uuid=lib_id,
                )

                # Library -> DocumentionFile relationship
                batch.add_reference(
                    from_object_class_name="Library",
                    from_object_uuid=lib_id,
                    from_property_name="hasDocumentionFile",
                    to_object_class_name="DocumentionFile",
                    to_object_uuid=doc_id,
                )


def embed_documentation_apify(
    libname: str,
    links: List[str],
    weaviate_client: weaviate.Client,
    exclude_dirs: Optional[List[str]] = None,
    lib_desc: Optional[str] = None,
    apify_key: str = secrets.apify_key,
):
    lib_obj = {
        "name": libname,
        "links": links,
        "description": lib_desc,
    }
    print(lib_obj)
    lib_id = weaviate_client.data_object.create(
        data_object=lib_obj, class_name="Library"
    )

    # TODO: fix, must enter api_key as parameter
    apify = ApifyWrapper()

    for link in links:
        loader = apify.call_actor(
            actor_id="apify/website-content-crawler",
            run_input={"startUrls": [{"url": link}]},
            dataset_mapping_function=lambda item: Document(
                page_content=item["text"] or "", metadata={"source": item["url"]}
            ),
        )
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        docs = text_splitter.split_documents(docs)
        client.batch.configure(batch_size=10)
        with weaviate_client.batch as batch:
            for doc in docs:
                doc
                doc_obj = {**doc.metadata, "content": doc.page_content}
                print(doc_obj)
                doc_id = batch.add_data_object(
                    data_object=doc_obj, class_name="DocumentionFile"
                )
                # DocumentionFile -> Library relationship
                batch.add_reference(
                    from_object_class_name="DocumentionFile",
                    from_object_uuid=doc_id,
                    from_property_name="fromLibrary",
                    to_object_class_name="Library",
                    to_object_uuid=lib_id,
                )

                # Library -> DocumentionFile relationship
                batch.add_reference(
                    from_object_class_name="Library",
                    from_object_uuid=lib_id,
                    from_property_name="hasDocumentionFile",
                    to_object_class_name="DocumentionFile",
                    to_object_uuid=doc_id,
                )


def get_retriever(
    libname: str,
    links: List[str],
    weaviate_client: weaviate.Client,
    exclude_dirs: Optional[List[str]] = None,
    lib_desc: Optional[str] = None,
):
    # query if library already exists
    result = (
        client.query.get(
            "Library",
            properties=["name"],
        )
        .with_where({"path": ["name"], "operator": "Equal", "valueText": libname})
        .do()
    )
    print(f"{result=}")
    library_exists = result["data"]["Get"]["Library"]
    if len(library_exists) == 0:
        embed_documentation_apify(
            libname=libname,
            links=links,
            weaviate_client=weaviate_client,
            exclude_dirs=exclude_dirs,
            lib_desc=lib_desc,
        )
    retriever = WeaviateHybridSearchRetriever(
        client=client,
        index_name="DocumentionFile",
        text_key="content",
        k=10,
        alpha=0.75,
    )
    return retriever


def get_relevant_documents(query: str, retriever: WeaviateHybridSearchRetriever):
    # clean up query that might be produced by an LLM
    query = query.replace("`", "").replace("'", "").replace('"', "")
    result = re.findall(r'"(.*?)"', query)
    if len(result) > 0:
        query = result[0]
    print(query)
    docs = retriever.get_relevant_documents(query=query)
    # print(f"{docs=}")
    relevant_docs = ""
    for doc in docs:
        relevant_docs += doc.page_content
    return relevant_docs


libname = "langchain"
links = [
    "https://langchain-langchain.vercel.app/docs/get_started/",
    "https://python.langchain.com/docs/modules/",
    "https://python.langchain.com/docs/use_cases",
    "https://python.langchain.com/docs/guides",
    "https://python.langchain.com/docs/integrations",
]
"""
apify = ApifyWrapper()
for link in links:
    #loader = RecursiveUrlLoader(url=link, exclude_dirs="")
    loader = apify.call_actor(
            actor_id="apify/website-content-crawler",
            run_input={"startUrls": [{"url": link}]},
            dataset_mapping_function=lambda item: Document(
                page_content=item["text"] or "", metadata={"source": item["url"]}
            ),
        )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
    tiny_docs=text_splitter.split_documents(docs)
    print(tiny_docs)

retriever = get_retriever(libname=libname, links=links, weaviate_client=client)
relevant_docs = get_relevant_documents(
    query="Using the langchain library, write code that loads a user given pdf file, chunks it and then creates a summary of it.",
    retriever=retriever,
)
print(relevant_docs)
"""
