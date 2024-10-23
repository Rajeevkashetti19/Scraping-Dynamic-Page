import streamlit as st
import pandas as pd
from io import BytesIO
import uuid

# Function to load an Excel file and return a dataframe
def load_excel(file):
    df = pd.read_excel(file)
    return df

# Function to perform operation 1: Sum of columns
def operation_sum(df):
    return df.sum().to_frame('Sum')

# Function to perform operation 2: Transpose
def operation_transpose(df):
    return df.T

# Function to perform operation 3: Descriptive statistics
def operation_describe(df):
    return df.describe()

# Function to download a dataframe as an Excel file
def download_excel(df, filename="result.xlsx"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Streamlit App
def main():
    st.title("Excel File Operations App")

    # Unique session identifier for each user to isolate their data
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Generate unique session ID

    # Session-specific state management
    session_id = st.session_state.session_id  # Unique to each user session

    # Initialize session state variables if not already set
    if f"{session_id}_uploaded_file" not in st.session_state:
        st.session_state[f"{session_id}_uploaded_file"] = None
    if f"{session_id}_results" not in st.session_state:
        st.session_state[f"{session_id}_results"] = {}
    if f"{session_id}_generated" not in st.session_state:
        st.session_state[f"{session_id}_generated"] = False
    if f"{session_id}_operations_selected" not in st.session_state:
        st.session_state[f"{session_id}_operations_selected"] = []

    # File uploader
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key=f"file_uploader_{session_id}")

    if uploaded_file is not None and st.session_state[f"{session_id}_uploaded_file"] != uploaded_file:
        st.session_state[f"{session_id}_uploaded_file"] = uploaded_file
        st.session_state[f"{session_id}_generated"] = False  # Reset state if a new file is uploaded
        st.session_state[f"{session_id}_df"] = load_excel(uploaded_file)  # Load the Excel file into session state
        st.write("Preview of uploaded file:")
        st.write(st.session_state[f"{session_id}_df"].head())

    # Once a file is uploaded
    if st.session_state[f"{session_id}_uploaded_file"] is not None:
        # Multi-select operations
        st.session_state[f"{session_id}_operations_selected"] = st.multiselect(
            "Select Operations",
            options=["Sum of columns", "Transpose", "Descriptive statistics"],
            default=st.session_state[f"{session_id}_operations_selected"],
            key=f"multiselect_{session_id}"
        )

        # "Generate" button for operations
        if st.button("Generate", key=f"generate_button_{session_id}") and not st.session_state[f"{session_id}_generated"]:
            st.session_state[f"{session_id}_results"] = {}  # Clear previous results

            # Perform the operations and store the results in session state
            if "Sum of columns" in st.session_state[f"{session_id}_operations_selected"]:
                st.session_state[f"{session_id}_results"]["sum"] = operation_sum(st.session_state[f"{session_id}_df"])
            if "Transpose" in st.session_state[f"{session_id}_operations_selected"]:
                st.session_state[f"{session_id}_results"]["transpose"] = operation_transpose(st.session_state[f"{session_id}_df"])
            if "Descriptive statistics" in st.session_state[f"{session_id}_operations_selected"]:
                st.session_state[f"{session_id}_results"]["describe"] = operation_describe(st.session_state[f"{session_id}_df"])

            st.session_state[f"{session_id}_generated"] = True  # Mark results as generated

        # Display and download the results without page reruns
        if st.session_state[f"{session_id}_generated"]:
            for key, result_df in st.session_state[f"{session_id}_results"].items():
                st.subheader(f"Result: {key}")
                st.write(result_df)
                st.download_button(
                    label=f"Download {key} result as Excel",
                    data=download_excel(result_df),
                    file_name=f"{key}_result_{session_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_button_{key}_{session_id}"
                )

# Ensure that the app retains the state between user interactions
if __name__ == "__main__":
    st.set_page_config(page_title="Excel Operations App", layout="wide")
    main()