import os

import duckdb
import matplotlib.pyplot as plt
import streamlit as st

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
    # SQL query to calculate average total stake for the selected date range
    date_range_query = f"""
        SELECT era, date, AVG(validator_total) AS avg_total_stake
        FROM {DATABASE_NAME}.dim_stakings0_joined
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date, era
        ORDER BY date
    """

    return con.execute(date_range_query).fetchdf()

# SQL query to calculate average total stake for the selected snapshot date
def get_data_for_snapshot_date(snapshot_date):
    con = connect_to_stakings0_metrics_db()
    snapshot_query = f"""
        SELECT era, AVG(validator_total) AS avg_total_stake
        FROM {DATABASE_NAME}.dim_stakings0_joined
        WHERE date = '{snapshot_date}'
        GROUP BY era
    """
    # Execute the queries
    return con.execute(snapshot_query).fetchdf()

def plot_average_total_stake(date_range_result, start_date, end_date):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(date_range_result["date"], date_range_result["avg_total_stake"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Average Total Stake")
    ax.set_title(f"Average Total Stake from {start_date} to {end_date}")
    ax.grid(True)
    st.pyplot(fig)

def main():
    st.set_page_config(page_title="Polkadot Staking Validator Stats", layout="wide")
    st.title("Polkadot Staking Validator Stats")

    con = connect_to_stakings0_metrics_db()
    min_date, max_date = con.execute(
        f"SELECT MIN(date), MAX(date) FROM {DATABASE_NAME}.dim_stakings0_joined"
    ).fetchone()

    # Snapshot Date Picker
    st.write("---")
    snapshot_date = st.date_input(
        "Select Snapshot Date", value=max_date, min_value=min_date, max_value=max_date
    )

    snapshot_result = get_data_for_snapshot_date(snapshot_date)

    # Display the results
    st.subheader(f"Average Total Stake on {snapshot_date}")
    st.write(snapshot_result)

    st.write("---")

    # Date Range Picker
    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End Date", min_value=start_date, max_value=max_date, value=max_date)
    apply_button = st.button("Apply")

    if apply_button:
        date_range_result = get_data_for_date_range(start_date, end_date)
        st.subheader(f"Average Total Stake from {start_date} to {end_date}")
        plot_average_total_stake(date_range_result, start_date, end_date)
        st.write(date_range_result)

    st.write("---")


if __name__ == "__main__":
    main()
