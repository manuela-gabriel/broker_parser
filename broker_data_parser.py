from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd
from enum import Enum
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OperationType(Enum):
    """Enumeration of possible financial operation types."""
    TRADE = "Trade"
    MONETARY_FLOW = "MonetaryFlow"
    SECURITY_FLOW = "SecurityFlow"
    MUTUAL_FUND = "MutualFund"

class FlowType(Enum):
    """Enumeration of possible monetary flow types."""
    MONETARY_DEPOSIT = "MonetaryDeposit"
    MONETARY_WITHDRAWAL = "MonetaryWithdrawal"
    FEE = "Fee"
    INTEREST_PAYMENT = "Interest Payment"
    TRANSFER_IN = "Transfer In"
    TRANSFER_OUT = "Transfer Out"
    OTHER = "Other"

@dataclass
class TradeOperation:
    """Data class representing a trade operation."""
    party_role: str  # "Purchase" or "Sale"
    agreement_date: str  # MM/DD/YYYY
    settlement_term: str  # "T" or "T+N"
    settlement_date: str  # MM/DD/YYYY
    exchange: str  # e.g., "BYMA"
    security_amount: float
    security_name: str
    net_payment_amount: float
    charge_1_name: Optional[str]
    charge_1_amount: Optional[float]
    charge_1_currency: Optional[str]

@dataclass
class MonetaryFlowOperation:
    """Data class representing a monetary flow operation."""
    flow_type: FlowType
    date: str  # MM/DD/YYYY
    asset_amount: float
    asset_name: str
    notes: str

@dataclass
class SecurityFlowOperation:
    """Data class representing a security flow operation."""
    flow_type: str  # "SecurityInflow" or "SecurityOutflow"
    date: str  # MM/DD/YYYY
    concept: str
    asset_amount: float
    asset_name: str
    gross_payment_amount: float
    notes: str

@dataclass
class MutualFundOperation:
    """Data class representing a mutual fund operation."""
    fund_operation_type: str  # "FundSubscription" or "FundRedemption"
    agreement_date: str  # MM/DD/YYYY
    settlement_term: str  # "T" or "T+N"
    settlement_date: str  # MM/DD/YYYY
    exchange: str
    security_amount: float
    security_name: str
    net_payment_amount: float
    currency: str

class BrokerDataParser:
    """Class for parsing and transforming broker data into structured formats."""
    
    def __init__(self):
        """Initialize the parser with default settings."""
        # Define possible column names for each field
        self.column_mapping = {
            'tipo_liquidacion': ['Tipo de Liquidación', 'Tipo de Liquidacion', 'Tipo de Liquidaci\xf3n', 'Tipo de LiquidaciÃ³n'],
            'fecha_concertacion': ['Fecha de Concertación', 'Fecha de Concertacion', 'Fecha de Concertaci\xf3n', 'Fecha de ConcertaciÃ³n'],
            'tipo_cuota': ['Tipo de Cuota'],
            'numero': ['Número', 'Numero', 'N\xfamero', 'NÃºmero'],
            'cuotapartes': ['Cuotapartes'],
            'valor_cuota': ['Valor Cuota'],
            'inversion_neta': ['Inversión Neta', 'Inversion Neta', 'Inversi\xf3n Neta', 'InversiÃ³n Neta']
        }
        
        # Store the actual column names found in the data
        self.actual_columns = {}

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find the actual column name from a list of possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
        raise ValueError(f"Could not find column with any of these names: {possible_names}")

    def _initialize_columns(self, df: pd.DataFrame):
        """Initialize the actual column names from the DataFrame."""
        for key, possible_names in self.column_mapping.items():
            self.actual_columns[key] = self._find_column(df, possible_names)
            logger.debug(f"Found column '{self.actual_columns[key]}' for {key}")

    def parse_row(self, row: pd.Series) -> Dict:
        """
        Parse a single row of broker data into a structured format.
        
        Args:
            row: A pandas Series containing the broker data row
            
        Returns:
            Dict containing the parsed operation data
            
        Raises:
            ValueError: If the operation type cannot be determined
        """
        try:
            # Skip empty rows or header rows
            tipo_liquidacion = row[self.actual_columns['tipo_liquidacion']]
            if pd.isna(tipo_liquidacion) or tipo_liquidacion == 'Fondo PELLEGRINI RENTA PESOS':
                logger.debug("Skipping header row")
                raise ValueError("Skipping header row")
                
            # Log the raw row data for debugging
            logger.debug(f"Processing row: {row.to_dict()}")
            
            # Parse the row
            return self._parse_pellegrini_mutual_fund(row)
                
        except Exception as e:
            logger.error(f"Error parsing row: {e}")
            raise

    def _parse_pellegrini_mutual_fund(self, row: pd.Series) -> Dict:
        """Parse a mutual fund operation in Pellegrini format."""
        try:
            # Clean and convert numeric values
            cuotapartes = self._clean_numeric_value(row[self.actual_columns['cuotapartes']])
            valor_cuota = self._clean_numeric_value(row[self.actual_columns['valor_cuota']])
            inversion_neta = self._clean_numeric_value(row[self.actual_columns['inversion_neta']])
            
            # Determine operation type
            operation_type = "FundRedemption" if row[self.actual_columns['tipo_liquidacion']] == "Rescate" else "FundSubscription"
            
            # Create the result dictionary
            result = {
                "operation_type": "MutualFund",
                "fund_operation_type": operation_type,
                "agreement_date": self._format_date(row[self.actual_columns['fecha_concertacion']]),
                "settlement_term": "T",
                "settlement_date": self._format_date(row[self.actual_columns['fecha_concertacion']]),
                "exchange": "Mercado de Fondos",
                "security_amount": abs(cuotapartes),
                "security_name": "PELLEGRINI RENTA PESOS",
                "net_payment_amount": abs(inversion_neta),
                "currency": "ARS",
                "tipo_cuota": str(row[self.actual_columns['tipo_cuota']]),
                "numero": str(row[self.actual_columns['numero']]),
                "valor_cuota": valor_cuota
            }
            
            logger.debug(f"Successfully parsed row: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in _parse_pellegrini_mutual_fund: {e}")
            raise

    def _clean_numeric_value(self, value: str) -> float:
        """Clean and convert numeric values from string format."""
        if pd.isna(value):
            return 0.0
            
        try:
            # Remove currency symbols, spaces, and convert comma to dot
            cleaned = str(value).replace('$', '').replace(' ', '').replace(',', '')
            return float(cleaned)
        except ValueError as e:
            logger.error(f"Error converting value '{value}' to float: {e}")
            return 0.0

    def _format_date(self, date_str: str) -> str:
        """Format date string to MM/DD/YYYY format."""
        if pd.isna(date_str):
            return ""
        try:
            # Handle dates in DD/MM/YYYY format
            date = datetime.strptime(date_str, "%d/%m/%Y")
            return date.strftime("%m/%d/%Y")
        except Exception as e:
            logger.error(f"Error formatting date '{date_str}': {e}")
            return ""

