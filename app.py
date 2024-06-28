import streamlit as st
import requests
import pickle
from googleapiclient.discovery import build
from streamlit_option_menu import option_menu

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# YouTube API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = 'AIzaSyDbkN_1mjfjG4wst54kDUQWKu74554TKXY'

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path

def details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    data_details = {"date": data["release_date"], "revenue": data["revenue"], "runtime": data["runtime"]}
    return data_details

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    movie_details = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        movie_details.append(details(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters, movie_details

def get_trailer(movie_name):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    search_response = youtube.search().list(
        q=movie_name + ' trailer', part='id,snippet', maxResults=1
    ).execute()
    trailer_video_id = search_response['items'][0]['id']['videoId']
    trailer_url = f'https://www.youtube.com/watch?v={trailer_video_id}'
    return trailer_url

# Streamlit app configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Option menu for navigation
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Welcome", "Recommendations", "Contact"],
        icons=["house", "film", "envelope"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Welcome":
    st.markdown(
        """
        <style>
        .welcome-container {
            text-align: center;
            padding: 50px;
            background: url("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            color: white;
        }
        .welcome-title {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .welcome-text {
            font-size: 24px;
            margin-bottom: 20px;
        }
        .carousel {
            display: flex;
            overflow-x: auto;
            scroll-behavior: smooth;
        }
        .carousel img {
            width: 300px;
            height: 450px;
            margin: 10px;
            border-radius: 10px;
        }
        </style>
        <div class="welcome-container">
            <div class="welcome-title">🎬 Welcome to the Movie Recommendation System! 🎬</div>
            <div class="welcome-text">
                Discover Your Next Favorite Movie<br>
                Our recommendation system helps you find movies you'll love.<br>
                Just select a movie you like, and we'll suggest similar movies for you to enjoy.<br>
                You can also watch trailers directly from our app!
            </div>
        </div>
        """, unsafe_allow_html=True
    )

elif selected == "Recommendations":
    st.title("Movie Recommendations")
    movie_list = movies['title'].values
    selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)
    if st.button('Show Recommendation'):
        with st.spinner('Loading...'):
            recommended_movie_names, recommended_movie_posters, movie_details = recommend(selected_movie)
            cols = st.columns(5)
            for i, col in enumerate(cols):
                col.text(recommended_movie_names[i])
                col.image(recommended_movie_posters[i])
                movie_data = movie_details[i]
                col.write(f"Release date: {movie_data['date']}")
                col.write(f"Revenue: {movie_data['revenue']}")
                col.write(f"Runtime: {movie_data['runtime']}")

    movie_name = st.text_input('Enter the name of the movie:')
    if st.button('Play Trailer'):
        trailer_url = get_trailer(movie_name)
        st.video(trailer_url)

elif selected == "Contact":
    st.title("Contact Me")
    st.write("Feel free to reach out if you have any questions or feedback!")

    with st.form(key='contact_form'):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")

        submit_button = st.form_submit_button(label='Submit')
        if submit_button:
            st.success(f"Thank you {name}! We have received your message.")

    st.markdown(
        """
        <div style="text-align: center;">
            <p style="font-size: 20px;">You can also find me on:</p>
            <p><a href="https://www.linkedin.com/in/Pushp-raj-gour" target="_blank">LinkedIn</a></p>
            <p><a href="https://github.com/pushpraj-gour" target="_blank">GitHub</a></p>
            <p><a href="mailto:rajrjpushp@gmail.com">Email</a></p>
        </div>
        """, unsafe_allow_html=True
    )
