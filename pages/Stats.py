import plotly.express as px
import pandas as pd
import streamlit as st


categories = ["C", "B", "A"]


tab1, tab2 = st.tabs(["Bar plots", "Box plots"])
with tab1:
    undertab1, undertab2 = st.tabs(["Inverse SP", "Cost of return"])
    percent = st.slider("Select the percent:", 1, 10, 5)
    size = len(st.session_state.edges)
    with undertab1:
        cut = st.session_state.edges.sort_values(by = "Inverse SP", ascending = False).head(int(percent/100*size))
        barplots = px.histogram(cut, "Groups", "Inverse SP", title = f"{percent}% top SP")
        barplots.update_xaxes(categoryorder='array', categoryarray=categories)
        st.plotly_chart(barplots)

    with undertab2:
        cut = st.session_state.edges.sort_values(by = "Cost of return", ascending = False).head(int(percent/100*size))
        barplots = px.histogram(cut, "Groups", "Cost of return", title = f"{percent}% top CoR")
        barplots.update_xaxes(categoryorder='array', categoryarray=categories)
        st.plotly_chart(barplots)


with tab2:
    undertab1, undertab2 = st.tabs(["Inverse SP", "Cost of return"])
    with undertab1:
        boxplots = px.box(st.session_state.edges, x = "Groups", y = "Inverse SP")
        boxplots.update_xaxes(categoryorder='array', categoryarray=categories)
        st.plotly_chart(boxplots)

    with undertab2:
        boxplots = px.box(st.session_state.edges, x = "Groups", y = "Cost of return")
        boxplots.update_xaxes(categoryorder='array', categoryarray=categories)
        st.plotly_chart(boxplots)

plotly_chart = px.scatter(st.session_state.edges, "Cost of return", "Inverse SP")
st.plotly_chart(plotly_chart)