def transform_data(input_file: str, output_file: str) -> None:
    """
    Transform broker data from input file to structured format in output file.
    
    Args:
        input_file: Path to input file (Excel or CSV)
        output_file: Path to output file (Excel or CSV)
        
    Raises:
        ValueError: If input/output file format is not supported
    """
    try:
        logger.info(f"Reading input file: {input_file}")
        
        # Read input file
        if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
            df = pd.read_excel(input_file)
        elif input_file.endswith('.csv'):
            df = pd.read_csv(input_file, encoding='latin1')
        else:
            raise ValueError("Input file must be Excel (.xlsx/.xls) or CSV (.csv)")
        
        logger.info(f"Successfully read {len(df)} rows from input file")
        logger.info(f"Columns in input file: {df.columns.tolist()}")
        
        # Initialize parser and columns
        parser = BrokerDataParser()
        parser._initialize_columns(df)
        
        # Process each row
        parsed_data = []
        for index, row in df.iterrows():
            try:
                parsed_row = parser.parse_row(row)
                parsed_data.append(parsed_row)
                logger.info(f"Successfully processed row {index}")
            except ValueError as e:
                if str(e) != "Skipping header row":
                    logger.error(f"Error processing row {index}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing row {index}: {e}")
                continue
        
        if not parsed_data:
            raise ValueError("No valid data was parsed from the input file")
        
        logger.info(f"Successfully parsed {len(parsed_data)} rows")
        
        # Convert to DataFrame
        result_df = pd.DataFrame(parsed_data)
        
        # Save output
        logger.info(f"Saving results to {output_file}")
        if output_file.endswith('.xlsx'):
            result_df.to_excel(output_file, index=False)
        elif output_file.endswith('.csv'):
            result_df.to_csv(output_file, index=False)
        else:
            raise ValueError("Output file must be Excel (.xlsx) or CSV (.csv)")
            
        logger.info("Successfully saved output file")
            
    except Exception as e:
        logger.error(f"Error in transform_data: {e}")
        raise

if __name__ == "__main__":
    input_file = "movimientos_Pellegrini.csv"
    output_file = "parsed_broker_data.xlsx"
    
    print(f"Processing input file: {input_file}")
    transform_data(input_file, output_file)
    print(f"Results saved to: {output_file}")
    
    # Read and display the results
    result_df = pd.read_excel(output_file)
    print("\nParsed Data Summary:")
    print("=" * 80)
    print(f"Total operations processed: {len(result_df)}")
    print("\nOperation Types:")
    print(result_df['operation_type'].value_counts())
    print("\nSample of parsed data:")
    print(result_df.head()) 