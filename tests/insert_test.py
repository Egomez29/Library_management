import mysql.connector
from connection import get_connection

connection = None
cursor = None

try:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.callproc("sp_addStudents", (
        "Prueba",
        "Python",
        "1er Año",
        "prueba.python@ejemplo.com",
        True
    ))

    connection.commit()
    print("Test student created")

except mysql.connector.Error as error:
    if connection is not None:
        connection.rollback()
    print("Error:", error)

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()    