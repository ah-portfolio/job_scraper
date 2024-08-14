import requests
import pandas as pd
import duckdb
import streamlit as st

# Create input fields in the Streamlit app
job_title = st.text_input("Job Title")
contracts = st.multiselect("Contract Type", ["contractor", "permanent", "fixed-term"])
location = st.text_input("Location")

# Call the API when the user submits the form
if st.button("Submit"):
    response = requests.post("http://scraper-app:80/scrape", json={
        "job_title": job_title,
        "contracts": [str(contract) for contract in contracts],
        "location": location
    })
    session_id = response.json()["session_id"]

    # Get the basic info and additional info from the API
    basic_info_response = requests.get(f"http://scraper-app:80/scrape/basic_info/{session_id}").json()[session_id]
    additional_info_response = requests.get(f"http://scraper-app:80/scrape/additional_info/{session_id}").json()[session_id]

    if not basic_info_response or not additional_info_response :
        st.write(f"No add found for your filters")
    
    else :
        # Parse the data into Pandas DataFrames
        basic_info = pd.DataFrame(basic_info_response)
        additional_info = pd.DataFrame(additional_info_response)

        # Save the data as Parquet files
        basic_info.to_parquet("basic_info.parquet")
        additional_info.to_parquet("additional_info.parquet")

        # Use DuckDB to generate KPIs
        conn = duckdb.connect()
        conn.execute("CREATE TABLE basic_info AS SELECT * FROM read_parquet('basic_info.parquet')")
        conn.execute("CREATE TABLE additional_info AS SELECT * FROM read_parquet('additional_info.parquet')")

        number_of_ads = conn.execute("SELECT COUNT(*) FROM basic_info").fetchone()[0]
        most_researched_skills = conn.execute("SELECT unnest(skills), COUNT(*) FROM basic_info GROUP BY skills ORDER BY COUNT(*) DESC LIMIT 10").fetchdf()
        date_of_publication_repartition = conn.execute("SELECT date, COUNT(*) FROM basic_info GROUP BY date").fetchdf()
        company_repartition = conn.execute("SELECT company, COUNT(*) FROM basic_info GROUP BY company").fetchdf()

        # Display the KPIs in the Streamlit app
        st.write(f"Number of ads: {number_of_ads}")
        st.write("Most researched skills:")
        st.table(most_researched_skills)
        st.write("Date of publication repartition:")
        st.bar_chart(date_of_publication_repartition.set_index("date"))
        st.write("Company repartition:")
        st.bar_chart(company_repartition.set_index("company"))
