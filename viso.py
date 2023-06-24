import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv("hotel_bookings.csv")

# Convert 'arrival_date_month' to datetime and extract month
df['arrival_date_month'] = pd.to_datetime(df['arrival_date_month'], format='%B')
df['arrival_month'] = df['arrival_date_month'].dt.month.astype(int)

# Set the title of the app
st.title('Hotel Bookings Analysis')
st.markdown(
    "This dashboard aims to analyze and present global hotel reservation data, specifically for city and resort hotels. Our goal is to identify key booking trends such as most frequent guests, their origin countries, peak booking times, and monthly cancellation rates. This data will help reveal unique hotel characteristics, providing valuable insights for hotel owners on topics like busiest months, likely cancellations, and profitable reservation types, thereby aiding them in making informed business decisions.")
st.markdown("------------------")  # Add a horizontal line

# Create a grouped dataframe for the plot
df_grouped = df.groupby(['country', 'hotel']).size().reset_index(name='counts')

# Pivot the dataframe to have hotels as columns
df_pivot = df_grouped.pivot(index='country', columns='hotel', values='counts').reset_index().fillna(0)
df_pivot['total'] = df_pivot['City Hotel'] + df_pivot['Resort Hotel']

# Date range slider for selecting a specific time period
date_range = st.slider("Select a Month Range", min_value=int(df['arrival_month'].min()),
                       max_value=int(df['arrival_month'].max()),
                       value=(int(df['arrival_month'].min()), int(df['arrival_month'].max())))

# Filter the data based on the selected date range
df_filtered = df[(df['arrival_month'] >= date_range[0]) & (df['arrival_month'] <= date_range[1])]

# Add a selectbox for country selection
country_options = ['All'] + list(df_filtered['country'].unique())
selected_country = st.sidebar.selectbox('Select Country To Filter', options=country_options)
st.sidebar.markdown(
    "This filter enables you to select a country and view order data specific to that country. It updates the first 4 graphs to show visualizations tailored to the selected country and provides a data overview section with the option to adjust the number of displayed rows")
st.sidebar.markdown("------------------")  # Add a horizontal line

if selected_country != 'All':
    df_filtered = df_filtered[df_filtered['country'] == selected_country]

# Add a selectbox for hotel type
hotel_type = st.sidebar.selectbox('Select Hotel Type To Filter', options=['All'] + list(df_filtered['hotel'].unique()))
st.sidebar.markdown(
    "Select a hotel type to filter the data and view order information specific to that type. The filter updates the first 4 graphs to show visualizations tailored to the selected hotel type and country, and provides a data overview section with adjustable row display.")
if hotel_type != 'All':
    df_filtered = df_filtered[df_filtered['hotel'] == hotel_type]

# Add a data overview section
if st.checkbox('Show Data Overview', value=True):
    st.subheader('Data Overview')

    # Add a number input field to select the number of rows
    num_rows = st.number_input('Enter number of rows', min_value=5, max_value=df_filtered.shape[0], value=5)

    st.write(df_filtered.head(num_rows))
    st.write(f"Number of rows: {df_filtered.shape[0]}")

# Filter for each hotel type
df_resort = df_filtered[df_filtered['hotel'] == 'Resort Hotel']
df_city = df_filtered[df_filtered['hotel'] == 'City Hotel']

# Calculate the total guests for each month
resort_guests = df_resort['arrival_month'].value_counts().sort_index()
city_guests = df_city['arrival_month'].value_counts().sort_index()

# Line chart for Resort and City
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=resort_guests.index, y=resort_guests.values, mode='lines+markers', name='Resort',
                          line=dict(color='blue')))
fig3.add_trace(
    go.Scatter(x=city_guests.index, y=city_guests.values, mode='lines+markers', name='City', line=dict(color='red')))
fig3.update_layout(title_text="Total guests by month", xaxis_title="Month", yaxis_title="Number of Guests")

# Filter data where 'is_canceled' is 1 (meaning the booking was cancelled)
canceled = df_filtered[df_filtered['is_canceled'] == 1]

# Count the number of cancellations for each distribution channel and hotel type
cancellation_counts = canceled.groupby(['hotel', 'distribution_channel']).size().reset_index(name='cancellation_count')

cancellation_counts = cancellation_counts.sort_values('cancellation_count', ascending=False)

# Create a bar chart for cancellations by distribution channel and hotel type
fig4 = px.bar(cancellation_counts, x='distribution_channel', y='cancellation_count', color='hotel',
              title='Cancellation Counts by Distribution Channel and Hotel Type',
              color_discrete_sequence=["green", "blue"])

