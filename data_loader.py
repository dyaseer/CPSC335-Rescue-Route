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
    """Raise ValueError for invalid records; allow empty lists.

    Quantities and capacities are whole units. Times are whole minutes from
    simulation start. Expired donations are valid records, rejected by matching.
    """
    # Step 1: List the required fields and types for each kind of record.
    donation_fields = {
        "donation_id": str, "donor_name": str, "food_type": str,
        "quantity": int, "expiry_time": int, "pickup_area": str, "ready_time": int,
    }
    recipient_fields = {
        "recipient_id": str, "organization_name": str,
        "accepted_food_types": list, "capacity": int, "area": str, "closing_time": int,
    }
    volunteer_fields = {
        "volunteer_id": str, "vehicle_capacity": int, "area": str,
        "available_from": int, "available_until": int, "max_pickups": int,
    }

    # Step 2: Check each list, its records, and its IDs.
    groups = [
        (donations, "donation_id", donation_fields),
        (recipients, "recipient_id", recipient_fields),
        (volunteers, "volunteer_id", volunteer_fields),
    ]
    for records, id_field, fields in groups:
        if not isinstance(records, list):
            raise ValueError(f"{id_field} records must be a list")
        seen_ids = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Each record must be a dictionary")
            for field, field_type in fields.items():
                if field not in record or type(record[field]) is not field_type:
                    raise ValueError(f"{field} is required and must be {field_type.__name__}")
                if field_type is str and not record[field].strip():
                    raise ValueError(f"{field} cannot be blank")
                if field_type is int and record[field] < 0:
                    raise ValueError(f"{field} cannot be negative")
            record_id = record[id_field]
            if record_id in seen_ids:
                raise ValueError(f"Duplicate {id_field}: {record_id}")
            seen_ids.add(record_id)

    # Step 3: Check rules that depend on the kind of record.
    for donation in donations:
        if donation["quantity"] == 0:
            raise ValueError("Donation quantity must be positive")
    for recipient in recipients:
        for food in recipient["accepted_food_types"]:
            if not isinstance(food, str) or not food.strip():
                raise ValueError("Accepted food types must be nonblank strings")
    for volunteer in volunteers:
        if volunteer["available_from"] > volunteer["available_until"]:
            raise ValueError("Volunteer availability starts after it ends")
