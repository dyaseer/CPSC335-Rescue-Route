"""Feasibility checks and resource updates (data and matching lead).

These functions can be passed directly to algorithms.schedule_fifo.
Use the existing lists of dictionaries; no custom data classes are needed.
Times are minutes from the simulation start. Agree on travel/service time
and area compatibility before implementing the checks and updates.
"""


def check_match(donation, recipient, volunteer):
    """Return (feasible, scheduled_time, reason) without changing any records.

    For rejection, return (False, None, a human-readable reason).
    For a match, return (True, scheduled_time, a human-readable reason).

    Inputs must already be validated. This simple model requires matching areas
    and uses no travel or service time. Pickup must happen before expiry,
    closing time, and the end of volunteer availability.
    """
    # Step 1: Check food type and location.
    if donation["food_type"] not in recipient["accepted_food_types"]:
        return False, None, "Recipient does not accept this food type"
    if donation["pickup_area"] != recipient["area"]:
        return False, None, "Recipient is in a different area"
    if donation["pickup_area"] != volunteer["area"]:
        return False, None, "Volunteer is in a different area"

    # Step 2: Check space and remaining pickups.
    if donation["quantity"] > recipient["capacity"]:
        return False, None, "Insufficient recipient capacity"
    if donation["quantity"] > volunteer["vehicle_capacity"]:
        return False, None, "Insufficient vehicle capacity"
    if volunteer["max_pickups"] <= 0:
        return False, None, "Volunteer has no pickups remaining"

    # Step 3: Find the earliest pickup time and check the deadlines.
    scheduled_time = max(donation["ready_time"], volunteer["available_from"])
    if scheduled_time >= donation["expiry_time"]:
        return False, None, "Donation expires before it can be picked up"
    if scheduled_time >= recipient["closing_time"]:
        return False, None, "Recipient is closed at pickup time"
    if scheduled_time >= volunteer["available_until"]:
        return False, None, "Volunteer is unavailable at pickup time"

    return True, scheduled_time, (
        "Food type and areas match; enough recipient and vehicle capacity is "
        "available; volunteer has pickups remaining; pickup is before expiry, "
        "recipient closing, and the end of volunteer availability"
    )


def update_resources(assignment, donation, recipients, volunteers):
    """Update the assigned recipient and volunteer in the scheduler's copies.

    Return None. Called only after an assignment with status 'assigned'.
    """
    # TODO: Find the recipient and volunteer using the IDs in assignment.
    # TODO: Subtract donation quantity from recipient capacity.
    # TODO: Decrease volunteer max_pickups and update available_from using
    # the agreed time model. Vehicle capacity remains a per-pickup limit.
    raise NotImplementedError
