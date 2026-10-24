import mysql.connector
from connection import get_connection


connection = None
cursor = None

try:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id_student FROM tbl_students WHERE stu_email = %s",
        ("prueba.python@ejemplo.com",)
    )
    estudiante = cursor.fetchone()

    if estudiante is None:
        print("No student found")
    else:
        id_student = estudiante[0]

        cursor.callproc("sp_updateStudents", (
            id_student,
            "Prueba",
            "Python",
            "2do Año",
            "prueba.python@ejemplo.com",
            True
        ))

        connection.commit()
        print("Student Up")

except mysql.connector.Error as error:
    if connection is not None:
        connection.rollback()
    print("Error:", error)

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()   