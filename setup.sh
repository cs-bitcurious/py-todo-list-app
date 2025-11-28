#!/bin/bash
# Setup script for Python Todo List Application

echo "Setting up Python Todo List Application..."
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python todo_app.py"
echo ""
echo "To run tests:"
echo "  python -m unittest test_todo_app.py -v"

