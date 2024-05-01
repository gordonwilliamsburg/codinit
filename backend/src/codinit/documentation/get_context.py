import logging
import os
import re
from typing import List, Optional

import weaviate
import weaviate.classes as wvc
from apify_client import ApifyClient
from weaviate.classes.query import Filter, QueryReference

from codinit.config import (
    DocumentationSettings,
    Secrets,
    documentation_settings,
    secrets,
)
from codinit.documentation.chunk_documents import chunk_document
from codinit.documentation.doc_schema import init_library_schema_weaviate
from codinit.documentation.pydantic_models import Library, WebScrapingData
from codinit.documentation.save_document import load_scraped_data_from_json
from codinit.weaviate_client import get_weaviate_client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# TODO: here is an issue: now the weaviate client operations is entangled with the library operations
# for example, initializing the schema is not related to a single library.
# this should be refactored into single responsibility
# Also better make an abstract class for library search so that in the future can be able to impelement other search dbs
class BaseWeaviateDocClient:
    """
    Base class for weaviate Documentation client.
    """

    def __init__(self, library: Library, client: weaviate.WeaviateClient) -> None:
        self.library = library
        self.client = client
        self.init_schema()

    def check_library_exists(self):
        self.client.connect()
        # query if library already exists and has documentation files
        library = self.client.collections.get("Library")
        query_library_result = library.query.fetch_objects(
            filters=wvc.query.Filter.by_property("name").equal(self.library.libname),
            limit=1,
        )
        self.client.close()
        print(f"{query_library_result=}")
        if len(query_library_result.objects) == 0:
            return False
        else:
            return True

    def get_lib_id(self) -> Optional[str]:
        object_id = None
        self.client.connect()
        # query if library already exists and has documentation files
        library = self.client.collections.get("Library")
        result = library.query.fetch_objects(
            filters=wvc.query.Filter.by_property("name").equal(self.library.libname),
            limit=1,
        )
        self.client.close()
        print(result)
        # get the id of a library from weaviate
        if len(result.objects) > 0:  # case where library exists at least once
            if len(result.objects) > 1:
                logging.warning(
                    f"More than one library with name {self.library.libname} found, returning first one."
                )
            object_id = result.objects[0].uuid
        else:  # case where result is {'data': {'Get': {'Library': []}}}
            logging.warning(f"Library ID for {self.library.libname} not found.")
        return object_id

    def check_library_has_docs(self, lib_id: str) -> int:
        """returns number of documents associated with one library in the database"""
        num_docs = 0
        self.client.connect()
        collection = self.client.collections.get("Library")
        result = collection.query.fetch_objects(
            filters=wvc.query.Filter.by_id().equal(lib_id),
            return_properties=["name"],
            return_references=[
                wvc.query.QueryReference(
                    link_on="hasDocumentationFile", return_properties=["title"]
                ),
            ],
        )
        self.client.close()
        logging.debug(
            f"Querying documentation for library with ID {lib_id} gives {result=}"
        )
        # get the number of documentation files associated with a library"
        """
        1. example, no docs exist:  result = {'data': {'Get': {'Library': [{'hasDocumentationFile': None,
            'name': 'langchain'}]}}}
        2. example, multiple docs exist: result = {'data': {'Get': {'Library': [{'hasDocumentationFile': [{'title': 'title1'}, {'title': 'title2'}], 'name': 'langchain'}]}}}
        """
        # Check if there are associated documentation files
        if result.objects:
            library_data = result.objects[0]
            logging.debug(
                f"library with ID {lib_id} has documentation files: {library_data=}"
            )
            """
            1. example, no docs exist: library_data = [{'hasDocumentationFile': None, 'name': 'langchain'}]
            2. example, multiple docs exist: library_data = [{'hasDocumentationFile': [{'title': 'title1'}, {'title': 'title2'}], 'name': 'langchain'}]
            """
            if library_data.references:
                documentation_files = library_data.references["hasDocumentationFile"]
                if documentation_files:
                    num_docs = len(documentation_files.objects)
                else:
                    logging.warning(
                        f"Library with ID {lib_id} has no documentation files."
                    )
            else:  # case where result={'data': {'Get': {'Library': []}}}
                logging.error(f"Error getting library with ID {lib_id} from weaviate.")
        return num_docs

    # TODO create test for this class
    def init_schema(self):
        init_library_schema_weaviate(client=self.client)

    def delete_related_documents(self):
        self.client.connect()
        try:
            documentation = client.collections.get("DocumentationFile")

            # Construct a filter to find all documents linked to the specific library
            filter_criteria = (
                Filter.by_ref(link_on="fromLibrary")
                .by_property("name")
                .equal(self.library.libname)
            )

            # Query to fetch all DocumentationFiles related to the specific Library ID
            response = documentation.query.fetch_objects(
                filters=filter_criteria,
                return_references=QueryReference(
                    link_on="fromLibrary", return_properties=["name"]
                ),
                limit=10000,  # Adjust the limit based on expected maximum or paginate queries
            )
            logging.info(f"deleting all documents from library {self.library.libname}")
            # Delete each DocumentationFile found
            for doc in response.objects:
                documentation.data.delete_by_id(doc.uuid)
                doc_query_response = documentation.query.fetch_object_by_id(doc.uuid)
                if doc_query_response is None:
                    logging.info(f"Document {doc.uuid} successfully deleted.")
                else:
                    logging.info(f"Document {doc.uuid} still exists.")
        finally:
            client.close()

    def delete_library(self):
        self.client.connect()
        try:
            library_collection = self.client.collections.get("Library")

            # Query to fetch the library by name
            library = library_collection.query.fetch_objects(
                filters=Filter.by_property("name").equal(self.library.libname),
                limit=1,  # Assuming library names are unique
            )
            logging.info(f"Deleting library {self.library.libname}")
            if library.objects:
                library_id = library.objects[0].uuid
                # Delete the library by its ID
                library_collection.data.delete_by_id(library_id)

                # Verify the deletion
                lib_query_response = library_collection.query.fetch_object_by_id(
                    library_id
                )
                if lib_query_response is None:
                    logging.info(
                        f"Library {self.library.libname} successfully deleted."
                    )
                else:
                    logging.info(f"Library {self.library.libname} still exists.")
            else:
                logging.info(f"No library found with the name {self.library.libname}.")
        finally:
            self.client.close()

    def delete_library_and_documents(self):
        # First, delete all related documentation files
        self.delete_related_documents()

        # Then, if all documents are successfully deleted, delete the library itself
        self.delete_library()


