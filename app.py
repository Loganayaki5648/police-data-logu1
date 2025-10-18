import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
import pymysql

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="NewPassword",
        database="traffic_stops_data",
        port=3306
    )
engine = create_engine("mysql+pymysql://root:NewPassword@127.0.0.1:3306/traffic_stops_data")

def run_query(sql):
    try:
        df = pd.read_sql(sql, engine)
        return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()


st.set_page_config(page_title="Traffic Stops Dashboard", layout="wide")
st.title(" Traffic Stops Dashboard")

@st.cache_data
def load_full_data():
    query = "SELECT * FROM police_post_logs LIMIT 500"
    return pd.read_sql(query, engine)

st.header("Full Police Stops Data")
df = load_full_data()
st.dataframe(df, use_container_width=True)

st.header("Quick Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Police Stops", len(df))
col2.metric("Total Arrests", df['is_arrested'].sum())
col3.metric("Total Warnings", df[df['stop_outcome']=='Warning'].shape[0])
col4.metric("Drug-Related Stops", df['drugs_related_stop'].sum())

def run_query(sql):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        col_names = [i[0] for i in cursor.description]
        cursor.close()
        conn.close()
        return pd.DataFrame(rows, columns=col_names)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()


query_dict = {
    "1. Top 10 vehicles in drug stop": """
        SELECT vehicle_number, COUNT(*) as total
        FROM police_post_logs
        WHERE drugs_related_stop = 1
        GROUP BY vehicle_number
        ORDER BY total DESC
        LIMIT 10;
    """,

  
    "2. Most searched vehicles": """
        SELECT vehicle_number, COUNT(*) as searches
        FROM police_post_logs
        WHERE search_conducted = 1
        GROUP BY vehicle_number
        ORDER BY searches DESC
        LIMIT 10;
    """,

    "3. Top arrest rate by age group": """
        SELECT driver_age, COUNT(*) as total, 
               SUM(is_arrested) as arrests,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate
        FROM police_post_logs
        GROUP BY driver_age
        HAVING total > 5
        ORDER BY arrest_rate DESC
        LIMIT 5;
    """,

    "4. Gender distribution by country": """
        SELECT country_name, driver_gender, COUNT(*) as total
        FROM police_post_logs
        GROUP BY country_name, driver_gender;
    """,
"5. Highest search rate: race & gender": """
        SELECT driver_race, driver_gender,
               COUNT(*) as total_stops,
               SUM(search_conducted) as searches,
               ROUND(SUM(search_conducted) * 100.0 / COUNT(*), 2) as search_rate
        FROM police_post_logs
        GROUP BY driver_race, driver_gender
        ORDER BY search_rate DESC
        LIMIT 5;
    """,

    "6. Peak stop time of day": """
        select hour(stop_time) as hour,
               COUNT(*) as total_stops
        FROM police_post_logs
        GROUP BY hour
        ORDER BY total_stops DESC
        LIMIT 5;
    """,

    "7. Avg stop duration by violation": """
        SELECT violation, ROUND(AVG(stop_duration), 2) as avg_duration
        FROM police_post_logs
        GROUP BY violation
        ORDER BY avg_duration DESC
        LIMIT 10;
    """,

    "8. Night stops higher arrest rate?": """
        SELECT CASE WHEN hour(stop_time) BETWEEN 20 AND 23 OR hour(stop_time) BETWEEN 0 AND 5 THEN 'Night' ELSE 'Day' END as time_period,
        COUNT(*) as total,
        SUM(is_arrested) as arrests,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate
        FROM police_post_logs
        GROUP BY time_period;
    """,

    "9. Violation search/arrests": """
        SELECT violation,
               COUNT(*) as total,
               SUM(search_conducted = 'Yes') as searches,
               SUM(is_arrested) as arrests,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate
        FROM police_post_logs
        GROUP BY violation
        ORDER BY arrest_rate DESC
        LIMIT 10;
    """,

    "10. Top violation for age < 25": """
        SELECT violation, COUNT(*) as total
        FROM police_post_logs
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY total DESC
        LIMIT 5;
    """,

    "11. Violation with lowest search/arrest rate": """
        SELECT violation,
               COUNT(*) as total,
               SUM(search_conducted = 'Yes') as searches,
               SUM(is_arrested) as arrests,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate
        FROM police_post_logs
        GROUP BY violation
        HAVING total > 10
        ORDER BY arrest_rate ASC
        LIMIT 5;
    """,

    "12. Top countries by drugs related stop rate": """
    SELECT country_name,
               COUNT(*) as total,
               SUM(drugs_related_stop = 'Yes') as drug_stops,
               ROUND(SUM(drugs_related_stop = 'Yes')*100.0/COUNT(*), 2) as rate
        FROM police_post_logs
        GROUP BY country_name
        ORDER BY rate DESC
        LIMIT 5;
    """,

    "13. Arrest rate by country and violation": """
        SELECT country_name, violation,
               COUNT(*) as total,
               SUM(is_arrested) as arrests,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate
        FROM police_post_logs
        GROUP BY country_name, violation
        ORDER BY arrest_rate DESC
        LIMIT 10;
    """,

    "14. Top country by search conducted stops": """
        SELECT country_name,
               SUM(search_conducted = 'Yes') as total_searches
        FROM police_post_logs
        GROUP BY country_name
        ORDER BY total_searches DESC
        LIMIT 5;
    """,

    "15. Year wise stops and arrest by country": """
        SELECT country_name,
               year(stop_date) as year,
               COUNT(*) as total_stops,
               SUM(is_arrested) as arrests
        FROM police_post_logs
        GROUP BY country_name, year
        ORDER BY year ASC;
    """,
    "16. Driver violation trends by age and race (join + subquery)": """
        SELECT p.driver_age, p.driver_race, p.violation, COUNT(*) as total
        FROM police_post_logs p
        WHERE p.driver_age IN (
            SELECT driver_age FROM police_post_logs GROUP BY driver_age HAVING COUNT(*) > 5
        )
        GROUP BY p.driver_age, p.driver_race, p.violation
        ORDER BY total DESC
        LIMIT 10;
    """,

    "17. Time analysis by year, month, hour (date + join)": """
        SELECT year(stop_date) as year,
               month(stop_date) as month,
               hour(stop_time) as hour,
               COUNT(*) as total_stops
        FROM police_post_logs
        GROUP BY year, month, hour
        ORDER BY year, month, hour;
    """,

    "18. Violation with high search and arrest rates": """
        SELECT violation,
               COUNT(*) as total,
               SUM(search_conducted = 'Yes') as searches,
               SUM(is_arrested) as arrests,
               ROUND(SUM(search_conducted = 'Yes')*100.0/COUNT(*), 2) as search_rate,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate FROM police_post_logs
               GROUP BY violation
               HAVING total > 10 AND search_rate > 50 AND arrest_rate > 40
               ORDER BY arrest_rate DESC
        LIMIT 5;
    """,

   "19.Driver demographics by country(age,gender,race)": """
        SELECT country_name,
               ROUND(AVG(driver_age), 1) as avg_age,
               SUM(driver_gender = 'Male') as male,
               SUM(driver_gender = 'Female') as female,
               COUNT(DISTINCT driver_race) as race_diversity
        FROM police_post_logs
        GROUP BY country_name
        ORDER BY avg_age DESC;
    """,

    "20. Top 5 violation with highest arrest rates": """
        SELECT violation,
               COUNT(*) as total,
               SUM(is_arrested) as arrests,
               ROUND(SUM(is_arrested)*100.0/COUNT(*), 2) as arrest_rate
        FROM police_post_logs
        GROUP BY violation
        HAVING total > 10
        ORDER BY arrest_rate DESC
        LIMIT 5;
    """
}
st.header("Advanced Insights")
selected_query = st.selectbox("Select a Query to Run", list(query_dict.keys()))
if st.button("Run Query"):
    result_df = run_query(query_dict[selected_query])
    st.dataframe(result_df, use_container_width=True)


