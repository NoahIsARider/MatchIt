# calculate_maximum.py
# Module for calculating maximum values from form submissions

import json
import os
from typing import Dict, List, Union, Tuple, Optional

# Data file paths
SUBMISSIONS_FILE = os.path.join('data', 'submissions.json')
FORMS_FILE = os.path.join('data', 'forms.json')


def load_data(file_path: str) -> List[Dict]:
    """
    Load data from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of dictionaries containing the data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return []


def is_numeric(value: str) -> bool:
    """
    Check if a value can be converted to a number
    
    Args:
        value: The value to check
        
    Returns:
        True if the value can be converted to a number, False otherwise
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def get_form_field_type(form_id: str, field_name: str) -> Optional[str]:
    """
    Get the type of a field in a form
    
    Args:
        form_id: ID of the form
        field_name: Name of the field
        
    Returns:
        Type of the field or None if not found
    """
    forms = load_data(FORMS_FILE)
    for form in forms:
        if form['id'] == form_id:
            for field in form['fields']:
                if field['name'] == field_name:
                    return field['type']
    return None


def calculate_maximum_for_field(form_id: str, field_name: str) -> Tuple[Optional[float], int, int]:
    """
    Calculate the maximum value for a specific field in a form's submissions
    
    Args:
        form_id: ID of the form
        field_name: Name of the field to calculate maximum for
        
    Returns:
        Tuple containing (maximum value or None if no numeric values found, 
                         count of numeric values used, 
                         count of non-numeric values skipped)
    """
    submissions = load_data(SUBMISSIONS_FILE)
    
    # Filter submissions for the specified form
    form_submissions = [s for s in submissions if s['form_id'] == form_id]
    
    if not form_submissions:
        return None, 0, 0
    
    # Check if the field is numeric type
    field_type = get_form_field_type(form_id, field_name)
    if field_type not in ['number', 'radio', 'select', 'checkbox']:
        return None, 0, 0
    
    numeric_values = []
    non_numeric_count = 0
    
    for submission in form_submissions:
        if field_name in submission['data']:
            value = submission['data'][field_name]
            
            # Handle different types of values
            if isinstance(value, list):  # For checkbox fields
                for item in value:
                    if is_numeric(item):
                        numeric_values.append(float(item))
                    else:
                        non_numeric_count += 1
            elif is_numeric(value):
                numeric_values.append(float(value))
            else:
                non_numeric_count += 1
    
    if not numeric_values:
        return None, 0, non_numeric_count
    
    maximum = max(numeric_values)
    return maximum, len(numeric_values), non_numeric_count


def calculate_all_field_maximums(form_id: str) -> Dict[str, Dict[str, Union[float, int, None]]]:
    """
    Calculate maximum values for all numeric fields in a form
    
    Args:
        form_id: ID of the form
        
    Returns:
        Dictionary with field names as keys and dictionaries containing maximum, 
        count of numeric values, and count of non-numeric values as values
    """
    forms = load_data(FORMS_FILE)
    form = next((f for f in forms if f['id'] == form_id), None)
    
    if not form:
        return {}
    
    results = {}
    
    for field in form['fields']:
        field_name = field['name']
        maximum, numeric_count, non_numeric_count = calculate_maximum_for_field(form_id, field_name)
        
        if maximum is not None:
            results[field_name] = {
                'maximum': maximum,
                'numeric_count': numeric_count,
                'non_numeric_count': non_numeric_count
            }
    
    return results