# refactor the following document to put all functions under one class
class WeaviateDocLoader(BaseWeaviateDocClient):
    """
    loads the documentation of a library from json and save it to weaviate.
    """

    def __init__(
        self,
        library: Library,
        client: weaviate.WeaviateClient,
        documentation_settings: DocumentationSettings = documentation_settings,
        secrets: Secrets = secrets,
    ):
        # superinit class
        super().__init__(library=library, client=client)
        self.documentation_settings = documentation_settings
        self.secrets = secrets
        self.apify_client = ApifyClient(secrets.apify_key)

    def load_json(self, filename: str) -> List[WebScrapingData]:
        return load_scraped_data_from_json(filename=filename)

    def get_raw_documentation(self) -> List[WebScrapingData]:
        """
        get the raw documentation from json file
        """
        data = []
        docs_dir = self.secrets.docs_dir
        filename = docs_dir + "/" + self.library.libname + ".json"
        # TODO check if all urls are present in the json file
        if os.path.exists(filename):
            logging.info(
                f"Loading scraped Documentation for library {self.library.libname} from {filename=}"
            )
            # load data using load_scraped_data_from_json function from codinit.documentation.save_document
            data = self.load_json(filename=filename)
        else:
            logging.error(f"{filename=} does not exist.")
        return data

    def chunk_doc(self, doc: WebScrapingData) -> List[str]:
        # chunk document using chunk_document function from codinit.chunk_documents.py
        chunks = chunk_document(
            document=doc.text,
            chunk_size=self.documentation_settings.chunk_size,
            overlap=self.documentation_settings.overlap,
        )
        return chunks

    # save document to weaviate
    def save_doc_to_weaviate(self, doc_obj: dict, lib_id: str) -> str:
        self.client.connect()
        documentation_collection = self.client.collections.get("DocumentationFile")
        library_collection = self.client.collections.get("Library")
        doc_id = documentation_collection.data.insert(properties=doc_obj)
        # TODO create hash of an object and query against object hash in library. If not found then save object.

        # DocumentationFile -> Library relationship
        documentation_collection.data.reference_add(
            from_uuid=doc_id,
            from_property="fromLibrary",
            to=lib_id,
        )

        # Library -> DocumentationFile relationship
        library_collection.data.reference_add(
            from_uuid=lib_id,
            from_property="hasDocumentationFile",
            to=doc_id,
        )
        logging.info(
            f"Saved document with DOC_ID {doc_id=} to library with LIB_ID {lib_id=}"
        )
        self.client.close()
        return doc_id

    # save library to weaviate
    def save_lib_to_weaviate(self):
        self.client.connect()

        # create library object
        lib_obj = {
            "name": self.library.libname,
            "links": self.library.links,
            "description": self.library.lib_desc,
        }
        library_collection = self.client.collections.get("Library")
        # save library object to weaviate
        lib_id = library_collection.data.insert(properties=lib_obj)
        self.client.close()
        logging.info(
            f"Saved library object {lib_id=} to weaviate,library has LIB_ID {lib_id=}"
        )
        return lib_id

    def get_or_create_library(self):
        """
        get or create library in weaviate
        returns lib_id
        """
        # check if library already exists
        if self.check_library_exists():
            # get library id
            lib_id = self.get_lib_id()
        else:
            # create library
            lib_id = self.save_lib_to_weaviate()
        return lib_id

    def get_or_create_documentation(self, doc_obj: dict, lib_id: str):
        """
        get or create documentation in weaviate
        returns doc_id
        """
        doc_id = self.save_doc_to_weaviate(doc_obj=doc_obj, lib_id=lib_id)
        return doc_id

    # embed documentation to weaviate
    def embed_documentation(self, data: List[WebScrapingData], lib_id: str):
        """Chunk documents and load them to weaviate.

        Args:
            data (List[WebScrapingData]): list of WebScrapingData objects
        """
        # iterate over data
        for doc in data:
            # chunk document using chunk_document function from codinit.chunk_documents.py
            chunks = self.chunk_doc(doc=doc)
            # iterate over chunks, with chunk and its order in doc
            for chunk_num, chunk in enumerate(chunks):
                # create doc_obj of the chunk according to DocumentationFile schema
                doc_obj = {
                    "title": doc.metadata.title,
                    "description": doc.metadata.description,
                    "chunknumber": chunk_num,
                    "source": str(doc.url),
                    "language": doc.metadata.languageCode,
                    "content": chunk,
                }
                # save chunk to weaviate
                doc_id = self.get_or_create_documentation(
                    doc_obj=doc_obj, lib_id=lib_id
                )
                logging.info(
                    f"Processed loading for chunk document with DOC_ID {doc_id=}"
                )

    # run
    def run(self):
        # get or create library
        lib_id = self.get_or_create_library()
        data = self.get_raw_documentation()
        n_docs = self.check_library_has_docs(lib_id=lib_id)
        if len(data) == 0:
            logging.error("No raw documentation data found.")
        elif n_docs == 0:
            logging.info(
                "Library has no documentation in weaviate. Embedding documentation now..."
            )
            self.embed_documentation(data=data, lib_id=lib_id)
            logging.info("Done embedding documentation.")


