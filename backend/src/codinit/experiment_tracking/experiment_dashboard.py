import streamlit as st

from codinit.experiment_tracking.experiment_pydantic_models import (
    CorrectionLoop,
    InitialCode,
    LintingAttempt,
    Run,
    SelfHealingBlock,
    Task,
)
from codinit.experiment_tracking.json_experiment_rw import read_from_json

# Set the page layout to wide
st.set_page_config(layout="wide")
# Load your data
run = read_from_json("data/dummy_run.json")  # Replace with your JSON file path


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
        st.markdown(f"> {initial_code.Documentation_Scraping.Relevant_Docs}")

    # Display Generated Plan
    with st.container():
        st.markdown("#### Generated Plan")
        st.markdown(f"> {', '.join(initial_code.Generated_Plan.Plan)}")

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
    with st.container():
        st.markdown("#### Lint Result")
        st.code(linting_attempt.Lint_Result, language="bash")
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


def display_correction_loop(correction_loop: CorrectionLoop):
    st.markdown(
        f"### Code Correction Attempt: {correction_loop.code_correction_attempt}"
    )
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
    st.markdown(f"### Self Healing Attempt {block.Self_Healing_Attempt}")
    st.write("Time:", block.time)
    st.write("Overall Metric:", block.Metric)
    if st.button(f"Show Details for Self Healing Attempt {block.Self_Healing_Attempt}"):
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


# Sidebar for selecting a run
selected_run_id = st.sidebar.selectbox("Select a Run", [run.Run_ID])

# Main area
st.title("Coding Assistant Dashboard")

# Display the selected run
selected_run = run
if selected_run:
    st.header(f"Run ID: {selected_run.Run_ID}")
    st.write(f"Git SHA: {selected_run.Git_SHA}")
    st.write(f"Commit Message: {selected_run.Commit_Message}")

    # Display each task in the selected run
    for task in selected_run.Tasks:
        display_task(task)
