"""Example script demonstrating how to use the Pellegrini parser."""

from pathlib import Path

from broker_parser.brokers.pellegrini.parser import PellegriniParser


def main():
    """Run the example script."""
    # Initialize the parser
    parser = PellegriniParser()

    # Path to the input file
    input_file = Path("src/broker_parser/brokers/pellegrini/movimientos_Pellegrini.csv")

    # Parse the file
    operations = parser.parse_file(input_file)

    # Print summary
    print(f"\nParsed {len(operations)} operations from {input_file}")
    print("\nOperation Types:")
    operation_types = {}
    for op in operations:
        op_type = op.operation_type.value
        operation_types[op_type] = operation_types.get(op_type, 0) + 1
    for op_type, count in operation_types.items():
        print(f"- {op_type}: {count}")

    # Print a sample of the parsed operations
    print("\nSample Operations:")
    for op in operations[:5]:  # Show first 5 operations
        print(f"\n{op.__class__.__name__}:")
        for field, value in op.__dict__.items():
            print(f"  {field}: {value}")


if __name__ == "__main__":
    main() 