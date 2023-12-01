import asyncio
from typing import List

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from pydantic import BaseModel

from codinit.code_editor import PythonCodeEditor
from codinit.config import client
from codinit.get_context_ import get_relevant_documents
from codinit.queries import get_functions
from codinit.task_executor import TaskExecutionConfig, TaskExecutor

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
    libraries: List[str]
    prompt: str
    source_code: str


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
        print(item.libraries)
        print(item.prompt)
        print(item.source_code)

        code_editor = PythonCodeEditor()
        config = TaskExecutionConfig()
        # libraries = item.libraries
        task = item.prompt
        # source_code=item.source_code
        task_executor = TaskExecutor(code_editor, config)
        retriever = WeaviateHybridSearchRetriever(
            client=client,
            index_name="DocumentionFile",
            text_key="content",
            k=5,
            alpha=0.75,
        )
        relevant_docs = get_relevant_documents(query=task, retriever=retriever)
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
                {"plan": "", "code": "", "error": f"dependencies to install: {deps}"}
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
        new_code, _, _ = task_executor.format_lint_code(
            code=new_code, dependencies=deps
        )
        error = task_executor.run_code(new_code)
        await websocket.send_json(
            {"plan": "\n".join(plan), "code": new_code, "error": error}
        )
        await asyncio.sleep(1)  # Add a sleep delay of 1 second
        # await websocket.send_text(new_code)
        # run generated code
        attempt = 0
        while "Failed" in error:
            if attempt > task_executor.config.coding_attempts:
                break
            # corrected code
            new_code = task_executor.code_corrector.execute(
                tool_choice="execute_code",
                chat_history=[],
                task=task,
                context=relevant_docs,
                source_code=new_code,
                error=error,
            )[0]
            new_code, _, _ = task_executor.format_lint_code(
                code=new_code, dependencies=deps
            )
            await websocket.send_json(
                {"plan": "\n".join(plan), "code": new_code, "error": error}
            )
            # await websocket.send_text(new_code)
            error = task_executor.run_code(new_code)
            attempt += 1
        await websocket.send_json(
            {
                "plan": "\n".join(plan),
                "code": new_code,
                "error": error,
                "is_final": True,
            }
        )
