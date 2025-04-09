import pytest
import importlib
import inspect

def test_debug_enemy_classes():
    """Debug test to check the enemy classes."""
    # List of enemy modules to check
    enemy_modules = [
        "src.entities.enemies.enemy",
        "src.entities.enemies.chaser",
        "src.entities.enemies.wander",
        "src.entities.enemies.shooter"
    ]

    # Check each module
    for module_name in enemy_modules:
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            print(f"\nSuccessfully imported {module_name}")

            # Get all classes in the module
            classes = inspect.getmembers(module, inspect.isclass)
            print(f"Classes in {module_name}:")
            for name, cls in classes:
                if cls.__module__ == module_name:
                    print(f"  - {name}")

                    # Check if the class has the necessary methods
                    methods = inspect.getmembers(cls, inspect.isfunction)
                    method_names = [name for name, _ in methods]
                    print(f"    Methods: {', '.join(method_names)}")
        except ImportError as e:
            print(f"\nError importing {module_name}: {e}")