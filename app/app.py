import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="NFL Rushing Stats Explorer", layout="wide")

st.title("🏈 NFL Football Stats (Rushing) Explorer")
st.markdown("""
This app performs simple web scraping of NFL Football player stats data (focusing on Rushing)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, requests, BeautifulSoup  
* **Data source:** [pro-football-reference.com](https://www.pro-football-reference.com/)
""")

st.sidebar.header("User Input Features")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(1990, 2023))))

@st.cache_data(show_spinner=True)
def load_data(year):
    url = f"https://www.pro-football-reference.com/years/{year}/rushing.htm"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    table = soup.find("table", {"id": "rushing"})
    if table is None:
        return pd.DataFrame()
    header_row = table.find("thead").find_all("tr")[-1]
    headers = [th.getText() for th in header_row.find_all("th")][1:]
    rows = table.find("tbody").find_all("tr")
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) != len(headers):
            continue
        data.append([col.getText() for col in cols])
    df = pd.DataFrame(data, columns=headers)
    df = df.fillna(0)
    return df

playerstats = load_data(selected_year)

required_columns = ["Tm", "Pos"]
missing = [col for col in required_columns if col not in playerstats.columns]
if missing:
    st.error(f"Missing required columns: {missing}. The site structure may have changed.")
    st.write("Available columns:", playerstats.columns.tolist())
    st.stop()

sorted_unique_team = sorted(playerstats["Tm"].unique())
selected_team = st.sidebar.multiselect("Team", sorted_unique_team, sorted_unique_team)

unique_pos = ["RB", "QB", "WR", "FB", "TE"]
selected_pos = st.sidebar.multiselect("Position", unique_pos, unique_pos)

df_selected_team = playerstats[
    (playerstats["Tm"].isin(selected_team)) & 
    (playerstats["Pos"].isin(selected_pos))
]

st.header("Display Player Stats of Selected Team(s)")
st.write(f"Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns.")
st.dataframe(df_selected_team)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

if st.button("Intercorrelation Heatmap"):
    df_numeric = df_selected_team.select_dtypes(include=[np.number])
    corr = df_numeric.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    with sns.axes_style("white"):
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(corr, mask=mask, vmax=1, square=True, annot=True, fmt=".2f", cmap="coolwarm")
    st.pyplot(fig)
