import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="NFL Rushing Stats Explorer", layout="wide")

st.title('NFL Football Stats (Rushing) Explorer')
st.markdown("""
This app performs simple web scraping of NFL Football player stats data (focusing on Rushing)!
* **Python libraries:** base64, pandas, streamlit, matplotlib, seaborn  
* **Data source:** [Pro-Football-Reference.com](https://www.pro-football-reference.com/)
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1990, 2021))))
debug_mode = st.sidebar.checkbox("Show raw table info")

@st.cache_data(show_spinner=True)
def load_data(year):
    url = f"https://www.pro-football-reference.com/years/{year}/rushing.htm"
    try:
        tables = pd.read_html(url, header=1)
        for table in tables:
            if "Age" in table.columns and "Tm" in table.columns and "Pos" in table.columns:
                df = table[table.Age != "Age"]
                df = df.fillna(0)
                df = df.drop(["Rk"], axis=1)
                return df, tables
        return pd.DataFrame(), tables
    except Exception:
        return pd.DataFrame(), []

playerstats, raw_tables = load_data(selected_year)

if playerstats.empty:
    st.error("Failed to load player stats. The table structure may have changed.")
    if debug_mode and raw_tables:
        st.subheader("Debug: Raw Table Structures")
        for i, table in enumerate(raw_tables):
            st.write(f"Table {i} Columns: {table.columns.tolist()}")
else:
    sorted_unique_team = sorted(playerstats.Tm.unique())
    selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

    unique_pos = ['RB', 'QB', 'WR', 'FB', 'TE']
    selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

    df_selected_team = playerstats[
        (playerstats.Tm.isin(selected_team)) & 
        (playerstats.Pos.isin(selected_pos))
    ]

    st.header('Display Player Stats of Selected Team(s)')
    st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
    st.dataframe(df_selected_team)

    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

    if st.button('Intercorrelation Heatmap'):
        st.header('Intercorrelation Matrix Heatmap')
        corr = df_selected_team.select_dtypes(include='number').corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        with sns.axes_style("white"):
            fig, ax = plt.subplots(figsize=(7, 5))
            sns.heatmap(corr, mask=mask, vmax=1, square=True, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)
