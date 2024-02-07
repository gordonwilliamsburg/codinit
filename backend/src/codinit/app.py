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
            time_stamp = datetime.datetime.now().isoformat()
            client = get_weaviate_client()
            task_executor.scrape_docs(library=library)
            relevant_docs = task_executor.get_docs(
                library=library, task=task, client=client
            )
            plan = task_executor.planner.execute(
                tool_choice="execute_plan",
                chat_history=[],
                task=task,
                context=relevant_docs,
            )[0]
            await websocket.send_json({"plan": "\n".join(plan), "code": ""})
            # install dependencies from plan
            if (
                task_executor.config.execute_code
                and task_executor.config.install_dependencies
            ):
                deps = task_executor.dependency_tracker.execute(
                    tool_choice="install_dependencies", chat_history=[], plan=plan
                )[0]
                await websocket.send_json(
                    {
                        "plan": "",
                        "code": "",
                        "error": f"dependencies to install: {deps}",
                    }
                )
                task_executor.install_dependencies(deps)
            chat_history = []
            chat_history.append(
                {"role": "assistant", "content": f"installed dependencies {deps}"}
            )
            # generate code
            new_code = task_executor.coder.execute(
                task=task,
                tool_choice="execute_code",
                chat_history=chat_history,
                plan=plan,
                context=relevant_docs,
            )[0]
            attempt = 0
            error, new_code = task_executor.code_correction_with_linting(
                new_code=new_code,
                deps=deps,
                relevant_docs=relevant_docs,
                attempt=attempt,
                time_stamp=time_stamp,
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
                time_stamp = datetime.datetime.now().isoformat()
                # corrected code
                error, new_code = task_executor.code_correction_with_linting(
                    new_code=new_code,
                    deps=deps,
                    relevant_docs=relevant_docs,
                    attempt=attempt,
                    time_stamp=time_stamp,
                )
                # await websocket.send_text(new_code)
                attempt += 1
            await websocket.send_json(
                {
                    "plan": "\n".join(plan),
                    "code": new_code,
                    "error": error,
                    "is_final": True,
                }
            )
