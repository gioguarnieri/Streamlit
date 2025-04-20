import streamlit as st
import pandas as pd
import geopandas as gpd
import osmnx as ox
import networkx as nx
import plotly.express as px
from urllib.parse import quote

st.set_page_config(page_title="City Statistics", page_icon="📊")

st.title("City Statistics")
st.write("This page provides basic statistics for a selected city's street network.")

# Function to get graph data for a city
def get_city_data(city):
    path_gh = 'https://raw.githubusercontent.com/gioguarnieri/CoR/refs/heads/main/Results/csv/'
    edges_file = city + "_edges.csv"
    nodes_file = city + "_nodes.csv"
    
    try:
        nodes = pd.read_csv(path_gh + quote(nodes_file), index_col=[0])
        edges = pd.read_csv(path_gh + quote(edges_file), index_col=[0,1,2])
        
        # Process data
        others = ["crossing", "living_street", "unclassified", "disused", "busway", "escape", "road", "ladder"]
        edges["highway"] = edges.highway.map(lambda x: "other" if x in others else x)
        
        # Convert to GeoDataFrames
        nodes_geo = gpd.GeoSeries.from_wkt(nodes.geometry)
        nodes_gdf = gpd.GeoDataFrame(data=nodes, geometry=nodes_geo)
        nodes_gdf = nodes_gdf.set_crs('epsg:4326', allow_override=True)
        
        edges_geo = gpd.GeoSeries.from_wkt(edges.geometry)
        edges_gdf = gpd.GeoDataFrame(data=edges, geometry=edges_geo)
        edges_gdf = edges_gdf.set_crs('epsg:4326', allow_override=True)
        
        return nodes_gdf, edges_gdf
    except Exception as e:
        st.error(f"Error loading data for {city}: {str(e)}")
        return None, None

# City selection
city_list_full = ["São Paulo", "Rio de Janeiro", "Atlanta", "Manhattan", "Barcelona", 
                  "Madrid", "Buenos Aires", "London", "Beijing", "Paris", "Cardiff", 
                  "Berlin", "Amsterdam", "São José dos Campos", "Los Angeles", 
                  "Wichita", "Toulouse", "Salt Lake"]

# Allow user to input a city name or select from the list
input_method = st.radio("Select input method:", ["Choose from list", "Enter city name"])

group1 = ['motorway', 'motorway_link', 'trunk', 'trunk_link']
group2 = ['primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link']
group3 = group1 + group2

if input_method == "Choose from list":
    city = st.selectbox("Select a city:", city_list_full)
else:
    city = st.text_input("Enter city name:")

if city in city_list_full:
    input_method = "Choose from list"

