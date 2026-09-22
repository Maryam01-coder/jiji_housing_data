# Importing library
import pandas as pd
import streamlit as st
import plotly.express as px

# set up config
st.set_page_config(
    page_title="Jiji House Listings",
    page_icon="🏘",
    layout="wide"
)

# @st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("jiji_housing_cleaned.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An Error occured: {e}")


def create_sidebar_filter(df):
    st.sidebar.header("🔍 Filters")

    house_type = st.sidebar.multiselect(
        "Choose House Type",
        options=df["house_type"].unique(),
        default=df["house_type"].unique(),
    )

    furnishing = st.sidebar.multiselect(
        "Select Furnishing Status",
        options=df["furnishing"].unique(),
        default=df["furnishing"].unique(),
    )
    region = st.sidebar.multiselect(
        "Select State",
        options=df["region_parent_name"].unique(),
        default=df["region_parent_name"].unique(),
    )

    st.sidebar.divider()

    size = st.sidebar.slider(
    "Select Property Size",
    min_value=int(df["property_size(sqm)"].min()),
    max_value=int(df["property_size(sqm)"].max()),
    value=(int(df["property_size(sqm)"].min()), int(df["property_size(sqm)"].max()))
    )
    bedrooms = st.sidebar.slider(
    "Select Number of Bedrooms",
    min_value=int(df["bedrooms"].min()),
    max_value=int(df["bedrooms"].max()),
    value=(int(df["bedrooms"].min()), int(df["bedrooms"].max()))
    )
    bathrooms = st.sidebar.slider(
    "Select Number of Bathrooms",
    min_value=int(df["bathrooms"].min()),
    max_value=int(df["bathrooms"].max()),
    value=(int(df["bathrooms"].min()), int(df["bathrooms"].max()))
    )
    return house_type, furnishing, region, size, bedrooms, bathrooms

def filter_data(df, house_type, furnishing, region, size, bedrooms, bathrooms):
    filtered_df = df[
        (df["house_type"].isin(house_type)) & 
        (df["furnishing"].isin(furnishing)) & 
        (df["region_parent_name"].isin(region)) & 
        (df["property_size(sqm)"] >= size[0]) &
        (df["property_size(sqm)"] <= size[1]) &
        (df["bedrooms"] >= bedrooms[0]) &
        (df["bedrooms"] <= bedrooms[1]) &
        (df["bathrooms"] >= bathrooms[0]) &
        (df["bathrooms"] <= bathrooms[1])
    ]

    return filtered_df 

def format_price(value):
    if value >= 1000000:
        return f"₦{value / 1000000:.1f}M"
    elif value >= 1000:
        return f"₦{value / 1000:.1f}K"
    else:
        return f"₦{value:,.0f}"

def display_metrics(filtered_df):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🏠 Total House", len(filtered_df))

    with col2:
        avg_price = filtered_df["price"].mean() if len(filtered_df) > 0 else 0
        st.metric("💲 Average Housing Price", format_price(avg_price))

    with col3:
        most_common_region = filtered_df["region_parent_name"].value_counts().idxmax() if len(filtered_df) > 0 else 0
        st.metric("🌃 Most Common State", f"{most_common_region}")

    with col4:
        most_common_house_type = filtered_df["house_type"].value_counts().idxmax() if len(filtered_df) > 0 else 0
        st.metric("🏠 Most Common House Type", f"{most_common_house_type}")

    with col5:
        furnished = (filtered_df["furnishing"] == "Furnished").sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("🏚 Furnished House", f"{furnished:.1f}%")

def charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning('No Filter Selected. Please Adjust Your Selection.')
        return

    st.subheader('Number of Listings Per State')
    region_count = filtered_df["region_parent_name"].value_counts()
    fig1 = px.bar(
        x=region_count.index,
        y=region_count.values,
    )
    fig1.update_layout(
        xaxis_title='Regions',
        yaxis_title='Frequency'
    )
    st.plotly_chart(fig1, width='stretch')

    st.subheader('Average Price Per State')
    avg_price = filtered_df.groupby("region_parent_name")["price"].mean().sort_values(ascending=False)
    fig2 = px.bar(
        x=avg_price.index,
        y=avg_price.values,
    )
    fig2.update_layout(
        xaxis_title='Regions',
        yaxis_title='Average Price'
    )
    st.plotly_chart(fig2, width='stretch')

    st.subheader('Distribution of Property Prices by Average')
    property_prices = filtered_df.groupby("house_type")['price'].mean()
    fig3 = px.histogram(
        x=property_prices.index,
        y=property_prices.values,
    )
    fig3.update_layout(
        xaxis_title='House_Type',
        yaxis_title='Prices'
    )
    fig3.update_traces(
    marker_line_color="white",
    marker_line_width=2
    )
    st.plotly_chart(fig3, width='stretch')

    st.subheader('Distribution of House Types')
    property_count = filtered_df["house_type"].value_counts()
    fig = px.histogram(
        x=property_count.index,
        y=property_count.values,
    )
    fig.update_layout(
        xaxis_title='House_Type',
        yaxis_title='Frequency',
        height=600
    )
    fig.update_traces(
    marker_line_color="white",
    marker_line_width=2
    )
    st.plotly_chart(fig, width='stretch')


    st.subheader('Price by Number of Bedrooms')
    fig4 = px.box(
        filtered_df,
        x="bedrooms",
        y="price",
        labels={
            "bedrooms": "Bedrooms",
            "price": "Price"
        }
    )
    fig4.update_layout(
        width=1000,
        height=600
    )
    st.plotly_chart(fig4, width='stretch')

    
    st.subheader('Property Size vs. Price')
    fig5 = px.scatter(
        filtered_df,
        x="property_size(sqm)",
        y="price",
        color="furnishing",
        labels={
            "property_size(sqm)": "Property Size",
            "price": "Price"
        }
    )
    st.plotly_chart(fig5, width='stretch')


    st.subheader('Furnishing Type Distribution') 
    furnish_count = filtered_df["furnishing"].value_counts()
    fig6 = px.pie(
        values=furnish_count.values,
        names=furnish_count.index,
    )
    st.plotly_chart(fig6, width="stretch")

    st.subheader('Correlation of Numeric Variables') 
    correlation = filtered_df[["property_size(sqm)", "price", "bedrooms", "bathrooms"]].corr()
    fig7 = px.imshow(
        correlation,
        text_auto=True,
        aspect="auto",
        labels=dict(
            color="Correlation"
        )
    )
    st.plotly_chart(fig7, width="stretch")    


def main():
    # load dataset
    df = load_dataset()

    # sidebar
    house_type, furnishing, region, size, bedrooms, bathrooms = create_sidebar_filter(df)

    # filtered_df 
    filtered_df = filter_data(df, house_type, furnishing, region, size, bedrooms, bathrooms)

    #main_layout
    st.title("🏡 Jiji House Listing Dashboard")
    st.subheader("Exploring property prices, locations, features, and market trends across Nigeria")
    st.markdown("---")

    #metrics
    display_metrics(filtered_df)

    #plotly_chart
    charts(filtered_df)

    #display table
    # table(filtered_df)

    with open("findings.md", "r", encoding="utf-8") as file:
        findings = file.read()

    st.markdown(findings)

if __name__ == "__main__":
    main()
