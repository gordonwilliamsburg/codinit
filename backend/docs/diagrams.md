# Diagram tools

## pyreverse

you can use `pyreverse` to automatically generate UML diagrams for your code. it is included in the package `pylint`. To use:

```bash
pyreverse code_dir
```

this is going to generate a file called called `classes.dot` which contains the UML diagram, and a file called `packages.dot`, which contains the dependency graph of your project. In order to convert this file to an image, you can use `dot`.
For this you need to locally install `graphviz` so that you can access the command `dot`. After installing `graphviz`, use the command:

```bash
dot -Tpng classes.dot > class_diagram.png
```

### Task execution Interaction Graph

```mermaid
graph TD;
    A[execute_and_log] -->|get_docs| B[get relevant documents]
    B -->|execute planner| C[generate coding plan]
    C -->|plan output| D[check config & install dependencies]
    D --> E[log dependency installation]
    D -->|execute coder| F[generate new code]
    F -->|code correction & linting| G[corrected code]
    G -->|error check| H{error check loop}
    H -->|Failed| I[attempt increment & re-correct]
    I --> H
    H -->|No Error| J[return new code]
```


### Task execution Sequence Diagram


```mermaid
sequenceDiagram
    participant Client as get_weaviate_client()
    participant Docs as get_docs()
    participant Planner as planner.execute()
    participant DepTracker as dependency_tracker.execute()
    participant Installer as install_dependencies()
    participant Coder as coder.execute()
    participant CodeCorr as code_correction_with_linting()
    participant ErrorCheck

    activate Client
    Client->>Docs: retrieve client
    deactivate Client

    activate Docs
    Docs->>Planner: get relevant documents
    deactivate Docs

    activate Planner
    Planner->>DepTracker: generate coding plan
    deactivate Planner

    activate DepTracker
    DepTracker->>Installer: execute dependencies plan
    deactivate DepTracker

    activate Installer
    Installer->>Coder: install dependencies
    deactivate Installer

    activate Coder
    Coder->>CodeCorr: generate new code
    deactivate Coder

    loop Until code is error-free or max attempts reached
        activate CodeCorr
        CodeCorr->>ErrorCheck: correct and lint code
        deactivate CodeCorr

        activate ErrorCheck
        ErrorCheck->>CodeCorr: check for errors
        deactivate ErrorCheck
    end

    CodeCorr->>Client: return final code
```

### App Sequence Diagram

```mermaid
sequenceDiagram
    participant Client as Web Client
    participant WS as WebSocket
    participant FastAPI as FastAPI Server
    participant Executor as TaskExecutor
    participant Weaviate as get_weaviate_client()
    participant Docs as get_docs()
    participant PlanGen as Planner
    participant Coder as Coder
    participant CodeCorr as code_correction_with_linting()

    Client->>WS: Connect to WebSocket (/generate/)
    WS->>FastAPI: Client connects
    FastAPI->>Executor: Initialize TaskExecutor
    Executor->>Weaviate: Retrieve client
    Weaviate->>Docs: Get relevant documents
    Docs->>PlanGen: Generate execution plan
    PlanGen->>Executor: Return execution plan
    Executor->>Coder: Generate initial code
    Coder->>CodeCorr: Correct and lint initial code
    alt Error Found
        CodeCorr->>Executor: Attempt to correct code
        Executor->>CodeCorr: Reapply corrections
    else No Error
    end
    Executor->>WS: Send final execution plan, code, and error status
    WS->>Client: Send response (JSON)
    Client->>WS: Send next request or close
    WS->>FastAPI: Close WebSocket
```
