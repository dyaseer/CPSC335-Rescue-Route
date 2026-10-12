# CPSC335-Rescue-Route

## Setup and usage

TODO: Add Python requirements, run instructions, and sample output once wired up.

## Architecture and data schema

TODO: Describe the modules, input fields, and assignment records.

## Algorithms and complexity

TODO: Confirm the greedy rule with the team and add actual comparison results.

### Why we use greedy

The greedy scheduler considers donations in this order:

1. Earlier expiration first, because that food has less time left to be rescued.
2. If expiration times match, larger quantities first, to try to rescue more food.
3. If quantities also match, earlier ready times first, to favor food ready sooner.
4. If all three values match, keep the original input order.

For each donation, it chooses the first recipient and volunteer that meet the
matching rules. It then updates their remaining resources before considering
the next donation. FIFO uses the same checks but keeps donation input order.

This rule is simple to explain and gives urgent food the first chance at limited
capacity. It makes a choice for the next donation rather than trying every
possible schedule. It aims to help urgent donations, but it does not guarantee
the most food rescued or the most donations assigned.

### Where greedy can fall short

- An urgent donation can use capacity that could have served several other
  donations. Larger quantities can also leave smaller donations without space.
- The first matching recipient or volunteer may be needed by a later donation
  that has fewer options. The scheduler does not go back and change its choices.
- Less urgent donations can be considered later and lose access to capacity,
  even if they appeared earlier in the input.
- Priority is based only on expiration, quantity, and ready time. It does not
  choose the best route or consider how long a donation has been waiting.

For example, suppose a recipient has capacity for 10 units. All other matching
checks pass. One donation has 6 units and expires sooner; two others have
5 units each and expire later. Greedy assigns the urgent 6-unit donation,
leaving only 4 units of capacity. Neither 5-unit donation fits. Choosing the two
5-unit donations instead would rescue 10 units, but leave the urgent donation
unassigned. This shows the trade-off between rescuing urgent food and rescuing
the greatest total quantity.

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
