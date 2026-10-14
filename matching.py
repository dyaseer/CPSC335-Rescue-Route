
"""Feasibility checks and resource updates for RescueRoute."""


def check_match(donation, recipient, volunteer):
    """Return (feasible, scheduled_time, reason) without changing records."""

    # Check food compatibility and location.
    if donation["food_type"] not in recipient["accepted_food_types"]:
        return False, None, (
            f"{recipient['organization_name']} does not accept "
            f"{donation['food_type'].replace('_', ' ')}"
        )

    if donation["pickup_area"] != recipient["area"]:
        return False, None, (
            f"{recipient['organization_name']} is in a different area"
        )

    if donation["pickup_area"] != volunteer["area"]:
        return False, None, (
            f"volunteer {volunteer['volunteer_id']} is in a different area"
        )

    # Check remaining recipient capacity and vehicle capacity.
    if donation["quantity"] > recipient["capacity"]:
        return False, None, (
            f"{recipient['organization_name']} has insufficient "
            f"remaining capacity ({recipient['capacity']} units available, "
            f"{donation['quantity']} required)"
        )

    if donation["quantity"] > volunteer["vehicle_capacity"]:
        return False, None, (
            f"volunteer {volunteer['volunteer_id']} cannot carry "
            f"{donation['quantity']} units "
            f"(vehicle capacity: {volunteer['vehicle_capacity']} units)"
        )

    if volunteer["max_pickups"] <= 0:
        return False, None, (
            f"volunteer {volunteer['volunteer_id']} has no pickups remaining"
        )

    # Find the earliest possible pickup time.
    scheduled_time = max(
        donation["ready_time"],
        volunteer["available_from"]
    )

    # Check all deadlines.
    if scheduled_time >= donation["expiry_time"]:
        return False, None, (
            f"the donation expires at minute {donation['expiry_time']}, "
            f"before pickup can occur at minute {scheduled_time}"
        )

    if scheduled_time >= recipient["closing_time"]:
        return False, None, (
            f"{recipient['organization_name']} closes at minute "
            f"{recipient['closing_time']}, before pickup can occur"
        )

    if scheduled_time >= volunteer["available_until"]:
        return False, None, (
            f"volunteer {volunteer['volunteer_id']} is unavailable "
            f"by pickup time {scheduled_time}"
        )

    # Explain why this match is feasible.
    remaining_minutes = donation["expiry_time"] - scheduled_time
    food_type = donation["food_type"].replace("_", " ")

    reason = (
        f"it expires in {remaining_minutes} minutes after the scheduled "
        f"pickup; {recipient['organization_name']} accepts {food_type}; "
        f"{recipient['capacity']} units of recipient capacity remain "
        f"and {donation['quantity']} are required; and volunteer "
        f"{volunteer['volunteer_id']} can carry the quantity and "
        f"has pickups remaining"
    )

    return True, scheduled_time, reason


def update_resources(assignment, donation, recipients, volunteers):
    """Update remaining recipient capacity and volunteer availability."""

    for recipient in recipients:
        if recipient["recipient_id"] == assignment["recipient_id"]:
            recipient["capacity"] -= donation["quantity"]
            break

    for volunteer in volunteers:
        if volunteer["volunteer_id"] == assignment["volunteer_id"]:
            volunteer["max_pickups"] -= 1
            volunteer["available_from"] = assignment["scheduled_time"]
            break
