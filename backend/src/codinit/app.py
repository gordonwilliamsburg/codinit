import asyncio
import csv
import datetime
import logging
from typing import List

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from codinit.code_editor import PythonCodeEditor
from codinit.config import eval_settings
from codinit.documentation.pydantic_models import Library
from codinit.main import get_git_info
from codinit.task_executor import TaskExecutionConfig, TaskExecutor
from codinit.weaviate_client import get_weaviate_client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


app = FastAPI()
origins = [
    "http://127.0.0.1:3000",  # replace with the origin of your Next.js app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    links: List[str]
    libname: str
    prompt: str
    source_code: str
    lib_repo_url: str


@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.websocket("/generate/")
async def generate(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        item = Item(**data)
        logging.info(f"item: {item}")
        library = Library(
            libname=item.libname, links=item.links, lib_repo_url=item.lib_repo_url
        )
        sha, message = get_git_info()
        with open(eval_settings.eval_dataset_location, "a+", newline="") as csvfile:
            fieldnames = [fieldname for fieldname in eval_settings.eval_columns]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            code_editor = PythonCodeEditor()
            config = TaskExecutionConfig()
            # libraries = item.libraries
            task = item.prompt
            # source_code=item.source_code
            task_executor = TaskExecutor(
                code_editor=code_editor,
                config=config,
                task=task,
                run_id=0,
                task_id=0,
                sha=sha,
                message=message,
                csv_writer=writer,
            )
            client = get_weaviate_client()
            attempt = 0
            initial_code_generation = task_executor.initial_code_generation(
                library=library, client=client
            )
            plan = initial_code_generation.Generated_Plan.Plan
            await websocket.send_json(
                {
                    "plan": "\n".join(plan),
                    "code": initial_code_generation.Coding_Agent.Generated_Code,
                }
            )
            error, new_code = task_executor.code_correction_with_linting(
                new_code=initial_code_generation.Coding_Agent.Generated_Code,
                deps=initial_code_generation.Dependencies.Dependencies,
                relevant_docs=initial_code_generation.Documentation_Scraping.Relevant_Docs,
                attempt=attempt,
            )
            await websocket.send_json(
                {"plan": "\n".join(plan), "code": new_code, "error": error}
            )
            await asyncio.sleep(1)  # Add a sleep delay of 1 second
            # await websocket.send_text(new_code)
            attempt = 1
            while "Failed" in error:
                if attempt > task_executor.config.coding_attempts:
                    break
                # corrected code

                await websocket.send_json(
                    {"plan": "\n".join(plan), "code": new_code, "error": error}
                )
                # corrected code
                error, new_code = task_executor.code_correction_with_linting(
                    new_code=new_code,
                    deps=initial_code_generation.Dependencies.Dependencies,
                    relevant_docs=initial_code_generation.Documentation_Scraping.Relevant_Docs,
                    attempt=attempt,
                )
                attempt += 1
            await websocket.send_json(
                {
                    "plan": "\n".join(plan),
                    "code": new_code,
                    "error": error,
                    "is_final": True,
                }
            )
