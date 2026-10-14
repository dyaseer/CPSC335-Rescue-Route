"""Behavior tests (product and quality lead).

Run with: python -m unittest discover -s tests -v
"""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from algorithms import compare_strategies, schedule_fifo, schedule_greedy
from data_loader import load_json, validate_data
from matching import check_match, update_resources
from metrics import calculate_metrics


class RescueRouteTests(unittest.TestCase):
    def test_volunteer_capacity_utilization(self):
        # Two assigned donations rescue 12 units in total.
        donations = [
            {"donation_id": "D-001", "quantity": 6, "expiry_time": 90},
            {"donation_id": "D-002", "quantity": 6, "expiry_time": 30},
        ]
        assignments = [
            {"donation_id": "D-001", "status": "assigned"},
            {"donation_id": "D-002", "status": "assigned"},
        ]
        recipients = [{"capacity": 20}]
        volunteers = [{"vehicle_capacity": 8, "max_pickups": 2}]

        # Two pickups allow 16 units, so 12 units uses 75% of that capacity.
        result = calculate_metrics(donations, recipients, volunteers, assignments)
        self.assertAlmostEqual(result["volunteer_capacity_utilization"], 75.0)

        # Include every volunteer's allowed pickup capacity in the total.
        volunteers.append({"vehicle_capacity": 4, "max_pickups": 1})
        result = calculate_metrics(donations, recipients, volunteers, assignments)
        self.assertAlmostEqual(result["volunteer_capacity_utilization"], 60.0)

        # No pickup capacity should return zero without dividing by zero.
        for volunteers in ([], [{"vehicle_capacity": 8, "max_pickups": 0}],
                           [{"vehicle_capacity": 0, "max_pickups": 2}]):
            with self.subTest(volunteers=volunteers):
                result = calculate_metrics([], [], volunteers, [])
                self.assertEqual(result["volunteer_capacity_utilization"], 0.0)

    def test_normal_matching(self):
        # Step 1: Create one donation, recipient, and volunteer that can match.
        donations = [{
            "donation_id": "D-001", "donor_name": "Campus Cafe",
            "food_type": "prepared_meals", "quantity": 6,
            "expiry_time": 90, "pickup_area": "Campus", "ready_time": 10,
        }]
        recipients = [{
            "recipient_id": "R-001", "organization_name": "Community Shelter",
            "accepted_food_types": ["prepared_meals"], "capacity": 10,
            "area": "Campus", "closing_time": 120,
        }]
        volunteers = [{
            "volunteer_id": "V-001", "vehicle_capacity": 8, "area": "Campus",
            "available_from": 20, "available_until": 120, "max_pickups": 2,
        }]

        # Step 2: Validate the data and run the real FIFO scheduler.
        validate_data(donations, recipients, volunteers)
        assignments = schedule_fifo(
            donations, recipients, volunteers, check_match, update_resources
        )

        # Step 3: Check the donation was matched to the right people and time.
        self.assertEqual(len(assignments), 1)
        assignment = assignments[0]
        self.assertEqual(assignment["status"], "assigned")
        self.assertEqual(assignment["donation_id"], "D-001")
        self.assertEqual(assignment["recipient_id"], "R-001")
        self.assertEqual(assignment["volunteer_id"], "V-001")
        # Food is ready at minute 10, but the volunteer starts at minute 20.
        self.assertEqual(assignment["scheduled_time"], 20)
        self.assertIsInstance(assignment["decision_reason"], str)
        self.assertTrue(assignment["decision_reason"].strip())

    def test_duplicate_donation_id(self):
        # Step 1: Create two valid donations with different IDs.
        donations = [
            {
                "donation_id": "D-001", "donor_name": "Campus Cafe",
                "food_type": "prepared_meals", "quantity": 6,
                "expiry_time": 90, "pickup_area": "Campus", "ready_time": 0,
            },
            {
                "donation_id": "D-002", "donor_name": "Campus Event",
                "food_type": "prepared_meals", "quantity": 4,
                "expiry_time": 30, "pickup_area": "Campus", "ready_time": 0,
            },
        ]

        # Step 2: Different donation IDs should pass validation.
        self.assertIsNone(validate_data(donations, [], []))

        # Step 3: Give both donations the same ID and check for a duplicate error.
        donations[1]["donation_id"] = "D-001"
        with self.assertRaisesRegex(ValueError, "Duplicate donation_id"):
            validate_data(donations, [], [])

    def test_expired_or_nearly_expired_donation(self):
        # Step 1: The volunteer can pick up the food at minute 20.
        donations = [{
            "donation_id": "D-001", "donor_name": "Campus Cafe",
            "food_type": "prepared_meals", "quantity": 6,
            "expiry_time": 19, "pickup_area": "Campus", "ready_time": 0,
        }]
        recipients = [{
            "recipient_id": "R-001", "organization_name": "Community Shelter",
            "accepted_food_types": ["prepared_meals"], "capacity": 10,
            "area": "Campus", "closing_time": 120,
        }]
        volunteers = [{
            "volunteer_id": "V-001", "vehicle_capacity": 8, "area": "Campus",
            "available_from": 20, "available_until": 120, "max_pickups": 2,
        }]

        # Step 2: Try food expiring before, at, and one minute after pickup.
        for expiry_time in (19, 20, 21):
            with self.subTest(expiry_time=expiry_time):
                donations[0]["expiry_time"] = expiry_time
                validate_data(donations, recipients, volunteers)
                assignments = schedule_fifo(
                    donations, recipients, volunteers, check_match, update_resources
                )
                self.assertEqual(len(assignments), 1)
                assignment = assignments[0]
                self.assertEqual(assignment["donation_id"], "D-001")

                # Pickup at or after expiry must be rejected.
                if expiry_time <= 20:
                    self.assertEqual(assignment["status"], "unassigned")
                    self.assertIsNone(assignment["recipient_id"])
                    self.assertIsNone(assignment["volunteer_id"])
                    self.assertIsNone(assignment["scheduled_time"])
                    self.assertIn("expires", assignment["decision_reason"])
                else:
                    # One minute left is enough in our no-travel-time model.
                    self.assertEqual(assignment["status"], "assigned")
                    self.assertEqual(assignment["recipient_id"], "R-001")
                    self.assertEqual(assignment["volunteer_id"], "V-001")
                    self.assertEqual(assignment["scheduled_time"], 20)
                    self.assertTrue(assignment["decision_reason"].strip())

    def test_incompatible_food_type(self):
        # Step 1: Donate prepared meals to a recipient that only accepts produce.
        donations = [{
            "donation_id": "D-001", "donor_name": "Campus Cafe",
            "food_type": "prepared_meals", "quantity": 6,
            "expiry_time": 90, "pickup_area": "Campus", "ready_time": 0,
        }]
        recipients = [{
            "recipient_id": "R-001", "organization_name": "Community Pantry",
            "accepted_food_types": ["produce"], "capacity": 10,
            "area": "Campus", "closing_time": 120,
        }]
        volunteers = [{
            "volunteer_id": "V-001", "vehicle_capacity": 8, "area": "Campus",
            "available_from": 0, "available_until": 120, "max_pickups": 2,
        }]

        # Step 2: Run scheduling with enough capacity and time for a pickup.
        validate_data(donations, recipients, volunteers)
        assignments = schedule_fifo(
            donations, recipients, volunteers, check_match, update_resources
        )

        # Step 3: Check the food type caused a rejection, with no assigned pair.
        self.assertEqual(len(assignments), 1)
        assignment = assignments[0]
        self.assertEqual(assignment["donation_id"], "D-001")
        self.assertEqual(assignment["status"], "unassigned")
        self.assertIsNone(assignment["recipient_id"])
        self.assertIsNone(assignment["volunteer_id"])
        self.assertIsNone(assignment["scheduled_time"])
        self.assertIn(
            "does not accept",
            assignment["decision_reason"]
        )

    def test_greedy_scheduling_reason(self):
        donations = [
            {
                "donation_id": "D-1014",
                "food_type": "prepared_meals",
                "quantity": 4,
                "expiry_time": 90,
                "pickup_area": "Campus",
                "ready_time": 0,
            },
            {
                "donation_id": "D-1002",
                "food_type": "prepared_meals",
                "quantity": 4,
                "expiry_time": 30,
                "pickup_area": "Campus",
                "ready_time": 0,
            },
        ]

        assignments = schedule_greedy(
            donations, [], [],
            check_match, update_resources
        )

        self.assertEqual(
            [a["donation_id"] for a in assignments],
            ["D-1002", "D-1014"]
        )

        self.assertIn(
            "considered first",
            assignments[0]["scheduling_reason"]
        )

        self.assertIn(
            "D-1002",
            assignments[1]["scheduling_reason"]
        )

        self.assertIn(
            "less remaining shelf life",
            assignments[1]["scheduling_reason"]
        )

    def matching_data(self):
        """Return fresh valid records for the scheduling edge cases."""
        return ([{
            "donation_id": "D-001", "donor_name": "Campus Cafe",
            "food_type": "prepared_meals", "quantity": 6,
            "expiry_time": 90, "pickup_area": "Campus", "ready_time": 10,
        }], [{
            "recipient_id": "R-001", "organization_name": "Community Shelter",
            "accepted_food_types": ["prepared_meals"], "capacity": 10,
            "area": "Campus", "closing_time": 120,
        }], [{
            "volunteer_id": "V-001", "vehicle_capacity": 8, "area": "Campus",
            "available_from": 0, "available_until": 120, "max_pickups": 2,
        }])

    def assert_unassigned(self, assignment, reason):
        self.assertEqual(assignment["status"], "unassigned")
        self.assertIsNone(assignment["recipient_id"])
        self.assertIsNone(assignment["volunteer_id"])
        self.assertIsNone(assignment["scheduled_time"])
        self.assertIn(reason, assignment["decision_reason"])

    def test_insufficient_recipient_capacity(self):
        for scheduler in (schedule_fifo, schedule_greedy):
            # One unit short must fail; exactly enough space must succeed.
            for capacity in (5, 6):
                with self.subTest(strategy=scheduler.__name__, capacity=capacity):
                    donations, recipients, volunteers = self.matching_data()
                    recipients[0]["capacity"] = capacity
                    validate_data(donations, recipients, volunteers)
                    assignments = scheduler(
                        donations, recipients, volunteers, check_match, update_resources
                    )
                    self.assertEqual(len(assignments), 1)
                    self.assertEqual(assignments[0]["donation_id"], "D-001")
                    if capacity < 6:
                        self.assert_unassigned(assignments[0], "insufficient remaining capacity")
                    else:
                        self.assertEqual(assignments[0]["status"], "assigned")
                        self.assertEqual(assignments[0]["recipient_id"], "R-001")

    def test_unavailable_or_undersized_volunteer(self):
        cases = (
            ({"vehicle_capacity": 5}, "cannot carry"),
            ({"available_until": 10}, "unavailable"),
            ({"available_from": 90}, "expires"),
            ({"max_pickups": 0}, "no pickups remaining"),
        )
        for scheduler in (schedule_fifo, schedule_greedy):
            for changes, reason in cases:
                with self.subTest(strategy=scheduler.__name__, changes=changes):
                    donations, recipients, volunteers = self.matching_data()
                    volunteers[0].update(changes)
                    validate_data(donations, recipients, volunteers)
                    assignments = scheduler(
                        donations, recipients, volunteers, check_match, update_resources
                    )
                    self.assertEqual(len(assignments), 1)
                    self.assertEqual(assignments[0]["donation_id"], "D-001")
                    self.assert_unassigned(assignments[0], reason)

    def test_competing_donations(self):
        cases = (
            (6, 2, "insufficient remaining capacity"),
            (12, 1, "no pickups remaining"),
            (12, 2, None),
        )
        for scheduler in (schedule_fifo, schedule_greedy):
            for capacity, pickups, rejection in cases:
                with self.subTest(strategy=scheduler.__name__, capacity=capacity,
                                  pickups=pickups):
                    donations, recipients, volunteers = self.matching_data()
                    donations.append(dict(donations[0], donation_id="D-002"))
                    recipients[0]["capacity"] = capacity
                    volunteers[0].update(vehicle_capacity=6, max_pickups=pickups)
                    validate_data(donations, recipients, volunteers)
                    original = deepcopy((donations, recipients, volunteers))
                    assignments = scheduler(
                        donations, recipients, volunteers, check_match, update_resources
                    )
                    self.assertEqual(
                        [a["donation_id"] for a in assignments], ["D-001", "D-002"]
                    )
                    self.assertEqual(assignments[0]["status"], "assigned")
                    if rejection:
                        self.assert_unassigned(assignments[1], rejection)
                    else:
                        # Vehicle capacity limits each pickup, so it can be reused.
                        self.assertEqual(assignments[1]["status"], "assigned")
                    metrics = calculate_metrics(
                        donations, recipients, volunteers, assignments
                    )
                    self.assertEqual(metrics["food_quantity_rescued"],
                                     6 if rejection else 12)
                    self.assertEqual((donations, recipients, volunteers), original)

    def test_empty_input(self):
        with TemporaryDirectory() as folder:
            file_path = Path(folder) / "empty.json"
            file_path.write_text("[]", encoding="utf-8")
            self.assertEqual(load_json(file_path), [])
            self.assertIsNone(validate_data([], [], []))
            # A zero-byte file is invalid JSON rather than an empty dataset.
            file_path.write_text("", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_json(file_path)

        for scheduler in (schedule_fifo, schedule_greedy):
            for missing in ("all", "donations", "recipients", "volunteers"):
                with self.subTest(strategy=scheduler.__name__, missing=missing):
                    donations, recipients, volunteers = self.matching_data()
                    if missing in ("all", "donations"):
                        donations = []
                    if missing in ("all", "recipients"):
                        recipients = []
                    if missing in ("all", "volunteers"):
                        volunteers = []
                    validate_data(donations, recipients, volunteers)
                    assignments = scheduler(
                        donations, recipients, volunteers, check_match, update_resources
                    )
                    if not donations:
                        self.assertEqual(assignments, [])
                    else:
                        self.assertEqual(len(assignments), 1)
                        self.assert_unassigned(assignments[0], "No recipients or volunteers")
                    self.assertEqual(
                        calculate_metrics(donations, recipients, volunteers, assignments),
                        {
                            "donations_received": len(donations),
                            "donations_assigned": 0,
                            "donations_unassigned": len(donations),
                            "food_quantity_rescued": 0,
                            "food_quantity_at_risk": 6 * len(donations),
                            "urgent_rescue_rate": 0.0,
                            "recipient_capacity_utilization": 0.0,
                            "volunteer_capacity_utilization": 0.0,
                        },
                    )

    def test_fifo_and_greedy_differ(self):
        donations, recipients, volunteers = self.matching_data()
        donations.append(dict(donations[0], donation_id="D-002", expiry_time=30))
        validate_data(donations, recipients, volunteers)
        original = deepcopy((donations, recipients, volunteers))
        results = []
        for scheduler, winner in ((schedule_fifo, "D-001"),
                                  (schedule_greedy, "D-002")):
            assignments = scheduler(
                donations, recipients, volunteers, check_match, update_resources
            )
            self.assertEqual(len(assignments), 2)
            self.assertEqual(assignments[0]["donation_id"], winner)
            self.assertEqual(assignments[0]["status"], "assigned")
            self.assertEqual(assignments[0]["recipient_id"], "R-001")
            self.assertEqual(assignments[0]["volunteer_id"], "V-001")
            self.assertEqual(assignments[0]["scheduled_time"], 10)
            loser = "D-002" if winner == "D-001" else "D-001"
            self.assertEqual(assignments[1]["donation_id"], loser)
            self.assert_unassigned(assignments[1], "insufficient remaining capacity")
            self.assertEqual((donations, recipients, volunteers), original)
            results.append(calculate_metrics(
                donations, recipients, volunteers, assignments
            ))

        fifo_metrics, greedy_metrics = results
        for metrics in results:
            self.assertEqual(metrics["donations_assigned"], 1)
            self.assertEqual(metrics["food_quantity_rescued"], 6)
            self.assertEqual(metrics["food_quantity_at_risk"], 6)
        self.assertEqual(fifo_metrics["urgent_rescue_rate"], 0.0)
        self.assertEqual(greedy_metrics["urgent_rescue_rate"], 100.0)
        self.assertEqual(compare_strategies(fifo_metrics, greedy_metrics), {
            "donations_assigned": 0,
            "food_quantity_rescued": 0,
            "urgent_rescue_rate": 100.0,
        })

    def test_fairness_or_starvation(self):
        donations, recipients, volunteers = self.matching_data()
        donations[0]["quantity"] = 4
        donations.append(dict(donations[0], donation_id="D-002", quantity=6))
        recipients[0]["capacity"] = 6
        validate_data(donations, recipients, volunteers)

        # With equal expiry, greedy favors the larger, later-arriving donation.
        # The earlier small donor loses capacity despite being feasible alone.
        # This shows unfairness in one run, not starvation across runs: rejected
        # donations are not retained in a waiting queue by the current program.
        alone = schedule_greedy(
            donations[:1], recipients, volunteers, check_match, update_resources
        )
        self.assertEqual(alone[0]["status"], "assigned")
        for scheduler, expected in (
            (schedule_fifo, {"D-001": "assigned", "D-002": "unassigned"}),
            (schedule_greedy, {"D-001": "unassigned", "D-002": "assigned"}),
        ):
            with self.subTest(strategy=scheduler.__name__):
                assignments = scheduler(
                    donations, recipients, volunteers, check_match, update_resources
                )
                self.assertEqual(len(assignments), 2)
                self.assertEqual(
                    {a["donation_id"]: a["status"] for a in assignments}, expected
                )
                for assignment in assignments:
                    if assignment["status"] == "unassigned":
                        self.assert_unassigned(assignment, "insufficient remaining capacity")
                if scheduler is schedule_greedy:
                    self.assertEqual(assignments[0]["donation_id"], "D-002")
                    self.assertIn("larger quantity", assignments[1]["scheduling_reason"])
