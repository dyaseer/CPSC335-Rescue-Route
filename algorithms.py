
"""FIFO baseline and urgency-first greedy scheduling."""

from copy import deepcopy


def schedule_fifo(donations, recipients, volunteers, check_match, update_resources):
    """Return one assignment or rejection per donation in input order."""

    donations = deepcopy(donations)
    recipients = deepcopy(recipients)
    volunteers = deepcopy(volunteers)
    assignments = []

    for donation in donations:
        assignment = {
            "donation_id": donation["donation_id"],
            "recipient_id": None,
            "volunteer_id": None,
            "scheduled_time": None,
            "decision_reason": "No recipients or volunteers available.",
            "status": "unassigned",
        }

        rejection_reasons = []

        for recipient in recipients:
            for volunteer in volunteers:
                feasible, scheduled_time, reason = check_match(
                    donation, recipient, volunteer
                )

                if feasible:
                    assignment.update({
                        "recipient_id": recipient["recipient_id"],
                        "volunteer_id": volunteer["volunteer_id"],
                        "scheduled_time": scheduled_time,
                        "decision_reason": reason,
                        "status": "assigned",
                    })
                    break

                rejection_reasons.append(reason)

            if assignment["status"] == "assigned":
                break

        if assignment["status"] == "assigned":
            update_resources(assignment, donation, recipients, volunteers)

        elif rejection_reasons:
            unique_reasons = list(dict.fromkeys(rejection_reasons))
            assignment["decision_reason"] = (
                "No feasible match could be found. Reasons identified "
                "during recipient and volunteer checks: "
                + "; ".join(unique_reasons)
            )

        assignments.append(assignment)

    return assignments


def greedy_priority(donation):
    """Earlier expiry, then larger quantity, then earlier ready time."""
    return (
        donation["expiry_time"],
        -donation["quantity"],
        donation["ready_time"],
    )


def _describe_priority(previous, current):
    """Explain why previous ranks ahead of current under the greedy rule."""

    if previous["expiry_time"] < current["expiry_time"]:
        difference = current["expiry_time"] - previous["expiry_time"]
        return (
            f"{previous['donation_id']} had less remaining shelf life "
            f"than {current['donation_id']} "
            f"(its expiry was {difference} minutes earlier)"
        )

    if previous["quantity"] > current["quantity"]:
        return (
            f"their expiry times were tied, but "
            f"{previous['donation_id']} had the larger quantity"
        )

    if previous["ready_time"] < current["ready_time"]:
        return (
            f"their expiry times and quantities were tied, but "
            f"{previous['donation_id']} had the earlier ready time"
        )

    return (
        f"{previous['donation_id']} appeared first in the input, "
        f"and their greedy priority values were tied"
    )


def schedule_greedy(
    donations, recipients, volunteers, check_match, update_resources
):
    """Schedule by urgency and record why each donation was considered."""

    ordered_donations = sorted(donations, key=greedy_priority)

    assignments = schedule_fifo(
        ordered_donations,
        recipients,
        volunteers,
        check_match,
        update_resources,
    )

    # Record why each donation was considered at its position in the order.
    for index, donation in enumerate(ordered_donations):
        if index == 0:
            reason = (
                f"{donation['donation_id']} was considered first because "
                f"it had the highest priority under the urgency-first "
                f"greedy rule."
            )
        else:
            previous = ordered_donations[index - 1]
            explanation = _describe_priority(previous, donation)
            reason = (
                f"Donation {donation['donation_id']} was considered after "
                f"{previous['donation_id']} because {explanation}."
            )

        assignments[index]["scheduling_reason"] = reason

    return assignments


def compare_strategies(fifo_metrics, greedy_metrics):
    """Return greedy-minus-FIFO differences for the comparison metrics."""

    differences = {}

    for metric in (
        "donations_assigned",
        "food_quantity_rescued",
        "urgent_rescue_rate",
    ):
        differences[metric] = (
            greedy_metrics[metric] - fifo_metrics[metric]
        )

    return differences
