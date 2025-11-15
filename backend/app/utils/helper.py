import os
import pandas as pd

FILENAME = "online_retail_II.csv"

def get_dataset_path() -> str:
    """
    Get the absolute path to the dataset file.
    :return:
    str: The absolute path to the dataset file.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, "dataset", FILENAME)


def load_dataset() -> pd.DataFrame:
    """
    Load the dataset from the CSV file.
    :return:
    pd.DataFrame: The loaded dataset.
    """

    dataset_path = get_dataset_path()
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

    df = pd.read_csv(dataset_path, encoding="unicode_escape")
    return df

def clean_and_prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset and prepare it for simulation by selecting a single product.
    :param df:
    pd.DataFrame: The raw dataset.
    :return:
    pd.DataFrame: The cleaned and prepared dataset for a single product.
    """
    df.dropna(subset=["Price", "Quantity", "InvoiceDate"], inplace=True)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

    if df.empty or "StockCode" not in df.columns:
        return pd.DataFrame()

    first_product_code = df["StockCode"].unique()[0]
    product_df = df[df["StockCode"] == first_product_code].head(500)
    return product_df
