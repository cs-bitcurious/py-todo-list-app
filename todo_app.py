"""
Todo List Application
A simple command-line todo list application with persistence.
"""

import json
import os
import re
from datetime import date, time, datetime
from typing import List, Dict, Optional


class TodoItem:
    """Represents a single todo item."""
    
    def __init__(self, text: str, completed: bool = False, todo_id: Optional[int] = None,
                 due_date: Optional[date] = None, due_time: Optional[time] = None):
        self.id = todo_id if todo_id is not None else id(self)
        self.text = text
        self.completed = completed
        self.due_date = due_date
        self.due_time = due_time
    
    def to_dict(self) -> Dict:
        """Convert todo item to dictionary for JSON serialization."""
        result = {
            'id': self.id,
            'text': self.text,
            'completed': self.completed
        }
        if self.due_date is not None:
            result['due_date'] = self.due_date.isoformat()
        if self.due_time is not None:
            result['due_time'] = self.due_time.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        """Create todo item from dictionary."""
        due_date = None
        due_time = None
        
        if 'due_date' in data and data['due_date'] is not None:
            due_date = date.fromisoformat(data['due_date'])
        if 'due_time' in data and data['due_time'] is not None:
            due_time = time.fromisoformat(data['due_time'])
        
        return cls(
            text=data['text'],
            completed=data['completed'],
            todo_id=data['id'],
            due_date=due_date,
            due_time=due_time
        )
    
    def __repr__(self) -> str:
        status = "✓" if self.completed else " "
        due_str = ""
        if self.due_date is not None:
            if self.due_time is not None:
                due_str = f" (Due: {self.due_date} {self.due_time.strftime('%H:%M')})"
            else:
                due_str = f" (Due: {self.due_date})"
        return f"[{status}] {self.text}{due_str} (ID: {self.id})"


class TodoList:
    """Manages a collection of todo items with persistence."""
    
    def __init__(self, storage_file: str = 'todos.json'):
        self.storage_file = storage_file
        self.todos: List[TodoItem] = []
        self.load()
    
    def add(self, text: str, due_date: Optional[date] = None, 
            due_time: Optional[time] = None) -> bool:
        """
        Add a new todo item.
        
        Args:
            text: The text of the todo item
            due_date: Optional due date for the task
            due_time: Optional due time for the task
            
        Returns:
            True if added successfully, False if validation failed
        """
        if not text or not text.strip():
            return False
        
        todo = TodoItem(text.strip(), due_date=due_date, due_time=due_time)
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
    
    def get_overdue(self) -> List[TodoItem]:
        """
        Get all overdue tasks (incomplete tasks past their due date/time).
        
        Returns:
            List of incomplete TodoItems that are past their due date/time
        """
        now = datetime.now()
        overdue = []
        
        for todo in self.todos:
            if todo.completed or todo.due_date is None:
                continue
            
            # Combine date and time for comparison
            if todo.due_time is not None:
                due_datetime = datetime.combine(todo.due_date, todo.due_time)
            else:
                # If no time specified, use end of day
                due_datetime = datetime.combine(todo.due_date, time.max)
            
            if due_datetime < now:
                overdue.append(todo)
        
        return overdue
    
    def get_due_today(self) -> List[TodoItem]:
        """
        Get all tasks due today.
        
        Returns:
            List of TodoItems due today
        """
        today = date.today()
        return [todo for todo in self.todos if todo.due_date == today]
    
    def get_due_soon(self, days: int = 7) -> List[TodoItem]:
        """
        Get all tasks due within the next N days.
        
        Args:
            days: Number of days to look ahead (default: 7)
            
        Returns:
            List of TodoItems due within the specified number of days
        """
        today = date.today()
        cutoff_date = date.fromordinal(today.toordinal() + days)
        
        return [
            todo for todo in self.todos
            if todo.due_date is not None
            and today <= todo.due_date <= cutoff_date
        ]
    
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


def parse_due_date_time(due_str: str) -> tuple[Optional[date], Optional[time]]:
    """
    Parse due date and time from string.
    
    Supports formats:
    - "YYYY-MM-DD" (date only)
    - "YYYY-MM-DD HH:MM" (date and time)
    - "YYYY-MM-DD HH:MM:SS" (date and time with seconds)
    
    Args:
        due_str: String containing date and optionally time
        
    Returns:
        Tuple of (date, time) or (None, None) if parsing fails
    """
    due_str = due_str.strip()
    
    # Try date and time format: "YYYY-MM-DD HH:MM" or "YYYY-MM-DD HH:MM:SS"
    datetime_pattern = r'^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?$'
    match = re.match(datetime_pattern, due_str)
    if match:
        try:
            date_part = date.fromisoformat(match.group(1))
            hour = int(match.group(2))
            minute = int(match.group(3))
            second = int(match.group(4)) if match.group(4) else 0
            
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                time_part = time(hour, minute, second)
                return date_part, time_part
        except (ValueError, AttributeError):
            pass
    
    # Try date only format: "YYYY-MM-DD"
    date_pattern = r'^(\d{4}-\d{2}-\d{2})$'
    match = re.match(date_pattern, due_str)
    if match:
        try:
            date_part = date.fromisoformat(match.group(1))
            return date_part, None
        except ValueError:
            pass
    
    return None, None


