"""
Todo List Application
A simple command-line todo list application with persistence.
"""

import json
import os
from typing import List, Dict, Optional


class TodoItem:
    """Represents a single todo item."""
    
    def __init__(self, text: str, completed: bool = False, todo_id: Optional[int] = None):
        self.id = todo_id if todo_id is not None else id(self)
        self.text = text
        self.completed = completed
    
    def to_dict(self) -> Dict:
        """Convert todo item to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'text': self.text,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        """Create todo item from dictionary."""
        return cls(
            text=data['text'],
            completed=data['completed'],
            todo_id=data['id']
        )
    
    def __repr__(self) -> str:
        status = "✓" if self.completed else " "
        return f"[{status}] {self.text} (ID: {self.id})"


class TodoList:
    """Manages a collection of todo items with persistence."""
    
    def __init__(self, storage_file: str = 'todos.json'):
        self.storage_file = storage_file
        self.todos: List[TodoItem] = []
        self.load()
    
    def add(self, text: str) -> bool:
        """
        Add a new todo item.
        
        Args:
            text: The text of the todo item
            
        Returns:
            True if added successfully, False if validation failed
        """
        if not text or not text.strip():
            return False
        
        todo = TodoItem(text.strip())
        self.todos.append(todo)
        self.save()
        return True
    
    def delete(self, todo_id: int) -> bool:
        """
        Delete a todo item by ID.
        
        Args:
            todo_id: The ID of the todo item to delete
            
        Returns:
            True if deleted, False if not found
        """
        initial_count = len(self.todos)
        self.todos = [todo for todo in self.todos if todo.id != todo_id]
        
        if len(self.todos) < initial_count:
            self.save()
            return True
        return False
    
    def toggle_complete(self, todo_id: int) -> bool:
        """
        Toggle the completion status of a todo item.
        
        Args:
            todo_id: The ID of the todo item to toggle
            
        Returns:
            True if toggled, False if not found
        """
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = not todo.completed
                self.save()
                return True
        return False
    
    def get_all(self) -> List[TodoItem]:
        """Get all todo items."""
        return self.todos.copy()
    
    def get_pending(self) -> List[TodoItem]:
        """Get all pending (incomplete) todo items."""
        return [todo for todo in self.todos if not todo.completed]
    
    def get_completed(self) -> List[TodoItem]:
        """Get all completed todo items."""
        return [todo for todo in self.todos if todo.completed]
    
    def count_pending(self) -> int:
        """Get the count of pending tasks."""
        return len(self.get_pending())
    
    def save(self) -> None:
        """Save todos to JSON file."""
        data = [todo.to_dict() for todo in self.todos]
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """Load todos from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.todos = [TodoItem.from_dict(item) for item in data]
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                self.todos = []
        else:
            self.todos = []
    
    def clear(self) -> None:
        """Clear all todos."""
        self.todos = []
        self.save()


def main():
    """Command-line interface for the todo app."""
    todo_list = TodoList()
    
    print("=== Todo List Application ===")
    print("Commands: add, list, complete, delete, pending, clear, quit")
    print()
    
    while True:
        command = input("Enter command: ").strip().lower()
        
        if command == 'quit' or command == 'q':
            print("Goodbye!")
            break
        
        elif command == 'add' or command.startswith('add '):
            if command.startswith('add '):
                text = command[4:].strip()
            else:
                text = input("Enter task: ").strip()
            
            if todo_list.add(text):
                print(f"✓ Added: {text}")
            else:
                print("✗ Error: Task cannot be empty or whitespace only")
        
        elif command == 'list' or command == 'ls':
            todos = todo_list.get_all()
            if todos:
                print("\nAll Tasks:")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print("No tasks found.")
        
        elif command == 'pending':
            todos = todo_list.get_pending()
            if todos:
                print(f"\nPending Tasks ({len(todos)}):")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print("No pending tasks.")
        
        elif command == 'complete' or command.startswith('complete '):
            if command.startswith('complete '):
                try:
                    todo_id = int(command[9:].strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    continue
            else:
                try:
                    todo_id = int(input("Enter task ID to complete: ").strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    continue
            
            if todo_list.toggle_complete(todo_id):
                print(f"✓ Task {todo_id} toggled")
            else:
                print(f"✗ Error: Task {todo_id} not found")
        
        elif command == 'delete' or command.startswith('delete '):
            if command.startswith('delete '):
                try:
                    todo_id = int(command[7:].strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    continue
            else:
                try:
                    todo_id = int(input("Enter task ID to delete: ").strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    continue
            
            if todo_list.delete(todo_id):
                print(f"✓ Task {todo_id} deleted")
            else:
                print(f"✗ Error: Task {todo_id} not found")
        
        elif command == 'clear':
            confirm = input("Are you sure you want to clear all tasks? (yes/no): ").strip().lower()
            if confirm == 'yes':
                todo_list.clear()
                print("✓ All tasks cleared")
            else:
                print("Clear cancelled")
        
        else:
            print(f"Unknown command: {command}")
            print("Commands: add, list, complete, delete, pending, clear, quit")
        
        print()


if __name__ == '__main__':
    main()

