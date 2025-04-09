"""Base parser class for all broker parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from .types import BrokerOperation


class BaseBrokerParser(ABC):
    """Abstract base class for all broker parsers."""

    def __init__(self, broker_name: str):
        """Initialize the parser with a broker name."""
        self.broker_name = broker_name

    @abstractmethod
    def parse_file(self, file_path: str | Path) -> List[BrokerOperation]:
        """Parse a broker file and return a list of operations.
        
        Args:
            file_path: Path to the broker file to parse
            
        Returns:
            List of parsed operations
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        pass

    @abstractmethod
    def validate_file(self, file_path: str | Path) -> bool:
        """Validate if a file can be parsed by this parser.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file can be parsed, False otherwise
        """
        pass

    def get_file_extension(self) -> str:
        """Get the expected file extension for this parser.
        
        Returns:
            The expected file extension (e.g., '.csv', '.xlsx')
        """
        return ".csv"  # Default to CSV, override in subclasses if needed

    def _validate_file_exists(self, file_path: str | Path) -> None:
        """Validate that the file exists.
        
        Args:
            file_path: Path to check
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def _validate_file_extension(self, file_path: str | Path) -> None:
        """Validate that the file has the correct extension.
        
        Args:
            file_path: Path to check
            
        Raises:
            ValueError: If the file extension is incorrect
        """
        path = Path(file_path)
        if path.suffix.lower() != self.get_file_extension().lower():
            raise ValueError(
                f"Invalid file extension. Expected {self.get_file_extension()}, "
                f"got {path.suffix}"
            ) 