def run_query(sql):
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


st.header(" Add New Police Stop Record")

with st.form("input_form", clear_on_submit=True):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["M", "F"])
    driver_age_raw = st.number_input("Driver Age (Raw)", min_value=10, max_value=100)
    driver_age = st.number_input("Driver Age", min_value=10, max_value=100)
    driver_race = st.text_input("Driver Race")
    violation_raw = st.text_input("Violation (Raw)")
    violation = st.text_input("Violation")
    search_conducted = st.checkbox("Search Conducted")
    search_type = st.text_input("Search Type")
    stop_outcome = st.selectbox("Stop Outcome", ["Arrest", "Warning", "Citation", "None"])
    is_arrested = st.checkbox("Arrested")
    stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min","30+Min"])
    drugs_related_stop = st.checkbox("Drugs Related Stop")
    vehicle_number = st.text_input("Vehicle Number")

    submitted = st.form_submit_button("Add Record")

    if submitted:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO police_post_logs (
                    stop_date, stop_time, country_name, driver_gender, driver_age_raw,
                    driver_age, driver_race, violation_raw, violation, search_conducted,
                    search_type, stop_outcome, is_arrested, stop_duration,
                    drugs_related_stop, vehicle_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            values = (
                stop_date, stop_time.strftime("%H:%M:%S"), country_name, driver_gender,
                driver_age_raw, driver_age, driver_race, violation_raw, violation,
                int(search_conducted), search_type, stop_outcome, int(is_arrested),
                stop_duration, int(drugs_related_stop), vehicle_number
            )
            cursor.execute(insert_sql, values)
            conn.commit()
            st.success("Record inserted successfully!")
        except Exception as e:
            st.error(f"Failed to add record: {e}")
        finally:
           cursor.close()
           conn.close()
           st.markdown("---")
           
st.subheader("View Latest Police Records")

if st.button("Show Latest Records"):
    latest_records = run_query("SELECT * FROM police_post_logs ORDER BY id DESC LIMIT 10")
    st.dataframe(latest_records)



st.header("Filter Data for Prediction")

gender_filter = st.selectbox("Filter by Gender", options=["All", "M", "F"])
race_filter = st.text_input("Filter by Driver Race (optional)")
search_filter = st.selectbox("Search Conducted?", options=["All", "Yes", "No"])

filtered_df = df.copy()

if gender_filter != "All":
    filtered_df = filtered_df[filtered_df['driver_gender'] == gender_filter]

if race_filter:
    filtered_df = filtered_df[filtered_df['driver_race'].str.contains(race_filter, case=False)]

if search_filter != "All":
    val = True if search_filter == "Yes" else False
    filtered_df = filtered_df[filtered_df['search_conducted'] == val]

st.dataframe(filtered_df, use_container_width=True)

st.header(" Predict Stop Outcome")

if not filtered_df.empty:
    sample = filtered_df.sample(1).iloc[0]
    if sample['search_conducted'] and sample['drugs_related_stop']:prediction = "High chance of Arrest"
    elif sample['stop_duration'] == "30+ Min":
        prediction = "Possible Warning or Arrest"
    else:
        prediction = "Likely Citation"

    st.write(f"Predicted Outcome: {prediction}")
else:
    st.warning("No data available after filtering.")
st.markdown("---")  
  
st.header("Natural Language Summary")
def generate_summary(row):
    stop_date = row['stop_date'] if row['stop_date'] else "Unknown date"
    stop_time = row['stop_time'] if row['stop_time'] else "Unknown time"
    gender = row.get('driver_gender', 'Unknown')
    age = row.get('driver_age', 'Unknown')
    violation = row.get('violation', 'Unknown violation')
    search = "No search was conducted" if not row.get('search_conducted', False) else "Search was conducted"
    outcome = row.get('stop_outcome', 'Unknown outcome').lower()
    duration = row.get('stop_duration', 'Unknown duration')
    drugs = "was drug-related" if row.get('drugs_related_stop', False) else "was not drug-related"

    summary = (
        f"A {age}-year-old {gender} driver was stopped for {violation} at {stop_time} on {stop_date}. "
        f"{search}, and received a {outcome}. "
        f"The stop lasted {duration} and {drugs}."
    )
    return summary
st.header("Natural Language Summary")
if not df.empty:
    st.info(generate_summary(df.iloc[0]))
else:
    st.info("No data available to summarize.")



