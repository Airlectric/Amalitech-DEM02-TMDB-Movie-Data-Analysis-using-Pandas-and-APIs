import matplotlib.pyplot as plt
import pandas as pd
from kpi_analysis import calculate_roi


def plot_revenue_vs_budget(df):
    plt.figure(figsize=(10,6))
    plt.scatter(df['budget_musd'], df['revenue_musd'])
    plt.xlabel('Budget (Millions USD)')
    plt.ylabel('Revenue (Millions USD)')
    plt.title('Revenue Vs Budget')
    plt.grid(True)
    plt.show()

def plot_roi_by_genre(df):
    df = calculate_roi(df)
    plt.figure(figsize=(12,6))
    df.groupby('genres')['roi'].mean().sort_values().plot(kind='bar')
    plt.title('ROI Distribution by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Average ROI')
    plt.grid(True)
    plt.show()

def plot_popularity_vs_rating(df):
    plt.figure(figsize=(10,6))
    plt.scatter(df['vote_average'], df['popularity'])
    plt.xlabel('Rating (vote average)')
    plt.ylabel('Popularity')
    plt.title('Popularity vs Rating')
    plt.grid(True)
    plt.show()

def plot_yearly_box_office(df):
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    yearly = df.groupby('release_year')['revenue_musd'].sum()
    plt.figure(figsize=(12,6))
    yearly.plot()
    plt.title('Yearly Box Office Performance')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue (Millions USD)')
    plt.grid(True)
    plt.show()

def plot_franchise_vs_standalone(df):

    df["is_franchise"] = df['belongs_to_collection'].notna()

    comparison = df.groupby('is_franchise')['revenue_musd'].mean()

    plt.figure(figsize=(8,6))
    comparison.plot(kind='bar')
    plt.title('Franchise vs Standalone Success')
    plt.xlabel('Movie Type')
    plt.ylabel('Average Revenue (Millions USD)')
    plt.grid(True)
    plt.show()


