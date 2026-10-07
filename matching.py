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
    """
    # TODO: Check accepted food types and area compatibility.
    # TODO: Check remaining recipient capacity, vehicle capacity, and max_pickups.
    # TODO: Check ready time, expiry, recipient closing time, and volunteer hours.
    raise NotImplementedError


def update_resources(assignment, donation, recipients, volunteers):
    """Update the assigned recipient and volunteer in the scheduler's copies.

    Return None. Called only after an assignment with status 'assigned'.
    """
    # TODO: Find the recipient and volunteer using the IDs in assignment.
    # TODO: Subtract donation quantity from recipient capacity.
    # TODO: Decrease volunteer max_pickups and update available_from using
    # the agreed time model. Vehicle capacity remains a per-pickup limit.
    raise NotImplementedError
