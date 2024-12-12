import csv
import os
import pandas as pd
from typing import Dict, List, Any

def detect_sql_type(values: List[Any]) -> str:
    """
    Detect the SQL data type based on column values.
    """
    # Remove None and empty values
    values = [v for v in values if v is not None and str(v).strip() != '']
    
    if not values:
        return 'TEXT'
    
    # Try to convert to integer
    try:
        all(int(str(x)) for x in values)
        max_val = max(int(str(x)) for x in values)
        min_val = min(int(str(x)) for x in values)
        
        if min_val >= -32768 and max_val <= 32767:
            return 'INTEGER'
        elif min_val >= -2147483648 and max_val <= 2147483647:
            return 'INTEGER'
        else:
            return 'BIGINT'
    except ValueError:
        pass
    
    # Try to convert to float
    try:
        all(float(str(x)) for x in values)
        return 'DECIMAL'
    except ValueError:
        pass
    
    # Check if boolean
    bool_values = {'true', 'false', '1', '0', 'yes', 'no'}
    if all(str(x).lower() in bool_values for x in values):
        return 'BOOLEAN'
    
    # Check string length
    max_length = max(len(str(x)) for x in values)
    if max_length <= 255:
        return f'VARCHAR({max_length})'
    
    return 'TEXT'

def csv_to_sql(csv_path: str, table_name: str = None) -> str:
    """
    Convert CSV file to SQL statements.
    """
    # Read CSV file using pandas
    df = pd.read_csv(csv_path)
    
    # If table name not provided, use CSV filename
    if table_name is None:
        table_name = os.path.splitext(os.path.basename(csv_path))[0]
    
    # Clean column names (remove spaces and special characters)
    df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
    
    # Detect column types
    column_types = {}
    for column in df.columns:
        column_types[column] = detect_sql_type(df[column].tolist())
    
    # Generate CREATE TABLE statement
    create_statement = f"CREATE TABLE {table_name} (\n"
    columns = [f"    {col} {column_types[col]}" for col in df.columns]
    create_statement += ",\n".join(columns)
    create_statement += "\n);\n\n"
    
    # Generate INSERT statements
    insert_statements = []
    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                values.append('NULL')
            elif column_types[col].startswith('VARCHAR') or column_types[col].startswith('TEXT'):
                values.append(f"'{str(value).replace(chr(39), chr(39)+chr(39))}'")
            else:
                values.append(str(value))
        
        insert_statement = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(values)});"
        insert_statements.append(insert_statement)
    
    return create_statement + "\n".join(insert_statements)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert CSV file to SQL statements')
    parser.add_argument('csv_path', help='Path to the CSV file')
    parser.add_argument('--table-name', help='Name of the SQL table (optional)')
    parser.add_argument('--output', help='Output SQL file path (optional)')
    
    args = parser.parse_args()
    
    # Generate SQL statements
    sql_statements = csv_to_sql(args.csv_path, args.table_name)
    
    # Determine output path
    output_path = args.output
    if output_path is None:
        output_path = os.path.splitext(args.csv_path)[0] + '.sql'
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(sql_statements)
    
    print(f"SQL file generated successfully: {output_path}")

if __name__ == '__main__':
    print()
    main()