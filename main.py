from metrics import calculate_metrics
from algorithms import *

def main():
    # TODO: Load and validate donation, recipient, and volunteer data.
    # TODO: Run FIFO and greedy separately on the same input.

    fifo_metrics = calculate_metrics(
        donations, recipients, volunteers, fifo_assignments
    )

    greedy_metrics = calculate_metrics(
        donations, recipients, volunteers, greedy_assignments
    )
    # TODO: Print decision explanations and compare metrics.
    pass


if __name__ == "__main__":
    main()
