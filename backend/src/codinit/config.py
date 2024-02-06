from typing import List, Type, TypeVar

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()
T = TypeVar("T", bound=BaseSettings)  # type: ignore


def from_yaml(cls: Type[T], yaml_file: str) -> T:  # type: ignore
    """Load settings from a YAML file and create an instance of the given class.

    Args:
        cls (Type[T]): The class of the settings object to be created.
        yaml_file (str): The path to the YAML file containing the settings.

    Returns:
        T: An instance of the settings class with the loaded settings.
    """
    with open(yaml_file, "r") as file:
        config_data = yaml.safe_load(file)
    return cls(**config_data)  # type: ignore


class Secrets(BaseSettings):  # type: ignore
    """settings class representing OpenAI API configuration."""

    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    huggingface_key: str = Field(..., validation_alias="HUGGINGFACE_KEY")
    persist_dir: str = Field(..., validation_alias="PERSIST_DIR")
    docs_dir: str = Field(..., validation_alias="DOCS_DIR")
    apify_key: str = Field(..., validation_alias="APIFY_KEY")
    repo_dir: str = Field(..., validation_alias="REPO_DIR")
    model_config = SettingsConfigDict(env_file="prod.env", env_file_encoding="utf-8")


class AgentSettings(BaseSettings):  # type: ignore
    """Configuration of coding agents"""

    planner_model: str
    dependency_model: str
    coder_model: str
    code_corrector_model: str
    linter_model: str


class EvalSettings(BaseSettings):  # type: ignore
    """Configuration for LLM output tracking table table"""

    eval_columns: List[str]
    eval_dataset_location: str


class DocumentationSettings(BaseSettings):  # type: ignore
    """Configuration for documentation generation"""

    chunk_size: int
    overlap: int
    top_k: int
    alpha: float


secrets = Secrets()

eval_settings = from_yaml(EvalSettings, "configs/eval.yaml")  # type: ignore
agent_settings = from_yaml(AgentSettings, "configs/agents.yaml")  # type: ignore
documentation_settings = from_yaml(DocumentationSettings, "configs/documentation.yaml")  # type: ignore
