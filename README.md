# Python Todo List Application

A simple, command-line todo list application built with Python, featuring persistence and comprehensive unit tests.

## Features

- ✅ Add, delete, and manage todo items
- ✅ Mark tasks as complete/incomplete
- ✅ Persistent storage using JSON files
- ✅ View all tasks, pending tasks, or completed tasks
- ✅ Input validation (rejects empty/whitespace-only tasks)
- ✅ Comprehensive unit test suite

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Setup

### 1. Create Virtual Environment

```bash
# Navigate to project directory
cd my-python-app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

No external dependencies required! The app uses only Python's standard library.

```bash
# Optional: upgrade pip
pip install --upgrade pip
```

## Usage

### Running the Application

```bash
python todo_app.py
```

### Available Commands

- `add` or `add <task>` - Add a new task
- `list` or `ls` - List all tasks
- `pending` - Show only pending (incomplete) tasks
- `complete <id>` - Toggle completion status of a task by ID
- `delete <id>` - Delete a task by ID
- `clear` - Clear all tasks (with confirmation)
- `quit` or `q` - Exit the application

### Example Session

```
=== Todo List Application ===
Commands: add, list, complete, delete, pending, clear, quit

Enter command: add Buy groceries
✓ Added: Buy groceries

Enter command: add Complete project
✓ Added: Complete project

Enter command: list

All Tasks:
  [ ] Buy groceries (ID: 1234567890)
  [ ] Complete project (ID: 1234567891)

Enter command: complete 1234567890
✓ Task 1234567890 toggled

Enter command: pending

Pending Tasks (1):
  [ ] Complete project (ID: 1234567891)

Enter command: quit
Goodbye!
```

## Running Tests

The project includes a comprehensive unit test suite covering all core functionality.

### Run All Tests

```bash
python -m unittest test_todo_app.py
```

Or using the verbose flag:

```bash
python -m unittest test_todo_app.py -v
```

### Test Coverage

The test suite includes:

1. **Test Case 1: Add Task** - Verifies adding new tasks and JSON file updates
2. **Test Case 2: Mark Complete** - Verifies toggling task completion status
3. **Test Case 3: Input Validation** - Verifies rejection of empty/whitespace-only tasks
4. Additional tests for delete, persistence, filtering, and edge cases

## Project Structure

```
my-python-app/
├── todo_app.py          # Main application code
├── test_todo_app.py     # Unit test suite
├── requirements.txt     # Dependencies (none required)
├── README.md            # This file
├── .gitignore          # Git ignore rules
└── todos.json          # Data storage (created at runtime, gitignored)
```

## Architecture

### Core Classes

- **`TodoItem`**: Represents a single todo item with id, text, and completion status
- **`TodoList`**: Manages the collection of todos with persistence to JSON file

### Key Methods

- `add(text)` - Add a new task (returns True/False for validation)
- `delete(todo_id)` - Delete a task by ID
- `toggle_complete(todo_id)` - Toggle completion status
- `get_all()` - Get all tasks
- `get_pending()` - Get incomplete tasks
- `get_completed()` - Get completed tasks
- `count_pending()` - Count pending tasks
- `save()` / `load()` - Persistence operations

## Development

### Code Style

The code follows PEP 8 style guidelines and includes:
- Type hints for better code clarity
- Docstrings for all classes and methods
- Clear separation of concerns

### Testing Strategy

- Unit tests use Python's `unittest` framework
- Tests use temporary files to avoid polluting the project
- Each test is isolated and independent
- Tests cover both success and failure cases

## License

This project is open source and available for educational purposes.

