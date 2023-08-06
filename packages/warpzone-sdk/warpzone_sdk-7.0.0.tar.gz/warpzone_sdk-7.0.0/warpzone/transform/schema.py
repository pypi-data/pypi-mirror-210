from hashlib import md5

import pandas as pd


class SchemaValidationError(Exception):
    """Error message when schema and dataframe have different column names"""

    def __init__(self, df_columns_set: set, schema_keys_set: set) -> None:
        difference = df_columns_set.symmetric_difference(schema_keys_set)
        message = f"Mismatch between dataframe and schema in column names {difference}"
        super().__init__(message)


class SchemaCastingError(Exception):
    """Error message when the data in dataframe
    cannot be casted to the type indicated in schema"""

    def __init__(self, column_name: str, schema_type: str) -> None:
        message = f"Data in column {column_name} cannot be casted to type {schema_type}"
        super().__init__(message)


def generate_and_stringify_schema(df: pd.DataFrame) -> dict[str:str]:
    columns = df.dtypes.astype(str)
    return columns.to_dict()


def calculate_schema_version(schema: dict) -> str:
    """create a md5 hash of schema, used as version in messages"""
    return md5(repr(schema).encode()).hexdigest()


def cast_to_schema(df: pd.DataFrame, schema: dict[str:str]):
    """Change dtypes pf columns of dataframe one by one to enable debugging
    and then reorder the dataframe based on the schema"""

    for column in df.columns.values:
        try:
            df[column] = df[column].astype(schema[column])
        except ValueError:
            raise SchemaCastingError(column, schema[column])

    return df[schema.keys()]


def dataframe_schema_recast(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    """Cast pandas DataFrame to given schema and order columns"""
    if set(df.columns.values) != set(schema.keys()):
        raise SchemaValidationError(set(df.columns.values), set(schema.keys()))
    df = cast_to_schema(df, schema)

    return df
