import pandas as pd


def load_dataset(uploaded_file):
    """
    Load a CSV or Excel file into a Pandas DataFrame.
    """

    file_name = uploaded_file.name.lower()

    # Check if the uploaded file is completely empty
    if uploaded_file.size == 0:
        raise ValueError("The uploaded file is empty.")

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError(
            "Unsupported file type. Please upload a CSV or Excel file."
        )

    # Check if the dataset contains no rows
    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    # Check if the dataset contains no columns
    if len(df.columns) == 0:
        raise ValueError("The dataset does not contain any columns.")

    return df