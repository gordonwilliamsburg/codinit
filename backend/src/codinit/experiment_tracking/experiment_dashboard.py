import os

import streamlit as st
from pydantic import ValidationError

from codinit.experiment_tracking.experiment_pydantic_models import (
    CorrectionLoop,
    InitialCode,
    LintingAttempt,
    SelfHealingBlock,
    Task,
)
from codinit.experiment_tracking.json_experiment_rw import read_from_json

# Set the page layout to wide
st.set_page_config(layout="wide")
# Load your data
run = read_from_json(
    "data/experiment_logs/Run_18/task_1_20240226160624.json"
)  # Replace with your JSON file path


def list_runs(base_dir: str):
    """
    List all run directories within the base directory.
    """
    return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]


def list_tasks(run_dir: str):
    """
    List all task JSON files within a run directory.
    """
    return [f for f in os.listdir(run_dir) if os.path.isfile(os.path.join(run_dir, f))]


def display_initial_code(initial_code: InitialCode):
    # Display Timestamp
    with st.container():
        st.write("Timestamp:", initial_code.Timestamp)

    # Display Documentation Scraping in Markdown
    with st.container():
        st.markdown("#### Documentation Search Results")
        st.write(
            "Number of Tokens in Docs:", initial_code.Documentation_Scraping.num_tokens
        )
        st.text(f"> {initial_code.Documentation_Scraping.Relevant_Docs}")

    # Display Generated Plan
    with st.container():
        st.markdown("#### Generated Plan")
        plan = "\n".join([f"{step}" for step in initial_code.Generated_Plan.Plan])
        st.markdown(plan)

    # Display Dependencies in a Python code block
    with st.container():
        st.markdown("#### Dependencies ")
        dependencies_code = "\n".join(
            [f"{dependency}" for dependency in initial_code.Dependencies.Dependencies]
        )
        st.code(dependencies_code, language="python")

    # Display Coding Agent Thought in Markdown
    with st.container():
        st.markdown("#### Coding Agent Thought")
        chat_message = st.chat_message("Agent Thought")
        chat_message.write(initial_code.Coding_Agent.Thought)

    # Display Generated Code with code formatting
    with st.container():
        st.markdown("#### Generated Code")
        st.code(initial_code.Coding_Agent.Generated_Code, language="python")


def display_linting_attempt(linting_attempt: LintingAttempt):
    st.markdown(f"### Lint Attempt: {linting_attempt.lint_attempt}")
    st.write("Metric:", linting_attempt.Metric)
    with st.container():
        st.write(f"Timestamp: {linting_attempt.Timestamp}")
    if linting_attempt.Code:
        st.markdown("#### Given Code")
        st.code(linting_attempt.Code, language="python")
    if linting_attempt.Lint_Query_Result:
        st.markdown("#### Lint Query Result from CodeBaseKG")
        st.text_area("", linting_attempt.Lint_Query_Result)
    if linting_attempt.Lint_Response:
        with st.container():
            st.markdown("#### Lint LLM Response")
            chat_message = st.chat_message("Lint Response")
            chat_message.write(linting_attempt.Lint_Response)
    if linting_attempt.Generated_Code:
        # Display Coding Agent Thought in Markdown
        with st.container():
            st.markdown("#### Coding Agent Thought")
            chat_message = st.chat_message("Agent Thought")
            chat_message.write(linting_attempt.Generated_Code.Thought)

        # Display Generated Code with code formatting
        with st.container():
            st.markdown("#### Generated Code")
            st.code(linting_attempt.Generated_Code.Generated_Code, language="python")

    with st.container():
        st.markdown("#### Lint Result")
        st.code(linting_attempt.Lint_Result, language="bash")


def display_correction_loop(correction_loop: CorrectionLoop):
    st.markdown("### Code Correction Attempt")
    st.write("Metric:", correction_loop.Metric)
    with st.container():
        st.write(f"Timestamp: {correction_loop.Timestamp}")
    with st.container():
        st.markdown("#### Error")
        st.code(correction_loop.Error1, language="bash")
    # Display Coding Agent Thought in Markdown
    with st.container():
        st.markdown("#### Coding Agent Thought")
        chat_message = st.chat_message("Agent Thought")
        chat_message.write(correction_loop.Generated_Code.Thought)
    # Display Generated Code with code formatting
    with st.container():
        st.markdown("#### Generated Code")
        st.code(correction_loop.Generated_Code.Generated_Code, language="python")
    with st.container():
        st.markdown("#### Lint Result")
        st.code(correction_loop.Lint_Result, language="bash")

    with st.container():
        st.markdown("#### Error")
        st.code(correction_loop.Error2, language="bash")


def display_self_healing_block(block: SelfHealingBlock):
    st.subheader(f"Generation ID: {block.Generation_ID}")
    st.write("Time:", block.time)
    st.write("Overall Metric:", block.Metric)
    if st.button(f"Show Details for Self Healing Attempt {block.Generation_ID}"):
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                for linting_attempt in block.Linting_Loop:
                    display_linting_attempt(linting_attempt)

            with col2:
                display_correction_loop(block.Correction_Loop)


def display_task(task: Task):
    st.subheader(f"Task ID: {task.Task_ID}")
    st.write(f"Task Description: {task.Task}")
    st.metric("Metric:", task.Metric)
    st.write(f"Time: {task.Time}")

    with st.expander("Initial Code Details"):
        display_initial_code(task.Initial_Code)

    for attempt in task.Generation_Attempts:
        display_self_healing_block(attempt)


base_dir = "data/experiment_logs"
runs = list_runs(base_dir)
selected_run = st.sidebar.selectbox("Select Run", runs)
if selected_run:
    run_dir = os.path.join(base_dir, selected_run)
    tasks = list_tasks(run_dir)
    selected_task_file = st.sidebar.selectbox("Select Task", tasks)

    if selected_task_file:
        file_path = os.path.join(run_dir, selected_task_file)
        try:
            # Assuming read_from_json function exists
            run_data = read_from_json(file_path)
        except ValidationError as e:
            st.error(f"Error loading task data: {e}")
        except FileNotFoundError:
            st.error("Selected task file not found.")

# Main area
st.title("Coding Assistant Dashboard")

# Display the selected run
selected_run = run_data
if selected_run:
    st.header(f"Run ID: {selected_run.Run_ID}")
    st.write(f"Git SHA: {selected_run.Git_SHA}")
    st.write(f"Commit Message: {selected_run.Commit_Message}")

    # Display each task in the selected run
    for task in selected_run.Tasks:
        display_task(task)
