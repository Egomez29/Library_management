import mysql.connector
from connection import get_connection


def display_book(book):
    print(f"Book ID: {book[0]} | Title: {book[1]}")
    print(f"Author: {book[2]} | ISBN: {book[3]}")
    print(f"Publisher: {book[4]} | Category: {book[5]}")
    print()


def close_resources(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def get_stored_rows(cursor):
    rows = []
    for result in cursor.stored_results():
        rows.extend(result.fetchall())
    return rows


def register_book(title, author, isbn, publisher, category):
    values = (title.strip(), author.strip(), isbn.strip(), publisher.strip(), category.strip())
    if not all(values):
        print("All book fields are required")
        return False

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_addBooks", values)
        connection.commit()
        print("Book added successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def show_books():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_listBooks")
        books = get_stored_rows(cursor)
        if not books:
            print("No books found")
        else:
            for book in books:
                display_book(book)
    except mysql.connector.Error as error:
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def search_book(book_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_searchBooks", (book_id,))
        books = get_stored_rows(cursor)
        if not books:
            print("Book not found")
            return None
        display_book(books[0])
        return books[0]
    except mysql.connector.Error as error:
        print("Error:", error)
        return None
    finally:
        close_resources(connection, cursor)


def update_book(book_id, title, author, isbn, publisher, category):
    values = (title.strip(), author.strip(), isbn.strip(), publisher.strip(), category.strip())
    if not all(values):
        print("All book fields are required")
        return False

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_book FROM tbl_books WHERE id_book = %s", (book_id,))
        if cursor.fetchone() is None:
            print("Book not found")
            return False
        cursor.callproc("sp_updateBooks", (book_id, *values))
        connection.commit()
        print("Book updated successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def delete_book(book_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_book FROM tbl_books WHERE id_book = %s", (book_id,))
        if cursor.fetchone() is None:
            print("Book not found")
            return False
        cursor.execute("SELECT COUNT(*) FROM tbl_book_copies WHERE id_book = %s", (book_id,))
        if cursor.fetchone()[0] > 0:
            print("Remove this book's copies before deleting the book")
            return False
        cursor.callproc("sp_deleteBooks", (book_id,))
        connection.commit()
        print("Book deleted successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)
