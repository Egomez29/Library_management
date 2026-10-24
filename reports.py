import mysql.connector
from connection import get_connection
from loans import mark_overdue_loans


def fetch_report(query, refresh_overdue=False):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        if refresh_overdue:
            mark_overdue_loans(cursor)
            connection.commit()

        cursor.execute(query)
        return cursor.fetchall()

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def show_available_books():
    books = fetch_report("""
        SELECT C.id_copy, B.bk_title, B.bk_author, C.cpy_inventory_code
        FROM tbl_books B
        INNER JOIN tbl_book_copies C ON B.id_book = C.id_book
        WHERE C.cpy_status = 'Available'
        ORDER BY B.bk_title, C.id_copy
    """)

    if books is None:
        return

    print("\n--- AVAILABLE BOOKS ---")

    if not books:
        print("No available books found")

    for book in books:
        print(
            f"Copy ID: {book[0]} | Title: {book[1]} | "
            f"Author: {book[2]} | Inventory: {book[3]}"
        )


def show_open_loans():
    loans = fetch_report("""
        SELECT L.id_loan, S.stu_name, S.stu_last_name,
               B.bk_title, L.ln_date, L.ln_due_date, L.ln_status
        FROM tbl_loans L
        INNER JOIN tbl_students S ON L.id_student = S.id_student
        INNER JOIN tbl_book_copies C ON L.id_copy = C.id_copy
        INNER JOIN tbl_books B ON C.id_book = B.id_book
        WHERE L.ln_rtrn_date IS NULL
          AND L.ln_status IN ('Active', 'Overdue')
        ORDER BY L.ln_due_date
    """, refresh_overdue=True)

    if loans is None:
        return

    print("\n--- OPEN LOANS ---")

    if not loans:
        print("No open loans found")

    for loan in loans:
        print(
            f"Loan ID: {loan[0]} | Student: {loan[1]} {loan[2]} | "
            f"Book: {loan[3]} | Loan date: {loan[4]} | "
            f"Due date: {loan[5]} | Status: {loan[6]}"
        )


def show_most_borrowed_books():
    books = fetch_report("""
        SELECT B.bk_title, B.bk_author, COUNT(L.id_loan) AS total_loans
        FROM tbl_loans L
        INNER JOIN tbl_book_copies C ON L.id_copy = C.id_copy
        INNER JOIN tbl_books B ON C.id_book = B.id_book
        GROUP BY B.id_book, B.bk_title, B.bk_author
        ORDER BY total_loans DESC, B.bk_title
    """)

    if books is None:
        return

    print("\n--- MOST BORROWED BOOKS ---")

    if not books:
        print("No loans found")

    for book in books:
        print(f"Title: {book[0]} | Author: {book[1]} | Loans: {book[2]}")