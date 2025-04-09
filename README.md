# Broker Parser

A collection of Python scripts for parsing and transforming financial broker data from different sources.

## Project Structure

```
broker_parser/
├── src/
│   └── broker_parser/
│       ├── brokers/           # Broker-specific parsers
│       │   └── pellegrini/    # Pellegrini broker parser
│       └── shared/            # Shared utilities and configurations
├── tests/
│   └── brokers/
│       └── pellegrini/        # Tests for Pellegrini parser
├── config/                    # Configuration files
└── docs/                     # Documentation
```

## Available Brokers

- Pellegrini

## Installation

1. Clone the repository:
```bash
git clone https://github.com/manuela-gabriel/broker_parser.git
cd broker_parser
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Each broker has its own parser module. To use a specific broker parser:

```python
from broker_parser.brokers.pellegrini.parser import PellegriniParser

parser = PellegriniParser()
parser.parse_file("path/to/input.csv")
```

## Development

- Follow PEP 8 style guide
- Use type hints
- Write tests for new features
- Update documentation

## License

MIT License - See LICENSE file for details 