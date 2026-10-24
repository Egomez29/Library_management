from datetime import date
from books import register_book, show_books, search_book, update_book, delete_book
from copies import register_copy, show_copies, search_copy, show_available, update_copy, delete_copy
from students import register_student, show_students, search_student, update_student, delete_student
from loans import (add_loan, delete_loan, list_active_students,list_loans, list_overdue_loans, search_loan, update_loan, return_loan)
from reports import show_available_books, show_open_loans, show_most_borrowed_books

def read_positive_int(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        if value.isdigit() and int(value) > 0:
            return int(value)
        print("Enter a valid positive number")


def read_date(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        try:
            return date.fromisoformat(value)
        except ValueError:
            print("Enter a valid date in YYYY-MM-DD format")


def read_text(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        if default is not None:
            return default
        print("This field is required")


def read_copy_status(prompt, default=None):
    while True:
        value = input(prompt).strip().title()
        if value == "" and default is not None:
            return default
        valid_statuses = ("Available", "Damaged", "Retired")
        if default == "Loaned":
            valid_statuses += ("Loaned",)
        if value in valid_statuses:
            return value
        print("Enter a valid copy status")


def read_student_status(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return bool(default)
        if value in ("0", "1"):
            return value == "1"
        print("Enter 1 for Active or 0 for Inactive")


def add_loan_screen():
    print("\n--- ACTIVE STUDENTS ---")
    list_active_students()

    student_id = read_positive_int("Student ID: ")
    copy_id = read_positive_int("Copy ID: ")
    loan_date = read_date("Loan date (YYYY-MM-DD, Enter for today): ", date.today())
    due_date = read_date("Due date (YYYY-MM-DD): ")
    add_loan(student_id, copy_id, loan_date, due_date)


def update_loan_screen():
    loan_id = read_positive_int("Loan ID to update: ")
    loan = search_loan(loan_id)
    if loan is None:
        return
    if loan[5] is not None or loan[6] == "Returned":
        print("Returned loans cannot be edited")
        return

    print("Press Enter to keep the current value")
    student_id = read_positive_int(f"Student ID [{loan[1]}]: ", loan[1])
    copy_id = read_positive_int(f"Copy ID [{loan[2]}]: ", loan[2])
    loan_date = read_date(f"Loan date [{loan[3]}]: ", loan[3])
    due_date = read_date(f"Due date [{loan[4]}]: ", loan[4])
    update_loan(loan_id, student_id, copy_id, loan_date, due_date)


def delete_loan_screen():
    loan_id = read_positive_int("Loan ID to delete: ")
    loan = search_loan(loan_id)
    if loan is None:
        return

    answer = input("Permanently delete this loan? (y/n): ").strip().lower()
    if answer == "y":
        delete_loan(loan_id)
    else:
        print("Deletion cancelled")


def return_loan_screen():
    loan_id = read_positive_int("Loan ID to return: ")
    loan = search_loan(loan_id)
    if loan is None:
        return
    if loan[5] is not None or loan[6] == "Returned":
        print("Loan has already been returned")
        return

    answer = input("Return this loan? (y/n): ").strip().lower()
    if answer == "y":
        return_loan(loan_id)
    else:
        print("Return cancelled")


def loans_menu():
    while True:
        print("\n--- LOANS ---")
        print("1. List loans")
        print("2. Search loan")
        print("3. Add loan")
        print("4. Update loan")
        print("5. Delete loan")
        print("6. List overdue loans")
        print("7. Return loan")
        print("0. Back")
        option = input("Choose an option: ").strip()

        if option == "1":
            list_loans()
        elif option == "2":
            loan_id = read_positive_int("Enter loan ID: ")
            search_loan(loan_id)
        elif option == "3":
            add_loan_screen()
        elif option == "4":
            update_loan_screen()
        elif option == "5":
            delete_loan_screen()
        elif option == "6":
            list_overdue_loans()
        elif option == "7":
            return_loan_screen()
        elif option == "0":
            return
        else:
            print("Invalid option")
            continue

        input("\nPress Enter to continue...")


def copies_menu():
    while True:
        print("\n--- BOOK COPIES ---")
        print("1. List all copies")
        print("2. List available copies")
        print("3. Add copy")
        print("4. Search copy")
        print("5. Update copy")
        print("6. Delete copy")
        print("0. Back")
        option = input("Choose an option: ").strip()

        if option == "1":
            show_copies()
        elif option == "2":
            show_available()
        elif option == "3":
            book_id = read_positive_int("Book ID: ")
            inventory_code = read_text("Inventory code: ")
            status = read_copy_status("Status (Enter for Available): ", "Available")
            register_copy(book_id, inventory_code, status)
        elif option == "4":
            copy_id = read_positive_int("Copy ID: ")
            search_copy(copy_id)
        elif option == "5":
            copy_id = read_positive_int("Copy ID to update: ")
            book_copy = search_copy(copy_id)
            if book_copy is not None:
                print("Press Enter to keep the current value")
                book_id = read_positive_int(f"Book ID [{book_copy[1]}]: ", book_copy[1])
                inventory_code = read_text(f"Inventory code [{book_copy[2]}]: ", book_copy[2])
                status = read_copy_status(f"Status [{book_copy[3]}]: ", book_copy[3])
                update_copy(copy_id, book_id, inventory_code, status)
        elif option == "6":
            copy_id = read_positive_int("Copy ID to delete: ")
            if search_copy(copy_id) is not None:
                answer = input("Permanently delete this copy? (y/n): ").strip().lower()
                if answer == "y":
                    delete_copy(copy_id)
                else:
                    print("Deletion cancelled")
        elif option == "0":
            return
        else:
            print("Invalid option")
            continue

        input("\nPress Enter to continue...")


def books_menu():
    while True:
        print("\n--- BOOKS ---")
        print("1. List books")
        print("2. Search book")
        print("3. Add book")
        print("4. Update book")
        print("5. Delete book")
        print("0. Back")
        option = input("Choose an option: ").strip()

        if option == "1":
            show_books()
        elif option == "2":
            book_id = read_positive_int("Book ID: ")
            search_book(book_id)
        elif option == "3":
            title = read_text("Title: ")
            author = read_text("Author: ")
            isbn = read_text("ISBN: ")
            publisher = read_text("Publisher: ")
            category = read_text("Category: ")
            register_book(title, author, isbn, publisher, category)
        elif option == "4":
            book_id = read_positive_int("Book ID to update: ")
            book = search_book(book_id)
            if book is not None:
                print("Press Enter to keep the current value")
                title = read_text(f"Title [{book[1]}]: ", book[1])
                author = read_text(f"Author [{book[2]}]: ", book[2])
                isbn = read_text(f"ISBN [{book[3]}]: ", book[3])
                publisher = read_text(f"Publisher [{book[4]}]: ", book[4])
                category = read_text(f"Category [{book[5]}]: ", book[5])
                update_book(book_id, title, author, isbn, publisher, category)
        elif option == "5":
            book_id = read_positive_int("Book ID to delete: ")
            if search_book(book_id) is not None:
                answer = input("Permanently delete this book? (y/n): ").strip().lower()
                if answer == "y":
                    delete_book(book_id)
                else:
                    print("Deletion cancelled")
        elif option == "0":
            return
        else:
            print("Invalid option")
            continue

        input("\nPress Enter to continue...")


def students_menu():
    while True:
        print("\n--- STUDENTS ---")
        print("1. List students")
        print("2. Search student")
        print("3. Add student")
        print("4. Update student")
        print("5. Delete student")
        print("0. Back")
        option = input("Choose an option: ").strip()

        if option == "1":
            show_students()
        elif option == "2":
            student_id = read_positive_int("Student ID: ")
            search_student(student_id)
        elif option == "3":
            name = read_text("Name: ")
            last_name = read_text("Last name: ")
            grade = read_text("Grade: ")
            email = read_text("Email: ")
            status = read_student_status("Status (1=Active, 0=Inactive): ")
            register_student(name, last_name, grade, email, status)
        elif option == "4":
            student_id = read_positive_int("Student ID to update: ")
            student = search_student(student_id)
            if student is not None:
                print("Press Enter to keep the current value")
                name = read_text(f"Name [{student[1]}]: ", student[1])
                last_name = read_text(f"Last name [{student[2]}]: ", student[2])
                grade = read_text(f"Grade [{student[3]}]: ", student[3])
                email = read_text(f"Email [{student[4]}]: ", student[4])
                current_status = "Active" if student[5] else "Inactive"
                status = read_student_status(
                    f"Status [{current_status}] (1=Active, 0=Inactive): ",
                    student[5]
                )
                update_student(student_id, name, last_name, grade, email, status)
        elif option == "5":
            student_id = read_positive_int("Student ID to delete: ")
            if search_student(student_id) is not None:
                answer = input("Permanently delete this student? (y/n): ").strip().lower()
                if answer == "y":
                    delete_student(student_id)
                else:
                    print("Deletion cancelled")
        elif option == "0":
            return
        else:
            print("Invalid option")
            continue

        input("\nPress Enter to continue...")

def reports_menu():
    while True:
        print("\n--- REPORTS ---")
        print("1. Available books")
        print("2. Open loans")
        print("3. Most borrowed books")
        print("0. Back")

        option = input("Choose an option: ").strip()

        if option == "1":
            show_available_books()
        elif option == "2":
            show_open_loans()
        elif option == "3":
            show_most_borrowed_books()
        elif option == "0":
            return
        else:
            print("Invalid option")
            continue

        input("\nPress Enter to continue...")

def main():
    while True:
        print("\n=== LIBRARY MANAGEMENT SYSTEM ===")
        print("1. Loans")
        print("2. Book copies")
        print("3. Books")
        print("4. Students")
        print("5. Reports")
        print("0. Exit")
        option = input("Choose an option: ").strip()

        if option == "1":
            loans_menu()
        elif option == "2":
            copies_menu()
        elif option == "3":
            books_menu()
        elif option == "4":
            students_menu()
        elif option == "5":
            reports_menu()
        elif option == "0":
            print("Goodbye")
            return
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
