#!/bin/bash
# Quick reference for running tests
echo "🧪 ContourEditor Test Runner"
echo "=============================="
echo ""
# Run all tests
if [ "$1" == "all" ]; then
    echo "Running all tests..."
    PYTHONPATH=src python3 -m pytest tests/ -v
# Run unit tests only
elif [ "$1" == "unit" ]; then
    echo "Running unit tests..."
    PYTHONPATH=src python3 -m pytest tests/unit/ -v
# Run integration tests only
elif [ "$1" == "integration" ]; then
    echo "Running integration tests..."
    PYTHONPATH=src python3 -m pytest tests/integration/ -v
# Run with coverage
elif [ "$1" == "coverage" ]; then
    echo "Running tests with coverage..."
    PYTHONPATH=src python3 -m pytest tests/ -v --cov-report=html --cov-report=term
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
# Run specific test file
elif [ -n "$1" ]; then
    echo "Running test file: $1"
    PYTHONPATH=src python3 -m pytest "$1" -v
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
fi
