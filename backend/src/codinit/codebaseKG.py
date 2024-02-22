import logging
import os
import time
from typing import Union

import libcst
import openai
import weaviate
import weaviate.classes as wvc
from git import Repo
from openai import RateLimitError

from codinit.weaviate_client import get_weaviate_client

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def call_GPT(user_prompt: str, modelname: str = "gpt-3.5-turbo-1106"):
    """
    Simple function to call OpenAI API without function calls.
    Args:
        user_prompt: will contain a request for explanation containing variables handed in at call time where we ask GPT to formulate
            an answer about the given varables.
        modelname: GPT model to use for API call

    """
    messages = []
    # Start by adding the user's message to the messages list
    messages.append({"role": "user", "content": user_prompt})
    try:
        # Call the ChatCompletion API to get the model's response and return the result
        response = openai.chat.completions.create(
            model=modelname,
            messages=messages,
        )
        # Convert the response to an OpenAIResponse object and return
        return response.choices[0].message.content
    except RateLimitError as e:
        logging.error(
            "Rate limit reached for ChatCompletion API while code base analysis, waiting to retry..."
        )
        logging.error(f"Exception: {e}")
        # TODO adjust this constant time to extract the wait time is reported in the exception
        wait_time = 10
        time.sleep(wait_time)
        raise
    except Exception as e:
        logging.error(
            "Unable to generate ChatCompletion response while code base analysis"
        )
        logging.error(f"Exception: {e}")
        raise  # Re-raise the exception to trigger the retry mechanism


def file_already_exists(
    filename: str, link: str, client: weaviate.WeaviateClient
) -> bool:
    """
    Checks if a file has already been visited before so it can be skipped.
    """
    client.connect()
    try:
        file_collection = client.collections.get("File")
        # query if library already exists and has documentation files
        query_file_result = file_collection.query.fetch_objects(
            return_properties=["name"],
            filters=wvc.query.Filter.by_property("name").equal(filename),
            limit=5,
        )
        logging.debug(f"Query if file already exists: {query_file_result=}")

        # Process the result to check if a file with the same link exists
        file_exists = False
        for item in query_file_result.objects:
            if item.properties["link"] == link:
                file_exists = True
                break
        return file_exists

    except Exception as e:
        logging.error(f"Error in querying Weaviate: {e}")
        client.close()
        return False


# Function that queries Weaviate db to find if repo has been processed there.
# takes repo_dir and client and finds out if it can find data for the repo_dir.
def check_if_repo_has_been_embedded(
    repo_dir: str, client: weaviate.WeaviateClient
) -> bool:
    client.connect()
    repository_collection = client.collections.get("Repository")
    repository_query_result = repository_collection.query.fetch_objects(
        return_properties=["name"],
        filters=wvc.query.Filter.by_property("name").equal(repo_dir),
        limit=5,
    )
    client.close()
    library_exists = repository_query_result.objects
    if len(library_exists) == 0:
        return False
    else:
        return True


def get_full_name(node):
    """
    Function to concatenate parts of a libcst.Name or libcst.Attribute node into a single string.
    """
    if isinstance(node, libcst.Name):
        # Base case: the node is a simple Name node
        return node.value
    elif isinstance(node, libcst.Attribute):
        # Recursive case: the node is an Attribute (like "os.path")
        # Get the full name of the "value" node (like "os") and append the name of this Attribute node (like "path")
        return get_full_name(node.value) + "." + node.attr.value


class FunctionInfoCollector(libcst.CSTVisitor):
    """
    Visitor for functions in the code file that is being parsed
    """

    def __init__(self):
        self.parameters = []
        self.local_variables = []
        self.return_value = []

    def visit_Param(self, node: libcst.Param):
        if isinstance(node.name, libcst.Name):
            self.parameters.append(node.name.value)

    def visit_Assign(self, node: libcst.Assign):
        for target in node.targets:
            if isinstance(target.target, libcst.Name):
                self.local_variables.append(target.target.value)

    def visit_Return(self, node: libcst.Return):
        if isinstance(node.value, libcst.Name):
            self.return_value.append(node.value.value)


