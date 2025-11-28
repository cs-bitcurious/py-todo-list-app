"""
Unit tests for the Todo List Application
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import date, time, datetime, timedelta
from todo_app import TodoItem, TodoList, parse_due_date_time


class TestTodoItem(unittest.TestCase):
    """Test cases for TodoItem class."""
    
    def test_todo_item_creation(self):
        """Test creating a todo item."""
        todo = TodoItem("Test task")
        self.assertEqual(todo.text, "Test task")
        self.assertFalse(todo.completed)
        self.assertIsNotNone(todo.id)
        self.assertIsNone(todo.due_date)
        self.assertIsNone(todo.due_time)
    
    def test_todo_item_with_id(self):
        """Test creating a todo item with specific ID."""
        todo = TodoItem("Test task", todo_id=123)
        self.assertEqual(todo.id, 123)
    
    def test_todo_item_with_due_date(self):
        """Test creating a todo item with due date only."""
        due_date = date(2024, 12, 25)
        todo = TodoItem("Test task", due_date=due_date)
        self.assertEqual(todo.due_date, due_date)
        self.assertIsNone(todo.due_time)
    
    def test_todo_item_with_due_date_and_time(self):
        """Test creating a todo item with due date and time."""
        due_date = date(2024, 12, 25)
        due_time = time(14, 30)
        todo = TodoItem("Test task", due_date=due_date, due_time=due_time)
        self.assertEqual(todo.due_date, due_date)
        self.assertEqual(todo.due_time, due_time)
    
    def test_todo_item_to_dict(self):
        """Test converting todo item to dictionary."""
        todo = TodoItem("Test task", completed=True, todo_id=456)
        data = todo.to_dict()
        
        self.assertEqual(data['id'], 456)
        self.assertEqual(data['text'], "Test task")
        self.assertTrue(data['completed'])
        self.assertNotIn('due_date', data)
        self.assertNotIn('due_time', data)
    
    def test_todo_item_to_dict_with_due_date(self):
        """Test converting todo item with due date to dictionary."""
        due_date = date(2024, 12, 25)
        todo = TodoItem("Test task", due_date=due_date, todo_id=456)
        data = todo.to_dict()
        
        self.assertEqual(data['due_date'], "2024-12-25")
        self.assertNotIn('due_time', data)
    
    def test_todo_item_to_dict_with_due_date_and_time(self):
        """Test converting todo item with due date and time to dictionary."""
        due_date = date(2024, 12, 25)
        due_time = time(14, 30, 0)
        todo = TodoItem("Test task", due_date=due_date, due_time=due_time, todo_id=456)
        data = todo.to_dict()
        
        self.assertEqual(data['due_date'], "2024-12-25")
        self.assertEqual(data['due_time'], "14:30:00")
    
    def test_todo_item_from_dict(self):
        """Test creating todo item from dictionary."""
        data = {'id': 789, 'text': 'Test task', 'completed': False}
        todo = TodoItem.from_dict(data)
        
        self.assertEqual(todo.id, 789)
        self.assertEqual(todo.text, 'Test task')
        self.assertFalse(todo.completed)
        self.assertIsNone(todo.due_date)
        self.assertIsNone(todo.due_time)
    
    def test_todo_item_from_dict_with_due_date(self):
        """Test creating todo item from dictionary with due date."""
        data = {
            'id': 789,
            'text': 'Test task',
            'completed': False,
            'due_date': '2024-12-25'
        }
        todo = TodoItem.from_dict(data)
        
        self.assertEqual(todo.due_date, date(2024, 12, 25))
        self.assertIsNone(todo.due_time)
    
    def test_todo_item_from_dict_with_due_date_and_time(self):
        """Test creating todo item from dictionary with due date and time."""
        data = {
            'id': 789,
            'text': 'Test task',
            'completed': False,
            'due_date': '2024-12-25',
            'due_time': '14:30:00'
        }
        todo = TodoItem.from_dict(data)
        
        self.assertEqual(todo.due_date, date(2024, 12, 25))
        self.assertEqual(todo.due_time, time(14, 30, 0))
    
    def test_todo_item_repr_without_due_date(self):
        """Test __repr__ without due date."""
        todo = TodoItem("Test task", todo_id=123)
        repr_str = repr(todo)
        self.assertIn("Test task", repr_str)
        self.assertIn("ID: 123", repr_str)
        self.assertNotIn("Due:", repr_str)
    
    def test_todo_item_repr_with_due_date(self):
        """Test __repr__ with due date only."""
        due_date = date(2024, 12, 25)
        todo = TodoItem("Test task", due_date=due_date, todo_id=123)
        repr_str = repr(todo)
        self.assertIn("Test task", repr_str)
        self.assertIn("Due: 2024-12-25", repr_str)
        self.assertIn("ID: 123", repr_str)
    
    def test_todo_item_repr_with_due_date_and_time(self):
        """Test __repr__ with due date and time."""
        due_date = date(2024, 12, 25)
        due_time = time(14, 30)
        todo = TodoItem("Test task", due_date=due_date, due_time=due_time, todo_id=123)
        repr_str = repr(todo)
        self.assertIn("Test task", repr_str)
        self.assertIn("Due: 2024-12-25 14:30", repr_str)
        self.assertIn("ID: 123", repr_str)


class TestTodoList(unittest.TestCase):
    """Test cases for TodoList class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_todos.json')
        self.todo_list = TodoList(storage_file=self.test_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_add_task(self):
        """Test Case 1: Add a new unique task and verify localStorage (JSON file) updates."""
        # Add a task
        result = self.todo_list.add("Test task")
        
        # Verify it was added successfully
        self.assertTrue(result)
        
        # Verify it's in the list
        todos = self.todo_list.get_all()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].text, "Test task")
        self.assertFalse(todos[0].completed)
        
        # Verify it was saved to file
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['text'], "Test task")
    
    def test_add_task_with_due_date(self):
        """Test adding task with due date."""
        due_date = date(2024, 12, 25)
        result = self.todo_list.add("Test task", due_date=due_date)
        
        self.assertTrue(result)
        todos = self.todo_list.get_all()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].due_date, due_date)
        self.assertIsNone(todos[0].due_time)
        
        # Verify persistence
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data[0]['due_date'], "2024-12-25")
            self.assertNotIn('due_time', data[0])
    
    def test_add_task_with_due_date_and_time(self):
        """Test adding task with due date and time."""
        due_date = date(2024, 12, 25)
        due_time = time(14, 30)
        result = self.todo_list.add("Test task", due_date=due_date, due_time=due_time)
        
        self.assertTrue(result)
        todos = self.todo_list.get_all()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].due_date, due_date)
        self.assertEqual(todos[0].due_time, due_time)
        
        # Verify persistence
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data[0]['due_date'], "2024-12-25")
            self.assertEqual(data[0]['due_time'], "14:30:00")
    
    def test_add_task_without_due_date(self):
        """Test adding task without due date (backward compatibility)."""
        result = self.todo_list.add("Test task")
        
        self.assertTrue(result)
        todos = self.todo_list.get_all()
        self.assertEqual(len(todos), 1)
        self.assertIsNone(todos[0].due_date)
        self.assertIsNone(todos[0].due_time)
    
    def test_add_multiple_tasks(self):
        """Test adding multiple tasks."""
        self.todo_list.add("Task 1")
        self.todo_list.add("Task 2")
        self.todo_list.add("Task 3")
        
        todos = self.todo_list.get_all()
        self.assertEqual(len(todos), 3)
    
    def test_mark_complete(self):
        """Test Case 2: Mark an item as complete and verify status field is toggled."""
        # Add a task
        self.todo_list.add("Test task")
        todos = self.todo_list.get_all()
        todo_id = todos[0].id
        
        # Verify initial state is incomplete
        self.assertFalse(todos[0].completed)
        
        # Toggle to complete
        result = self.todo_list.toggle_complete(todo_id)
        self.assertTrue(result)
        
        # Verify it's now completed
        todos = self.todo_list.get_all()
        self.assertTrue(todos[0].completed)
        
        # Verify status in file
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertTrue(data[0]['completed'])
        
        # Toggle back to incomplete
        self.todo_list.toggle_complete(todo_id)
        todos = self.todo_list.get_all()
        self.assertFalse(todos[0].completed)
    
    def test_input_validation_empty(self):
        """Test Case 3a: Attempt to add empty task and verify storage is unchanged."""
        initial_count = len(self.todo_list.get_all())
        
        # Try to add empty string
        result = self.todo_list.add("")
        self.assertFalse(result)
        
        # Verify no task was added
        self.assertEqual(len(self.todo_list.get_all()), initial_count)
        
        # Verify file wasn't created or is empty
        if os.path.exists(self.test_file):
            with open(self.test_file, 'r') as f:
                data = json.load(f)
                self.assertEqual(len(data), initial_count)
    
    def test_input_validation_whitespace(self):
        """Test Case 3b: Attempt to add whitespace-only task and verify storage is unchanged."""
        initial_count = len(self.todo_list.get_all())
        
        # Try to add whitespace-only strings
        self.assertFalse(self.todo_list.add("   "))
        self.assertFalse(self.todo_list.add("\t\n\r"))
        self.assertFalse(self.todo_list.add("  \t  \n  "))
        
        # Verify no tasks were added
        self.assertEqual(len(self.todo_list.get_all()), initial_count)
    
    def test_delete_task(self):
        """Test deleting a task."""
        # Add tasks
        self.todo_list.add("Task 1")
        self.todo_list.add("Task 2")
        todos = self.todo_list.get_all()
        task_id = todos[0].id
        
        # Delete a task
        result = self.todo_list.delete(task_id)
        self.assertTrue(result)
        
        # Verify it was deleted
        todos = self.todo_list.get_all()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].text, "Task 2")
        
        # Verify file was updated
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
    
    def test_delete_nonexistent_task(self):
        """Test deleting a task that doesn't exist."""
        result = self.todo_list.delete(99999)
        self.assertFalse(result)
    
    def test_toggle_nonexistent_task(self):
        """Test toggling a task that doesn't exist."""
        result = self.todo_list.toggle_complete(99999)
        self.assertFalse(result)
    
    def test_get_pending(self):
        """Test getting pending tasks."""
        self.todo_list.add("Task 1")
        self.todo_list.add("Task 2")
        self.todo_list.add("Task 3")
        
        todos = self.todo_list.get_all()
        self.todo_list.toggle_complete(todos[0].id)
        
        pending = self.todo_list.get_pending()
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0].text, "Task 2")
        self.assertEqual(pending[1].text, "Task 3")
    
    def test_get_completed(self):
        """Test getting completed tasks."""
        self.todo_list.add("Task 1")
        self.todo_list.add("Task 2")
        
        todos = self.todo_list.get_all()
        self.todo_list.toggle_complete(todos[0].id)
        
        completed = self.todo_list.get_completed()
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].text, "Task 1")
    
    def test_get_overdue(self):
        """Test getting overdue tasks."""
        # Add tasks with different due dates
        past_date = date.today() - timedelta(days=1)
        future_date = date.today() + timedelta(days=1)
        
        self.todo_list.add("Overdue task", due_date=past_date)
        self.todo_list.add("Future task", due_date=future_date)
        self.todo_list.add("Task without due date")
        
        overdue = self.todo_list.get_overdue()
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].text, "Overdue task")
    
    def test_get_overdue_with_time(self):
        """Test getting overdue tasks with time consideration."""
        yesterday = date.today() - timedelta(days=1)
        past_time = time(10, 0)
        
        self.todo_list.add("Overdue task", due_date=yesterday, due_time=past_time)
        
        overdue = self.todo_list.get_overdue()
        self.assertEqual(len(overdue), 1)
    
    def test_get_overdue_excludes_completed(self):
        """Test that completed tasks are not included in overdue."""
        past_date = date.today() - timedelta(days=1)
        
        self.todo_list.add("Overdue completed", due_date=past_date)
        self.todo_list.add("Overdue incomplete", due_date=past_date)
        
        todos = self.todo_list.get_all()
        # Mark first task as completed
        self.todo_list.toggle_complete(todos[0].id)
        
        overdue = self.todo_list.get_overdue()
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].text, "Overdue incomplete")
    
    def test_get_overdue_excludes_no_due_date(self):
        """Test that tasks without due dates are not included in overdue."""
        self.todo_list.add("Task without due date")
        
        overdue = self.todo_list.get_overdue()
        self.assertEqual(len(overdue), 0)
    
    def test_get_due_today(self):
        """Test getting tasks due today."""
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        
        self.todo_list.add("Task due today", due_date=today)
        self.todo_list.add("Task due tomorrow", due_date=tomorrow)
        self.todo_list.add("Task without due date")
        
        due_today = self.todo_list.get_due_today()
        self.assertEqual(len(due_today), 1)
        self.assertEqual(due_today[0].text, "Task due today")
    
    def test_get_due_soon(self):
        """Test getting tasks due within specified days."""
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        next_week = date.today() + timedelta(days=7)
        next_month = date.today() + timedelta(days=30)
        
        self.todo_list.add("Task due tomorrow", due_date=tomorrow)
        self.todo_list.add("Task due next week", due_date=next_week)
        self.todo_list.add("Task due next month", due_date=next_month)
        self.todo_list.add("Task without due date")
        
        due_soon = self.todo_list.get_due_soon(days=7)
        self.assertEqual(len(due_soon), 2)
        self.assertIn("Task due tomorrow", [t.text for t in due_soon])
        self.assertIn("Task due next week", [t.text for t in due_soon])
    
    def test_get_due_soon_default_days(self):
        """Test get_due_soon with default 7 days."""
        today = date.today()
        next_week = date.today() + timedelta(days=7)
        
        self.todo_list.add("Task due next week", due_date=next_week)
        
        due_soon = self.todo_list.get_due_soon()
        self.assertEqual(len(due_soon), 1)
    
    def test_get_due_soon_excludes_past(self):
        """Test that get_due_soon excludes past dates."""
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)
        
        self.todo_list.add("Past task", due_date=yesterday)
        self.todo_list.add("Future task", due_date=tomorrow)
        
        due_soon = self.todo_list.get_due_soon(days=7)
        self.assertEqual(len(due_soon), 1)
        self.assertEqual(due_soon[0].text, "Future task")
    
    def test_count_pending(self):
        """Test counting pending tasks."""
        self.todo_list.add("Task 1")
        self.todo_list.add("Task 2")
        self.todo_list.add("Task 3")
        
        self.assertEqual(self.todo_list.count_pending(), 3)
        
        todos = self.todo_list.get_all()
        self.todo_list.toggle_complete(todos[0].id)
        
        self.assertEqual(self.todo_list.count_pending(), 2)
    
    def test_persistence(self):
        """Test that todos persist across TodoList instances."""
        # Create first instance and add tasks
        todo_list1 = TodoList(storage_file=self.test_file)
        todo_list1.add("Task 1")
        todo_list1.add("Task 2")
        
        # Create second instance and verify tasks are loaded
        todo_list2 = TodoList(storage_file=self.test_file)
        todos = todo_list2.get_all()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0].text, "Task 1")
        self.assertEqual(todos[1].text, "Task 2")
    
    def test_persistence_with_due_dates(self):
        """Test that todos with due dates persist correctly."""
        due_date = date(2024, 12, 25)
        due_time = time(14, 30)
        
        # Create first instance and add task with due date
        todo_list1 = TodoList(storage_file=self.test_file)
        todo_list1.add("Task with due date", due_date=due_date, due_time=due_time)
        
        # Create second instance and verify due date is loaded
        todo_list2 = TodoList(storage_file=self.test_file)
        todos = todo_list2.get_all()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].due_date, due_date)
        self.assertEqual(todos[0].due_time, due_time)
    
    def test_backward_compatibility_loading_old_format(self):
        """Test loading old JSON format without due_date/due_time fields."""
        # Create JSON file with old format
        old_data = [
            {'id': 123, 'text': 'Old task', 'completed': False}
        ]
        with open(self.test_file, 'w') as f:
            json.dump(old_data, f)
        
        # Load and verify it works
        todo_list = TodoList(storage_file=self.test_file)
        todos = todo_list.get_all()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].text, "Old task")
        self.assertIsNone(todos[0].due_date)
        self.assertIsNone(todos[0].due_time)
    
    def test_clear(self):
        """Test clearing all tasks."""
        self.todo_list.add("Task 1")
        self.todo_list.add("Task 2")
        self.todo_list.clear()
        
        self.assertEqual(len(self.todo_list.get_all()), 0)
        
        # Verify file is empty
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 0)
    
    def test_trim_whitespace(self):
        """Test that task text is trimmed of leading/trailing whitespace."""
        self.todo_list.add("  Task with spaces  ")
        todos = self.todo_list.get_all()
        self.assertEqual(todos[0].text, "Task with spaces")


