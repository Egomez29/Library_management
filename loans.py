import mysql.connector
from datetime import date
from connection import get_connection


def display_loan(loan):
    return_date = loan[5] if loan[5] is not None else "Not returned"
    print(f"Loan ID: {loan[0]}")
    print(f"Student ID: {loan[1]} | Copy ID: {loan[2]}")
    print(f"Loan date: {loan[3]} | Due date: {loan[4]}")
    print(f"Return date: {return_date} | Status: {loan[6]}")
    print()


def close_resources(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def mark_overdue_loans(cursor):
    cursor.execute("""
        UPDATE tbl_loans
        SET ln_status = 'Overdue'
        WHERE ln_status = 'Active'
          AND ln_rtrn_date IS NULL
          AND ln_due_date < %s
    """, (date.today(),))


def get_stored_rows(cursor):
    rows = []
    for result in cursor.stored_results():
        rows.extend(result.fetchall())
    return rows


def list_loans():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        mark_overdue_loans(cursor)
        connection.commit()
        cursor.callproc("sp_listLoans")
        loans = get_stored_rows(cursor)

        if not loans:
            print("No loans found")
        else:
            for loan in loans:
                display_loan(loan)

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def search_loan(loan_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        mark_overdue_loans(cursor)
        connection.commit()
        cursor.callproc("sp_searchLoans", (loan_id,))
        loans = get_stored_rows(cursor)

        if not loans:
            print("Loan not found")
            return None
        display_loan(loans[0])
        return loans[0]

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return None
    finally:
        close_resources(connection, cursor)


def list_overdue_loans():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        mark_overdue_loans(cursor)
        connection.commit()
        cursor.callproc("sp_listOverdueLoans")
        loans = get_stored_rows(cursor)

        if not loans:
            print("No overdue loans found")
        else:
            for loan in loans:
                display_loan(loan)

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def list_active_students():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_student, stu_name, stu_last_name
            FROM tbl_students
            WHERE stu_status = 1
            ORDER BY id_student
        """)
        students = cursor.fetchall()

        if not students:
            print("No active students found")
        else:
            for student in students:
                print(f"{student[0]} - {student[1]} {student[2]}")

    except mysql.connector.Error as error:
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def check_student(cursor, student_id):
    cursor.execute(
        "SELECT stu_status FROM tbl_students WHERE id_student = %s",
        (student_id,)
    )
    student = cursor.fetchone()
    if student is None:
        raise ValueError("Student not found")
    if not student[0]:
        raise ValueError("Student is inactive")


def check_available_copy(cursor, copy_id):
    cursor.execute(
        "SELECT cpy_status FROM tbl_book_copies WHERE id_copy = %s FOR UPDATE",
        (copy_id,)
    )
    book_copy = cursor.fetchone()
    if book_copy is None:
        raise ValueError("Book copy not found")
    if book_copy[0] != "Available":
        raise ValueError("Book copy is not available")

    cursor.execute("""
        SELECT COUNT(*) FROM tbl_loans
        WHERE id_copy = %s
          AND ln_status IN ('Active', 'Overdue')
          AND ln_rtrn_date IS NULL
    """, (copy_id,))
    if cursor.fetchone()[0] > 0:
        raise ValueError("Book copy already has an open loan")


def release_copy_if_unused(cursor, copy_id):
    cursor.execute("""
        SELECT COUNT(*) FROM tbl_loans
        WHERE id_copy = %s
          AND ln_status IN ('Active', 'Overdue')
          AND ln_rtrn_date IS NULL
    """, (copy_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            UPDATE tbl_book_copies SET cpy_status = 'Available'
            WHERE id_copy = %s AND cpy_status = 'Loaned'
        """, (copy_id,))


def add_loan(student_id, copy_id, loan_date, due_date):
    connection = None
    cursor = None
    try:
        if due_date < loan_date:
            raise ValueError("Due date cannot be before loan date")
        connection = get_connection()
        cursor = connection.cursor()
        check_student(cursor, student_id)
        check_available_copy(cursor, copy_id)
        cursor.callproc("sp_addLoans", (student_id, copy_id, loan_date, due_date))
        mark_overdue_loans(cursor)
        connection.commit()
        print("Loan added successfully")
        return True

    except (mysql.connector.Error, ValueError) as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def update_loan(loan_id, student_id, copy_id, loan_date, due_date):
    connection = None
    cursor = None
    try:
        if due_date < loan_date:
            raise ValueError("Due date cannot be before loan date")
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_copy, ln_rtrn_date, ln_status
            FROM tbl_loans WHERE id_loan = %s FOR UPDATE
        """, (loan_id,))
        loan = cursor.fetchone()
        if loan is None:
            raise ValueError("Loan not found")
        if loan[1] is not None or loan[2] == "Returned":
            raise ValueError("Returned loans cannot be edited")

        old_copy_id = loan[0]
        check_student(cursor, student_id)
        if copy_id != old_copy_id:
            check_available_copy(cursor, copy_id)

        status = "Overdue" if due_date < date.today() else "Active"
        cursor.callproc("sp_updateLoans", (
            loan_id, student_id, copy_id, loan_date, due_date, None, status
        ))
        if copy_id != old_copy_id:
            release_copy_if_unused(cursor, old_copy_id)
            cursor.execute("""
                UPDATE tbl_book_copies SET cpy_status = 'Loaned'
                WHERE id_copy = %s
            """, (copy_id,))
        connection.commit()
        print("Loan updated successfully")
        return True

    except (mysql.connector.Error, ValueError) as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def delete_loan(loan_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_copy, ln_rtrn_date, ln_status
            FROM tbl_loans WHERE id_loan = %s FOR UPDATE
        """, (loan_id,))
        loan = cursor.fetchone()
        if loan is None:
            raise ValueError("Loan not found")

        cursor.callproc("sp_deleteLoans", (loan_id,))
        if loan[1] is None and loan[2] in ("Active", "Overdue"):
            release_copy_if_unused(cursor, loan[0])
        connection.commit()
        print("Loan deleted successfully")
        return True

    except (mysql.connector.Error, ValueError) as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def return_loan(loan_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ln_date, ln_rtrn_date, ln_status
            FROM tbl_loans WHERE id_loan = %s FOR UPDATE
        """, (loan_id,))
        loan = cursor.fetchone()

        if loan is None:
            raise ValueError("Loan not found")
        if loan[1] is not None or loan[2] == "Returned":
            raise ValueError("Loan has already been returned")
        if date.today() < loan[0]:
            raise ValueError("Return date cannot be before loan date")

        cursor.callproc("sp_returnLoan", (loan_id, date.today()))
        connection.commit()
        print("Loan returned successfully")
        return True

    except (mysql.connector.Error, ValueError) as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)
