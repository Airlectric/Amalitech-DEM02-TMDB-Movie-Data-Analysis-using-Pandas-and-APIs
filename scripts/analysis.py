import pandas as pd
import matplotlib.pyplot as plt

def movies_to_dataframe(movies):
    return pd.DataFrame(movies)

def top_movies_by_popularity(df, n=10):
    return df.nlargest(n, "popularity")[["title", "vote_average", "popularity"]]

def plot_top_vote_average(df, n=10):
    df_sorted = df.sort_values("vote_average", ascending=False).head(n)
    plt.figure(figsize=(10,5))
    plt.bar(df_sorted["title"], df_sorted["vote_average"])
    plt.title("Top Movies by Vote Average")
    plt.xticks(rotation=45, ha='right')
    plt.show()