def extract_function_info(function_node):
    """
    Extract function information from function node, collects code, parameters, variables used in the function
    and rerurn value.
    """
    function_code = libcst.Module([function_node]).code
    visitor = FunctionInfoCollector()
    function_node.visit(visitor)
    return {
        "code": function_code,
        "parameters": visitor.parameters,
        "variables": visitor.local_variables,
        "return_value": visitor.return_value,
    }


class AttributeCollector(libcst.CSTVisitor):
    """
    Visitor to collect attributes from classes
    """

    def __init__(self):
        self.attributes = []

    def visit_AnnAssign(self, node: libcst.AnnAssign):
        if isinstance(node.target, libcst.Name):
            self.attributes.append(node.target.value)


def extract_attributes(class_node):
    """Gives back a list of Class attributes"""
    visitor = AttributeCollector()
    class_node.visit(visitor)
    return visitor.attributes


# TODO handle out of context length for descriptions
def parse_file(
    file_content: str,
    file_name: str,
    link: str,
    weaviate_client: weaviate.WeaviateClient,
):
    weaviate_client.connect()
    """Parse a single file and store its entities and their relationships in Weaviate."""

    # takes the Python source code (stored as a string in file_content) and parses it into an AST, which is stored in module.
    module = libcst.parse_module(file_content)
    # File entity
    file = {"name": file_name, "link": link}

    file_collection = weaviate_client.collections.get("File")
    import_collection = weaviate_client.collections.get("Import")
    function_collection = weaviate_client.collections.get("Function")
    class_collection = weaviate_client.collections.get("Class")
    # Create file in Weaviate and get its id
    file_id = file_collection.data.insert(properties=file)
    logging.debug(f"Embedded file {file_name} with {file_id=}")
    # Repository -> File relationship
    for node in module.children:
        if isinstance(node, libcst.SimpleStatementLine):
            node = node.body[0]
            if isinstance(node, libcst.ImportFrom):
                """
                when a libcst.ImportFrom object is encountered, we first get the full name of the module being imported from.
                Then, for each name being imported, we append the full name of that name to the module name (with a dot in between)
                to form the full name of the import. This ensures that imports of the form from module import function, Class
                are properly represented.
                """

                module_name = get_full_name(node.module)
                for name in node.names:
                    import_name = module_name + "." + get_full_name(name.name)
                    # print(f"visited import node {import_name}")
                    import_obj = {
                        "name": import_name,
                    }
                    # print(f"{import_obj=}")

                    # Create import in Weaviate and get its ID
                    import_id = import_collection.data.insert(properties=import_obj)

                    # File -> Import relationship
                    file_collection.data.reference_add(
                        from_uuid=file_id,
                        to=import_id,
                        from_property="hasImport",
                    )

            elif isinstance(node, libcst.Import):
                # Import entity
                for name in node.names:
                    import_name = get_full_name(name.name)
                    # print(f"visited import node {import_name}")
                    import_obj = {
                        "name": import_name,
                    }
                    # print(f"{import_obj=}")
                    # Create import in Weaviate and get its ID
                    import_id = import_collection.data.insert(properties=import_obj)

                    # File -> Import relationship
                    file_collection.data.reference_add(
                        from_uuid=file_id,
                        to=import_id,
                        from_property="hasImport",
                    )

                    # Import -> File relationship
                    import_collection.data.reference_add(
                        from_uuid=import_id,
                        from_property="belongsToFile",
                        to=file_id,
                    )

        elif isinstance(node, libcst.FunctionDef):
            # Function entity
            function_name = node.name.value
            # print(f"visited function node {function_name}")
            function_info = extract_function_info(node)
            description = ""
            """
            prompt_template = You have the following python function with name: {function_name}, function info: {function_info},
                belongs to file: {file_name}.
                What is the purpose of this function?
                Write a description of the function given the provided information.

            function_prompt = prompt_template.format(
                function_name=function_name,
                function_info=function_info,
                file_name=file_name,
            )"""
            # description = call_GPT(user_prompt=function_prompt)
            function_obj = {
                **function_info,
                "name": function_name,
                "description": description,
            }
            # print(f"{function_obj=}")
            # Create function in Weaviate and get its ID
            function_id = function_collection.data.insert(properties=function_obj)

            # File -> Function relationship
            file_collection.data.reference_add(
                from_uuid=file_id,
                from_property="hasFunction",
                to=function_id,
            )

            # TODO Function -> Code relationship

        elif isinstance(node, libcst.ClassDef):
            # Class entity
            class_name = node.name.value
            logging.info(f"visited class node {class_name}")
            class_attributes = extract_attributes(node)
            # class_code = libcst.Module([node]).code
            class_description = ""
            try:
                """
                prompt_template = You have the following class named {class_name} with code {class_code} and belongs to file: {file_name}.
                    What is the purpose of this class?
                    Write a description of the class given the provided information.

                class_prompt = prompt_template.format(
                    class_name=class_name, class_code=class_code, file_name=file_name
                )"""
                # class_description = call_GPT(user_prompt=class_prompt)
            except Exception as e:
                class_description = ""
                logging.error(e)

            class_obj = {
                "name": class_name,
                "attributes": class_attributes,
                "description": class_description,
            }
            logging.info(f"Created class object {class_obj=}")

            # Create class in Weaviate and get its ID
            class_id = class_collection.data.insert(properties=class_obj)

            # File -> Class relationship
            file_collection.data.reference_add(
                from_uuid=file_id,
                from_property="hasClass",
                to=class_id,
            )

            for sub_node in node.body.body:
                if isinstance(sub_node, libcst.FunctionDef):
                    # Function entity
                    function_name = sub_node.name.value
                    description = ""
                    # print(f"visited function class node {function_name}")
                    try:
                        function_info = extract_function_info(sub_node)
                        """
                        prompt_template = You have the following python function with name: {function_name}, function info: {function_info},
                            belongs to class: {class_name}, belongs to file: {file_name}.
                            What is the purpose of this function?
                            Write a description of the function given the provided information.

                        function_prompt = prompt_template.format(
                            function_name=function_name,
                            class_name=class_name,
                            function_info=function_info,
                            file_name=file_name,
                        )"""
                        # description = call_GPT(user_prompt=function_prompt)
                        function_obj = {
                            "name": function_name,
                            "description": description,
                            **function_info,
                        }
                        # print(f"{function_obj=}")
                        # Create function in Weaviate and get its ID
                        function_id = function_collection.data.insert(
                            properties=function_obj
                        )
                        # Class -> Function relationship
                        class_collection.data.reference_add(
                            from_uuid=class_id,
                            from_property="hasFunction",
                            to=function_id,
                        )
                        # Function -> File relationship
                        function_collection.data.reference_add(
                            from_uuid=function_id,
                            from_property="belongsToFile",
                            to=file_id,
                        )
                        # Function -> Class relationship
                        function_collection.data.reference_add(
                            from_uuid=function_id,
                            from_property="belongsToClass",
                            to=class_id,
                        )
                        # File -> Function relationship
                        file_collection.data.reference_add(
                            from_uuid=file_id,
                            from_property="hasFunction",
                            to=function_id,
                        )
                    except AttributeError as e:
                        logging.error(e)

    return file_id


