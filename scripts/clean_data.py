import pandas as pd
import numpy as np

def drop_irrelevant_columns(movies_df, columns_to_drop):
    """Drops irrelevant columns from the movie data."""
    return movies_df.drop(columns=columns_to_drop, errors='ignore')

def extract_json_field(df, col, key, join_with="|"):
    """
    Extract values from nested JSON-like structures in a DataFrame column.
    - If entry is dict -> return entry[key]
    - If entry is list -> return join of [item[key] for item in entry]
    - Otherwise -> return NaN
    """
    def extract(x):
        if isinstance(x, dict) and key in x:
            return x[key]
        elif isinstance(x, list):
            return join_with.join([item.get(key, '') for item in x if key in item])
        return np.nan
    
    df[col] = df[col].apply(extract)
    return df

def convert_numeric(df, cols):
    """Converts specified columns to numeric types, coercing errors to NaN."""
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    return df

def convert_to_datetime(df, cols):
    """Converts specified columns to datetime types, coercing errors to NaT."""
    df[cols] = df[cols].apply(pd.to_datetime, errors='coerce')
    return df


def clean_movie_data(movies_df):
    """Cleans and preprocesses the movie data."""

    # Extract relevant fields from JSON-like columns
    json_columns = {
        'belongs_to_collection': 'name',
        'genres': 'name',
        'spoken_languages': 'english_name',
        'production_companies': 'name',
        'production_countries': 'name',
    }
    for col, key in json_columns.items():
        movies_df = extract_json_field(movies_df, col, key)

    # Convert numeric columns
    numeric_columns = ['budget', 'popularity', 'id', 'revenue', 'runtime', 'vote_average', 'vote_count']
    movies_df = convert_numeric(movies_df, numeric_columns)

    # Convert date columns
    date_columns = ['release_date']
    movies_df = convert_to_datetime(movies_df, date_columns)

    return movies_df







