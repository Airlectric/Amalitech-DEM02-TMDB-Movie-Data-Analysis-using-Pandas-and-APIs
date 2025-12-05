import pandas as pd
import numpy as np
from logger_config import logger


# ------------------------------------------------
# KPI Calculations for Best/Worst Performing Movies
# ---------------------------------------------------------
def calculate_profit(df):
    logger.info("Calculating profit (revenue - budget) in millions USD")
    df = df.copy()
    df['profit'] = df['revenue_musd'] - df['budget_musd']
    return df


def calculate_roi(df):
    logger.info("Calculating ROI (only for movies with budget >= 10M USD)")
    df = df.copy()
    df['roi'] = df.apply(
        lambda x: x['revenue_musd'] / x['budget_musd'] if x['budget_musd'] >= 10 else np.nan,
        axis=1
    )
    return df


def rank_movies(df, metric, ascending=False, top_n=10):
    """Ranks movies based on a specified metric and returns the top N movies."""
    logger.info(f"Ranking top {top_n} movies by '{metric}' (ascending={ascending})")
    return df.sort_values(by=metric, ascending=ascending).head(top_n)


def get_kpis(df):
    logger.info("Starting KPI calculation: profit, ROI, and top rankings")
    df = calculate_profit(df)
    df = calculate_roi(df)
    
    kpis = {
        "higest_revenue": rank_movies(df, "revenue_musd", ascending=False),
        "higest_budget": rank_movies(df, "budget_musd", ascending=False),
        "higest_profit": rank_movies(df, "profit", ascending=False),
        "lowest_profit": rank_movies(df, "profit", ascending=True),

        # Including the movies with the Budget >= 10M
        "higest_roi": rank_movies(df[df['budget_musd'] >= 10], "roi", ascending=False),
        "lowest_roi": rank_movies(df[df['budget_musd'] >= 10], "roi", ascending=True),

        "most_voted": rank_movies(df, "vote_count", ascending=False),

        # Including movies with vote_count >= 10
        "highest_rated": rank_movies(df[df['vote_count'] >= 10], "vote_average", ascending=False),
        'lowest_rated': rank_movies(df[df['vote_count'] >= 10], "vote_average", ascending=True),

        'most_popular': rank_movies(df, "popularity", ascending=False)
    }
    logger.info("KPI dictionary generated successfully")
    return kpis


# -------------------------------------
# Advanced filtering and search
# ------------------------------------------
def search_best_scifi_action_bruce(df):
    logger.info("Searching for best Sci-Fi + Action movies starring Bruce Willis")
    mask = (
        df['genres'].str.contains('Science Fiction', case=False, na=False, regex=False)
        & df['genres'].str.contains("Action", case=False, na=False, regex=False)
        & df['cast'].str.contains('Bruce Willis', case=False, na=False, regex=False)
    )
    result = df[mask].sort_values('vote_average', ascending=False)
    logger.info(f"Found {len(result)} Sci-Fi/Action movies with Bruce Willis")
    return result


def search_uma_thurman_tarentino(df):
    logger.info("Searching for movies with Uma Thurman directed by Quentin Tarantino")
    mask = (
        df['cast'].str.contains('Uma Thurman', case=False, na=False, regex=False)
        & df['director'].str.contains('Quentin Tarantino', case=False, na=False, regex=False)
    )
    result = df[mask].sort_values('vote_average', ascending=False)
    logger.info(f"Found {len(result)} Uma Thurman + Quentin Tarantino collaborations")
    return result


# -----------------------------------------------
# Franchise VS standalone Performance
# ------------------------------------------
def franchise_vs_standalone(df):
    logger.info("Comparing franchise vs standalone movie performance")
    df = calculate_roi(df)
    df["is_franchise"] = df['belongs_to_collection'].notna()
    
    grouped = df.groupby('is_franchise').agg(
        mean_revenue=('revenue_musd', 'mean'),
        median_roi=('roi', 'median'),
        mean_budget=('budget_musd', 'mean'),
        mean_popularity=('popularity', 'mean'),
        mean_rating=('vote_average', 'mean')
    )
    logger.info("Franchise vs standalone comparison completed")
    return grouped


# -----------------------------------------------
# Most Successful Franchises
# ------------------------------------------
def franchise_success(df):
    logger.info("Analyzing most successful movie franchises by total revenue")
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
    
    logger.info(f"Franchise success analysis completed – {len(grouped)} franchises ranked")
    return grouped


# -----------------------------------------------
# Most Successful Directors
# ---------------------------------------------------
def director_success(df, top_n=10):
    logger.info(f"Calculating top {top_n} most successful directors by total revenue")
    df = df.copy()
    
    # Explode directors (in case of multiple directors separated by '|')
    df_exploded = df.assign(director=df['director'].str.split('|')).explode('director')
    
    grouped = df_exploded.groupby('director').agg(
        total_movies_directed=('id', 'count'),
        total_revenue_musd=('revenue_musd', 'sum'),
        mean_rating=('vote_average', 'mean'),
    ).sort_values(by='total_revenue_musd', ascending=False).head(top_n)
    
    logger.info(f"Director success ranking completed – top {top_n} returned")
    return grouped