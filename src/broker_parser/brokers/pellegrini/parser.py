"""Parser for Pellegrini broker data files."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

    COLUMN_MAPPING = {
        "tipo": "Tipo de Liquidación",
        "fecha": "Fecha de Concertación",
        "tipo_cuota": "Tipo de Cuota",
        "numero": "Número",
        "cantidad": "Cuotapartes",
        "precio": "Valor Cuota",
        "importe": "Inversión Neta",
    }

    OPERATION_TYPE_MAPPING = {
        "Rescate": "FundRedemption",
        "Suscripción": "FundSubscription",
    }

    def __init__(self):
        """Initialize the Pellegrini parser."""
        super().__init__("Pellegrini")
        self._ticker_mappings: Dict[str, str] = {}
        self._load_ticker_mappings()
        self._base_fund_name: str = ""

    def _load_ticker_mappings(self) -> None:
        """Load ticker mappings from Especies.csv file.
        
        The file should contain:
        - 'Instrumento' column: Name of the broker/instrument
        - 'Ticker' column: Corresponding ticker symbol
        """
        try:
            # Get the path to the species file
            species_file = Path(__file__).parent.parent.parent.parent / "Especies.csv"
            
            if not species_file.exists():
                # Try in the root directory
                species_file = Path("/workspaces/Cursor/Especies.csv")
                if not species_file.exists():
                    logger.warning(f"Species file not found at {species_file}")
                    return
                
            # Read the CSV file and store it
            self._especies_df = pd.read_csv(species_file)
            
            # Verify required columns exist
            required_columns = ["Instrumento", "Ticker"]
            if not all(col in self._especies_df.columns for col in required_columns):
                logger.error(f"Required columns not found in {species_file}: {required_columns}")
                return
                
            logger.info(f"Loaded Especies file with {len(self._especies_df)} entries")
            
        except Exception as e:
            logger.error(f"Error loading ticker mappings: {str(e)}")

    def _extract_fund_name(self, df: pd.DataFrame) -> str:
        """Extract the base fund name from the second row of the DataFrame.
        
        Args:
            df: DataFrame containing the file contents
            
        Returns:
            Base fund name without class information
        """
        try:
            # Get the second row (index 1)
            second_row = df.iloc[0]
            
            # Get the fund name from the first column
            fund_name = second_row.iloc[0]
            print(f"Raw fund name from second row: '{fund_name}'")
            
            # Clean up the fund name
            fund_name = fund_name.strip()
            
            # Remove the word "Fondo" if present
            if "Fondo" in fund_name:
                fund_name = fund_name.replace("Fondo", "").strip()
            
            print(f"Cleaned fund name: '{fund_name}'")
            return fund_name
            
        except Exception as e:
            logger.error(f"Error extracting fund name: {str(e)}")
            return "Pellegrini"  # Default fallback

    def _get_ticker_for_fund(self, fund_name: str, share_class: str) -> str:
        """Get the ticker for a fund name and share class combination.
        
        Args:
            fund_name: Base fund name (e.g. "PELLEGRINI RENTA FIJA")
            share_class: Share class (e.g. "A" or "B")
            
        Returns:
            Corresponding ticker from Especies.csv
        """
        try:
            # Clean up the fund name and share class
            fund_name = fund_name.strip().lower()
            share_class = f"clase {share_class.strip().lower()}"
            print(f"Fund name: {fund_name}, Share class: {share_class}")
            
            # Remove "pellegrini" if it appears twice
            if fund_name.startswith("pellegrini"):
                fund_name = fund_name.replace("pellegrini", "", 1).strip()
                print(fund_name)
            
            # Filter the Especies DataFrame to find matching instruments
            # Convert Instrumento column to lowercase for case-insensitive comparison
            df = self._especies_df.copy()
            df['Instrumento_lower'] = df['Instrumento'].str.lower()
            
            # Filter rows where Instrumento contains both the fund name and share class
            mask = (
                df['Instrumento_lower'].str.contains(fund_name, na=False) & 
                df['Instrumento_lower'].str.contains(share_class, na=False)
            )
            matches = df[mask]
            
            if len(matches) == 1:
                # If we found exactly one match, use its ticker
                ticker = matches['Ticker'].iloc[0]
                logger.info(f"Found ticker {ticker} for {fund_name} {share_class}")
                return ticker
            elif len(matches) > 1:
                # If we found multiple matches, log a warning and use the first one
                logger.warning(f"Found multiple matches for {fund_name} {share_class}: {matches['Ticker'].tolist()}")
                return matches['Ticker'].iloc[0]
            else:
                # If no match found, log a warning and return the original name
                logger.warning(f"No ticker found for {fund_name} {share_class}")
                return f"pellegrini {fund_name} - {share_class}"
                
        except Exception as e:
            logger.error(f"Error finding ticker: {str(e)}")
            return f"pellegrini {fund_name} - {share_class}"

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
        file_path = Path(file_path)
        self._validate_file_exists(file_path)
        self._validate_file_extension(file_path)

        try:
            # Read CSV file with explicit encoding
            df = pd.read_csv(file_path, encoding='utf-8')
            
            print("\nExtracting fund name from file...")
            # Extract base fund name from the file
            self._base_fund_name = self._extract_fund_name(df)
            print(f"Base fund name extracted: '{self._base_fund_name}'")
            logger.info(f"Processing operations for fund: {self._base_fund_name}")
            
            # Parse each row into operations
            operations = []
            for idx, row in df.iterrows():
                try:
                    print(f"\nProcessing row {idx}...")
                    operation = self._parse_row(row)
                    if operation:
                        operations.append(operation)
                except Exception as e:
                    logger.error(f"Error parsing row {idx}: {str(e)}")
                    logger.error(f"Row content: {row.to_dict()}")
                    continue
            
            logger.info(f"Successfully parsed {len(operations)} operations from {file_path}")
            return operations
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise ValueError(f"Error parsing file: {str(e)}")

    def _parse_row(self, row: pd.Series) -> Optional[BrokerOperation]:
        """Parse a single row into an operation.
        
        Args:
            row: Row to parse
            
        Returns:
            Parsed operation or None if the row is invalid
        """
        try:
            # Skip rows with NaN values
            if pd.isna(row["Fecha de Concertación"]):
                return None
                
            # Parse date
            date = datetime.strptime(row["Fecha de Concertación"], "%d/%m/%Y")
            
            # Get share class and find corresponding ticker
            share_class = row["Tipo de Cuota"]
            
            # Print operation details
            print(f"  Operation type: {row['Tipo de Liquidación']}")
            print(f"  Fund name: '{self._base_fund_name}'")
            print(f"  Share class: '{share_class}'")
            
            ticker = self._get_ticker_for_fund(self._base_fund_name, share_class)
            print(f"  Found ticker: {ticker}")
            
            # Determine operation type
            operation_type = self._get_operation_type(row["Tipo de Liquidación"])
            
            # Clean numeric values
            cantidad = self._clean_numeric(row["Cuotapartes"])
            precio = self._clean_numeric(row["Valor Cuota"])
            importe = self._clean_numeric(row["Inversión Neta"])
            
            # Create MutualFund operation
            fund = MutualFund(
                date=date,
                operation_type=operation_type,
                description=row["Tipo de Liquidación"],
                amount=abs(importe),
                fund_name=ticker,  # Use the ticker as fund_name
                quantity=abs(cantidad),
                nav=precio,
                total_amount=abs(importe),
                broker=self.broker_name,
            )
            return fund
            
        except Exception as e:
            logger.error(f"Error in _parse_row: {str(e)}")
            logger.error(f"Row content: {row.to_dict()}")
            return None

    def write_to_excel(self, operations: List[BrokerOperation], output_path: str | Path) -> None:
        """Write parsed operations to an Excel file.
        
        Args:
            operations: List of parsed operations
            output_path: Path where to save the Excel file
            
        Raises:
            ValueError: If the operations list is empty
        """
        if not operations:
            raise ValueError("No operations to write to Excel file")
            
        try:
            # Convert operations to DataFrame
            data = []
            for op in operations:
                if isinstance(op, MutualFund):
                    data.append({
                        "fund_operation_type": self.OPERATION_TYPE_MAPPING.get(op.description, op.description),
                        "agreement_date": op.date.strftime("%m/%d/%Y"),
                        "settlement_term": "T",  # Since we don't have settlement date, assume T
                        "settlement_date": op.date.strftime("%m/%d/%Y"),  # Same as agreement date
                        "exchange": "Mercado de Fondos",
                        "security_amount": op.quantity,
                        "security_name": op.fund_name,  # Use the ticker stored in fund_name
                        "net_payment_amount": op.total_amount,
                        "currency": op.currency
                    })
            
            df = pd.DataFrame(data)
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write to Excel with formatting
                df.to_excel(writer, sheet_name='Operations', index=False)
                
                # Get the worksheet
                worksheet = writer.sheets['Operations']
                
                # Format column widths
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
                
                # Format header
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    cell.alignment = cell.alignment.copy(horizontal='center')
            
            logger.info(f"Successfully wrote {len(operations)} operations to {output_path}")
            
        except Exception as e:
            logger.error(f"Error writing to Excel file {output_path}: {str(e)}")
            raise ValueError(f"Error writing to Excel file: {str(e)}")

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
            df = pd.read_csv(file_path, encoding="latin1", nrows=1)
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
        required_columns = list(self.COLUMN_MAPPING.values())
        return all(col in df.columns for col in required_columns)

    def _get_operation_type(self, operation_type: str) -> OperationType:
        """Get the operation type from a string.
        
        Args:
            operation_type: String representation of the operation type
            
        Returns:
            OperationType enum value
        """
        # For Pellegrini, all operations are mutual fund operations
        return OperationType.MUTUAL_FUND

    def _clean_numeric(self, value: str | float) -> float:
        """Clean and convert numeric values from string format.
        
        Args:
            value: String or float value to clean and convert
            
        Returns:
            Cleaned float value
        """
        try:
            if isinstance(value, float):
                return value
                
            # Remove currency symbols, commas, and spaces
            cleaned = str(value).replace("$", "").replace(",", "").replace(" ", "")
            
            # Handle negative values
            is_negative = "-" in cleaned
            cleaned = cleaned.replace("-", "")
            
            result = float(cleaned)
            return -result if is_negative else result
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error cleaning numeric value '{value}': {str(e)}")
            return 0.0 