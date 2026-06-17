"""Run all tests."""
import sys
import unittest
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo))
    loader = unittest.TestLoader()
    suite = loader.discover(str(Path(__file__).parent), pattern="test_*.py", top_level_dir=str(repo))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
