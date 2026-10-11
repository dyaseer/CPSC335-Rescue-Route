"""JSON loading and input validation (data and matching lead)."""
import json

def load_json(file_path):
    """Return a list of record dictionaries from a JSON file."""
    # TODO: Open the file, read JSON, and reject a non-list or non-record input.
    with open(file_path, 'r') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Loaded data is not a list")
    if not all(isinstance(record, dict) for record in data):
        raise ValueError("Not all records are dictionaries")
    return data


def validate_data(donations, recipients, volunteers):
    """Raise ValueError for invalid input; return None when all records are valid."""
    # TODO: Check required fields and their types using the sample JSON schema.
    if not isinstance(donations, list) or not isinstance(recipients, list) or not isinstance(volunteers, list):
        raise ValueError("Input parameters must be lists") 
    # TODO: Detect duplicate IDs within each entity list.
    if len(donations) != len(set(record.get("id") for record in donations)):
        raise ValueError("Duplicate IDs found in donations")
    if len(recipients) != len(set(record.get("id") for record in recipients)):
        raise ValueError("Duplicate IDs found in recipients")
    if len(volunteers) != len(set(record.get("id") for record in volunteers)):
        raise ValueError("Duplicate IDs found in volunteers")
    # TODO: Validate food types, quantities, capacities, and pickup limits.
    # TODO: Validate times and availability ranges; allow empty lists.
    raise NotImplementedError
