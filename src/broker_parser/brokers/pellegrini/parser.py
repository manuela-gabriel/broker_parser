"""Parser for Pellegrini broker data files."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from broker_parser.shared.base_parser import BaseBrokerParser
from broker_parser.shared.types import (
    BrokerOperation,
    MonetaryFlow,
    MutualFund,
    OperationType,
    SecurityFlow,
    Trade,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PellegriniParser(BaseBrokerParser):
    """Parser for Pellegrini broker data files."""

    def __init__(self):
        """Initialize the Pellegrini parser."""
        super().__init__("Pellegrini")

    def parse_file(self, file_path: str | Path) -> List[BrokerOperation]:
        """Parse a Pellegrini broker file and return a list of operations.
        
        Args:
            file_path: Path to the Pellegrini file to parse
            
        Returns:
            List of parsed operations
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        self._validate_file_exists(file_path)
        self._validate_file_extension(file_path)

        try:
            df = pd.read_csv(file_path, encoding="latin1")
            operations = self._parse_dataframe(df)
            logger.info(f"Successfully parsed {len(operations)} operations from {file_path}")
            return operations
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise ValueError(f"Error parsing file: {str(e)}")

    def validate_file(self, file_path: str | Path) -> bool:
        """Validate if a file can be parsed by the Pellegrini parser.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file can be parsed, False otherwise
        """
        try:
            self._validate_file_exists(file_path)
            self._validate_file_extension(file_path)
            df = pd.read_csv(file_path, encoding="latin1")
            return self._validate_dataframe(df)
        except Exception:
            return False

    def _validate_dataframe(self, df: pd.DataFrame) -> bool:
        """Validate if a DataFrame has the expected Pellegrini format.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if the DataFrame is valid, False otherwise
        """
        required_columns = ["Fecha", "Tipo", "Especie", "Cantidad", "Precio", "Importe"]
        return all(col in df.columns for col in required_columns)

    def _parse_dataframe(self, df: pd.DataFrame) -> List[BrokerOperation]:
        """Parse a DataFrame into a list of operations.
        
        Args:
            df: DataFrame to parse
            
        Returns:
            List of parsed operations
        """
        operations = []
        for _, row in df.iterrows():
            try:
                operation = self._parse_row(row)
                if operation:
                    operations.append(operation)
            except Exception as e:
                logger.warning(f"Error parsing row: {str(e)}")
                continue
        return operations

    def _parse_row(self, row: pd.Series) -> Optional[BrokerOperation]:
        """Parse a single row into an operation.
        
        Args:
            row: Row to parse
            
        Returns:
            Parsed operation or None if the row is invalid
        """
        try:
            date = datetime.strptime(row["Fecha"], "%d/%m/%Y")
            operation_type = self._get_operation_type(row["Tipo"])
            
            if operation_type == OperationType.TRADE:
                return Trade(
                    date=date,
                    operation_type=operation_type,
                    description=row["Tipo"],
                    amount=float(row["Importe"]),
                    symbol=row["Especie"],
                    quantity=float(row["Cantidad"]),
                    price=float(row["Precio"]),
                    total_amount=float(row["Importe"]),
                    broker=self.broker_name,
                )
            elif operation_type == OperationType.MONETARY_FLOW:
                return MonetaryFlow(
                    date=date,
                    operation_type=operation_type,
                    description=row["Tipo"],
                    amount=float(row["Importe"]),
                    flow_type="IN" if float(row["Importe"]) > 0 else "OUT",
                    broker=self.broker_name,
                )
            elif operation_type == OperationType.SECURITY_FLOW:
                return SecurityFlow(
                    date=date,
                    operation_type=operation_type,
                    description=row["Tipo"],
                    amount=float(row["Importe"]),
                    symbol=row["Especie"],
                    quantity=float(row["Cantidad"]),
                    flow_type="IN" if float(row["Cantidad"]) > 0 else "OUT",
                    broker=self.broker_name,
                )
            elif operation_type == OperationType.MUTUAL_FUND:
                return MutualFund(
                    date=date,
                    operation_type=operation_type,
                    description=row["Tipo"],
                    amount=float(row["Importe"]),
                    fund_name=row["Especie"],
                    quantity=float(row["Cantidad"]),
                    nav=float(row["Precio"]),
                    total_amount=float(row["Importe"]),
                    broker=self.broker_name,
                )
            return None
        except Exception as e:
            logger.warning(f"Error parsing row: {str(e)}")
            return None

    def _get_operation_type(self, operation_type: str) -> OperationType:
        """Get the operation type from a string.
        
        Args:
            operation_type: String representation of the operation type
            
        Returns:
            OperationType enum value
        """
        operation_type = operation_type.upper()
        if "COMPRA" in operation_type or "VENTA" in operation_type:
            return OperationType.TRADE
        elif "TRANSFERENCIA" in operation_type:
            return OperationType.MONETARY_FLOW
        elif "DEPOSITO" in operation_type or "RETIRO" in operation_type:
            return OperationType.SECURITY_FLOW
        elif "FONDO" in operation_type:
            return OperationType.MUTUAL_FUND
        else:
            return OperationType.MONETARY_FLOW  # Default to monetary flow 