import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("San Francisco Airbnb Dashboard 🌁")

@st.cache_data
def load_data():
    df = pd.read_csv("listings.csv")

    keep_cols = [
        "neighbourhood_group_cleansed", "neighbourhood_cleansed",
        "room_type", "price", "latitude", "longitude",
        "estimated_revenue_l365d", "number_of_reviews"
    ]
    df = df[keep_cols]

    df["price"] = pd.to_numeric(
        df["price"].astype(str).replace(r"[\$,]", "", regex=True),
        errors="coerce"
    )

    df["estimated_revenue_l365d"] = pd.to_numeric(df["estimated_revenue_l365d"], errors="coerce")
    df["number_of_reviews"]      = pd.to_numeric(df["number_of_reviews"], errors="coerce")

    df = df.dropna(subset=["price", "latitude", "longitude",
                           "estimated_revenue_l365d", "number_of_reviews"])

    df = df[(df["price"] < 1000) & (df["estimated_revenue_l365d"] < 500_000)]

    return df

df = load_data()

st.sidebar.header("🔍 Filter Listings")

room_type = st.sidebar.selectbox("Room Type", df["room_type"].unique())
price_limit = st.sidebar.slider(
    "Max Price ($)", 0, int(df["price"].max()), 500
)

filtered_df = df[(df["room_type"] == room_type) & (df["price"] <= price_limit)]


st.subheader("📈 Estimated Revenue vs. Number of Reviews")

scatter = (
    alt.Chart(filtered_df)
    .mark_circle(size=60)
    .encode(
        x=alt.X("number_of_reviews:Q", title="Number of Reviews"),
        y=alt.Y("estimated_revenue_l365d:Q", title="Estimated Revenue (≤ $500 K)"),
        color=alt.Color("neighbourhood_group_cleansed:N", title="Region"),
        tooltip=[
            "neighbourhood_cleansed", "price", "estimated_revenue_l365d",
            "number_of_reviews"
        ],
    )
    .properties(width=700, height=400)
)

st.altair_chart(scatter, use_container_width=True)


st.subheader("💲 Price Distribution")

hist = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x=alt.X("price:Q", bin=alt.Bin(maxbins=40), title="Price ($)"),
        y=alt.Y("count():Q", title="Listing Count"),
        tooltip=["count()"],
    )
    .properties(width=400, height=300)
)

st.altair_chart(hist, use_container_width=True)


st.subheader("🏘️ Median Price by Neighborhood")

sel = alt.selection_multi(fields=["neighbourhood_cleansed"], bind="legend")

bar = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x=alt.X("median(price):Q", title="Median Price ($)"),
        y=alt.Y("neighbourhood_cleansed:N", sort="-x", title="Neighborhood"),
        color="neighbourhood_cleansed:N",
        opacity=alt.condition(sel, alt.value(1), alt.value(0.3)),
        tooltip=["neighbourhood_cleansed", "median(price):Q"],
    )
    .add_params(sel)
    .properties(width=600, height=500)
)

st.altair_chart(bar, use_container_width=True)
