import json
from codinit.documentation.save_document import save_scraped_data_as_json


def test_save_scraped_data_as_json(mocker, sample_data):
    # use mocker.patch to mock the built-in open function
    # allows to track how open is called without actually performing file operations.
    mock_file_open = mocker.patch('builtins.open', mocker.mock_open())

    filename = "test_data.json"
    save_scraped_data_as_json(sample_data, filename)

    # Construct the expected JSON string
    expected_json_str = json.dumps(
        [item.model_dump() for item in sample_data],
        ensure_ascii=False,
        indent=4
    )

    # checks that the function save_scraped_data_as_json called the funciton open with the correct arguments
    # purpose: ensure that function interacts with the file system as expected
    mock_file_open.assert_called_once_with(filename, 'w', encoding='utf-8')

    # Concatenate all the arguments of write calls
    # because json.dump writes to the file object in multiple small chunks.
    written_content = "".join(call_args[0][0] for call_args in mock_file_open().write.call_args_list)

    # assert that the concatenated string matches the expected JSON content
    assert written_content == expected_json_str