def analyze_directory(
    directory: str, repo_url: str, weaviate_client: weaviate.WeaviateClient
):
    """
    Analyzes all Python files in a directory (and its subdirectories), collects a
    list of dictionaries containing filename, function names, and class names for each file.
    """
    weaviate_client.connect()
    logging.info(f"Analyzing Code Directory {directory=}")
    # File entity
    directory_obj = {
        "name": directory,
        "link": repo_url,
    }
    repository_collection = weaviate_client.collections.get("Repository")
    # Create file in Weaviate and get its id
    directory_id = repository_collection.data.insert(properties=directory_obj)
    logging.info(
        f"created directory object in weaviate db {directory_obj=} with {directory_id=}"
    )
    for root, _, files in os.walk(directory):
        logging.info(f"Found following files in directory {root=}: {files=}")
        for file in files:
            if file.endswith(".py"):  # Process only Python files
                file_path = os.path.join(root, file)
                logging.info(
                    f"Analyzing file {file_path=}, will skip if analysis exists---------"
                )
                with open(file_path, "r") as f:
                    file_content = f.read()
                file_exists = file_already_exists(
                    filename=file, link=file_path, client=weaviate_client
                )
                if not file_exists:
                    file_id = parse_file(
                        file_content, file, file_path, weaviate_client
                    )  # Analyze the file and add its data to the weaviate db
                    logging.info(
                        f"File analysis complete. Analyzed file {file_id=}---------"
                    )
                    # Repository -> File relationship
                    repository_collection.data.reference_add(
                        from_uuid=directory_id,
                        from_property="hasFile",
                        to=file_id,
                    )

    return directory_id


