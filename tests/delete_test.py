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
        print("Test student was not found")
    else:
        cursor.callproc("sp_deleteStudents", (estudiante[0],))
        connection.commit()
        print("Test student deleted")

except mysql.connector.Error as error:
    if connection is not None:
        connection.rollback()
    print("Error:", error)

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()   