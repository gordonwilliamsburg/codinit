import json
import os
from codinit.documentation.get_context import WeaviateDocLoader
import weaviate
import pytest
from unittest.mock import Mock, mock_open, call
from unittest.mock import patch
from codinit.documentation.doc_schema import library_class, documentation_file_class
# Create a fixture to mock the weaviate.Client object
@pytest.fixture
def mock_client():
    """
    A mock of the Weaviate client's interactions. Specifically, will mock the create and reference.add methods of the data_object attribute of the Weaviate client.
    This will allow to verify that the method correctly saves a document and establishes the necessary relationships in Weaviate.
    """
    # Create a mock of the weaviate.Client
    client = Mock(spec=weaviate.Client)

    client.data_object = Mock()
    client.data_object.create = Mock()
    client.data_object.reference = Mock()
    client.data_object.reference.add = Mock()
    client.schema = Mock()
    client.schema.get= Mock(return_value= {'classes': [library_class, documentation_file_class]})
    client.schema.create= Mock()
    return client

def test_weaviate_doc_loader_initialization(mock_client, mock_documentation_settings, mock_library, mock_secrets):
    # Mock ApifyClient using create_autospec to respect the signature of the real class
    with patch('codinit.documentation.get_context.ApifyClient', create_autospec=True) as mock_apify_client_constructor:
        # Initialize WeaviateDocLoader
        doc_loader = WeaviateDocLoader(
            library=mock_library,
            client=mock_client,
            documentation_settings=mock_documentation_settings,
            secrets=mock_secrets
        )

        # Assertions to ensure all attributes are set correctly
        assert doc_loader.library == mock_library
        assert doc_loader.client == mock_client
        assert doc_loader.documentation_settings == mock_documentation_settings
        assert doc_loader.secrets == mock_secrets
        # Check that an ApifyClient instance was created with the correct API key
        mock_apify_client_constructor.assert_called_with(mock_secrets.apify_key)


def test_get_raw_documentation_file_exists(mock_library, mock_client, mock_documentation_settings, mock_secrets, sample_data):
    """
    verifies that the file existence check, file reading, and data loading are called with the correct arguments,
    and that the method returns the correct data.
    """
    # Mock os.path.exists to simulate the file exists function, simulates the presence of the JSON file.
    mock_exists = Mock(return_value=True)
    os.path.exists = mock_exists

    # Mock the load_scraped_data_from_json function, simulates the loading of data from the JSON file.
    mock_load_json = Mock(return_value=sample_data)
    WeaviateDocLoader.load_json = mock_load_json

    # mock the file open and read operations.
    mock_file_open = mock_open(read_data=json.dumps([data.dict() for data in sample_data]))
    with patch('builtins.open', mock_file_open):
        # Initialize WeaviateDocLoader
        doc_loader = WeaviateDocLoader(
            library=mock_library,
            client=mock_client,
            documentation_settings=mock_documentation_settings,
            secrets=mock_secrets
        )

        # Call get_raw_documentation
        result = doc_loader.get_raw_documentation()

        # Check if file exists was called
        mock_exists.assert_called_once_with(mock_secrets.docs_dir + "/" + mock_library.libname + ".json")

        # Check if load_json was called with the correct filename
        mock_load_json.assert_called_once_with(filename=mock_secrets.docs_dir + "/" + mock_library.libname + ".json")

        # Assert that the returned data matches the sample data
        assert result == sample_data

def test_chunk_doc(mock_library, mock_client, mock_documentation_settings, mock_secrets, sample_data):
    # Initialize WeaviateDocLoader
    doc_loader = WeaviateDocLoader(
        library=mock_library,
        client=mock_client,
        documentation_settings=mock_documentation_settings,
        secrets=mock_secrets
    )

    # Mock the chunk_document function
    with patch('codinit.documentation.get_context.chunk_document', return_value=["chunk1", "chunk2"]) as mock_chunk_document:
        sample_web_scraping_data = sample_data[0]
        # Call chunk_doc
        result = doc_loader.chunk_doc(doc=sample_web_scraping_data)

        # Check if chunk_document was called with correct parameters
        mock_chunk_document.assert_called_once_with(
            document=sample_web_scraping_data.text,
            chunk_size=mock_documentation_settings.chunk_size,
            overlap=mock_documentation_settings.overlap
        )

        # Assert that the returned chunks match the mock return value
        assert result == ["chunk1", "chunk2"]

def test_save_doc_to_weaviate(mock_library, mock_client, mock_documentation_settings, mock_secrets):
    # Initialize WeaviateDocLoader
    doc_loader = WeaviateDocLoader(
        library=mock_library,
        client=mock_client,
        documentation_settings=mock_documentation_settings,
        secrets=mock_secrets
    )

    # Create a mock document object and a mock library ID
    mock_doc_obj = {"some": "data"}
    mock_lib_id = "mock_lib_id"
    mock_doc_id = "mock_doc_id"

    # Mock the Weaviate client's create and reference.add methods
    mock_client.data_object.create.return_value = mock_doc_id

    # Call save_doc_to_weaviate methood
    doc_loader.save_doc_to_weaviate(doc_obj=mock_doc_obj, lib_id=mock_lib_id)

    # Assert that create was called correctly
    mock_client.data_object.create.assert_called_once_with(
        data_object=mock_doc_obj, class_name="DocumentationFile"
    )

    # Assert that reference.add was called correctly for both relationships
    calls = [
        call(
            from_class_name="DocumentationFile",
            from_uuid=mock_doc_id,
            from_property_name="fromLibrary",
            to_class_name="Library",
            to_uuid=mock_lib_id,
        ),
        call(
            from_class_name="Library",
            from_uuid=mock_lib_id,
            from_property_name="hasDocumentationFile",
            to_class_name="DocumentationFile",
            to_uuid=mock_doc_id,
        )
    ]
    mock_client.data_object.reference.add.assert_has_calls(calls, any_order=True)

def test_weaviate_doc_loader_integration(test_embedded_weaviate_client, mock_library, mock_documentation_settings, mock_secrets, sample_data):
    # Initialize WeaviateDocLoader
    doc_loader = WeaviateDocLoader(
        library=mock_library,
        client=test_embedded_weaviate_client,
        documentation_settings=mock_documentation_settings,
        secrets=mock_secrets
    )
    # Example operation: Create or get a library
    lib_id = doc_loader.get_or_create_library()
    # Example operation: Embed documentation
    doc_loader.embed_documentation(data=sample_data, lib_id=lib_id)

    # Perform assertions or verifications
    # Example: Retrieve and verify the saved document from Weaviate
    query_result = test_embedded_weaviate_client.query.get('Library', properties=['name', "hasDocumentationFile {... on DocumentationFile {title}}"]).do()

    # query_result : {'data': {'Get': {'Library': [{'hasDocumentationFile': [{'title': 'Example Title'}], 'name': 'langchain'}]}}}
    assert query_result['data']['Get']['Library']
    assert query_result['data']['Get']['Library'][0]['name'] == mock_library.libname
    assert query_result['data']['Get']['Library'][0]['hasDocumentationFile'][0]['title'] == sample_data[0].metadata.title

    query_result = test_embedded_weaviate_client.query.get('DocumentationFile', properties=['fromLibrary {... on Library {name}}']).do()
    # query_result: {'data': {'Get': {'DocumentationFile': [{'fromLibrary': [{'name': 'langchain'}]}]}}}
    assert query_result['data']['Get']['DocumentationFile']
    assert query_result['data']['Get']['DocumentationFile'][0]['fromLibrary'][0]['name'] == mock_library.libname

# TODO test that the given doc adheres to the weaviate schema
