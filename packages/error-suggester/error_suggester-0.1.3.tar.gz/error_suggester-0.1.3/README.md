# Error Suggester

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A Python library for error suggestions.

## Installation

```bash
pip install error-suggester
```

## Usage

```python
from error_suggester import ErrorSuggester

# Initialize ErrorSuggester with your OpenAI API key and enable auto suggestions
ErrorSuggester('YOUR_API_KEY').enable_auto_suggestions()

```

## Features

- Automatic error suggestions based on the provided error message.
- Helps in identifying possible resolutions for encountered errors and exceptions.
