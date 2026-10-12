# CPSC335-Rescue-Route

## Setup and usage

TODO: Add Python requirements, run instructions, and sample output once wired up.

## Architecture and data schema

TODO: Describe the modules, input fields, and assignment records.

## Algorithms and complexity

TODO: Add the final algorithm design, agreed greedy rule, and comparison results.

### Complexity analysis

**D** = donations, **R** = recipients, and **V** = volunteers.
Time means how much work the function does. Space means how much extra memory
it needs. O(1) means the amount of work or memory stays the same as input grows.

For this analysis, assume each record is small, each match check takes O(1)
time, and rejection messages come from a fixed set of short reasons. Updating
resources can take O(R + V) time to find the selected recipient and volunteer.
The table assumes there is at least one recipient and one volunteer.

| Function | Worst-case time | Extra memory, including results |
| --- | --- | --- |
| `schedule_fifo` | O(D + R + V + D × R × V) | O(D + R + V + R × V) |
| `greedy_priority` | O(1) | O(1) |
| `schedule_greedy` | O(D log D + D + R + V + D × R × V) | O(D + R + V + R × V) |
| `compare_strategies` | O(1) | O(1) |

**FIFO:** For each donation, the program may check every recipient with every
volunteer. That gives D × R × V checks in the worst case. Finding a match early
means fewer checks. Copying the input adds O(D + R + V) work and memory. This
copy lets FIFO and greedy run without changing the original data.

FIFO also stores one result per donation and temporarily keeps up to R × V
rejection reasons for the current donation. This is why its memory use includes
R × V. If every failed pair produces a different reason, the saved explanations
can grow to O(D × R × V) instead of O(D).

**Greedy:** First, the program sorts donations, which takes O(D log D) time.
Then it uses the same matching steps as FIFO. Sorting needs O(D) extra memory,
which is already included in the table's memory total.

**Priority and comparison:** Creating a three-value priority tuple takes O(1).
Comparing three metrics also takes O(1). Calculating those metrics is separate.

**Empty lists:** No donations means no matching work, but resource lists are
still copied. With no volunteers, FIFO still visits each recipient for each
donation. A time bound that also covers empty lists is
O(D + R + V + D(RV + R + V)); greedy adds its sorting cost.

Check these assumptions again when the data lead finishes the matching helpers.

## Tests

Run `python -m unittest discover -s tests -v`.
The current test skeletons are skipped and do not validate program behavior yet.

## Assumptions and limitations

TODO: Document the simulation rules, metric definitions, and fairness trade-offs.

## Team contributions and references

TODO: Add roles, contributions, external references, and course-required AI disclosure.
