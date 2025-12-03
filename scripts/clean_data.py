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

def extract_production_countries(df, col='origin_country', join_with="|"):
    """
    Extracts country codes from the production_countries column.
    """
    def extract_countries(x):
        if isinstance(x, list):
            return join_with.join([item for item in x ])
        return np.nan
    
    df[col] = df[col].apply(extract_countries)
    return df

def inspect_categorical_columns_using_value_counts(df, cols):
    """Prints value counts for specified categorical columns."""
    for col in cols:
        print(f"Value counts for column: ====== {col} ======")
        print(df[col].value_counts(dropna=False))
        print("\n")


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

    movies_df = extract_production_countries(movies_df, col='origin_country')

    # Convert numeric columns
    numeric_columns = ['budget', 'popularity', 'id', 'revenue', 'runtime', 'vote_average', 'vote_count']
    movies_df = convert_numeric(movies_df, numeric_columns)

    # Convert date columns
    date_columns = ['release_date']
    movies_df = convert_to_datetime(movies_df, date_columns)

    return movies_df


# ------------------------------------
# Replace unrealistic / placeholder values
# ---------------------------------------
def replace_zero_values(df):
    """Replaces unrealistic placeholder values in the DataFrame."""
    df.loc[df['budget'] == 0, 'budget'] = np.nan
    df.loc[df['revenue'] == 0, 'revenue'] = np.nan
    df.loc[df['runtime'] == 0, 'runtime'] = np.nan
    return df

def convert_budget_to_millions(df):
    """Converts budget from dollars to millions of dollars."""
    df['budget'] = df['budget'] / 1_000_000
    df['revenue'] = df['budget'] / 1_000_000
    return df

def clean_text_placeholders(df):
    """Cleans text placeholders in the DataFrame."""
    text_columns = ['tagline', 'overview']
    for col in text_columns:
        df.loc[df[col].str.upper().isin(['No Tagline', 'No Overview', "No Data", ""]), col] = np.nan
    return df


def adjust_vote_average(df):
    """Sets vote_average to NaN where vote_count is zero."""
    if 'vote_count' in df.columns and 'vote_average' in df.columns:
        df.loc[df['vote_count'] == 0, 'vote_average'] = np.nan
    return df

def replace_unrealistic_values(df):
    """Applies all unrealistic value replacements."""
    df = replace_zero_values(df)
    df = convert_budget_to_millions(df)
    df = clean_text_placeholders(df)
    df = adjust_vote_average(df)
    return df


# ------------------------------------
# Dropping NA's and Duplicates
# ---------------------------------------

def remove_duplicates(df):
    """Removes duplicate rows from the DataFrame."""
    if 'id 'in df.columns:
        return df.drop_duplicates(subset=['id'])
    return df.drop_duplicates()

def drop_rows_with_na_in_critical_columns(df, critical_columns):
    """Drops rows with NA values in critical columns."""
    return df.dropna(subset=critical_columns)

def keep_rows_with_min_non_nan(df, min_non_nan = 10):
    """Keeps rows with at least min_non_nan non-NA values."""
    return df[df.notna().sum(axis=1) >= min_non_nan]

def filter_released_movies(df):
    if 'status' in df.columns:
        df = df[df['status'] == 'Released'].copy()
        df = df.drop(columns=['status'])
    return df

def removing_na_and_duplicates(df):
    """Applies all NA and duplicate removal steps."""
    df = remove_duplicates(df)
    critical_columns = ['title', 'id']
    df = drop_rows_with_na_in_critical_columns(df, critical_columns)
    df = keep_rows_with_min_non_nan(df, min_non_nan=10)
    df = filter_released_movies(df)
    return df



# -------------------------------------
# Reordering and Finalizing DataFrame
# ---------------------------------------

def reorder_columns(df, desired_order):
    """Reorders DataFrame columns based on the desired order."""
    existing_columns = [col for col in desired_order if col in df.columns]
    remaining_columns = [col for col in df.columns if col not in existing_columns]
    new_order = existing_columns + remaining_columns
    return df[new_order]

def reset_index(df):
    """Resets the DataFrame index."""
    return df.reset_index(drop=True)

def finalize_dataframe(df):
    """Finalizes the DataFrame by reordering columns and resetting the index."""
    desired_order = ['id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
                    'original_language', 'budget_musd', 'revenue_musd', 'production_companies',
                    'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime',
                    'overview', 'spoken_languages', 'poster_path', 'cast', 'cast_size', 'director', 'crew_size']
    df = reorder_columns(df, desired_order)
    df = reset_index(df)
    return df










