CREATE DATABASE db_library;
USE db_library;

-- DROP DATABASE db_library;

-- ------------------------------ Tables ------------------  

CREATE TABLE tbl_students(
	id_student int not null primary key auto_increment,
    stu_name varchar(105) not null,
    stu_last_name varchar(105) not null,
    stu_grade varchar(50) not null,
    stu_email varchar(150) not null unique,
    stu_status boolean not null default true
);	

CREATE TABLE tbl_books(
	id_book int not null primary key auto_increment,
    bk_title varchar(150) not null, 
    bk_author varchar(150) not null,
    bk_isbn varchar(20) not null unique, 
    bk_publisher varchar(150) not null,
    bk_category varchar(100) not null
);

CREATE TABLE  tbl_book_copies(
	id_copy int not null primary key auto_increment,
    id_book int not null,
    cpy_inventory_code varchar(30) not null unique,
    cpy_status ENUM('Available','Loaned','Damaged','Retired') not null default 'Available',
    FOREIGN KEY (id_book) REFERENCES tbl_books (id_book)
);

CREATE TABLE tbl_loans(
	id_loan int not null primary key auto_increment,
    id_student int not null,
    id_copy int not null,
    ln_date date not null,
    ln_due_date date not null,
    ln_rtrn_date date null default null,
	ln_status ENUM('Active','Returned','Overdue') not null Default 'Active',
    FOREIGN KEY (id_student) REFERENCES tbl_students (id_student),
    FOREIGN KEY (id_copy) REFERENCES tbl_book_copies (id_copy),
    
	CHECK (ln_due_date >= ln_date)
);

-- ------------------------- INSERT INTO -------------------------

INSERT INTO tbl_students
(stu_name, stu_last_name, stu_grade, stu_email, stu_status)
VALUES
('Carlos', 'Mendez', '1er Año', 'carlos.mendez@email.com', TRUE),
('Andrea', 'Lopez', '2do Año', 'andrea.lopez@email.com', TRUE),
('Jose', 'Ramirez', '3er Año', 'jose.ramirez@email.com', TRUE),
('Maria', 'Gomez', '1er Año', 'maria.gomez@email.com', TRUE),
('Daniel', 'Castillo', '4to Año', 'daniel.castillo@email.com', TRUE);


INSERT INTO tbl_books
(bk_title, bk_author, bk_isbn, bk_publisher, bk_category)
VALUES
('Don Quijote de la Mancha', 'Miguel de Cervantes', '9788420412146', 'Alfaguara', 'Literatura'),
('Cien Años de Soledad', 'Gabriel Garcia Marquez', '9780307474728', 'Vintage Espanol', 'Novela'),
('1984', 'George Orwell', '9780451524935', 'Signet Classics', 'Distopia'),
('El Principito', 'Antoine de Saint-Exupery', '9780156012195', 'Mariner Books', 'Ficcion'),
('Clean Code', 'Robert C. Martin', '9780132350884', 'Prentice Hall', 'Programacion');


INSERT INTO tbl_book_copies
(id_book, cpy_inventory_code, cpy_status)
VALUES
(1, 'INV-001', 'Available'),
(2, 'INV-002', 'Available'),
(3, 'INV-003', 'Loaned'),
(4, 'INV-004', 'Available'),
(5, 'INV-005', 'Loaned');


INSERT INTO tbl_loans
(id_student, id_copy, ln_date, ln_due_date, ln_rtrn_date, ln_status)
VALUES
(1, 3, '2026-09-15', '2026-09-22', NULL, 'Overdue'),
(2, 5, '2026-09-20', '2026-10-04', NULL, 'Active'),
(3, 1, '2026-09-01', '2026-09-10', '2026-09-08', 'Returned'),
(4, 2, '2026-09-05', '2026-09-15', '2026-09-14', 'Returned'),
(5, 4, '2026-09-10', '2026-09-20', '2026-09-18', 'Returned');

-- ---------------------------- Selects -----------------------------------------

SELECT * FROM tbl_students;

SELECT * FROM tbl_books;

SELECT * FROM tbl_book_copies;

SELECT * FROM tbl_loans;

-- ---------------------------- Stored Procedures -------------------------------


-- ----------------------------------------- Students Stored Procedure
-- Add Students

DELIMITER $$
	Create procedure sp_addStudents(in studentName varchar(105), in studentLastName varchar(105), in studentGrade varchar(50), in studentEmail varchar(150), in studentStatus boolean)
		begin
			Insert into tbl_students(stu_name, stu_last_name, stu_grade, stu_email, stu_status)
				values (studentName, studentLastName, studentGrade, studentEmail, studentStatus);
		end $$
