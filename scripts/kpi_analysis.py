import pandas as pd
import numpy as np

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
        df['genres'].str.contains('Science Fiction', case=False, na=False)
        & df['genres'].str.contains("Action", case=False, na=False)
        & df['cast'].str.contains('Brue Willis', case=False, na=False)
    )
    return df[mask].sort_values('vote_average', ascending=False)

def search_uma_thurman_tarentino(df):
    mask = (
        df['cast'].str.contains('Uma Thurman', case=False, na=False)
        & df['director'].str.contains('Quentin Tarantino', case=False, na=False)
    )
    return df[mask].sort_values('vote_average', ascending=False)


