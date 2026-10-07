"""JSON loading and input validation (data and matching lead)."""


def load_json(file_path):
    """Return a list of record dictionaries from a JSON file."""
    # TODO: Open the file, read JSON, and reject a non-list or non-record input.
    raise NotImplementedError


def validate_data(donations, recipients, volunteers):
    """Raise ValueError for invalid input; return None when all records are valid."""
    # TODO: Check required fields and their types using the sample JSON schema.
    # TODO: Detect duplicate IDs within each entity list.
    # TODO: Validate food types, quantities, capacities, and pickup limits.
    # TODO: Validate times and availability ranges; allow empty lists.
    raise NotImplementedError
