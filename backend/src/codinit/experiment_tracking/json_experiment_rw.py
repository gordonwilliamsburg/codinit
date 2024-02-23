import json

from pydantic import TypeAdapter

from codinit.experiment_tracking.experiment_pydantic_models import Run


# Write a list of Run objects to a JSON file
def write_to_json(file_path: str, data: Run):
    with open(file_path, "w", encoding="utf-8") as file:
        # Convert the Pydantic models to JSON
        json_data = data.model_dump_json()
        json.dump(json_data, file, ensure_ascii=False, indent=4)


def read_from_json2(file_path: str) -> Run:
    with open(file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        typeadapter = TypeAdapter(Run)
        # create list of WebScrapingData models from json data
        return typeadapter.validate_python(json_data)


def read_from_json(file_path: str) -> Run:
    with open(file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        # Ensure json_data is a dictionary, not a string
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        # Create a Run instance from the json data
        return Run(**json_data)
