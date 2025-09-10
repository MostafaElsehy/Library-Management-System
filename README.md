# Library Management System

A comprehensive console-based Python application that provides complete book and user management with borrowing, returns, popularity tracking, and graph‑based recommendations.

## 🏫 Overview

This Library Management System showcases solid Python design with clear separation between domain models, services, and UI helpers. It supports CRUD operations, a borrow queue when copies are unavailable, top‑K popular books, and a recommendation engine that leverages a simple user–book graph and user interests.

## ✨ Features

### 📚 Books & Users
- **CRUD Operations**: Create, read, update, and delete books and users
- **Search**: Filter books by title, author, or genre
- **Structured Models**: `Book`, `User`, and base `LibraryItem` with validation

### 🔄 Borrowing Workflow
- **Borrow/Return**: Safe borrowing with availability checks and returns
- **Request Queue**: FIFO queue when copies are unavailable (auto-processed on return)
- **Popularity Tracking**: `borrow_count` increments to support rankings

### 📈 Analytics & Recommendations
- **Top‑K Books**: List the most borrowed books
- **Recommendations**: Graph traversal + interests + popularity scoring

### 🖥️ Console UI
- **Consistent Output**: Title, subtitles, tables, and status messages
- **Simple Menu Flow**: Numbered options and validated inputs

### 💾 Persistence
- **JSON Storage**: Automatically loads state on startup and saves on exit
- **Location**: `data/library.json` (ignored by Git)

## 🏗️ Architecture

### Design Principles
- **Separation of Concerns**: Domain, services, UI, and utilities
- **Data Structures**: Custom `LinkedListQueue` and `Graph` to illustrate CS basics

### Module/Class Structure
```
src/book.py
├── LibraryItem (base)
└── Book (domain model)

src/user.py
└── User (domain model)

src/data_structures.py
├── LinkedListQueue[T]
└── Graph (undirected)

src/library.py
└── Library (service: CRUD, borrow/return, queries)

src/recommendation.py
└── RecommendationEngine

src/ui.py
└── Console helpers (title, table, messages)

src/app.py
└── CLI entry point and menu loop
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.9 or later**

### Installation
1. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### First Run
The app seeds a few demo books and users at startup so you can explore features immediately.

## 🔧 Usage Guide

### Start the Application
- Windows: `python .\src\app.py`
- macOS/Linux: `python src/app.py`

### Main Menu Options
1. **Add Book** – Create a new book
2. **Remove Book** – Delete a book by ID
3. **Update Book** – Modify title/author/genre
4. **Add User** – Create a user with interests
5. **Borrow Book** – Borrow if available, else enqueue
6. **Return Book** – Return and auto-process queue
7. **Show Available Books** – List books with copies left
8. **Show Top‑K Books** – Most borrowed rankings
9. **Recommend Books** – Personalized suggestions
10. **Exit** – Quit the application

When you exit, the current state (books, users, borrow queue, popularity) is saved to `data/library.json`. Next launch will restore this state automatically.

## 🔒 Security Considerations

### Current Implementation
- **In‑Memory Storage**: Data is kept in memory during runtime
- **No Secrets**: Application does not require authentication

### Recommended Improvements
- **Persistence Layer**: Add database or file storage
- **Input Hardening**: Expand validation and error handling
 - Note: Basic JSON persistence is included; switch to a database for multi‑user or concurrent scenarios

## 🛠️ Technical Details

### Data Structures
- `LinkedListQueue[T]`: O(1) enqueue/dequeue; used for borrow requests
- `Graph`: Undirected adjacency list; used for recommendations (BFS)

### Testing & Quality
- (Optional) Tests: `pytest`
- (Optional) Lint: `ruff check .`
- (Optional) Format: `black .`
- (Optional) Type Check: `mypy .`

## 📁 Project Structure
```
Library-Management-System/
├── src/
│   ├── app.py
│   ├── book.py
│   ├── data_structures.py
│   ├── library.py
│   ├── recommendation.py
│   ├── ui.py
│   └── user.py
├── data/                 # runtime state (JSON), ignored by Git
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## 🐛 Known Issues
1. JSON persistence is basic (single-user, no concurrency guarantees)
2. Minimal validation in CLI prompts
3. Simple recommendation heuristic (educational)

## 👥 Contributing
Contributions are welcome via pull requests.

## 📄 License
MIT © 2025 elseh — see `LICENSE`.

## 📞 Support
If you have questions or issues:
1. Review this README and docstrings in `src/`
2. Open an issue or PR if something can be improved