if city:
    # Load data for the selected city
    if input_method == "Choose from list":
        nodes, edges = get_city_data(city)
    else:
        G = ox.graph_from_place(city, network_type='drive')
        nodes, edges = ox.graph_to_gdfs(G)
    
    if nodes is not None and edges is not None:
        st.write(f"## Statistics for {city}")
        
        # Calculate basic statistics
        total_nodes = len(nodes)
        total_edges = len(edges)
        total_length = edges['length'].sum()
        avg_length = edges['length'].mean()
        


        
        if input_method == "Choose from list":
            # Highway type distribution
            highway_counts = edges['highway'].value_counts()
            highway_percentages = (highway_counts / total_edges * 100).round(2)
            
            # Group distribution
            group_counts = edges['Groups'].value_counts()
            group_percentages = (group_counts / total_edges * 100).round(2)
            # Create statistics table
            stats_data = {
                "Metric": [
                    "Total Nodes (Intersections)", 
                    "Total Edges (Street Segments)", 
                    "Total Street Length (m)",
                    "Average Street Segment Length (m)",
                    "Group A Percentage (%)",
                    "Group B Percentage (%)",
                    "Group C Percentage (%)",
                    "Average Inverse SP",
                    "Average Cost of Return",
                    "Average Edge Betweenness"
                ],
                "Value": [
                    total_nodes,
                    total_edges,
                    f"{total_length:.2f}",
                    f"{avg_length:.2f}",
                    f"{group_percentages.get('A', 0):.2f}",
                    f"{group_percentages.get('B', 0):.2f}",
                    f"{group_percentages.get('C', 0):.2f}",
                    f"{edges['Inverse SP'].mean():.2f}",
                    f"{edges['Cost of return'].mean():.2f}",
                    f"{edges['Edge Betweenness'].mean():.6f}"
                ]
            }

        
            # Additional statistics
            st.write("### Detailed Metrics")
            
            tab1, tab2, tab3 = st.tabs(["Inverse SP", "Cost of Return", "Edge Betweenness"])
            
            with tab1:
                st.write("#### Inverse SP Statistics")
                isp_stats = edges['Inverse SP'].describe().reset_index()
                isp_stats.columns = ['Statistic', 'Value']
                st.table(isp_stats)
                
                fig_isp = px.histogram(
                    edges, 
                    x="Inverse SP", 
                    color="Groups",
                    title="Inverse SP Distribution"
                )
                st.plotly_chart(fig_isp)
            
            with tab2:
                st.write("#### Cost of Return Statistics")
                cor_stats = edges['Cost of return'].describe().reset_index()
                cor_stats.columns = ['Statistic', 'Value']
                st.table(cor_stats)
                
                fig_cor = px.histogram(
                    edges, 
                    x="Cost of return", 
                    color="Groups",
                    title="Cost of Return Distribution"
                )
                st.plotly_chart(fig_cor)
            
            with tab3:
                st.write("#### Edge Betweenness Statistics")
                eb_stats = edges['Edge Betweenness'].describe().reset_index()
                eb_stats.columns = ['Statistic', 'Value']
                st.table(eb_stats)
                
                fig_eb = px.histogram(
                    edges, 
                    x="Edge Betweenness", 
                    color="Groups",
                    title="Edge Betweenness Distribution"
                )
                st.plotly_chart(fig_eb)
        


        else:
            edges["highway"] = edges.highway.map(lambda x: x[0] if isinstance(x, list) else x)

            edges["Groups"] = edges.highway

            edges["Groups"] = edges.highway.map(lambda x: 'C' if x  not in group3 else x)
            edges["Groups"] = edges.Groups.map(lambda x: 'A' if x  in group1 else x)
            edges["Groups"] = edges.Groups.map(lambda x: 'B' if x  in group2 else x)
            # Highway type distribution
            highway_counts = edges['highway'].value_counts()
            highway_percentages = (highway_counts / total_edges * 100).round(2)
            
            # Group distribution
            group_counts = edges['Groups'].value_counts()
            group_percentages = (group_counts / total_edges * 100).round(2)
            stats_data = {
                "Metric": [
                    "Total Nodes (Intersections)", 
                    "Total Edges (Street Segments)", 
                    "Total Street Length (m)",
                    "Average Street Segment Length (m)",
                    "Group A Percentage (%)",
                    "Group B Percentage (%)",
                    "Group C Percentage (%)",
                ],
                "Value": [
                    total_nodes,
                    total_edges,
                    f"{total_length:.2f}",
                    f"{avg_length:.2f}",
                    f"{group_percentages.get('A', 0):.2f}",
                    f"{group_percentages.get('B', 0):.2f}",
                    f"{group_percentages.get('C', 0):.2f}",
                ]
            }

        
        stats_df = pd.DataFrame(stats_data)
        st.table(stats_df)
        
        # Highway type distribution
        st.write("### Highway Type Distribution")
        fig_highway = px.pie(
            values=highway_counts.values,
            names=highway_counts.index,
            title="Highway Types"
        )
        st.plotly_chart(fig_highway)
        
        # Group distribution
        st.write("### Group Distribution")
        fig_groups = px.pie(
            values=group_counts.values,
            names=group_counts.index,
            title="Groups",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_groups)


    else:
        st.warning(f"No data available for {city}. Please select a different city.")

       # Download options
        st.write("### Download Data")
        
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv().encode('utf-8')
        
    csv_nodes = convert_df_to_csv(nodes.drop(columns=['geometry']))
    csv_edges = convert_df_to_csv(edges.drop(columns=['geometry']))

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Nodes Data",
            data=csv_nodes,
            file_name=f'{city}_nodes_stats.csv',
            mime='text/csv',
        )
    with col2:
        st.download_button(
            label="Download Edges Data",
            data=csv_edges,
            file_name=f'{city}_edges_stats.csv',
            mime='text/csv',
        )