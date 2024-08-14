import requests
import pandas as pd
import duckdb
import streamlit as st

st.set_page_config(page_title="Job Scraper", page_icon=":guardsman:", layout="wide")
st.markdown(
    """
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #008080;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create a left panel for filters
with st.sidebar:
    st.markdown('<p class="title">Job Scraper</p>', unsafe_allow_html=True)
    job_title = st.text_input("Job Title")
    contracts = st.multiselect("Contract Type", ["contractor", "permanent", "fixed-term"])
    location = st.text_input("Location")
    submit_button = st.button("Submit")


# Call the API when the user submits the form
if submit_button:
    with st.spinner('Wait for it...'):
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
            most_researched_skills = conn.execute('''with unnested_skills 
                                                as (
                                                    SELECT upper(unnest(skills)) as skill
                                                    FROM additional_info
                                                )
                                                select skill, count(*) as count
                                                from unnested_skills
                                                group by skill
                                                order by count(*) desc
                                                LIMIT 10;''').fetchdf()
            date_of_publication_repartition = conn.execute("SELECT date, COUNT(*) as count FROM basic_info GROUP BY date").fetchdf()
            company_repartition = conn.execute("SELECT company, COUNT(*) as count FROM basic_info GROUP BY company").fetchdf()

            # Display the KPIs in the Streamlit app
            st.write(f"Number of ads: {number_of_ads}")
            kpi_number_of_ads = st.columns(1)
            kpi_number_of_ads.metric(
                label="Nb of ads 🔢",
                value=number_of_ads)
            st.write("Most researched skills:")
            st.bar_chart(most_researched_skills.set_index("skill"))
            st.write("Date of publication repartition:")
            st.scatter_chart(date_of_publication_repartition.set_index("date"))
            st.write("Company repartition:")
            st.bar_chart(company_repartition.set_index("company"))
