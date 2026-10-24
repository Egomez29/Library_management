import mysql.connector
from connection import get_connection


def display_student(student):
    status = "Active" if student[5] else "Inactive"
    print(f"Student ID: {student[0]} | Name: {student[1]} {student[2]}")
    print(f"Grade: {student[3]} | Email: {student[4]} | Status: {status}")
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


def register_student(name, last_name, grade, email, status):
    values = (name.strip(), last_name.strip(), grade.strip(), email.strip(), status)
    if not all(values[:4]):
        print("All student fields are required")
        return False

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_addStudents", values)
        connection.commit()
        print("Student added successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def show_students():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_listStudents")
        students = get_stored_rows(cursor)

        if not students:
            print("No students found")
        else:
            for student in students:
                display_student(student)
    except mysql.connector.Error as error:
        print("Error:", error)
    finally:
        close_resources(connection, cursor)


def search_student(student_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.callproc("sp_searchStudents", (student_id,))
        students = get_stored_rows(cursor)

        if not students:
            print("Student not found")
            return None

        display_student(students[0])
        return students[0]
    except mysql.connector.Error as error:
        print("Error:", error)
        return None
    finally:
        close_resources(connection, cursor)


def update_student(student_id, name, last_name, grade, email, status):
    values = (name.strip(), last_name.strip(), grade.strip(), email.strip(), status)
    if not all(values[:4]):
        print("All student fields are required")
        return False

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id_student FROM tbl_students WHERE id_student = %s",
            (student_id,)
        )

        if cursor.fetchone() is None:
            print("Student not found")
            return False

        cursor.callproc("sp_updateStudents", (student_id, *values))
        connection.commit()
        print("Student updated successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)


def delete_student(student_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id_student FROM tbl_students WHERE id_student = %s",
            (student_id,)
        )

        if cursor.fetchone() is None:
            print("Student not found")
            return False

        cursor.execute(
            "SELECT COUNT(*) FROM tbl_loans WHERE id_student = %s",
            (student_id,)
        )

        if cursor.fetchone()[0] > 0:
            print("Students with loan history cannot be deleted")
            return False

        cursor.callproc("sp_deleteStudents", (student_id,))
        connection.commit()
        print("Student deleted successfully")
        return True
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        print("Error:", error)
        return False
    finally:
        close_resources(connection, cursor)