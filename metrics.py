"""Result metrics (product and quality lead)."""


def calculate_metrics(donations, recipients, volunteers, assignments):
    """Return a metrics dictionary using original inputs and scheduler results."""
    # TODO: Count donations received, assigned, and unassigned.
    donation_by_id = {
        donation["donation_id"]: donation
        for donation in donations
    }

    assigned_ids = {
        assignment.get("donation_id")
        for assignment in assignments
        if assignment.get("status") == "assigned"
    }

    assigned_ids.intersection_update(donation_by_id)
    donations_received = len(donations)
    donations_assigned = len(assigned_ids)
    donations_unassigned = donations_received - donations_assigned

    
    # TODO: Calculate food quantity rescued and at risk.
    # TODO: Calculate urgent rescue rate using the team's agreed urgent group.
    # TODO: Calculate recipient and volunteer capacity utilization using the
    # agreed denominators. Handle empty input and division by zero.
    # Use these comparison keys: donations_assigned, food_quantity_rescued,
    # and urgent_rescue_rate (also used by algorithms.compare_strategies).
    raise NotImplementedError
