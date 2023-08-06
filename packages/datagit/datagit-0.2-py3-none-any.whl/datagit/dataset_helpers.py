import pandas as pd

def assert_dataset_has_unique_key(dataset: pd.DataFrame) -> None:
    first_column = dataset.columns[0]

    if first_column != "unique_key":
        raise ValueError(f"The first column is not named 'unique_key'")

    # Check if the first column is unique
    values = dataset[first_column].tolist()
    if len(values) != len(set(values)):
        raise ValueError(f"The {first_column} column is not unique")

def sort_dataframe_on_first_column_and_assert_is_unique(df: pd.DataFrame) -> pd.DataFrame:
    assert_dataset_has_unique_key(df)
    
    sorted_df = df.sort_values(by=['unique_key'])
    return sorted_df