import streamlit as st
import pandas as pd
from io import BytesIO

# Function to handle file upload and return dataframe
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

# Function to download data as Excel
def download_excel(df, filename="result.xlsx"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Callback function to perform operations when "Generate" is clicked
def generate_operations():
    df = st.session_state[f"{st.session_state.session_id}_df"]
    operations = st.session_state[f"{st.session_state.session_id}_operations"]

    # Store results in session state
    results_key = f"{st.session_state.session_id}_results"
    if results_key not in st.session_state:
        st.session_state[results_key] = {}

    # Perform operations based on selection
    if "Sum of columns" in operations:
        st.session_state[results_key]["sum"] = operation_sum(df)
    if "Transpose" in operations:
        st.session_state[results_key]["transpose"] = operation_transpose(df)
    if "Descriptive statistics" in operations:
        st.session_state[results_key]["describe"] = operation_describe(df)

    st.session_state[f"{st.session_state.session_id}_generated"] = True

# Streamlit App
def main():
    st.title("Excel File Operations App")

    # Initialize session-specific state to avoid user data collision
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(st.experimental_get_query_params()) or str(st.experimental_get_url()).split("?")[-1]

    # Initialize user-specific session state variables for storing data and results
    df_key = f"{st.session_state.session_id}_df"
    results_key = f"{st.session_state.session_id}_results"
    operations_key = f"{st.session_state.session_id}_operations"
    generated_key = f"{st.session_state.session_id}_generated"

    if df_key not in st.session_state:
        st.session_state[df_key] = None
    if results_key not in st.session_state:
        st.session_state[results_key] = {}
    if operations_key not in st.session_state:
        st.session_state[operations_key] = []
    if generated_key not in st.session_state:
        st.session_state[generated_key] = False  # Track if generation is done

    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    if uploaded_file is not None:
        st.session_state[df_key] = load_excel(uploaded_file)  # Store dataframe in session state
        st.write("Preview of uploaded file:")
        st.write(st.session_state[df_key].head())

    if st.session_state[df_key] is not None:
        # Operations to select
        st.session_state[operations_key] = st.multiselect(
            "Select Operations", 
            options=["Sum of columns", "Transpose", "Descriptive statistics"]
        )

        # "Generate" button that uses a callback
        if st.button("Generate", on_click=generate_operations):
            st.session_state[generated_key] = True

        # Display download buttons only if operations are generated
        if st.session_state[generated_key]:
            for key, result_df in st.session_state[results_key].items():
                st.subheader(f"Result: {key}")
                st.write(result_df)
                st.download_button(
                    label=f"Download {key} result as Excel",
                    data=download_excel(result_df),
                    file_name=f"{key}_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Ensure that the app retains the state between user interactions
if __name__ == "__main__":
    st.set_page_config(page_title="Excel Operations App", layout="wide")
    main()