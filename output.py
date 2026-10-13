"""Console output (product and quality lead)."""


def print_assignments(strategy_name, assignments):
    """Print each donation's outcome and decision_reason; return None."""
    # Show which strategy produced these results.
    print(f"\n{strategy_name} assignments")
    # Stop here if there are no donations to display.
    if not assignments:
        print("No donations to process.")
        return

    # Show each donation and whether it found a match.
    for assignment in assignments:
        donation_id = assignment["donation_id"]
        if assignment["status"] == "assigned":
            # A matched donation has a recipient, volunteer, and pickup time.
            print(f"{donation_id}: assigned.")
            print("  Recipient:", assignment["recipient_id"])
            print("  Volunteer:", assignment["volunteer_id"])
            print("  Pickup time (minutes):", assignment["scheduled_time"])
        else:
            print(f"{donation_id}: unassigned.")
        # Explain the result, whether the donation was assigned or rejected.
        print("  Reason:", assignment["decision_reason"])


def print_comparison(fifo_metrics, greedy_metrics, differences):
    """Print both strategies' metrics and comparison differences; return None."""
    # Give the dictionary keys readable names for the console.
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
    # These values are percentages; the others are counts or quantities.
    percentage_metrics = {
        "urgent_rescue_rate",
        "recipient_capacity_utilization",
        "volunteer_capacity_utilization",
    }

    print("\nFIFO vs. greedy comparison")
    # Show the FIFO and greedy values for each metric.
    for metric, label in labels.items():
        print(label)
        if metric in percentage_metrics:
            # Show percentages with one digit after the decimal point.
            print(f"  FIFO: {fifo_metrics[metric]:.1f}%")
            print(f"  Greedy: {greedy_metrics[metric]:.1f}%")
        else:
            print("  FIFO:", fifo_metrics[metric])
            print("  Greedy:", greedy_metrics[metric])

        # Show a difference only when compare_strategies calculated one.
        if metric in differences:
            if metric in percentage_metrics:
                # For example, 75% minus 50% is 25 percentage points.
                print("  Greedy minus FIFO:", differences[metric], "percentage points")
            else:
                print("  Greedy minus FIFO:", differences[metric])
