import pandas as pd
import streamlit as st

from codinit.config import eval_settings

st.set_page_config(
    page_icon=":female_vampire:",
    page_title="Code Assistant Evaluation Dashboard",
    layout="wide",
)


# Load the CSV data
@st.cache_data
def load_data():
    return pd.read_csv(eval_settings.eval_dataset_location)


df = load_data()

st.title("Experiment Overview")


def app():
    st.title("Experiment Results")
    # 1. Aggregation

    # Aggregate metric at the Run_ID level
    run_aggregated = (
        df.groupby(["Run_ID", "Commit_Message"])["Metric"].sum().reset_index()
    )

    # Create two columns
    left_column, right_column = st.columns(2)

    # Display table on the left column
    left_column.table(run_aggregated)

    # Allow users to select a run
    selected_run = left_column.selectbox(
        "Select a run:", run_aggregated["Run_ID"].unique()
    )

    if selected_run:
        # Filter tasks under the selected run
        tasks_df = df[df["Run_ID"] == selected_run]

        # Aggregate metric at the Task_ID level for the selected run
        task_aggregated = tasks_df.groupby("Task_ID")["Metric"].sum().reset_index()

        # Display aggregated metric for each Task_ID under the selected run on the right column
        right_column.table(task_aggregated)

        # Allow users to select a task in the right column
        selected_task = right_column.selectbox(
            "Select a Task_ID:", task_aggregated["Task_ID"]
        )

        # Filter generations under the selected task
        generations_df = df[df["Task_ID"] == selected_task]

        # Aggregate metric at the Generation_ID level for the selected task
        generation_aggregated = (
            generations_df.groupby("Generation_ID")["Metric"].sum().reset_index()
        )

        # Display metrics for each Generation_ID under the selected task in the right column below the tasks table
        right_column.table(generation_aggregated)


if __name__ == "__main__":
    app()
