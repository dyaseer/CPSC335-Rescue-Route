"""FIFO baseline and urgency-first greedy scheduling (algorithm lead)."""

# TODO: Analyze time and space complexity for both schedulers using
# D = donations, R = recipients, and V = volunteers. Include sorting and matching.


def schedule_fifo(donations, recipients, volunteers):
    """Return one assignment or rejection per donation, in input order."""
    # TODO: Copy resource data so this run does not change the original input.
    # Use the data lead's matching and resource-update helpers for each donation.
    raise NotImplementedError


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
