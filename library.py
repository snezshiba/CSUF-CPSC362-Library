import sqlite3
from sqlite3 import Error

DB_NAME = "library.db"

# ----------------------------------------------------------
# DATABASE CONNECTION
# ----------------------------------------------------------

def get_connection():
	#ESTABLISH CONNECTION TO SQLITE DB AND ENABLE FOREIGN KEY CONSTRAINTS
	conn = sqlite3.connect(DB_NAME)
	conn.execute("PRAGMA foreign_keys = ON;")
	return conn
	
# ----------------------------------------------------------
# INPUT HELPERS
# ----------------------------------------------------------

def read_line(prompt):
	# READ INPUT FROM USER (CAN BE EMPTY LINES)
	return input(prompt).strip()
	
def read_int(prompt):
	# READS INTEGER INPUT
	#WILL KEEP PROMPTING UNTIL VALID NUMBER ENTERED
	while True:
		value = input(prompt).strip()
		try:
			return int(value)
		except ValueError:
			print("Enter a valid number.")
			
def read_nonempty(prompt):
	# ENSURES USER INPUT IS NOT EMPTY
	while True:
		value = input(prompt).strip()
		if value:
			return value
		print("Input cannot be empty.")
		
# ----------------------------------------------------------
# DB EXECUTION HELPERS
# ----------------------------------------------------------	

def execute_non_query(conn, sql, params=()):
	# EXECUTES INSERT, DELETE, AND UPDATE QUERIES
	# UTILIZES PARAMETERIZED SQL TO PREVEL SQL INJECTION
	try:
		cur = conn.cursor()
		cur.execute(sql, params)
		conn.commit()
		print("SQL Executed Successfully.\n")
		return True
	except Error as e:
		print(f"SQL ERROR: {e}\n")
		return False
	
def execute_query(conn, sql, params=()):
	# EXECUTES SELECT QUERIES AND RETURNS RESULTS
	try: 
		curr = conn.cursor()
		curr.execute(sql, params)
		rows = curr.fetchall()
		columns = [desc[0] for desc in curr.description] if curr.description else []
		return columns, rows
	except Error as e:
		print(f"SQL ERROR: {e}\n")
		return [], []
		
def print_rows(columns, rows):
	# PRINTS QUERY RESULTS IN FORMATTED WAY
	if not rows:
		print("No records were able to be found.\n")
		return
	for row in rows:
		print("-----------------------")
		for i, col in enumerate(columns):
			value = row[i] if row[i] is not None else "NULL"
			print(f"{col}: {value}")
		print()
		
# ----------------------------------------------------------
# Menu Display
# ----------------------------------------------------------
	
def show_menu():
	# DISPLAYS MAIN SYSTEM MENU
	print(" ========================= ")
	print(" Library Management System ")
	print(" ========================= ")
	print("1. Add User")
	print("2. Register Member")
	print("3. Add Category")
	print("4. Add Author")
	print("5. Add Book")
	print("6. Link Book to Author")
	print("7. Borrow Book")
	print("8. Return Book")
	print("9. Place Reservation")
	print("10. Cancel Reservation")
	print("11. Pay Fine")
	print("12. Report - Overdue Books")
	print("13. Report - Popular Books")
	print("14. Report Inventory List")
	print("15. Exit")
	print(" ========================= ")
	
# ----------------------------------------------------------
# Functions/Features
# ----------------------------------------------------------

def add_user(conn):
	# CREATE NEW USER
	username = read_nonempty("Username: ")
	password = read_nonempty("Password: ")
	role = read_nonempty("Role (Admin/Librarian/Member): ")
	
	sql = "INSERT INTO Users (username, password, role) VALUES (?, ?, ?);"
	execute_non_query(conn, sql, (username, password, role))
	
def register_member(conn):
	# REGISTERS MEMBER LINKED TO EXISTING USER
	user_id = read_int("User ID: ")
	fname = read_nonempty("First Name: ")
	minit = read_line("Middle Initial: ")
	lname = read_nonempty("Last Name: ")
	email = read_nonempty("Email: ")
	phone = read_line("Phone Number: ")
	address = read_line("Address: ")
	
	sql = "INSERT INTO Members (user_id, fname, minit, lname, email, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?);"
	execute_non_query(conn, sql, (user_id, fname, minit, lname, email, phone, address))
	
