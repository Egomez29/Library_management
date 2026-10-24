import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="db_library"
    )


if __name__ == "__main__":
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection.is_connected():
            print("Connection successful")

            cursor = connection.cursor()
            cursor.callproc("sp_listStudents")

            for result in cursor.stored_results():
                for student in result.fetchall():
                    print(student)

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
            print("Connection closed")