import os
from typing import List, Type, TypeVar

import weaviate
import yaml
from dotenv import load_dotenv
from pydantic import BaseSettings, Field
from weaviate.embedded import EmbeddedOptions

# Load .env file
load_dotenv()
T = TypeVar("T", bound=BaseSettings)


def from_yaml(cls: Type[T], yaml_file: str) -> T:
    """Load settings from a YAML file and create an instance of the given class.

    Args:
        cls (Type[T]): The class of the settings object to be created.
        yaml_file (str): The path to the YAML file containing the settings.

    Returns:
        T: An instance of the settings class with the loaded settings.
    """
    with open(yaml_file, "r") as file:
        config_data = yaml.safe_load(file)
    return cls(**config_data)


class Secrets(BaseSettings):
    """settings class representing OpenAI API configuration."""

    openai_api_key: str = Field(
        "" if os.getenv("TESTING") else ..., env="OPENAI_API_KEY"
    )
    huggingface_key: str = Field(
        "" if os.getenv("TESTING") else ..., env="HUGGINGFACE_KEY"
    )
    persist_dir: str = Field("" if os.getenv("TESTING") else ..., env="PERSIST_DIR")
    model_path: str = Field("" if os.getenv("TESTING") else ..., env="MODEL_PATH")
    repo_path: str = Field("" if os.getenv("TESTING") else ..., env="REPO_DIR")
    docs_dir: str = Field("" if os.getenv("TESTING") else ..., env="DOCS_DIR")
    weaviate_url: str = Field("" if os.getenv("TESTING") else ..., env="WEAVIATE_URL")
    apify_key: str = Field("" if os.getenv("TESTING") else ..., env="APIFY_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AgentSettings(BaseSettings):
    """Configuration of coding agents"""

    planner_model: str
    dependency_model: str
    coder_model: str
    code_corrector_model: str
    linter_model: str


class EvalSettings(BaseSettings):
    """Configuration for LLM output tracking table table"""

    eval_columns: List[str]
    eval_dataset_location: str


secrets = Secrets()

eval_settings = from_yaml(EvalSettings, "configs/eval.yaml")
agent_settings = from_yaml(AgentSettings, "configs/agents.yaml")
client = weaviate.Client(
    embedded_options=EmbeddedOptions(
        persistence_data_path=secrets.persist_dir,
        additional_env_vars={
            "ENABLE_MODULES": "text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai"
        },
    ),
    additional_headers={
        "X-HuggingFace-Api-Key": secrets.huggingface_key,
        "X-OpenAI-Api-Key": secrets.openai_api_key,
    },
)
