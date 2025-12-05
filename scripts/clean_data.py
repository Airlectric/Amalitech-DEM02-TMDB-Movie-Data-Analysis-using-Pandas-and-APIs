import pandas as pd
import numpy as np
from logger_config import logger


def drop_irrelevant_columns(movies_df, columns_to_drop):
    """Drops irrelevant columns from the movie data."""
    logger.info(f"Dropping columns: {columns_to_drop}")
    return movies_df.drop(columns=columns_to_drop, errors='ignore')


def extract_json_field(df, col, key, join_with="|"):
    """
    Extract values from nested JSON-like structures in a DataFrame column.
    - If entry is dict -> return entry[key]
    - If entry is list -> return join of [item[key] for item in entry]
    - Otherwise -> return NaN
    """
    logger.info(f"Extracting field '{key}' from column '{col}'")
    
    def extract(x):
        if isinstance(x, dict) and key in x:
            return x[key]
        elif isinstance(x, list):
            return join_with.join([item.get(key, '') for item in x if key in item])
        return np.nan
   
    df[col] = df[col].apply(extract)
    return df


def extract_credit_json_fields(df, col='credits', join_with="|"):
    """
    Extracts cast and crew information from the credits column.
    """
    logger.info(f"Extracting cast & crew from column '{col}'")
    
    def extract_cast(x):
        if isinstance(x, dict) and 'cast' in x:
            cast_list = x['cast']
            cast_names = [member.get('name', '') for member in cast_list if 'name' in member]
            return join_with.join(cast_names)
        return np.nan
    
    def extract_director(x):
        if isinstance(x, dict) and 'crew' in x:
            crew_list = x['crew']
            directors = [member.get('name', '') for member in crew_list 
                        if member.get('job', '') == 'Director' and 'name' in member]
            return join_with.join(directors)
        return np.nan
    
    df['cast'] = df[col].apply(extract_cast)
    df['cast_size'] = df[col].apply(lambda x: len(x['cast']) if isinstance(x, dict) and 'cast' in x else 0)
    df['director'] = df[col].apply(extract_director)
    df['crew_size'] = df[col].apply(lambda x: len(x['crew']) if isinstance(x, dict) and 'crew' in x else 0)
    df.drop(columns=[col], inplace=True)
    logger.info(f"Finished extracting credits – dropped original '{col}' column")
    return df


def extract_production_countries(df, col='origin_country', join_with="|"):
    """
    Extracts country codes from the production_countries column.
    """
    logger.info(f"Extracting production countries from column '{col}'")
    
    def extract_countries(x):
        if isinstance(x, list):
            return join_with.join([item for item in x])
        return np.nan
   
    df[col] = df[col].apply(extract_countries)
    return df


def inspect_categorical_columns_using_value_counts(df, cols):
    """Prints value counts for specified categorical columns."""
    logger.info(f"Inspecting value counts for columns: {cols}")
    for col in cols:
        print(f"Value counts for column: ====== {col} ======")
        print(df[col].value_counts(dropna=False))
        print("\n")


def convert_numeric(df, cols):
    """Converts specified columns to numeric types, coercing errors to NaN."""
    logger.info(f"Converting columns to numeric: {cols}")
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    return df


def convert_to_datetime(df, cols):
    """Converts specified columns to datetime types, coercing errors to NaT."""
    logger.info(f"Converting columns to datetime: {cols}")
    df[cols] = df[cols].apply(pd.to_datetime, errors='coerce')
    return df


def clean_movie_data(movies_df):
    """Cleans and preprocesses the movie data."""
    logger.info("Starting clean_movie_data pipeline")
    
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
    movies_df = extract_credit_json_fields(movies_df, col='credits')
    
    numeric_columns = ['budget', 'popularity', 'id', 'revenue', 'runtime', 'vote_average', 'vote_count']
    movies_df = convert_numeric(movies_df, numeric_columns)
    
    date_columns = ['release_date']
    movies_df = convert_to_datetime(movies_df, date_columns)
    
    logger.info("Finished clean_movie_data pipeline")
    return movies_df


# ------------------------------------
# Replace unrealistic / placeholder values
# ---------------------------------------
def replace_zero_values(df):
    """Replaces unrealistic placeholder values in the DataFrame."""
    logger.info("Replacing zero values in budget, revenue, runtime with NaN")
    df.loc[df['budget'] == 0, 'budget'] = np.nan
    df.loc[df['revenue'] == 0, 'revenue'] = np.nan
    df.loc[df['runtime'] == 0, 'runtime'] = np.nan
    return df


