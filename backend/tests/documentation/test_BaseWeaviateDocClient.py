import pytest
from codinit.documentation.get_context import BaseWeaviateDocClient
from codinit.documentation.pydantic_models import Library
import weaviate
import logging

@pytest.fixture
def mock_library():
    libname = "langchain"
    links = [
        "https://langchain-langchain.vercel.app/docs/get_started/",
        "https://python.langchain.com/docs/modules/"
    ]
    library = Library(libname=libname, links=links)
    return library

def test_check_library_exists_true(mock_library, mocker):
    # Create a mock for the client
    mock_client = mocker.Mock(spec=weaviate.Client)

    # Mocking the chain with appropriate return values
    mock_client.query = mocker.Mock()

    # Set a return value for the scenario being tested
    mock_result = {"data": {"Get": {"Library": [{"name": "langchain"}]}}}
    mock_client.query.get().with_where().do = mocker.Mock(return_value=mock_result)

    # Create an instance of the class with the mocked client
    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    # Act
    result = client.check_library_exists()

    # Assert
    assert result is True

def test_check_library_exists_false(mock_library, mocker):
    # Create a mock for the client
    mock_client = mocker.Mock(spec=weaviate.Client)

    # Mocking the chain with appropriate return values
    mock_client.query = mocker.Mock()

    # Set a return value for the scenario being tested
    mock_result = {'data': {'Get': {'Library': []}}}
    mock_client.query.get().with_where().do = mocker.Mock(return_value=mock_result)

    # Create an instance of the class with the mocked client
    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    # Act
    result = client.check_library_exists()

    # Assert
    assert result is False

def test_get_lib_id_found(mock_library, mocker):
    # Arrange the mock client to return an ID
    mock_client = mocker.Mock(spec=weaviate.Client)
    mock_client.query = mocker.Mock()
    mock_result = {'data': {'Get': {'Library': [{'name': 'langchain', '_additional': {'id': '1234567890'}}]}}}
    mock_client.query.get().with_where().with_additional().do = mocker.Mock(return_value=mock_result)

    # Create an instance of the class with the mocked client
    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    # Act
    result = client.get_lib_id()

    # Assert
    assert result == '1234567890'



def test_get_lib_id_multiple_found(mock_library, mocker):
    # Arrange the mock client to return multiple IDs
    mock_client = mocker.Mock(spec=weaviate.Client)
    mock_client.query = mocker.Mock()
    mock_result = {'data': {'Get': {'Library': [{'name': 'langchain', '_additional': {'id': '1234567890'}}, {'name': 'langchain', '_additional': {'id': '9876543210'}}]}}}
    mock_client.query.get().with_where().with_additional().do = mocker.Mock(return_value=mock_result)

    # Create an instance of the class with the mocked client
    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    # Act
    result = client.get_lib_id()

    # Assert
    assert result == '1234567890'


def test_get_lib_id_not_found(mock_library, mocker):
    # Arrange the mock client to return no ID
    mock_client = mocker.Mock(spec=weaviate.Client)
    mock_client.query = mocker.Mock()
    mock_result = {'data': {'Get': {'Library': []}}}
    mock_client.query.get().with_where().with_additional().do = mocker.Mock(return_value=mock_result)

    # Create an instance of the class with the mocked client
    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    # Act
    result = client.get_lib_id()

    # Assert
    assert result is None



def test_check_library_has_no_docs(mock_library, mocker, caplog):
    # Mock client setup
    mock_client = mocker.Mock(spec=weaviate.Client)
    mock_client.query = mocker.Mock()
    mock_result = {'data': {'Get': {'Library': [{'hasDocumentationFile': None, 'name': 'langchain'}]}}}
    mock_client.query.get().with_where().do = mocker.Mock(return_value=mock_result)

    # Create an instance of the class with the mocked client
    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    with caplog.at_level(logging.WARNING):
        # Act
        num_docs = client.check_library_has_docs(lib_id='lib_with_no_docs_id')

        # Assert
        assert num_docs == 0
        assert 'Library with ID lib_with_no_docs_id has no documentation files.' in caplog.text


def test_check_library_has_multiple_docs(mock_library, mocker):
    # Mock client setup
    mock_client = mocker.Mock(spec=weaviate.Client)
    mock_client.query = mocker.Mock()

    # Correct mock result
    mock_result = {
        'data': {
            'Get': {
                'Library': [
                    {
                        'hasDocumentationFile': [{'title': 'title1'}, {'title': 'title2'}],
                        'name': 'langchain'
                    }
                ]
            }
        }
    }
    mock_client.query.get().with_where().do = mocker.Mock(return_value=mock_result)

    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    # Act
    num_docs = client.check_library_has_docs(lib_id='test_id')

    # Assert
    assert num_docs == 2

def test_check_library_has_no_docs_with_nonexistent_library(mock_library, mocker, caplog):
    # Mock client setup
    mock_client = mocker.Mock(spec=weaviate.Client)
    mock_client.query = mocker.Mock()
    mock_client.query.get().with_where().do.return_value = {'data': {'Get': {'Library': []}}}

    client = BaseWeaviateDocClient(library=mock_library, client=mock_client)

    with caplog.at_level(logging.ERROR):
        # Act with a non-existent lib_id
        num_docs = client.check_library_has_docs(lib_id="nonexistent_lib_id")

        # Assert
        assert num_docs == 0
        assert "Error getting library with ID nonexistent_lib_id from weaviate." in caplog.text
