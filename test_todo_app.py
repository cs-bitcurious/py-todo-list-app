"""
Unit tests for the Todo List Application
"""

import unittest
import os
import json
import tempfile
import shutil
from todo_app import TodoItem, TodoList


class TestTodoItem(unittest.TestCase):
    """Test cases for TodoItem class."""
    
    def test_todo_item_creation(self):
        """Test creating a todo item."""
        todo = TodoItem("Test task")
        self.assertEqual(todo.text, "Test task")
        self.assertFalse(todo.completed)
        self.assertIsNotNone(todo.id)
    
    def test_todo_item_with_id(self):
        """Test creating a todo item with specific ID."""
        todo = TodoItem("Test task", todo_id=123)
        self.assertEqual(todo.id, 123)
    
    def test_todo_item_to_dict(self):
        """Test converting todo item to dictionary."""
        todo = TodoItem("Test task", completed=True, todo_id=456)
        data = todo.to_dict()
        
        self.assertEqual(data['id'], 456)
        self.assertEqual(data['text'], "Test task")
        self.assertTrue(data['completed'])
    
    def test_todo_item_from_dict(self):
        """Test creating todo item from dictionary."""
        data = {'id': 789, 'text': 'Test task', 'completed': False}
        todo = TodoItem.from_dict(data)
        
        self.assertEqual(todo.id, 789)
        self.assertEqual(todo.text, 'Test task')
        self.assertFalse(todo.completed)


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


if __name__ == '__main__':
    unittest.main()

