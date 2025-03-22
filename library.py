import sqlite3
import os
from PIL import Image

# Ensure the database file is created
db_path = os.path.join(os.getcwd(), "library.db")

def get_connection():
    """Creates a new SQLite connection per function call (thread-safe)."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn, conn.cursor()

# Create table if not exists
def init_db():
    conn, cursor = get_connection()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER NOT NULL,
        genre TEXT NOT NULL,
        read_status INTEGER NOT NULL,  -- 1 = Read, 0 = Not Read
        cover_image TEXT
    )
    """)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

def add_book(title, author, year, genre, read_status, cover_image=None):
    """Add a new book to the database with a valid cover image path."""
    conn, cursor = get_connection()
    cover_path = None

    if cover_image:
        # Ensure the 'covers' directory exists
        if not os.path.exists("covers"):
            os.makedirs("covers")

        # Keep the original extension
        extension = os.path.splitext(cover_image if isinstance(cover_image, str) else cover_image.name)[1].lower()
        if extension not in [".jpg", ".jpeg", ".png"]:
            extension = ".jpg"  # Default to JPG if an unknown extension

        cover_path = os.path.join("covers", f"{title.replace(' ', '_')}{extension}")

        try:
            img = Image.open(cover_image)
            img.save(cover_path)  # Save the image properly
            cover_path = os.path.abspath(cover_path)  # Store absolute path in DB
        except Exception as e:
            print("❌ Error saving image:", e)
            cover_path = None

    cursor.execute("""
        INSERT INTO books (title, author, year, genre, read_status, cover_image)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, author, year, genre, read_status, cover_path))

    conn.commit()
    conn.close()
    print(f"✅ Book '{title}' added successfully!")

def remove_book(book_id):
    """Remove a book by ID and delete its cover image if it exists."""
    conn, cursor = get_connection()
    cursor.execute("SELECT cover_image FROM books WHERE id = ?", (book_id,))
    cover_image_path = cursor.fetchone()

    if cover_image_path and cover_image_path[0] and os.path.exists(cover_image_path[0]):
        os.remove(cover_image_path[0])  # Delete the cover image file

    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    print(f"✅ Book ID {book_id} removed successfully!")

def get_books():
    """Retrieve all books."""
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books