def main():
    """Command-line interface for the todo app."""
    todo_list = TodoList()
    
    print("=== Todo List Application ===")
    print("Commands: add, list, complete, delete, pending, overdue, due-today, due-soon, clear, quit")
    print("Add task with due date: add <task> --due YYYY-MM-DD [HH:MM]")
    print()
    
    while True:
        command = input("Enter command: ").strip()
        command_lower = command.lower()
        
        if command_lower == 'quit' or command_lower == 'q':
            print("Goodbye!")
            break
        
        elif command_lower == 'add' or command_lower.startswith('add '):
            # Parse add command with optional --due flag
            text = ""
            due_date = None
            due_time = None
            
            if command_lower.startswith('add '):
                rest = command[4:].strip()
            else:
                rest = input("Enter task: ").strip()
            
            # Check for --due flag
            if '--due' in rest:
                parts = rest.split('--due', 1)
                text = parts[0].strip()
                due_str = parts[1].strip() if len(parts) > 1 else ""
                
                if due_str:
                    parsed_date, parsed_time = parse_due_date_time(due_str)
                    if parsed_date is not None:
                        due_date = parsed_date
                        due_time = parsed_time
                    else:
                        print("✗ Error: Invalid date/time format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM")
                        print()
                        continue
                else:
                    print("✗ Error: --due flag requires a date")
                    print()
                    continue
            else:
                text = rest
            
            if todo_list.add(text, due_date=due_date, due_time=due_time):
                due_info = ""
                if due_date:
                    if due_time:
                        due_info = f" (Due: {due_date} {due_time.strftime('%H:%M')})"
                    else:
                        due_info = f" (Due: {due_date})"
                print(f"✓ Added: {text}{due_info}")
            else:
                print("✗ Error: Task cannot be empty or whitespace only")
        
        elif command_lower == 'list' or command_lower == 'ls':
            todos = todo_list.get_all()
            if todos:
                print("\nAll Tasks:")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print("No tasks found.")
        
        elif command_lower == 'pending':
            todos = todo_list.get_pending()
            if todos:
                print(f"\nPending Tasks ({len(todos)}):")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print("No pending tasks.")
        
        elif command_lower == 'overdue':
            todos = todo_list.get_overdue()
            if todos:
                print(f"\nOverdue Tasks ({len(todos)}):")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print("No overdue tasks.")
        
        elif command_lower == 'due-today':
            todos = todo_list.get_due_today()
            if todos:
                print(f"\nTasks Due Today ({len(todos)}):")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print("No tasks due today.")
        
        elif command_lower.startswith('due-soon'):
            days = 7
            if command_lower.startswith('due-soon '):
                try:
                    days = int(command_lower[9:].strip())
                except ValueError:
                    print("✗ Error: Please provide a valid number of days")
                    print()
                    continue
            
            todos = todo_list.get_due_soon(days=days)
            if todos:
                print(f"\nTasks Due in Next {days} Days ({len(todos)}):")
                for todo in todos:
                    print(f"  {todo}")
            else:
                print(f"No tasks due in the next {days} days.")
        
        elif command_lower == 'complete' or command_lower.startswith('complete '):
            if command_lower.startswith('complete '):
                try:
                    todo_id = int(command_lower[9:].strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    print()
                    continue
            else:
                try:
                    todo_id = int(input("Enter task ID to complete: ").strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    print()
                    continue
            
            if todo_list.toggle_complete(todo_id):
                print(f"✓ Task {todo_id} toggled")
            else:
                print(f"✗ Error: Task {todo_id} not found")
        
        elif command_lower == 'delete' or command_lower.startswith('delete '):
            if command_lower.startswith('delete '):
                try:
                    todo_id = int(command_lower[7:].strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    print()
                    continue
            else:
                try:
                    todo_id = int(input("Enter task ID to delete: ").strip())
                except ValueError:
                    print("✗ Error: Please provide a valid task ID")
                    print()
                    continue
            
            if todo_list.delete(todo_id):
                print(f"✓ Task {todo_id} deleted")
            else:
                print(f"✗ Error: Task {todo_id} not found")
        
        elif command_lower == 'clear':
            confirm = input("Are you sure you want to clear all tasks? (yes/no): ").strip().lower()
            if confirm == 'yes':
                todo_list.clear()
                print("✓ All tasks cleared")
            else:
                print("Clear cancelled")
        
        else:
            print(f"Unknown command: {command}")
            print("Commands: add, list, complete, delete, pending, overdue, due-today, due-soon, clear, quit")
        
        print()


if __name__ == '__main__':
    main()

