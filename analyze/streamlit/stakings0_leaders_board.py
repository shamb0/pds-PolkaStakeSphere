import os

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import squarify
import streamlit as st
from loguru import logger

DATABASE_NAME = "transform_stakings0"

def get_stakings0_metrics_db_path():
    stakings0_metrics_db = os.environ.get("PSS_STAKING0_TRANSFORMED_METRICS_SINK")
    if not stakings0_metrics_db:
        raise ValueError("Environment variable PSS_STAKING0_TRANSFORMED_METRICS_SINK is not set.")

    if not os.path.isfile(stakings0_metrics_db):
        raise FileNotFoundError(f"The specified stakings0 metrics db file does not exist: {stakings0_metrics_db}")

    return stakings0_metrics_db

def connect_to_stakings0_metrics_db(read_only=True):
    db_path = get_stakings0_metrics_db_path()
    return duckdb.connect(database=db_path, read_only=read_only)

def get_data_for_date_range(start_date, end_date):
    con = connect_to_stakings0_metrics_db()
    query = f"""
    SELECT *
    FROM {DATABASE_NAME}.dim_stakings0_joined
    WHERE date >= '{start_date}' AND date <= '{end_date}'
    """
    df = con.execute(query).fetchdf()
    df_filtered = df[(df['validator'].notnull()) & (df['validator_commission'].notnull())]
    return df, df_filtered

def display_commission_rate_tables(df_filtered):
    # Commission rates of validators
    # Top 10 maximum commission rates
    top_10_max_commission = df_filtered.nlargest(10, 'validator_commission')[['validator', 'validator_commission']]

    # Top 10 minimum commission rates
    top_10_min_commission = df_filtered.nsmallest(10, 'validator_commission')[['validator', 'validator_commission']]

    # Create two columns for the tables
    col1, col2 = st.columns(2)

    # Display the tables side by side
    with col1:
        st.subheader("Top 10 Maximum Commission Rates")
        st.table(top_10_max_commission)

    with col2:
        st.subheader("Top 10 Minimum Commission Rates")
        st.table(top_10_min_commission)

# Scatter plot: Number of nominators vs. total stake
def plot_nominators_vs_total_stake(df):
    st.subheader("Number of Nominators vs. Total Stake")
    fig, ax = plt.subplots(figsize=(24, 6))
    ax.scatter(df['nominatorcnt'], df['validator_total'])
    ax.set_xlabel("Number of Nominators")
    ax.set_ylabel("Total Stake")
    st.pyplot(fig)

# Heatmap: Staking APR across eras
def plot_staking_apr_heatmap(df):
    st.subheader("Staking APR Across Eras")
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot_df = df.pivot(index='validator', columns='era', values='validator_staking_apr')
    sns.heatmap(pivot_df, cmap='YlGnBu', ax=ax)
    ax.set_xlabel("Era")
    ax.set_ylabel("Validator")
    st.pyplot(fig)

# Stacked area chart: Proportion of active and inactive validators over time
def plot_stacked_area_chart(df):
    st.subheader("Proportion of Active and Inactive Validators Over Time")

    # Replace NULL values in validator_is_active with False
    df['validator_is_active'] = df['validator_is_active'].fillna(False)

    active_validators = df.groupby('date')['validator_is_active'].sum()
    inactive_validators = df.groupby('date').size() - active_validators

    # Convert inactive_validators to numeric data type and handle NaN values
    inactive_validators = inactive_validators.astype(float)
    inactive_validators = inactive_validators.fillna(0)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.stackplot(active_validators.index, [active_validators, inactive_validators], labels=['Active', 'Inactive'])
    ax.legend(loc='upper left')
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Validators")
    st.pyplot(fig)

# Pie chart: Distribution of staking rewards among validators
def plot_stacked_pie_chart(df):
    st.subheader("Distribution of Staking Rewards Among Validators")

    # Filter out rows with None or NaN values in 'validator_staking_rewards'
    df_filtered = df[df['validator_staking_rewards'].notna()]

    # Group by validator and calculate the sum of staking rewards
    validator_rewards = df_filtered.groupby('validator')['validator_staking_rewards'].sum()

    # Get the top 10 validators by staking rewards
    top_validators = validator_rewards.nlargest(10)

    # Calculate the sum of rewards for the remaining validators
    other_rewards = validator_rewards.sum() - top_validators.sum()

    # Create a new Series with the top validators and 'Other' category
    data = pd.concat([top_validators, pd.Series({'Other': other_rewards})])

    # Create labels for the pie chart with shortened validator addresses
    labels = [validator[:5] for validator in top_validators.index] + ['Other']

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(data, labels=labels, autopct='%1.1f%%')
    ax.set_title("Staking Rewards Distribution")
    st.pyplot(fig)

# Treemap: Normalized stake of validators relative to total stake
def plot_treemap(df):
    st.subheader("Normalized Stake of Validators Relative to Total Stake")

    # Filter out rows with None or NaN values in 'validator_normalized_staking_apr'
    df_filtered = df[df['validator_normalized_staking_apr'].notna()]

    # Get the top 10 validators by normalized staking APR
    top_validators = df_filtered.nlargest(10, 'validator_normalized_staking_apr')

    # Calculate the sum of normalized staking APR for the remaining validators
    other_stake = df_filtered['validator_normalized_staking_apr'].sum() - top_validators['validator_normalized_staking_apr'].sum()

    # Create a new DataFrame with the top validators and 'Other' category
    data = pd.concat([top_validators[['validator_normalized_staking_apr']], pd.DataFrame({'validator_normalized_staking_apr': [other_stake]}, index=['Other'])])

    # Create labels for the treemap with shortened validator addresses
    labels = [validator[:5] for validator in top_validators['validator']] + ['Other']

    fig, ax = plt.subplots(figsize=(12, 6))
    squarify.plot(sizes=data['validator_normalized_staking_apr'], label=labels, alpha=.8, ax=ax)
    ax.set_title("Normalized Stake of Validators")
    st.pyplot(fig)

def main():
    st.set_page_config(page_title="Validators Leaders Board", layout="wide")
    st.title("Validators Leaders Board")

    con = connect_to_stakings0_metrics_db()
    min_date, max_date = con.execute(
        f"SELECT MIN(date), MAX(date) FROM {DATABASE_NAME}.dim_stakings0_joined"
    ).fetchone()

    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End Date", min_value=start_date, max_value=max_date, value=max_date)

    apply_button = st.button("Apply")

    if apply_button:
        logger.info(f"Selected Date Range {start_date} - {end_date}")
        df, df_filtered = get_data_for_date_range(start_date, end_date)
        display_commission_rate_tables(df_filtered)
        plot_nominators_vs_total_stake(df)
        plot_staking_apr_heatmap(df)
        plot_stacked_area_chart(df)
        plot_stacked_pie_chart(df)
        plot_treemap(df)

if __name__ == "__main__":
    main()
