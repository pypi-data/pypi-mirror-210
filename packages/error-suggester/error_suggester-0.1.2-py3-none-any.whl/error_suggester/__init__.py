# your-library/__init__.py

from .error_suggester import ErrorSuggester
# Import other modules or define any utility functions or classes

__version__ = '0.1.2'

# Optionally, you can specify which symbols are imported when someone uses `from your_library import *`
__all__ = [
    'ErrorSuggester',
    # Add other symbols here
]