def clone_repo(repo_url: str, local_dir: Union[str, os.PathLike]) -> None:
    """
    Clones a Git repository to a specified local directory.

    :param repo_url: URL of the Git repository to clone.
    :param local_dir: Local directory path where the repository should be cloned.
    """
    try:
        Repo.clone_from(repo_url, local_dir)
        logging.info(f"Repository cloned successfully to {local_dir}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


# Function that checks if repo has been cloned using libname
# takes libname and repo_dir and finds out if it can find a folder with libname
def check_if_repo_has_been_cloned(repo_dir: Union[str, os.PathLike]) -> bool:
    if os.path.isdir(repo_dir):
        return True
    else:
        return False


def clone_repo_if_not_exists(repo_url: str, local_dir: Union[str, os.PathLike]) -> None:
    if not check_if_repo_has_been_cloned(local_dir):
        clone_repo(repo_url, local_dir)
        logging.info(f"Repository cloned successfully to {local_dir}")
    else:
        logging.info(f"Repository has already been cloned to {local_dir}")


# check if library has been embedded to weaviate, otherwise embed it using analyze_directory
def embed_repository_if_not_exists(
    repo_dir: str, repo_url: str, client: weaviate.WeaviateClient
) -> None:
    if not check_if_repo_has_been_embedded(repo_dir, client):
        logging.info(f"Found no embedding for library {repo_dir=}, embedding now...")
        analyze_directory(
            directory=repo_dir,
            repo_url=repo_url,
            weaviate_client=client,
        )
        logging.info(
            f"Repository {repo_dir=} has now been embedded successfully to Weaviate"
        )
    else:
        logging.info(f"Repository {repo_dir=} has already been embedded to Weaviate")


def run_codebase_analysis(
    repo_dir: str, libname: str, repo_url: str, client: weaviate.WeaviateClient
) -> None:
    logging.info(f"Running analysis for {libname=}")
    repo_dir = repo_dir + "/" + libname
    clone_repo_if_not_exists(repo_url, local_dir=repo_dir)
    embed_repository_if_not_exists(repo_dir, repo_url, client)
    logging.info(f"Analysis for {libname=} completed successfully")


# check if repo has been cloned
# if not, clone it
# check if repo has been analyzed
# if not, analyze it
if __name__ == "__main__":
    from codinit.config import secrets

    libname = "langchain"
    repo_dir = secrets.repo_dir
    repo_url = "https://github.com/langchain-ai/langchain.git"
    client = get_weaviate_client()
    run_codebase_analysis(
        repo_dir=repo_dir, libname=libname, repo_url=repo_url, client=client
    )
    """
    analyze_directory(
        directory= repo_dir + "/libs/langchain/langchain",
        repo_url=repo_url,
        client=client,
    )
    """
