"""Result metrics (product and quality lead)."""


def calculate_metrics(donations, recipients, volunteers, assignments):
    """Return a metrics dictionary using original inputs and scheduler results.
    
    Use the original input capacities and pickup limits, before scheduling.
    Volunteer utilization measures food rescued against total allowed pickup capacity.
    Keep in mind that any urgency rates, or any rates that are returned, are returned in percentage form,
    eg. 0% through 100% = 0 through 100"""

    #Handling empty inputs
    donations = donations or []
    recipients = recipients or []
    volunteers = volunteers or []
    assignments = assignments or []
    
    #Count donations received, assigned, and unassigned.
    donation_by_id = {
        donation["donation_id"]: donation
        for donation in donations
    }

    assigned_ids = {
        assignment["donation_id"]
                for assignment in assignments
                if (
                    assignment.get("status") == "assigned"
                    and assignment.get("donation_id") in donation_by_id
                )
    }

    donations_received = len(donations)
    donations_assigned = len(assigned_ids)
    donations_unassigned = donations_received - donations_assigned


    #Calculate food quantity rescued and at risk.
    food_quantity_rescued = sum(
        donation_by_id[donation_id]["quantity"]
        for donation_id in assigned_ids
    )
    food_quantity_at_risk = sum(
        donation["quantity"]
        for donation in donations
        if donation["donation_id"] not in assigned_ids
    )

    #Calculate urgent rescue rate using the team's agreed urgent group.
    if donations:
        earliest_expiry = min(
            donation["expiry_time"] for donation in donations
        )
        urgent_donations = [
            donation for donation in donations
            if donation["expiry_time"] == earliest_expiry
        ]
        urgent_assigned = sum(
            1 for donation in urgent_donations
            if donation["donation_id"] in assigned_ids
        )
        urgent_rescue_rate = (
            100.0 * urgent_assigned / len(urgent_donations)
        )
    else:
        urgent_rescue_rate = 0.0

    #Calculate recipient and volunteer capacity utilization using the
    # agreed denominators. Handle empty input and division by zero.
    # Use these comparison keys: donations_assigned, food_quantity_rescued,
    # and urgent_rescue_rate (also used by algorithms.compare_strategies).
    total_recipient_capacity = sum(
        recipient["capacity"] for recipient in recipients
    )
    # Each volunteer can carry their vehicle capacity on each allowed pickup.
    total_volunteer_capacity = sum(
        volunteer["vehicle_capacity"] * volunteer["max_pickups"]
        for volunteer in volunteers
    )

    recipient_capacity_utilization = (
        100.0 * food_quantity_rescued / total_recipient_capacity
        if total_recipient_capacity > 0
        else 0.0
    )
    volunteer_capacity_utilization = (
        100.0 * food_quantity_rescued / total_volunteer_capacity
        if total_volunteer_capacity > 0
        else 0.0
    )

    return {
        "donations_received": donations_received,
        "donations_assigned": donations_assigned,
        "donations_unassigned": donations_unassigned,
        "food_quantity_rescued": food_quantity_rescued,
        "food_quantity_at_risk": food_quantity_at_risk,
        "urgent_rescue_rate": urgent_rescue_rate,
        "recipient_capacity_utilization": recipient_capacity_utilization,
        "volunteer_capacity_utilization": volunteer_capacity_utilization,
    }