def convert_budget_to_millions(df):
    """Converts budget from dollars to millions of dollars."""
    logger.info("Converting budget & revenue to millions of USD")
    df['budget_musd'] = df['budget'] / 1_000_000
    df['revenue_musd'] = df['revenue'] / 1_000_000
    df.drop(columns=['budget', 'revenue'], inplace=True)
    return df


def clean_text_placeholders(df):
    """Cleans text placeholders in the DataFrame."""
    logger.info("Cleaning placeholder text in tagline & overview")
    text_columns = ['tagline', 'overview']
    for col in text_columns:
        df.loc[df[col].str.upper().isin(['NO TAGLINE', 'NO OVERVIEW', "NO DATA", ""]), col] = np.nan
    return df


def adjust_vote_average(df):
    """Sets vote_average to NaN where vote_count is zero."""
    logger.info("Setting vote_average to NaN when vote_count == 0")
    if 'vote_count' in df.columns and 'vote_average' in df.columns:
        df.loc[df['vote_count'] == 0, 'vote_average'] = np.nan
    return df


def replace_unrealistic_values(df):
    """Applies all unrealistic value replacements."""
    logger.info("Starting replace_unrealistic_values pipeline")
    df = replace_zero_values(df)
    df = convert_budget_to_millions(df)
    df = clean_text_placeholders(df)
    df = adjust_vote_average(df)
    logger.info("Finished replace_unrealistic_values pipeline")
    return df


# ------------------------------------
# Dropping NA's and Duplicates
# ---------------------------------------
def remove_duplicates(df):
    """Removes duplicate rows from the DataFrame."""
    logger.info("Removing duplicate rows")
    if 'id' in df.columns:
        df = df.drop_duplicates(subset=['id'])
    else:
        df = df.drop_duplicates()
    logger.info(f"Rows after duplicate removal: {len(df)}")
    return df


def drop_rows_with_na_in_critical_columns(df, critical_columns):
    """Drops rows with NA values in critical columns."""
    logger.info(f"Dropping rows with NA in critical columns: {critical_columns}")
    before = len(df)
    df = df.dropna(subset=critical_columns)
    logger.info(f"Rows removed: {before - len(df)} and Remaining: {len(df)}")
    return df


def keep_rows_with_min_non_nan(df, min_non_nan=10):
    """Keeps rows with at least min_non_nan non-NA values."""
    logger.info(f"Keeping only rows with >= {min_non_nan} non-NA values")
    before = len(df)
    df = df[df.notna().sum(axis=1) >= min_non_nan]
    logger.info(f"Rows removed: {before - len(df)} and Remaining: {len(df)}")
    return df


def filter_released_movies(df):
    logger.info("Filtering for released movies only")
    if 'status' in df.columns:
        before = len(df)
        df = df[df['status'] == 'Released'].copy()
        df = df.drop(columns=['status'])
        logger.info(f"Kept only 'Released' movies: {len(df)} (removed {before - len(df)})")
    else:
        logger.info("No 'status' column found – skipping released-movie filter")
    return df


def removing_na_and_duplicates(df):
    """Applies all NA and duplicate removal steps."""
    logger.info("Starting removing_na_and_duplicates pipeline")
    df = remove_duplicates(df)
    critical_columns = ['title', 'id']
    df = drop_rows_with_na_in_critical_columns(df, critical_columns)
    df = keep_rows_with_min_non_nan(df, min_non_nan=10)
    df = filter_released_movies(df)
    logger.info(f"Final dataset size after NA & duplicate removal: {len(df)} rows")
    return df


# -------------------------------------
# Reordering and Finalizing DataFrame
# ---------------------------------------
def reorder_columns(df, desired_order):
    """Reorders DataFrame columns based on the desired order."""
    logger.info("Reordering columns according to desired order")
    existing_columns = [col for col in desired_order if col in df.columns]
    remaining_columns = [col for col in df.columns if col not in existing_columns]
    new_order = existing_columns + remaining_columns
    return df[new_order]


def reset_index(df):
    """Resets the DataFrame index."""
    logger.info("Resetting DataFrame index")
    return df.reset_index(drop=True)


def finalize_dataframe(df):
    """Finalizes the DataFrame by reordering columns and resetting the index."""
    logger.info("Finalizing DataFrame (reordering + index reset)")
    desired_order = ['id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
                     'original_language', 'budget_musd', 'revenue_musd', 'production_companies',
                     'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime',
                     'overview', 'spoken_languages', 'poster_path', 'cast', 'cast_size', 'director', 'crew_size']
    df = reorder_columns(df, desired_order)
    df = reset_index(df)
    logger.info(f"DataFrame finalized – shape: {df.shape}")
    return df