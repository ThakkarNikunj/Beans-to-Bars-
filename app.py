import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pycountry

# Page Configuration
st.set_page_config(
    page_title="Beans to Bars",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .card {
        background-color: #000000;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 15px;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #34495e;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv('Chocolate Sales.csv')
    df['Amount'] = df['Amount'].str.replace('[$,]', '', regex=True).astype(float)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Month'] = df['Date'].dt.month_name()
    df['Year'] = df['Date'].dt.year
    df['Revenue per Box'] = df['Amount'] / df['Boxes Shipped']
    return df

df = load_data()

# Dashboard Header
st.title(" Chocolate Sales Analytics")

# Sidebar Filters
with st.sidebar:
    st.header("Filters")
    countries = st.multiselect(
        "Countries",
        options=sorted(df['Country'].unique()),
        default=df['Country'].unique()
    )
    products = st.multiselect(
        "Products",
        options=sorted(df['Product'].unique()),
        default=df['Product'].unique()
    )

# Apply filters
filtered_df = df[
    (df['Country'].isin(countries)) & 
    (df['Product'].isin(products))
]

# Key Metrics
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    total_sales = filtered_df['Amount'].sum()
    st.markdown(f"""
    <div class="card">
        <div>Total Sales</div>
        <div class="metric-value">${total_sales:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    total_boxes = filtered_df['Boxes Shipped'].sum()
    st.markdown(f"""
    <div class="card">
        <div>Total Boxes Shipped</div>
        <div class="metric-value">{total_boxes:,}</div>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    avg_revenue = total_sales / total_boxes if total_boxes > 0 else 0
    st.markdown(f"""
    <div class="card">
        <div>Revenue per Box</div>
        <div class="metric-value">${avg_revenue:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)



# 1. Monthly Sales Comparison Bar Chart 📅

st.markdown('<div class="section-header"> Monthly Sales Comparison</div>', unsafe_allow_html=True)

monthly_sales = filtered_df.groupby(['Year', 'Month'])['Amount'].sum().reset_index()
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

fig = px.bar(
    monthly_sales,
    x='Month',
    y='Amount',
    color='Year',
    barmode='group',
    category_orders={'Month': month_order},
    labels={'Amount': 'Sales ($)'}
)
st.plotly_chart(fig, use_container_width=True)



# 3. Daily Sales Trend Line Chart 📈
st.markdown('<div class="section-header"> Daily Sales Trend</div>', unsafe_allow_html=True)

daily_sales = filtered_df.groupby('Date')['Amount'].sum().reset_index()
fig = px.line(
    daily_sales,
    x='Date',
    y='Amount',
    labels={'Amount': 'Sales ($)'}
)
st.plotly_chart(fig, use_container_width=True)






# 5. Country-Product Matrix 🌍

st.markdown('<div class="section-header">Top Products by Country</div>', unsafe_allow_html=True)

top_combos = filtered_df.groupby(['Country', 'Product'])['Amount'].sum().nlargest(15).reset_index()
fig = px.bar(
    top_combos,
    x='Amount',
    y='Country',
    color='Product',
    orientation='h',
    labels={'Amount': 'Sales ($)'}
)
st.plotly_chart(fig, use_container_width=True)





# sales by country
st.markdown('<div class="section-header">Sales by Country (Map)</div>', unsafe_allow_html=True)

# Convert country names to ISO codes
def country_to_iso(country_name):
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
    except:
        return None

country_sales = filtered_df.groupby('Country')['Amount'].sum().reset_index()
country_sales['ISO'] = country_sales['Country'].apply(country_to_iso)

fig = px.choropleth(
    country_sales,
    locations="ISO",
    color="Amount",
    hover_name="Country",
    color_continuous_scale=px.colors.sequential.Plasma,
    labels={'Amount': 'Total Sales ($)'}
)
st.plotly_chart(fig, use_container_width=True)






# 5. Top Products Bar Chart
st.markdown('<div class="section-header"> Top Performing Products</div>', unsafe_allow_html=True)
top_products = filtered_df.groupby('Product')['Amount'].sum().nlargest(10).reset_index()
fig = px.bar(
    top_products,
    x='Amount',
    y='Product',
    orientation='h',
    color='Amount',
    labels={'Amount': 'Total Sales ($)', 'Product': ''}
)
st.plotly_chart(fig, use_container_width=True)







# 1. Sales Trend by Weekday
st.markdown('<div class="section-header"> Sales by Day of Week</div>', unsafe_allow_html=True)
weekday_sales = filtered_df.groupby('Date')['Amount'].sum().reset_index()
weekday_sales['Weekday'] = weekday_sales['Date'].dt.day_name()
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
fig = px.box(
    weekday_sales,
    x='Weekday',
    y='Amount',
    category_orders={'Weekday': weekday_order},
    labels={'Amount': 'Daily Sales ($)', 'Weekday': ''}
)
st.plotly_chart(fig, use_container_width=True)







# top 10 sales of the day
st.markdown('<div class="section-header">🏆 Top 10 Sales Days</div>', unsafe_allow_html=True)

top_days = filtered_df.groupby('Date')['Amount'].sum().nlargest(10).reset_index()
top_days['FormattedDate'] = top_days['Date'].dt.strftime('%b %d, %Y')

fig = px.bar(
    top_days,
    x='FormattedDate',
    y='Amount',
    labels={'Amount': 'Sales ($)', 'FormattedDate': 'Date'}
)
fig.update_layout(xaxis={'categoryorder':'total descending'})
st.plotly_chart(fig, use_container_width=True)






# Prepare animated data
growth_df = filtered_df.groupby(['Year', 'Product']).agg({
    'Amount': 'sum',
    'Boxes Shipped': 'sum'
}).reset_index()
growth_df['Revenue per Box'] = growth_df['Amount'] / growth_df['Boxes Shipped']

fig = px.scatter(
    growth_df,
    x="Boxes Shipped",
    y="Amount",
    size="Revenue per Box",
    color="Product",
    animation_frame="Year",
    hover_name="Product",
    size_max=45,
    range_x=[growth_df['Boxes Shipped'].min()*0.9, growth_df['Boxes Shipped'].max()*1.1],
    range_y=[growth_df['Amount'].min()*0.9, growth_df['Amount'].max()*1.1],
    labels={'Amount': 'Total Revenue ($)', 'Boxes Shipped': 'Boxes Shipped'}
)
st.plotly_chart(fig, use_container_width=True)




# revenune vs box
st.markdown('<div class="section-header"> Volume vs Revenue</div>', unsafe_allow_html=True)
ratio_df = filtered_df.groupby('Product').agg({
    'Amount': 'sum',
    'Boxes Shipped': 'sum'
}).reset_index()
ratio_df['Ratio'] = ratio_df['Amount'] / ratio_df['Boxes Shipped']

fig = px.scatter(
    ratio_df,
    x='Boxes Shipped',
    y='Amount',
    size='Ratio',
    color='Ratio',
    hover_name='Product',
    log_x=True,
    labels={
        'Amount': 'Total Revenue ($)',
        'Boxes Shipped': 'Boxes Shipped (log scale)',
        'Ratio': 'Revenue/Box'
    }
)
st.plotly_chart(fig, use_container_width=True)






# 4. Monthly Sales Comparison
st.markdown('<div class="section-header">Monthly Sales Trends</div>', unsafe_allow_html=True)
monthly_sales = filtered_df.groupby(['Year', 'Month'])['Amount'].sum().reset_index()
fig = px.line(
    monthly_sales,
    x='Month',
    y='Amount',
    color='Year',
    markers=True,
    labels={'Amount': 'Sales ($)', 'Month': ''}
)
st.plotly_chart(fig, use_container_width=True)


















# 2. Product Sales Composition 🍫

st.markdown('<div class="section-header"> Product Sales Composition</div>', unsafe_allow_html=True)

product_sales = filtered_df.groupby('Product')['Amount'].sum().nlargest(10)
fig = px.pie(
    product_sales,
    values=product_sales.values,
    names=product_sales.index,
    hole=0.3
)
st.plotly_chart(fig, use_container_width=True)




st.markdown('<div class="section-header"> Sales Hierarchy</div>', unsafe_allow_html=True)

sunburst_data = filtered_df.groupby(['Country', 'Product'])['Amount'].sum().reset_index()

fig = px.sunburst(
    sunburst_data,
    path=['Country', 'Product'],
    values='Amount',
    color='Amount',
    color_continuous_scale='RdBu',
    hover_data=['Amount']
)
st.plotly_chart(fig, use_container_width=True)




# Country Performance
st.markdown('<div class="section-header">🌎 Country Performance</div>', unsafe_allow_html=True)

country_sales = filtered_df.groupby('Country')['Amount'].sum()
top_country = country_sales.idxmax()
max_sales = country_sales.max()
total_sales = country_sales.sum()

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = max_sales,
    title = f"Top Country: {top_country}",
    gauge = {
        'axis': {'range': [0, total_sales*0.5]},
        'steps': [
            {'range': [0, total_sales*0.25], 'color': "lightgray"},
            {'range': [total_sales*0.25, total_sales*0.5], 'color': "gray"}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': max_sales}
    }
))
st.plotly_chart(fig, use_container_width=True)



# Raw Data
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data",
        data=csv,
        file_name="chocolate_sales.csv",
        mime="text/csv"
    )









