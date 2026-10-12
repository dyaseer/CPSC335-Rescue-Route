"""FIFO baseline and urgency-first greedy scheduling (algorithm lead).

Proposed greedy rule: earliest expiry_time, then largest quantity, then earliest
ready_time. Complete ties keep input order. Confirm this rule with the team.
"""

from copy import deepcopy

# TODO: Analyze time and space complexity for both schedulers using
# D = donations, R = recipients, and V = volunteers. Include sorting and matching.


def schedule_fifo(donations, recipients, volunteers, check_match, update_resources):
    """Return one assignment or rejection per donation, in input order.

    Inputs are validated lists of dictionaries. The data lead supplies:
    check_match(donation, recipient, volunteer) -> (feasible, time, reason)
    update_resources(assignment, donation, recipients, volunteers) -> None

    check_match must not change resources. update_resources changes the working
    copies after an assignment. Recipient and volunteer input order decides
    which feasible pair is selected first.
    """
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
            # Keep each distinct explanation once, in the order encountered.
            assignment["decision_reason"] = "No feasible match: " + "; ".join(
                dict.fromkeys(rejection_reasons)
            )

        assignments.append(assignment)

    return assignments


def greedy_priority(donation):
    """Return (expiry_time, -quantity, ready_time) for ascending sorting."""
    # Negating quantity puts larger donations first when expiration is tied.
    return (donation["expiry_time"], -donation["quantity"], donation["ready_time"])


def schedule_greedy(donations, recipients, volunteers, check_match, update_resources):
    """Schedule by expiry, then quantity, then ready time; preserve complete ties.

    Use the same matching helpers as FIFO. sorted creates a new list, and FIFO
    copies the records and resources so the original inputs stay unchanged.
    """
    ordered_donations = sorted(donations, key=greedy_priority)
    return schedule_fifo(
        ordered_donations, recipients, volunteers, check_match, update_resources
    )


def compare_strategies(fifo_metrics, greedy_metrics):
    """Return greedy-minus-FIFO differences for the three comparison metrics.

    Both input dictionaries must contain the metric keys below. Positive values
    favor greedy; negative values favor FIFO; zero indicates a tie. Urgent rescue
    rates use percentages, so their difference is in percentage points.
    """
    differences = {}
    for metric in (
        "donations_assigned",
        "food_quantity_rescued",
        "urgent_rescue_rate",
    ):
        differences[metric] = greedy_metrics[metric] - fifo_metrics[metric]
    return differences
