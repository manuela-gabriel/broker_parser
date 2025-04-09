# Broker Data Parser

A Python package for parsing and transforming financial broker data into structured formats.

## Features

- Parses broker data from CSV and Excel files
- Supports multiple operation types (Trades, Monetary Flows, Security Flows, Mutual Funds)
- Handles different data formats and encodings
- Provides detailed logging and error handling
- Type-safe implementation with comprehensive type annotations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from broker_parser import transform_data

# Transform broker data
transform_data("input.csv", "output.xlsx")
```

## Project Structure

```
broker_parser/
├── src/
│   └── broker_parser/
│       ├── __init__.py
│       ├── parser.py
│       └── types.py
├── tests/
│   ├── __init__.py
│   └── test_parser.py
├── docs/
│   └── index.rst
├── config/
│   └── ruff.toml
├── requirements.txt
└── README.md
```

## Development

### Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Testing

Run tests with coverage:
```bash
pytest --cov=src tests/
```

### Code Style

The project uses:
- Ruff for linting
- Black for code formatting
- isort for import sorting
- mypy for type checking

Run all checks:
```bash
ruff check .
black .
isort .
mypy .
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 