DELIMITER ;

call sp_addStudents('Fernando', 'Gomez', '2do Año', 'fernando.gomez@email.com', true);


-- List Students

DELIMITER $$
	Create procedure sp_listStudents()
		begin
			Select S.id_student,
            S.stu_name,
            S.stu_last_name,
            S.stu_grade,
            S.stu_email,
            S.stu_status
				from tbl_students S;
        end $$
DELIMITER ;

call sp_listStudents();


-- Update Students

DELIMITER $$
	Create procedure sp_updateStudents(in idStudent int, in studentName varchar(105), in studentLastName varchar(105), in studentGrade varchar(50), in studentEmail varchar(150), in studentStatus boolean)
		begin
			Update tbl_students
				set stu_name = studentName, stu_last_name = studentLastName, stu_grade = studentGrade, stu_email = studentEmail, stu_status = studentStatus
					where id_student = idStudent;
        end $$
DELIMITER ;

call sp_updateStudents(6, 'Fernando', 'Gomez', '3er Año', 'fernando.gomez@email.com', true);


-- Search Students

DELIMITER $$
	Create procedure sp_searchStudents(in idStudent int)
		begin
			Select S.id_student,
            S.stu_name,
            S.stu_last_name,
            S.stu_grade,
            S.stu_email,
            S.stu_status
				from tbl_students S
					where id_student = idStudent;
        end $$
DELIMITER ;

call sp_searchStudents(6);


-- Delete Students

DELIMITER $$
	Create procedure sp_deleteStudents(in idStudent int)
		begin
			Delete from tbl_students
				where id_student = idStudent;
        end $$
DELIMITER ;

call sp_deleteStudents(6);



-- ----------------------------------------- Books Stored Procedure
-- Add Books

DELIMITER $$
	Create procedure sp_addBooks(in bookTitle varchar(150), in bookAuthor varchar(150), in bookIsbn varchar(20), in bookPublisher varchar(150), in bookCategory varchar(100))
		begin
			Insert into tbl_books(bk_title, bk_author, bk_isbn, bk_publisher, bk_category)
				values (bookTitle, bookAuthor, bookIsbn, bookPublisher, bookCategory);
        end $$
DELIMITER ;

