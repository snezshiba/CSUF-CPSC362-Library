PRAGMA foreign_keys = ON;

-- Drop tables in dependency order
DROP TABLE IF EXISTS Fines;
DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS Loans;
DROP TABLE IF EXISTS Book_Author;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Authors;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Members;
DROP TABLE IF EXISTS Users;

-- =========================================
-- USERS TABLE
-- Stores login info and role
-- =========================================
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'librarian', 'member'))
);

-- =========================================
-- MEMBERS TABLE
-- Stores member profile info linked to Users
-- =========================================
CREATE TABLE Members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    fname TEXT NOT NULL,
    minit TEXT,
    lname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- =========================================
-- CATEGORIES TABLE
-- Stores book categories
-- =========================================
CREATE TABLE Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- =========================================
-- AUTHORS TABLE
-- Stores author names
-- =========================================
CREATE TABLE Authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- =========================================
-- BOOKS TABLE
-- Stores book inventory info
-- =========================================
CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ISBN TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    publisher TEXT,
    year INTEGER,
    category_id INTEGER,
    copies_total INTEGER NOT NULL CHECK (copies_total >= 0),
    copies_available INTEGER NOT NULL CHECK (
        copies_available >= 0 AND copies_available <= copies_total
    ),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL
);

-- =========================================
-- BOOK_AUTHOR TABLE
-- Many-to-many relationship between books and authors
-- =========================================
CREATE TABLE Book_Author (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE CASCADE
);

-- =========================================
-- LOANS TABLE
-- Stores borrowing records
-- =========================================
CREATE TABLE Loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    checkout_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL CHECK (status IN ('checked_out', 'returned')),
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);

-- =========================================
-- RESERVATIONS TABLE
-- Stores book reservations
-- =========================================
CREATE TABLE Reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    reservation_date TEXT NOT NULL DEFAULT (date('now')),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'fulfilled')),
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);

-- =========================================
-- FINES TABLE
-- Stores fines tied to a loan
-- =========================================
CREATE TABLE Fines (
    fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    paid INTEGER NOT NULL DEFAULT 0 CHECK (paid IN (0, 1)),
    FOREIGN KEY (loan_id) REFERENCES Loans(loan_id) ON DELETE CASCADE
);
