
"""Human-readable console output for RescueRoute."""


def print_assignments(
    strategy_name, assignments, donations, recipients
):
    """Display assignment results and explanations."""

    print(f"\n{'=' * 12} {strategy_name} Assignments {'=' * 12}")

    if not assignments:
        print("No donations to process.")
        return

    donation_by_id = {
        donation["donation_id"]: donation
        for donation in donations
    }

    recipient_by_id = {
        recipient["recipient_id"]: recipient
        for recipient in recipients
    }

    for assignment in assignments:
        donation_id = assignment["donation_id"]
        status = assignment["status"]
        donation = donation_by_id.get(donation_id)

        print()

        if status == "assigned":
            recipient = recipient_by_id.get(assignment["recipient_id"])
            recipient_name = (
                recipient["organization_name"]
                if recipient
                else assignment["recipient_id"]
            )

            volunteer_id = assignment["volunteer_id"]
            scheduled_time = assignment["scheduled_time"]

            print(f"[ASSIGNED] Donation {donation_id}")

            print(
                f"Donation {donation_id} was assigned to "
                f"{recipient_name} with volunteer {volunteer_id} "
                f"because {assignment['decision_reason']}."
            )

            print(
                f"Scheduled pickup: minute {scheduled_time} "
                f"of the simulation."
            )

        else:
            print(f"[UNASSIGNED] Donation {donation_id}")

            print(
                f"Donation {donation_id} could not be assigned. "
                f"{assignment['decision_reason']}."
            )

        # Greedy results include a separate explanation of priority order.
        scheduling_reason = assignment.get("scheduling_reason")

        if scheduling_reason:
            print(f"Scheduling decision: {scheduling_reason}")


def print_comparison(fifo_metrics, greedy_metrics, differences):
    """Print strategy metrics and the greedy-minus-FIFO differences."""

    labels = {
        "donations_received": "Donations received",
        "donations_assigned": "Donations assigned",
        "donations_unassigned": "Donations unassigned",
        "food_quantity_rescued": "Food quantity rescued (units)",
        "food_quantity_at_risk": "Food quantity at risk (units)",
        "urgent_rescue_rate": "Urgent rescue rate",
        "recipient_capacity_utilization": "Recipient capacity utilization",
        "volunteer_capacity_utilization": "Volunteer capacity utilization",
    }

    percentage_metrics = {
        "urgent_rescue_rate",
        "recipient_capacity_utilization",
        "volunteer_capacity_utilization",
    }

    print("\nFIFO vs. greedy comparison")

    for metric, label in labels.items():
        print(label)

        if metric in percentage_metrics:
            print(f"  FIFO: {fifo_metrics[metric]:.1f}%")
            print(f"  Greedy: {greedy_metrics[metric]:.1f}%")
        else:
            print(f"  FIFO: {fifo_metrics[metric]}")
            print(f"  Greedy: {greedy_metrics[metric]}")

        if metric in differences:
            if metric == "urgent_rescue_rate":
                print(
                    f"  Greedy minus FIFO: "
                    f"{differences[metric]:.1f} percentage points"
                )
            elif metric in percentage_metrics:
                print(
                    f"  Greedy minus FIFO: "
                    f"{differences[metric]:.1f} percentage points"
                )
            else:
                print(
                    f"  Greedy minus FIFO: "
                    f"{differences[metric]}"
                )
