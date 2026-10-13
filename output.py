"""Console output (product and quality lead)."""


def print_assignments(strategy_name, assignments):
    """Print each donation's outcome and decision_reason; return None."""
    print(f"\n{strategy_name} assignments")
    if not assignments:
        print("No donations to process.")
        return

    for assignment in assignments:
        donation_id = assignment["donation_id"]
        if assignment["status"] == "assigned":
            print(f"{donation_id}: assigned.")
            print("  Recipient:", assignment["recipient_id"])
            print("  Volunteer:", assignment["volunteer_id"])
            print("  Pickup time (minutes):", assignment["scheduled_time"])
        else:
            print(f"{donation_id}: unassigned.")
        print("  Reason:", assignment["decision_reason"])


def print_comparison(fifo_metrics, greedy_metrics, differences):
    """Print both strategies' metrics and comparison differences; return None."""
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
            print("  FIFO:", fifo_metrics[metric])
            print("  Greedy:", greedy_metrics[metric])

        if metric in differences:
            if metric in percentage_metrics:
                print("  Greedy minus FIFO:", differences[metric], "percentage points")
            else:
                print("  Greedy minus FIFO:", differences[metric])
