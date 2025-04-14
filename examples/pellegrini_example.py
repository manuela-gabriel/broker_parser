"""Example script for parsing Pellegrini broker files."""

import logging
from pathlib import Path

from broker_parser.brokers.pellegrini.parser import PellegriniParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    """Run the Pellegrini parser example."""
    # Initialize parser
    parser = PellegriniParser()
    
    # Use the example file
    file_path = Path("src/broker_parser/brokers/pellegrini/Movimiento Fondos Pellegrini.csv")
    print(f"\nProcessing file: {file_path}")
    
    try:
        # Parse the file
        operations = parser.parse_file(file_path)
        
        # Create output file name
        output_path = file_path.parent / f"{file_path.stem}_parsed.xlsx"
        
        # Write to Excel
        parser.write_to_excel(operations, output_path)
        
        # Print summary
        print(f"\nParsed {len(operations)} operations from {file_path}")
        print(f"Operations written to {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return

if __name__ == "__main__":
    main() 