
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------- PAGE CONFIGURATION --------------------

st.set_page_config(
    page_title="CineScope | IMDb Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #15152b, #101827);
    color: #f5f6ff;
}
[data-testid="stSidebar"] {
    background: #111426;
    border-right: 1px solid #292d48;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.hero {
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(115deg, #29204d, #182c4c, #171b32);
    border: 1px solid #41416b;
    margin-bottom: 25px;
}
.hero h1 {
    font-size: 42px;
    color: white;
}
.hero p {
    color: #c5c9e8;
    font-size: 16px;
}
.metric-card {
    background: linear-gradient(145deg, #1c2139, #171b2d);
    border: 1px solid #343956;
    padding: 21px;
    border-radius: 18px;
    min-height: 125px;
}
.metric-label {
    color: #b5bbd7;
    font-size: 14px;
}
.metric-value {
    font-size: 29px;
    font-weight: 750;
    color: white;
    margin-top: 8px;
}
.metric-note {
    color: #a99aff;
    font-size: 12px;
    margin-top: 5px;
}
.movie-highlight {
    background: linear-gradient(120deg, #382c5c, #222b49);
    border: 1px solid #55517f;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# -------------------- LOAD CSV --------------------

CSV_FILE = Path(__file__).with_name("imdb_top250.csv")

st.sidebar.markdown("# 🎬 CineScope")
st.sidebar.caption("IMDb Movie Analytics")
st.sidebar.divider()

if not CSV_FILE.exists():
    st.error("imdb_top250.csv not found. Run imdb_scraper.py first.")
    st.stop()

try:
    df = pd.read_csv(CSV_FILE)
except Exception as error:
    st.error(f"Unable to read CSV: {error}")
    st.stop()

required_columns = ["Rank", "Movie Name", "Year", "IMDb Rating"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV columns do not match the expected format.")
    st.write("Expected columns:", required_columns)
    st.write("Found columns:", df.columns.tolist())
    st.stop()

df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
df["IMDb Rating"] = pd.to_numeric(
    df["IMDb Rating"].astype(str).str.extract(r"(\d+\.?\d*)")[0],
    errors="coerce"
)
df["Year"] = pd.to_numeric(
    df["Year"].astype(str).str.extract(r"(\d{4})")[0],
    errors="coerce"
)

df = df.dropna(subset=["Movie Name", "IMDb Rating"]).copy()
df["Movie Name"] = df["Movie Name"].astype(str)

if df.empty:
    st.error("No valid movie records found in the CSV.")
    st.stop()


# -------------------- SIDEBAR FILTERS --------------------

st.sidebar.subheader("🔎 Explore Movies")

search_text = st.sidebar.text_input(
    "Search movie title",
    placeholder="e.g. The Dark Knight"
)

valid_years = df["Year"].dropna()

if not valid_years.empty:
    year_min = int(valid_years.min())
    year_max = int(valid_years.max())

    if year_min < year_max:
        year_range = st.sidebar.slider(
            "Release year",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max)
        )
    else:
        year_range = (year_min, year_max)
else:
    year_range = None

rating_min = float(df["IMDb Rating"].min())
rating_max = float(df["IMDb Rating"].max())

if rating_min < rating_max:
    min_rating = st.sidebar.slider(
        "Minimum IMDb rating",
        min_value=rating_min,
        max_value=rating_max,
        value=rating_min,
        step=0.1
    )
else:
    min_rating = rating_min

sort_choice = st.sidebar.selectbox(
    "Sort movies by",
    [
        "IMDb Rating: Highest first",
        "Rank: Best first",
        "Year: Newest first"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Built with Python • Selenium • Pandas • Streamlit • Plotly")


# -------------------- FILTER DATA --------------------

filtered_df = df.copy()

if search_text.strip():
    filtered_df = filtered_df[
        filtered_df["Movie Name"].str.contains(
            search_text.strip(), case=False, na=False
        )
    ]

if year_range is not None:
    filtered_df = filtered_df[
        filtered_df["Year"].between(
            year_range[0], year_range[1], inclusive="both"
        ) | filtered_df["Year"].isna()
    ]

filtered_df = filtered_df[
    filtered_df["IMDb Rating"] >= min_rating
]

if sort_choice == "IMDb Rating: Highest first":
    filtered_df = filtered_df.sort_values(
        "IMDb Rating", ascending=False
    )
elif sort_choice == "Rank: Best first":
    filtered_df = filtered_df.sort_values(
        "Rank", ascending=True, na_position="last"
    )
else:
    filtered_df = filtered_df.sort_values(
        "Year", ascending=False, na_position="last"
    )


# -------------------- HERO HEADER --------------------

st.markdown("""
<div class="hero">
    <h1>🎬 CineScope</h1>
    <p>Your cinematic universe — explore, compare and discover
    the world's highest-rated movies.</p>
    <span>✦ MOVIE INSIGHTS &nbsp; ✦ RATING ANALYTICS &nbsp; ✦ TOP 250</span>
</div>
""", unsafe_allow_html=True)


# -------------------- SUMMARY CARDS --------------------

total_movies = len(filtered_df)
average_rating = (
    filtered_df["IMDb Rating"].mean() if total_movies else 0
)
highest_rating = (
    filtered_df["IMDb Rating"].max() if total_movies else 0
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎞️ MOVIES FOUND</div>
        <div class="metric-value">{total_movies:,}</div>
        <div class="metric-note">Matching your filters</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⭐ AVERAGE RATING</div>
        <div class="metric-value">{average_rating:.2f}</div>
        <div class="metric-note">Out of 10</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🏆 HIGHEST RATING</div>
        <div class="metric-value">{highest_rating:.1f}</div>
        <div class="metric-note">Top score in selection</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    if not valid_years.empty:
        year_span = f"{int(valid_years.min())}–{int(valid_years.max())}"
    else:
        year_span = "N/A"

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📅 YEAR SPAN</div>
        <div class="metric-value">{year_span}</div>
        <div class="metric-note">Years in the dataset</div>
    </div>
    """, unsafe_allow_html=True)


# -------------------- TOP MOVIE SPOTLIGHT --------------------

if total_movies:
    top_movie = filtered_df.loc[
        filtered_df["IMDb Rating"].idxmax()
    ]

    top_year = (
        int(top_movie["Year"])
        if pd.notna(top_movie["Year"]) else "Unknown"
    )
    top_rank = (
        int(top_movie["Rank"])
        if pd.notna(top_movie["Rank"]) else "N/A"
    )

    st.subheader("🏆 Movie Spotlight")

    st.markdown(f"""
    <div class="movie-highlight">
        <div style="color:#c6b7ff;font-size:13px;letter-spacing:2px;">
            HIGHEST-RATED IN YOUR SELECTION
        </div>
        <div style="font-size:27px;font-weight:750;margin-top:8px;">
            {top_movie["Movie Name"]}
        </div>
        <div style="color:#d0d4f0;margin-top:7px;">
            📅 {top_year} &nbsp; • &nbsp;
            🏅 Rank {top_rank} &nbsp; • &nbsp;
            ⭐ {top_movie["IMDb Rating"]:.1f}/10
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------- RATING CHARTS --------------------

st.subheader("📊 Movie Analytics")

left, right = st.columns(2)

if total_movies:
    top10 = (
        filtered_df.nlargest(10, "IMDb Rating")
        .sort_values("IMDb Rating", ascending=True)
    )

    with left:
        st.markdown("#### ⭐ Top Rated Movies")

        fig_bar = px.bar(
            top10,
            x="IMDb Rating",
            y="Movie Name",
            orientation="h",
            text="IMDb Rating",
            color="IMDb Rating",
            color_continuous_scale=["#5b4bdb", "#a78bfa", "#67e8f9"],
            template="plotly_dark"
        )

        fig_bar.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )
        fig_bar.update_layout(
            height=430,
            margin=dict(l=5, r=30, t=20, b=15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis_title="IMDb Rating",
            yaxis_title=""
        )

        st.plotly_chart(fig_bar, width="stretch")

    with right:
        st.markdown("#### 📈 Rating Distribution")

        fig_hist = px.histogram(
            filtered_df,
            x="IMDb Rating",
            nbins=12,
            color_discrete_sequence=["#8b7bff"],
            template="plotly_dark"
        )

        fig_hist.update_layout(
            height=430,
            margin=dict(l=5, r=10, t=20, b=15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="IMDb Rating",
            yaxis_title="Number of Movies"
        )

        st.plotly_chart(fig_hist, width="stretch")


# -------------------- RELEASE YEAR CHART --------------------

if total_movies and filtered_df["Year"].notna().any():
    st.subheader("🗓️ Movies Across the Years")

    year_counts = (
        filtered_df.dropna(subset=["Year"])
        .groupby("Year")
        .size()
        .reset_index(name="Movie Count")
    )

    fig_year = px.area(
        year_counts,
        x="Year",
        y="Movie Count",
        markers=True,
        color_discrete_sequence=["#8b7bff"],
        template="plotly_dark"
    )

    fig_year.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=5, r=10, t=15, b=10)
    )

    st.plotly_chart(fig_year, width="stretch")


# -------------------- MOVIE LEADERBOARD --------------------

st.subheader("🎥 Movie Leaderboard")
st.caption("Search and filter movies using the sidebar.")

if total_movies:
    display_df = filtered_df[required_columns].copy()

    display_df["Year"] = display_df["Year"].apply(
        lambda year: int(year) if pd.notna(year) else None
    )
    display_df["IMDb Rating"] = display_df["IMDb Rating"].round(1)

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        height=400,
        column_config={
            "Rank": st.column_config.NumberColumn(
                "Rank", format="%d"
            ),
            "Movie Name": st.column_config.TextColumn("Movie Title"),
            "Year": st.column_config.NumberColumn("Release Year"),
            "IMDb Rating": st.column_config.ProgressColumn(
                "IMDb Rating",
                min_value=0,
                max_value=10,
                format="%.1f ⭐"
            )
        }
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ Download Filtered Movies CSV",
        data=csv_data,
        file_name="cinescope_filtered_movies.csv",
        mime="text/csv"
    )

else:
    st.info(
        "No movies match your filters. Try changing the search or rating."
    )


# -------------------- FOOTER --------------------

st.divider()
st.caption(
    "CineScope | IMDb Movie Rating Scraper & Analytics Dashboard"
)
st.caption(
    "Data note: If the scraper used its public dataset fallback, "
    "the ratings are historical dataset values, not live IMDb data."
)
