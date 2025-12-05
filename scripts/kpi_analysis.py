import pandas as pd
import numpy as np
from logging_config import logger

# ------------------------------------------------
# KPI Calculations for Best/Worst Performing Movies
# ---------------------------------------------------------

def calculate_profit(df):
    df = df.copy()
    df['profit'] = df['revenue_musd'] - df['budget_musd']
    return df

def calculate_roi(df):
    df = df.copy()
    df['roi'] = df.apply(lambda x : x['revenue_musd']/ x['budget_musd'] if x['budget_musd'] >= 10 else np.nan, axis=1)
    return df

def rank_movies(df, metric, ascending=False, top_n=10):
    """Ranks movies based on a specified metric and returns the top N movies."""
    return df.sort_values(by=metric, ascending=ascending).head(top_n)

def get_kpis(df):
    df = calculate_profit(df)
    df = calculate_roi(df)

    return {
        "higest_revenue": rank_movies(df, "revenue_musd", ascending=False),
        "higest_budget": rank_movies(df, "budget_musd", ascending=False),
        "higest_profit": rank_movies(df, "profit", ascending=False),
        "lowest_profit": rank_movies(df, "profit", ascending=True),
        "higest_roi": rank_movies(df.dropna(subset=['roi']), "roi", ascending=False),
        "lowest_roi": rank_movies(df.dropna(subset=['roi']), "roi", ascending=True),
        "most_voted": rank_movies(df, "vote_count", ascending=False),
        "highest_rated": rank_movies(df, "vote_average", ascending=False),
        'lowest_rated': rank_movies(df, "vote_average", ascending=True),
        'most_popular': rank_movies(df, "popularity", ascending=False)
    }

# -------------------------------------
# Advanced filtering and search
# ------------------------------------------
def search_best_scifi_action_bruce(df):
    mask = (
        df['genres'].str.contains('Science Fiction', case=False, na=False, regex=False)
        & df['genres'].str.contains("Action", case=False, na=False, regex=False)
        & df['cast'].str.contains('Bruce Willis', case=False, na=False, regex=False)
    )
    return df[mask].sort_values('vote_average', ascending=False)

def search_uma_thurman_tarentino(df):
    mask = (
        df['cast'].str.contains('Uma Thurman', case=False, na=False, regex=False)
        & df['director'].str.contains('Quentin Tarantino', case=False, na=False, regex=False)
    )
    return df[mask].sort_values('vote_average', ascending=False)


# -----------------------------------------------
# Franchise VS standalone Performance
# ------------------------------------------

def franchise_vs_standalone(df):
    df = calculate_roi(df)

    df["is_franchise"] = df['belongs_to_collection'].notna()

    grouped = df.groupby('is_franchise').agg(
        mean_revenue=('revenue_musd', 'mean'),
        median_roi=('roi', 'median'),
        mean_budget=('budget_musd', 'mean'),
        mean_popularity=('popularity', 'mean'),
        mean_rating=('vote_average', 'mean')
    )

    return grouped


# -----------------------------------------------
# Most Successful Franchises
# ------------------------------------------
def franchise_success(df):
    df = df.copy()

    df = df.dropna(subset=['belongs_to_collection'])

    grouped = df.groupby('belongs_to_collection').agg(
        count_movies=('id', 'count'),

        total_budget_musd=('budget_musd', 'sum'),
        mean_budget_musd=('budget_musd', 'mean'),
        
        total_revenue_musd=('revenue_musd', 'sum'),
        mean_revenue_musd=('revenue_musd', 'mean'),

        mean_rating=('vote_average', 'mean'),
    ).sort_values(by='total_revenue_musd', ascending=False)

    return grouped

# -----------------------------------------------
# Most Successful Directors 
# ---------------------------------------------------
def director_success(df, top_n=10):
    df = df.copy()

    # Exploded the DataFrame to have one row per director
    df_exploded = df.assign(director=df['director'].str.split('|')).explode('director')

    grouped = df_exploded.groupby('director').agg(
        total_movies_directed=('id', 'count'),
        
        total_revenue_musd=('revenue_musd', 'sum'),

        mean_rating=('vote_average', 'mean'),
    ).sort_values(by='total_revenue_musd', ascending=False).head(top_n)

    return grouped
