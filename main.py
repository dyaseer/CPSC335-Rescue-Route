from pathlib import Path

from algorithms import schedule_fifo, schedule_greedy, compare_strategies
from data_loader import load_json, validate_data
from matching import check_match, update_resources
from metrics import calculate_metrics
from output import print_assignments, print_comparison

def main():
    # Step 1: Find the data folder beside this file and load the three lists.
    data_folder = Path(__file__).parent / "data"
    donations = load_json(data_folder / "donations.json")
    recipients = load_json(data_folder / "recipients.json")
    volunteers = load_json(data_folder / "volunteers.json")

    # Step 2: Check the data before trying to schedule donations.
    validate_data(donations, recipients, volunteers)

    # Step 3: Run each strategy on the same input. Each makes its own copies.
    fifo_assignments = schedule_fifo(
        donations, recipients, volunteers, check_match, update_resources
    )
    greedy_assignments = schedule_greedy(
        donations, recipients, volunteers, check_match, update_resources
    )

    # Step 4: Calculate results using the original capacities.
    fifo_metrics = calculate_metrics(
        donations, recipients, volunteers, fifo_assignments
    )

    greedy_metrics = calculate_metrics(
        donations, recipients, volunteers, greedy_assignments
    )
    # Step 5: Compare the results and show the decisions for both strategies.
    differences = compare_strategies(fifo_metrics, greedy_metrics)
    print_assignments("FIFO", fifo_assignments)
    print_assignments("Greedy", greedy_assignments)
    print_comparison(fifo_metrics, greedy_metrics, differences)


if __name__ == "__main__":
    main()
