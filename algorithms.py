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
    # TODO: Build the priority tuple. Stable sorting preserves input order
    # when all three values are tied.
    raise NotImplementedError


def schedule_greedy(donations, recipients, volunteers):
    """Return one assignment or rejection per donation, in greedy priority order."""
    # TODO: Copy resource data and sort donations using greedy_priority.
    # Use the same matching and resource rules as FIFO.
    raise NotImplementedError


def compare_strategies(fifo_metrics, greedy_metrics):
    """Return greedy-minus-FIFO differences using the quality lead's metrics."""
    # TODO: Compare assigned donations, rescued quantity, and urgent rescue rate.
    # Discuss where greedy helps and where it may defer less urgent donations.
    raise NotImplementedError
