#!/bin/bash
# Test runner for workpiece_editor package
echo "🔧 Workpiece Editor Test Runner"
echo "================================"
echo ""
# Disable ROS pytest plugin to avoid collection errors
PYTEST_DISABLE_ROS="-p no:launch_testing_ros_pytest_entrypoint"
# Run all workpiece_editor tests
if [ "$1" == "all" ]; then
    echo "Running all workpiece_editor tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/ -v $PYTEST_DISABLE_ROS
# Run adapter tests
elif [ "$1" == "adapter" ]; then
    echo "Running WorkpieceAdapter tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_workpiece_adapter.py -v $PYTEST_DISABLE_ROS
# Run manager tests
elif [ "$1" == "manager" ]; then
    echo "Running WorkpieceManager tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_workpiece_manager.py -v $PYTEST_DISABLE_ROS
# Run builder tests
elif [ "$1" == "builder" ]; then
    echo "Running WorkpieceEditorBuilder tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_workpiece_builder.py -v $PYTEST_DISABLE_ROS
# Run model tests
elif [ "$1" == "models" ]; then
    echo "Running model tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_workpiece_models.py -v $PYTEST_DISABLE_ROS
# Run handler tests
elif [ "$1" == "handlers" ]; then
    echo "Running handler tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_handlers.py -v $PYTEST_DISABLE_ROS
# Run integration tests
elif [ "$1" == "integration" ]; then
    echo "Running integration tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_integration.py -v $PYTEST_DISABLE_ROS
# Run with coverage
elif [ "$1" == "coverage" ]; then
    echo "Running workpiece_editor tests with coverage..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/ -v \
        --cov=src/workpiece_editor \
        --cov-report=html:htmlcov/workpiece_editor \
        --cov-report=term-missing \
        $PYTEST_DISABLE_ROS
    echo ""
    echo "📊 Coverage report generated in htmlcov/workpiece_editor/index.html"
# Run quick smoke test
elif [ "$1" == "quick" ]; then
    echo "Running quick smoke tests..."
    PYTHONPATH=src python3 -m pytest tests/workpiece_editor/test_integration.py::TestWorkpieceEditorIntegration::test_layer_name_compatibility -v $PYTEST_DISABLE_ROS
# Run specific test file
elif [ -n "$1" ]; then
    echo "Running test file: $1"
    PYTHONPATH=src python3 -m pytest "$1" -v $PYTEST_DISABLE_ROS
# Show help
else
    echo "Usage:"
    echo "  ./RUN_WORKPIECE_TESTS.sh all         - Run all workpiece_editor tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh adapter     - Run WorkpieceAdapter tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh manager     - Run WorkpieceManager tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh builder     - Run WorkpieceEditorBuilder tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh models      - Run model tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh handlers    - Run handler tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh integration - Run integration tests"
    echo "  ./RUN_WORKPIECE_TESTS.sh coverage    - Run with coverage report"
    echo "  ./RUN_WORKPIECE_TESTS.sh quick       - Run quick smoke test"
    echo "  ./RUN_WORKPIECE_TESTS.sh <file>      - Run specific test file"
    echo ""
    echo "Examples:"
    echo "  ./RUN_WORKPIECE_TESTS.sh all"
    echo "  ./RUN_WORKPIECE_TESTS.sh adapter"
    echo "  ./RUN_WORKPIECE_TESTS.sh coverage"
    echo "  ./RUN_WORKPIECE_TESTS.sh tests/workpiece_editor/test_workpiece_adapter.py"
    echo ""
    echo "📦 Test Statistics:"
    echo "   - 59 test functions across 6 test files"
    echo "   - Coverage: adapters, managers, builders, models, handlers"
    echo ""
    echo "Note: ROS pytest plugin is automatically disabled"
fi