def add_category(conn):
	# ADDS NEW BOOK CATEGORY
	name = read_nonempty("Category Name: ")
	
	sql = "INSERT INTO Categories (name) VALUES (?);"
	execute_non_query(conn, sql, (name,))
	
def add_author(conn):
	# ADDS NEW AUTHOR
	name = read_nonempty("Author's Name: ")
	
	sql = "INSERT INTO Authors (name) VALUES (?);"
	execute_non_query(conn, sql, (name,))
	
def add_book(conn):
	# ADDS NEW BOOK 
	isbn = read_nonempty("ISBN: ")
	title = read_nonempty("Title: ")
	publisher = read_line("Publisher: ")
	year = read_int("Year: ")
	category_id = read_int ("Category ID: ")
	total = read_int("Total Copies: ")
	
	# INITIALIZE COPIES AVAILABLE
	if total < 0:
		print("Total copies CANNOT be negative.\n")
		return
	
	sql = "INSERT INTO Books (ISBN, title, publisher, year, category_id, copies_total, copies_available) VALUES (?, ?, ?, ?, ?, ?, ?);"
	execute_non_query(conn, sql, (isbn, title, publisher, year, category_id, total, total))
	
def link_book_author(conn):
	book_id = read_int("Book ID: ")
	author_id = read_int("Author ID: ")
	
	sql = "INSERT INTO Book_Author (book_id, author_id) VALUES (?, ?);"
	execute_non_query(conn, sql, (book_id, author_id))
	
def borrow_book(conn):
    # BORROWS BOOKS, CHECKS THAT BOOK AND MEMBER EXIST,
    # CHECKS AVAILABLE COPIES, INSERTS LOAN RECORD,
    # USES TRANSACTION TO ENSURE CONSISTENCY

    book_id = read_int("Book ID: ")
    member_id = read_int("Member ID: ")
    checkout_date = read_nonempty("Checkout Date (YYYY-MM-DD): ")
    due_date = read_nonempty("Due Date (YYYY-MM-DD): ")

    try:
        cur = conn.cursor()

        # CHECK IF BOOK EXISTS
        cur.execute(
            "SELECT copies_available FROM Books WHERE book_id = ?;",
            (book_id,)
        )
        book_row = cur.fetchone()

        if book_row is None:
            print("Error: Book ID does not exist.\n")
            return

        # CHECK IF MEMBER EXISTS
        cur.execute(
            "SELECT member_id FROM Members WHERE member_id = ?;",
            (member_id,)
        )
        member_row = cur.fetchone()

        if member_row is None:
            print("Error: Member ID does not exist.\n")
            return

        # CHECK IF COPIES ARE AVAILABLE
        copies_available = book_row[0]
        if copies_available <= 0:
            print("No copies are available.\n")
            return

        # BEGIN TRANSACTION
        conn.execute("BEGIN;")

        # DECREASE AVAILABLE COPIES
        cur.execute(
            "UPDATE Books SET copies_available = copies_available - 1 "
            "WHERE book_id = ?;",
            (book_id,)
        )

        # INSERT LOAN RECORD
        cur.execute(
            "INSERT INTO Loans (book_id, member_id, checkout_date, due_date, status) "
            "VALUES (?, ?, ?, ?, 'checked_out');",
            (book_id, member_id, checkout_date, due_date)
        )

        conn.commit()
        print("Book loaned successfully.\n")

    except Error as e:
        try:
            conn.rollback()
        except Error:
            pass
        print(f"SQL ERROR: {e}\n")
		
def return_book(conn):
	# RETURN BOOK, UPDATE LOAN STATUS, INCREASE AVAILABLE COPIES, USE TRANSACTION TO ENSURE CONSISTENCY
	
	loan_id = read_int("Loan ID: ")
	return_date = read_nonempty("Return Date (YYYY-MM-DD): ")
	
	try:
		cur = conn.cursor()
		conn.execute("BEGIN;")
		
		# GET BOOK ID FROM THE LOAN
		cur.execute(
			"SELECT book_id FROM Loans WHERE loan_id = ? AND status = 'checked_out';",
			(loan_id,)
		)
		row = cur.fetchone()
		
		if not row:
			conn.rollback()
			print("Invalid or already returned.\n")
			return
		
		book_id = row[0]
		
		# UPDATE LOAN
		cur.execute(
			"UPDATE Loans SET return_date = ?, status = 'returned' WHERE loan_id = ?;",
            (return_date, loan_id)
		)
		
		# RESTORE INVENTORY
		cur.execute(
			"UPDATE Books SET copies_available = copies_available + 1 WHERE book_id = ?;", (book_id,)
		)
		
		conn.commit()
		print("Book returned successfully.\n")
		
	except Error as e:
		conn.rollback()
		print(f"SQL ERROR: {e}\n")
		