class WeaviateDocQuerier(BaseWeaviateDocClient):
    """
    queries the documentation of a library from weaviate.
    """

    def __init__(
        self,
        library: Library,
        client: weaviate.WeaviateClient,
        documentation_settings: DocumentationSettings = documentation_settings,
    ) -> None:
        super().__init__(library=library, client=client)
        self.documentation_settings = documentation_settings
        # create retriever
        self.client = self.client

    # get retriever
    def query_weaviate_docs(self, query: str):
        self.client.connect()
        documentation_collection = self.client.collections.get("DocumentationFile")
        response = documentation_collection.query.hybrid(
            query=query,
            alpha=self.documentation_settings.alpha,
            return_metadata=wvc.query.MetadataQuery(score=True, explain_score=True),
            limit=self.documentation_settings.top_k,
        )
        docs = response.objects
        self.client.close()
        return docs

    # get relevant documents for a query
    def get_relevant_documents(self, query: str) -> str:
        # clean up query that might be produced by an LLM
        query = query.replace("`", "").replace("'", "").replace('"', "")
        result = re.findall(r'"(.*?)"', query)
        if len(result) > 0:
            query = result[0]
        logging.info(f"Retrieving relevant documents for query: {query}")
        docs = self.query_weaviate_docs(query=query)
        logging.info(f"{docs=}")
        relevant_docs = ""
        for doc in docs:
            relevant_docs += doc.properties["content"]
        return relevant_docs


if __name__ == "__main__":
    # libname = "langchain"
    # links = [
    #     "https://langchain-langchain.vercel.app/docs/get_started/",
    #     # "https://python.langchain.com/docs/modules/",
    #     # "https://python.langchain.com/docs/use_cases",
    #     # "https://python.langchain.com/docs/guides",
    #     # "https://python.langchain.com/docs/integrations",
    # ]
    # library_repo_url = "https://github.com/langchain-ai/langchain.git"
    # library = Library(libname=libname, links=links, lib_repo_url=library_repo_url)

    # client = get_weaviate_client()
    # # base_weaviate_doc_client = BaseWeaviateDocClient(library=library, client=client)
    # # base_weaviate_doc_client.run()
    # weaviate_doc_loader = WeaviateDocLoader(library=library, client=client)
    # # weaviate_doc_loader.run()

    # weaviate_doc_querier = WeaviateDocQuerier(
    #     library=library, client=weaviate_doc_loader.client
    # )
    # docs = weaviate_doc_querier.get_relevant_documents(
    #     query="Using the langchain library, write code that illustrates usage of the library."
    # )
    # print(docs)
    # print(weaviate_doc_loader.get_lib_id())
    # num_docs = weaviate_doc_loader.check_library_has_docs(lib_id="some_id")
    # print(num_docs)

    libname = "quadquery"
    links = [
        "https://cadquery.readthedocs.io/en/latest/index.html",
    ]
    library_repo_url = "https://github.com/CadQuery/cadquery.git"
    library = Library(libname=libname, links=links, lib_repo_url=library_repo_url)

    client = get_weaviate_client()
    base_weaviate_doc_client = BaseWeaviateDocClient(library=library, client=client)
    base_weaviate_doc_client.delete_library()

    # weaviate_doc_loader = WeaviateDocLoader(library=library, client=client)
    # # weaviate_doc_loader.run()

    # weaviate_doc_querier = WeaviateDocQuerier(
    #     library=library, client=weaviate_doc_loader.client
    # )
    # docs = weaviate_doc_querier.get_relevant_documents(
    #     query="Using the langchain library, write code that illustrates usage of the library."
    # )
    # print(docs)
