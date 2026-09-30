import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MovieLens Dashboard", layout="wide")

# --- DATA LOADING & PREPROCESSING ---
@st.cache_data
def load_data():
    df = pd.read_csv("movie_ratings.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: `movie_ratings.csv` not found in the project root directory.")
    st.stop()

st.title("🎬 MovieLens Analytics Dashboard")
st.markdown("Exploring ratings, release trends, and genre dynamics.")

# --- INTERACTIVE CONTROLS (Task 4 Requirement) ---
st.sidebar.header("Dashboard Controls")

# Widget 1: Rating Threshold Slider for Question 4
rating_floor = st.sidebar.slider(
    "Minimum Ratings Floor (Top Movies)", 
    min_value=10, 
    max_value=300, 
    value=50, 
    step=10,
    help="Adjust the minimum review threshold to see how top-rated movies change."
)

# Widget 2: Genre Multi-Select Filter
all_genres = sorted(list(set(g for sublist in df['genres'].dropna().str.split('|') for g in sublist)))
selected_genres = st.sidebar.multiselect(
    "Filter by Genres", 
    options=all_genres, 
    default=[],
    help="Select genres to narrow down dataset views."
)

# Apply global genre filter if selected
filtered_df = df.copy()
if selected_genres:
    # Keep movies that contain at least one of the selected genres
    mask = filtered_df['genres'].apply(lambda x: any(g in str(x).split('|') for g in selected_genres))
    filtered_df = filtered_df[mask]

# --- TASK 1: THE 4 REQUIRED VISUALIZATIONS ---

col1, col2 = st.columns(2)

# Question 1: Genre Breakdown
with col1:
    st.subheader("1. Genre Breakdown")
    st.markdown("*Movies can have multiple genres; each genre is counted independently after splitting the pipe-separated string.*")
    
    genre_df = df.assign(genre=df['genres'].str.split('|')).explode('genre')
    genre_counts = genre_df['genre'].value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Count']
    
    fig_q1 = px.bar(
        genre_counts.sort_values('Count', ascending=True), 
        x='Count', 
        y='Genre', 
        orientation='h',
        title="Distribution of Movie Ratings by Genre"
    )
    st.plotly_chart(fig_q1, use_container_width=True)

# Question 2: Genre Satisfaction
with col2:
    st.subheader("2. Genre Satisfaction")
    st.markdown("*Average rating calculated per genre.*")
    
    genre_ratings = genre_df.groupby('genre')['rating'].mean().reset_index()
    genre_ratings.columns = ['Genre', 'Average Rating']
    genre_ratings = genre_ratings.sort_values('Average Rating', ascending=False)
    
    fig_q2 = px.bar(
        genre_ratings, 
        x='Average Rating', 
        y='Genre', 
        orientation='h',
        title="Average Rating by Genre",
        range_x=[0, 5]
    )
    st.plotly_chart(fig_q2, use_container_width=True)

col3, col4 = st.columns(2)

# Question 3: Ratings Over Time
with col3:
    st.subheader("3. Ratings Over Time")
    st.markdown("*Mean rating tracked across movie release years.*")
    
    time_ratings = filtered_df.groupby('year')['rating'].mean().reset_index()
    
    fig_q3 = px.line(
        time_ratings, 
        x='year', 
        y='rating', 
        title="Mean Rating by Movie Release Year",
        markers=True
    )
    fig_q3.update_xaxes(title="Release Year")
    fig_q3.update_yaxes(title="Mean Rating", range=[0, 5])
    st.plotly_chart(fig_q3, use_container_width=True)

# Question 4: Best Movies, With a Floor
with col4:
    st.subheader("4. Top 5 Best-Rated Movies")
    st.markdown(f"*Filtered for movies with $\ge {rating_floor}$ ratings.*")
    
    movie_stats = filtered_df.groupby('title').agg(
        mean_rating=('rating', 'mean'),
        rating_count=('rating', 'count')
    ).reset_index()
    
    top_movies = movie_stats[movie_stats['rating_count'] >= rating_floor] \
        .sort_values(by='mean_rating', ascending=False) \
        .head(5)
    
    if not top_movies.empty:
        fig_q4 = px.bar(
            top_movies.sort_values('mean_rating', ascending=True),
            x='mean_rating',
            y='title',
            orientation='h',
            title=f"Top 5 Movies (Floor: {rating_floor} ratings)",
            text='rating_count'
        )
        fig_q4.update_xaxis(range=[0, 5])
        fig_q4.update_traces(texttemplate='Count: %{text}', textposition='inside')
        st.plotly_chart(fig_q4, use_container_width=True)
    else:
        st.warning("No movies match this rating threshold with the current filters.")