def make_res(conn):
	# PLACE RESERVATIONS FOR BOOKS
	book_id = read_int("Book ID: ")
	member_id = read_int("Member ID: ")
	
	sql = "INSERT INTO Reservations (book_id, member_id, status) VALUES (?, ?, 'active');"
	execute_non_query(conn, sql, (book_id, member_id))

def cancel_res(conn):
	# CANCEL EXISTING RESERVATION
	reservation_id = read_int("Reservation ID: ")
	
	sql = "UPDATE Reservations SET status = 'cancelled' WHERE reservation_id = ?;"
	execute_non_quert(conn, sql, (reservation_id,))

def pay_fine(conn):
	# MARKS A FINE AS PAID
	fine_id = read_int("Fine ID: ")
	
	sql = "UPDATE Fines SET paid = 1 WHERE fine_id =?;"
	execute_non_query(conn, sql, (fine_id,))
		
# ----------------------------------------------------------
# Reporting
# ----------------------------------------------------------

def report_overdue(conn):
	# DISPLAYS OVERDUE BOOKS
	today = read_nonempty("Today's Date (YYYY-MM-DD): ")
	
	sql = "SELECT Books.title, Members.fname, Members.lname, Loans.due_date FROM Loans JOIN Books ON Loans.book_id = Books.book_id JOIN Members ON Loans.member_id = Members.member_id WHERE Loans.status = 'checked_out' AND Loans.return_date IS NULL AND Loans.due_date < ?;"
	columns, rows = execute_query(conn, sql, (today,))
	print_rows(columns, rows)
	
def report_popular(conn):
	# DISPLAYS POPULAR BOOKS BASED ON LOAN COUNT
	sql = "SELECT Books.title, COUNT(Loans.loan_id) AS total_loans FROM Books LEFT JOIN Loans ON Books.book_id = Loans.book_id GROUP BY Books.book_id ORDER BY total_loans DESC;"
	columns, rows = execute_query(conn, sql)
	print_rows(columns, rows)
	
def report_inventory(conn):
	# DISPLAYS INVENTORY OF ALL BOOKS
	print("\n ===== INVENTORY =====")
	
	sql = "SELECT book_id, title, ISBN, copies_total, copies_available FROM Books;"
	columns, rows = execute_query(conn, sql)
	print_rows(columns, rows)
	
# ----------------------------------------------------------
# Main Loop
# ----------------------------------------------------------

# REDO WHEN ADDING LOGIN SYSTEM
def main():
	# MAIN PROGRAM LOOP
	try:
		conn = get_connection()
		print("Database Connected.\n")
	except Error as e:
		print(f"Connection failed: {e}")
		return
		
	while True:
		show_menu()
		
		try:
			choice = int(input("Enter Choice: "))
		except ValueError:
			print("Invalid Input.\n")
			continue
		
		if choice == 1:
			add_user(conn)
		elif choice == 2:
			register_member(conn)
		elif choice == 3:
			add_category(conn)
		elif choice == 4:
			add_author(conn)
		elif choice == 5:
			add_book(conn)
		elif choice == 6:
			link_book_author(conn)
		elif choice == 7:
			borrow_book(conn)
		elif choice == 8:
			return_book(conn)
		elif choice == 9:
			make_res(conn)
		elif choice == 10:
			cancel_res(conn)
		elif choice == 11: 
			pay_fine(conn)
		elif choice == 12:
			report_overdue(conn)
		elif choice == 13:
			report_popular(conn)
		elif choice == 14:
			report_inventory(conn)
		elif choice == 15:
			print("Exiting...")
			break
		else:
			print("Invalid Choice.\n")
		
	conn.close()
		
if __name__ == "__main__":
	main()
	
	
	
	
