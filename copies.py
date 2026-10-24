import mysql.connector
from connection import get_connection


VALID_STATUSES = ("Available", "Loaned", "Damaged", "Retired")


def display_copy(book_copy):
    print(
        f"Copy ID: {book_copy[0]} | Book ID: {book_copy[1]} | "
        f"Inventory: {book_copy[2]} | Status: {book_copy[3]}"
    )


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


def register_copy(book_id, inventory_code, status="Available"):
    inventory_code = inventory_code.strip()
    if not inventory_code or status not in ("Available", "Damaged", "Retired"):
        print("Enter an inventory code and a valid initial status")
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
        cursor.callproc("sp_addBookCopies", (book_id, inventory_code, status))
        connection.commit()
        print("Book copy added successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def show_copies():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_listBookCopies")
        copies = get_stored_rows(cursor)
        if not copies:
            print("No book copies found")
        else:
            for book_copy in copies:
                display_copy(book_copy)
    except mysql.connector.Error as error:
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def search_copy(copy_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_searchBookCopies", (copy_id,))
        copies = get_stored_rows(cursor)
        if not copies:
            print("Book copy not found")
            return None
        display_copy(copies[0])
        return copies[0]
    except mysql.connector.Error as error:
        print("Error:", error)
        return None
    finally:
        close_resources(connection, cursor)


def show_available():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT C.id_copy, C.cpy_inventory_code, B.bk_title
            FROM tbl_book_copies C
            INNER JOIN tbl_books B ON C.id_book = B.id_book
            WHERE C.cpy_status = 'Available'
            ORDER BY B.bk_title
        """)
        copies = cursor.fetchall()
        if not copies:
            print("No available copies found")
        else:
            for book_copy in copies:
                print(f"{book_copy[0]} - {book_copy[1]} - {book_copy[2]}")
    except mysql.connector.Error as error:
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def update_copy(copy_id, book_id, inventory_code, status):
    inventory_code = inventory_code.strip()
    if not inventory_code or status not in VALID_STATUSES:
        print("Enter an inventory code and a valid status")
        return False

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_book, cpy_status FROM tbl_book_copies
            WHERE id_copy = %s FOR UPDATE
        """, (copy_id,))
        current = cursor.fetchone()
        if current is None:
            print("Book copy not found")
            return False

        cursor.execute("SELECT COUNT(*) FROM tbl_loans WHERE id_copy = %s", (copy_id,))
        has_history = cursor.fetchone()[0] > 0
        if book_id != current[0] and has_history:
            print("The book cannot change because this copy has loan history")
            return False

        cursor.execute("""
            SELECT COUNT(*) FROM tbl_loans
            WHERE id_copy = %s AND ln_status IN ('Active', 'Overdue')
              AND ln_rtrn_date IS NULL
        """, (copy_id,))
        has_open_loan = cursor.fetchone()[0] > 0
        if status != current[1] and has_open_loan:
            print("A loaned copy cannot change status")
            return False
        if status == "Loaned" and current[1] != "Loaned":
            print("Only a loan can mark a copy as Loaned")
            return False

        cursor.callproc("sp_updateBookCopies", (copy_id, book_id, inventory_code, status))
        connection.commit()
        print("Book copy updated successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def delete_copy(copy_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_copy FROM tbl_book_copies WHERE id_copy = %s", (copy_id,))
        if cursor.fetchone() is None:
            print("Book copy not found")
            return False
        cursor.execute("SELECT COUNT(*) FROM tbl_loans WHERE id_copy = %s", (copy_id,))
        if cursor.fetchone()[0] > 0:
            print("Book copies with loan history cannot be deleted")
            return False
        cursor.callproc("sp_deleteBookCopies", (copy_id,))
        connection.commit()
        print("Book copy deleted successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)
