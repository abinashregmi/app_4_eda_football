import streamlit as st
import pandas as pd

st.title("🏈 NFL Football Stats (Rushing)")
st.markdown("Exploratory Data Analysis of NFL Football Stats")

df = pd.read_csv("nfl_rushing.csv")
df = df[df['Age'].index]  # Removes duplicate index if present

selected_year = st.sidebar.selectbox('Year', list(reversed(range(1990, 2023))))
df_selected_year = df[df.Year == selected_year]

unique_team = sorted(df_selected_year.Team.unique())
selected_team = st.sidebar.multiselect('Team', unique_team, unique_team)

unique_pos = sorted(df_selected_year.Pos.unique())
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

df_selected_team = df_selected_year[df_selected_year.Team.isin(selected_team)]
df_selected_team = df_selected_team[df_selected_team.Pos.isin(selected_pos)]

st.subheader("Display Player Stats of Selected Team(s)")
st.dataframe(df_selected_team)

def filedownload(df):
    return df.to_csv(index=False)

st.download_button("Download CSV File", filedownload(df_selected_team), "playerstats.csv", "text/csv")