call sp_addBooks('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 'Mariner Books', 'Fantasy');


-- List Books

DELIMITER $$
	Create procedure sp_listBooks()
		begin
			Select B.id_book,
            B.bk_title,
            B.bk_author,
            B.bk_isbn,
            B.bk_publisher,
            B.bk_category
				from tbl_books B;
        end $$
DELIMITER ;

call sp_listBooks();


-- Update Books

DELIMITER $$
	Create procedure sp_updateBooks(in idBook int, in bookTitle varchar(150), in bookAuthor varchar(150), in bookIsbn varchar(20), in bookPublisher varchar(150), in bookCategory varchar(100))
		begin
			Update tbl_books
				set bk_title = bookTitle, bk_author = bookAuthor, bk_isbn = bookIsbn, bk_publisher = bookPublisher, bk_category = bookCategory
					where id_book = idBook;
        end $$
DELIMITER ;

call sp_updateBooks(6, 'The Hobbit', 'J.R.R. Tolkien', '9780547928227', 'HarperCollins', 'Fantasy');


-- Search Books

DELIMITER $$
	Create procedure sp_searchBooks(in idBook int)
		begin
			Select B.id_book,
            B.bk_title,
            B.bk_author,
            B.bk_isbn,
            B.bk_publisher,
            B.bk_category
				from tbl_books B
					where id_book = idBook;
        end $$
DELIMITER ;

call sp_searchBooks(6);


-- Delete Books

DELIMITER $$
	Create procedure sp_deleteBooks(in idBook int)
		begin
			Delete from tbl_books
				where id_book = idBook;
        end $$
DELIMITER ;

call sp_deleteBooks(6);



-- ----------------------------------------- Book Copies Stored Procedure
-- Add Book Copies

DELIMITER $$
	Create procedure sp_addBookCopies(in idBook int, in inventoryCode varchar(30), in copyStatus varchar(20))
		begin
			Insert into tbl_book_copies(id_book, cpy_inventory_code, cpy_status)
				values (idBook, inventoryCode, copyStatus);
        end $$
DELIMITER ;

call sp_addBookCopies(1, 'INV-006', 'Available');


-- List Book Copies

DELIMITER $$
	Create procedure sp_listBookCopies()
		begin
			Select C.id_copy,
            C.id_book,
            C.cpy_inventory_code,
            C.cpy_status
				from tbl_book_copies C;
        end $$
DELIMITER ;

call sp_listBookCopies();


-- Update Book Copies

DELIMITER $$
	Create procedure sp_updateBookCopies(in idCopy int, in idBook int, in inventoryCode varchar(30), in copyStatus varchar(20))
		begin
			Update tbl_book_copies
				set id_book = idBook, cpy_inventory_code = inventoryCode, cpy_status = copyStatus
					where id_copy = idCopy;
        end $$
DELIMITER ;

call sp_updateBookCopies(6, 2, 'INV-006', 'Available');


-- Search Book Copies

DELIMITER $$
	Create procedure sp_searchBookCopies(in idCopy int)
		begin
			Select C.id_copy,
            C.id_book,
            C.cpy_inventory_code,
            C.cpy_status
				from tbl_book_copies C
					where id_copy = idCopy;
        end $$
DELIMITER ;

call sp_searchBookCopies(6);


-- Delete Book Copies

DELIMITER $$
	Create procedure sp_deleteBookCopies(in idCopy int)
		begin
			Delete from tbl_book_copies
				where id_copy = idCopy;
        end $$
DELIMITER ;

call sp_deleteBookCopies(6);



-- ----------------------------------------- Loans Stored Procedure
-- Add Loans

DELIMITER $$
	Create procedure sp_addLoans(in idStudent int, in idCopy int, in loanDate date, in dueDate date)
		begin
			Insert into tbl_loans(id_student, id_copy, ln_date, ln_due_date, ln_rtrn_date, ln_status)
				values (idStudent, idCopy, loanDate, dueDate, null, 'Active');

			Update tbl_book_copies
				set cpy_status = 'Loaned'
					where id_copy = idCopy;
        end $$
DELIMITER ;

call sp_addLoans(1, 1, '2026-09-30', '2026-10-07');


-- List Loans

DELIMITER $$
	Create procedure sp_listLoans()
		begin
			Select L.id_loan,
            L.id_student,
            L.id_copy,
            L.ln_date,
            L.ln_due_date,
            L.ln_rtrn_date,
            L.ln_status
				from tbl_loans L;
        end $$
DELIMITER ;

call sp_listLoans();


-- Update Loans

DELIMITER $$
	Create procedure sp_updateLoans(in idLoan int, in idStudent int, in idCopy int, in loanDate date, in dueDate date, in returnDate date, in loanStatus varchar(20))
		begin
			Update tbl_loans
				set id_student = idStudent, id_copy = idCopy, ln_date = loanDate, ln_due_date = dueDate, ln_rtrn_date = returnDate, ln_status = loanStatus
					where id_loan = idLoan;
        end $$
DELIMITER ;

call sp_updateLoans(6, 1, 1, '2026-09-30', '2026-10-10', null, 'Active');


-- Search Loans

DELIMITER $$
	Create procedure sp_searchLoans(in idLoan int)
		begin
			Select L.id_loan,
            L.id_student,
            L.id_copy,
            L.ln_date,
            L.ln_due_date,
            L.ln_rtrn_date,
            L.ln_status
				from tbl_loans L
					where id_loan = idLoan;
        end $$
DELIMITER ;

call sp_searchLoans(6);


-- Return Loan

DELIMITER $$
	Create procedure sp_returnLoan(in idLoan int, in returnDate date)
		begin
			Update tbl_loans
				set ln_rtrn_date = returnDate, ln_status = 'Returned'
					where id_loan = idLoan;

			Update tbl_book_copies
				set cpy_status = 'Available'
					where id_copy = (
						Select id_copy
							from tbl_loans
								where id_loan = idLoan
					);
        end $$
DELIMITER ;

call sp_returnLoan(6, '2026-10-05');


-- Delete Loans

DELIMITER $$
	Create procedure sp_deleteLoans(in idLoan int)
		begin
			Delete from tbl_loans
				where id_loan = idLoan;
        end $$
DELIMITER ;

call sp_deleteLoans(6);


-- List Overdue Loans

DELIMITER $$
	Create procedure sp_listOverdueLoans()
		begin
			Select L.id_loan,
            L.id_student,
            L.id_copy,
            L.ln_date,
            L.ln_due_date,
            L.ln_rtrn_date,
            L.ln_status
				from tbl_loans L
					where L.ln_status = 'Overdue';
        end $$
DELIMITER ;

call sp_listOverdueLoans();

call sp_listStudents();

call sp_listBooks();

call sp_listBookCopies();

call sp_listLoans();