# For each hotel type
temp = pd.DataFrame()
for hotel in df_filtered['hotel'].unique():
    # Calculate the value counts for each market segment
    temp[hotel] = df_filtered[df_filtered['hotel'] == hotel]['market_segment'].value_counts()

# Reset the index and rename the columns
temp_reset = temp.reset_index().rename(columns={'index': 'market_segment'})

# Reshape the dataframe for plotly express
temp_melt = temp_reset.melt(id_vars='market_segment', value_vars=df_filtered['hotel'].unique(),
                            var_name='Hotel Type', value_name='Number of Guests')

temp_melt = temp_melt.sort_values('Number of Guests', ascending=False)

# Create the bar plot
fig5 = px.bar(temp_melt,
              x='market_segment',
              y='Number of Guests',
              color='Hotel Type',
              title='Total guests for each hotel Grouped by market segment',
              labels={'market_segment': 'Market Segment'},
              color_discrete_sequence=["green", "blue"])

# data = df[df['is_canceled'] == 0]
df_filtered = df_filtered[df_filtered['is_canceled'] == 0]
fig6 = px.box(data_frame=df_filtered, x='reserved_room_type', y='adr', color='hotel',
              color_discrete_sequence=px.colors.qualitative.G10, title='Average Daily Rate by Room Type')
fig6.update_layout(width=800, height=600)

# Create buttons to toggle the visibility of the graphs
button_labels = ['Total guests for Resort and City hotel by month',
                 'Cancellation Counts by Distribution Channel',
                 'Total guests for each hotel Grouped by market segment',
                 'Average Daily Rate by Room Type']

button_values = [0, 1, 2, 3]
selected_button = st.radio('Select a graph to display:', button_values, format_func=lambda x: button_labels[x])

if selected_button == 0:
    st.plotly_chart(fig3)
    st.markdown(
        "The goal of this graph is to compare the number of guests between the City Hotel and the Resort Hotel and identify the patterns and trends in guest numbers over time, The graph illustrates that the City Hotel consistently hosts a larger number of guests compared to the Resort Hotel. A notable trend across both establishments is the peak in guest numbers during August, indicating a high season. Conversely, the period from November to February appears to be a low season, with significantly fewer guests.")
    st.markdown("------------------")  # Add a horizontal line
elif selected_button == 1:
    st.plotly_chart(fig4)
    st.markdown(
        "The graph demonstrates that the majority of cancellations are initiated via travel agencies or tour operators. Furthermore, it's evident that the City Hotel experiences a higher rate of cancellations compared to the Resort Hotel.")
    st.markdown("------------------")  # Add a horizontal line
elif selected_button == 2:
    st.plotly_chart(fig5)
    st.markdown(
        "The goal of this graph is to provide insights into the market segments for the hotels. This graph indicates that the predominant channel for bookings is through online travel agencies. Additionally, it's observable that the City Hotel garners more bookings across all market segments, with the exception of direct bookings, where the Resort Hotel takes the lead.")
    st.markdown("------------------")  # Add a horizontal line
elif selected_button == 3:
    st.plotly_chart(fig6)
    st.markdown(
        "The goal of this graph is to depict the relationship between the average price per room and its type. The figure shows that the average price per room depends on its type and the standard deviation.The graph aims to illustrate the popularity of different room types by showcasing the booking frequency. It also provides a comparison between the two hotel types based on room availability. The Average Daily Rate (ADR) is utilized as an index to indicate the average cost per night for reservations. This graph conveniently presents the ADR comparison across a range of diverse room types, offering valuable insights into pricing variations.")
    st.markdown("------------------")  # Add a horizontal line

# Create the interactive plot
fig1 = px.choropleth(df_pivot, locations='country', color='total',
                     title='Number of Bookings Per Country',
                     labels={'total': 'Total Number of Bookings', 'country': 'Country'},
                     hover_name='country',
                     color_continuous_scale=px.colors.sequential.Plasma,
                     projection='natural earth',
                     hover_data={'City Hotel': True, 'Resort Hotel': True})

st.plotly_chart(fig1)
st.markdown(
    "The goal of this graph is to provide a comprehensive overview of the regions with the highest order volumes. This choropleth map presents a comprehensive view of the geographical distribution of the hotel's guests by illustrating the total number of bookings per country. It's evident that Western Europe stands out with a higher volume of bookings compared to other regions. The prevalence of blue hues across the map signifies that reservations from these countries are relatively lower."
    " the graph allows zooming in to obtain more precise and detailed information.")
st.markdown("------------------")  # Add a horizontal line