class TestParseDueDateTime(unittest.TestCase):
    """Test cases for parse_due_date_time function."""
    
    def test_parse_date_only(self):
        """Test parsing date only format."""
        date_obj, time_obj = parse_due_date_time("2024-12-25")
        self.assertEqual(date_obj, date(2024, 12, 25))
        self.assertIsNone(time_obj)
    
    def test_parse_date_and_time(self):
        """Test parsing date and time format."""
        date_obj, time_obj = parse_due_date_time("2024-12-25 14:30")
        self.assertEqual(date_obj, date(2024, 12, 25))
        self.assertEqual(time_obj, time(14, 30, 0))
    
    def test_parse_date_and_time_with_seconds(self):
        """Test parsing date and time with seconds."""
        date_obj, time_obj = parse_due_date_time("2024-12-25 14:30:45")
        self.assertEqual(date_obj, date(2024, 12, 25))
        self.assertEqual(time_obj, time(14, 30, 45))
    
    def test_parse_invalid_date(self):
        """Test parsing invalid date format."""
        date_obj, time_obj = parse_due_date_time("invalid-date")
        self.assertIsNone(date_obj)
        self.assertIsNone(time_obj)
    
    def test_parse_invalid_time(self):
        """Test parsing invalid time format."""
        date_obj, time_obj = parse_due_date_time("2024-12-25 25:99")
        self.assertIsNone(date_obj)
        self.assertIsNone(time_obj)
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        date_obj, time_obj = parse_due_date_time("")
        self.assertIsNone(date_obj)
        self.assertIsNone(time_obj)
    
    def test_parse_whitespace(self):
        """Test parsing whitespace string."""
        date_obj, time_obj = parse_due_date_time("   ")
        self.assertIsNone(date_obj)
        self.assertIsNone(time_obj)


if __name__ == '__main__':
    unittest.main()

