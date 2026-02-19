#!/bin/bash
# Quick reference for running tests
echo "🧪 ContourEditor Test Runner"
echo "=============================="
echo ""

# Use venv python if available, otherwise fall back to system python
if [ -f ".venv/bin/python3" ]; then
    PYTHON=".venv/bin/python3"
    echo "Using venv python: $PYTHON"
else
    PYTHON="python3"
    echo "⚠️  Warning: venv not found, using system python"
fi
echo ""

# Disable ROS pytest plugin to avoid collection errors
PYTEST_DISABLE_ROS="-p no:launch_testing_ros_pytest_entrypoint"

# Run all tests
if [ "$1" == "all" ]; then
    echo "Running all tests..."
    PYTHONPATH=src $PYTHON -m pytest tests/ -v $PYTEST_DISABLE_ROS
# Run unit tests only
elif [ "$1" == "unit" ]; then
    echo "Running unit tests..."
    PYTHONPATH=src $PYTHON -m pytest tests/unit/ -v $PYTEST_DISABLE_ROS
# Run integration tests only
elif [ "$1" == "integration" ]; then
    echo "Running integration tests..."
    PYTHONPATH=src $PYTHON -m pytest tests/integration/ -v $PYTEST_DISABLE_ROS
# Run with coverage
elif [ "$1" == "coverage" ]; then
    echo "Running tests with coverage..."
    PYTHONPATH=src $PYTHON -m pytest tests/ -v --cov-report=html --cov-report=term $PYTEST_DISABLE_ROS
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
# Run specific test file
elif [ -n "$1" ]; then
    echo "Running test file: $1"
    PYTHONPATH=src $PYTHON -m pytest "$1" -v $PYTEST_DISABLE_ROS
# Show help
else
    echo "Usage:"
    echo "  ./RUN_TESTS.sh all         - Run all tests"
    echo "  ./RUN_TESTS.sh unit        - Run unit tests only"
    echo "  ./RUN_TESTS.sh integration - Run integration tests only"
    echo "  ./RUN_TESTS.sh coverage    - Run with coverage report"
    echo "  ./RUN_TESTS.sh <file>      - Run specific test file"
    echo ""
    echo "Examples:"
    echo "  ./RUN_TESTS.sh all"
    echo "  ./RUN_TESTS.sh tests/unit/test_event_bus.py"
    echo "  ./RUN_TESTS.sh coverage"
    echo ""
    echo "Note: ROS pytest plugin is automatically disabled"
fi
