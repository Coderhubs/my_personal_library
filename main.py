
import streamlit as st
import os
from PIL import Image
import library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64

# Ensure necessary directories exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")


# Streamlit Page Config
st.set_page_config(page_title="Library Manager", layout="wide")
header_image = "library_image.jpg"  # Replace with your actual image file

if os.path.exists(header_image):
    st.image(header_image, use_container_width=True)

# Function to convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Apply Custom Styles with a Background Banner
base64_image = get_base64_image("library_image.jpg")  # Replace with your image path
st.markdown(
    f"""
    <style>
        /* Main App Background Image */
         
        .stApp {{
           background : #ffffff; /* Updated vibrant color */
              background-size: cover;
            
        }}

        /* Sidebar Gradient Background */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(to bottom, black, gray);
            color: white;
        }}
        
        /* Library Manager Header Background */
        .stTitle {{
            background: linear-gradient(to right, #ffffff, #bfc2c6 ); /* Updated vibrant color */
            padding: 15px;
            border-radius: 8px;
            color: black;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
            
        h1 {{
            color: #000000; /* Updated vibrant color */ 
        }}

        /* Book Card - Simpler Background & Readable Text */
        .book-card {{
            background: #ffffff; /* White background */
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            text-align: center;
            font-size: 14px;
            border: 2px solid  #7d7e81;
            font-weight: 500;
            color: #000000;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: 'sans-serif';
            line-height: 1.5;
        }}

        /* Hover Effect */
        .book-card:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }}

        /* Adjust Sidebar Text Color */
        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Search Container Styling */
       
       
        /* Search Bar Custom Styling */
        input[type="text"] {{
            width: 100%;
            padding: 10px;
            border-radius: 10px;
            border: 2px solid  #7d7e81;
            background-color: #ffffff;
            color: #000000;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            font-size: 18px;
            flex: 1;
            outline: none;
            padding-left: 10px;
        }}

        
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.title("Library Manager")
page = st.sidebar.radio("Navigate", ["Home", "Add Book", "Search Books", "Statistics", "Remove Book", "Exit"])

# Home Page
if page == "Home":
    st.markdown("<h1 class='stTitle' style='color: #000000;'>📚 My Book Collection</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")
    st.markdown('<div class="search-container">  <input type="text" placeholder="Search Books..."></div>', unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")

    books = library.get_books()
    cols = st.columns(4)
    
    for i, book in enumerate(books):
        with cols[i % 4]:
            title, author, year, genre, read_status, cover_image = book[1:7]
            image_path = cover_image if cover_image and os.path.exists(cover_image) else 'default_cover.png'
            st.image(image_path, width=120)

            st.markdown(f"""<div class='book-card'><b>{title}</b><br>Author:{author}<br>Year:{year}<br>Genre:{genre}<br>✅ {'Read' if read_status else 'Unread'}</div>""", unsafe_allow_html=True)

# Add Book Page
elif page == "Add Book":
    st.markdown("<h1 class='stTitle' style='color: #000000;'> ADD BOOK DETAILS </h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")

    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.number_input("Publication Year", min_value=1000, max_value=9999, step=1)
    genre = st.text_input("Genre")
    read_status = st.checkbox("Mark as Read")
    cover_image = st.file_uploader("Upload Book Cover", type=["jpg", "png", "jpeg"])
    
    if cover_image:
        img = Image.open(cover_image)
        st.image(img, caption="Book Cover", width=150)
    
    if st.button("Add Book"):
        if title and author and genre:
            image_path = None
            if cover_image:
                image_path = os.path.join("uploads", cover_image.name)
                with open(image_path, "wb") as f:
                    f.write(cover_image.getbuffer())
            library.add_book(title, author, year, genre, int(read_status), image_path)
            st.success(f"'{title}' added successfully!")
        else:
            st.error("Please fill in all fields.")

# Search Books
elif page == "Search Books":
    st.title("🔍 Search Books")
    query = st.text_input("Enter book title, author, or genre:")
    if query:
        books = [book for book in library.get_books() if query.lower() in str(book).lower()]
        if books:
            for book in books:
                st.write(f"📖 {book[1]} by {book[2]} ({book[3]})")
        else:
            st.warning("No books found.")

# Statistics Page
elif page == "Statistics":
    st.title("📊 Reading Statistics")
    books = library.get_books()
    read_count = sum(1 for book in books if book[5] == 1)
    unread_count = len(books) - read_count
    
    genre_counts = {}
    for book in books:
        genre = book[4]
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    genre_df = pd.DataFrame({"Genre": list(genre_counts.keys()), "Count": list(genre_counts.values())})
    
    if not genre_df.empty:
        plt.figure(figsize=(10, 4))
        sns.barplot(x="Genre", y="Count", data=genre_df, palette="coolwarm")
        plt.xticks(rotation=30)
        st.pyplot(plt)
    else:
        st.warning("No books available for statistics.")

# Remove Book Page
elif page == "Remove Book":
    st.title("🗑️ Remove Book")
    books = library.get_books()
    book_options = {f"{book[1]} by {book[2]}": book[0] for book in books}
    book_to_remove = st.selectbox("Select a book to remove", list(book_options.keys()))
    
    if st.button("Remove Book"):
        library.remove_book(book_options[book_to_remove])
        st.success(f"'{book_to_remove}' removed successfully!")

# Exit Page
elif page == "Exit":
    st.title("👋 Exit Library Manager")
    if st.button("Exit App"):
        st.write("Exiting application...")
        os._exit(0)