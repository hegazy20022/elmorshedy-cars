import pandas as pd
from ui_labels import COLUMN_LABELS_AR, VALUE_LABELS_AR


def translate_dataframe_columns(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    mapping = COLUMN_LABELS_AR.get(table_key, {})
    return df.rename(columns=mapping)


def translate_cell_value(column_name: str, value):
    # حالات خاصة زي status و mode و intent
    if column_name in VALUE_LABELS_AR:
        return VALUE_LABELS_AR[column_name].get(value, value)

    # bool
    if isinstance(value, bool):
        return VALUE_LABELS_AR.get("bool", {}).get(value, value)

    return value


def translate_dataframe_values(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    mapping = COLUMN_LABELS_AR.get(table_key, {})
    df_copy = df.copy()

    for col in df_copy.columns:
        df_copy[col] = df_copy[col].apply(lambda v: translate_cell_value(col, v))

    return df_copy
