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
