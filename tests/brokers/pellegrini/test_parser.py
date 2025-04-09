import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_csv_reading():
    """Test reading the CSV file and display its contents."""
    try:
        # Read the CSV file
        df = pd.read_csv('movimientos_Pellegrini.csv', encoding='latin1')
        
        # Display basic information
        logger.info(f"Number of rows: {len(df)}")
        
        # Display all column names
        logger.info("\nAll column names:")
        for col in df.columns:
            logger.info(f"Column: '{col}'")
        
        # Display first few rows
        logger.info("\nFirst 5 rows:")
        print(df.head())
        
        # Check for empty values
        logger.info("\nEmpty values per column:")
        print(df.isna().sum())
        
        # Try to access the column with the accent
        try:
            liquidacion_col = df['Tipo de Liquidación']
            logger.info("\nUnique values in 'Tipo de Liquidación':")
            print(liquidacion_col.unique())
        except KeyError:
            # Try alternative column names
            possible_names = [
                'Tipo de Liquidación',
                'Tipo de Liquidacion',
                'Tipo de Liquidaci\xf3n',
                'Tipo de LiquidaciÃ³n'
            ]
            logger.info("\nTrying alternative column names:")
            for name in possible_names:
                if name in df.columns:
                    logger.info(f"Found column: '{name}'")
                    print(df[name].unique())
        
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")

if __name__ == "__main__":
    test_csv_reading() 