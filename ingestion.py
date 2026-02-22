import pandas as pd
import os

def load_file(file):
    """
    Loads a file (CSV or Excel) into a pandas DataFrame.
    
    Args:
        file: A file-like object or path to the file.
        
    Returns:
        pd.DataFrame: The loaded data.
        
    Raises:
        ValueError: If the file type is not supported.
    """
    try:
        # Determine file extension if it's a path, otherwise trust the uploaded file object
        if isinstance(file, str):
             filename = file
        else:
             filename = file.name
             
        if filename.endswith('.csv'):
            return pd.read_csv(file)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            return pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
    except Exception as e:
        raise e
