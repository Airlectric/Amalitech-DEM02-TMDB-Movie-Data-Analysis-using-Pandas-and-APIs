import pandas as pd

def drop_irrelevant_columns(movies_df, columns_to_drop):
    """Drops irrelevant columns from the movie data."""
    return movies_df.drop(columns=columns_to_drop, errors='ignore')