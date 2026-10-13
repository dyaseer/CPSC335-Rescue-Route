"""Behavior tests and unfinished test skeletons (product and quality lead).

Run with: python -m unittest discover -s tests -v
Remove each test's skip decorator as real assertions are added. Skipped tests are
unfinished work, not evidence that the program works.
"""

import unittest

from algorithms import schedule_fifo
from data_loader import validate_data
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
        self.assertIn("does not accept this food type", assignment["decision_reason"])

    @unittest.skip("Test assertions are not implemented yet")
    def test_insufficient_recipient_capacity(self):
        # TODO: Assert rejection when recipient capacity is too small.
        pass

    @unittest.skip("Test assertions are not implemented yet")
    def test_unavailable_or_undersized_volunteer(self):
        # TODO: Assert rejection for unavailable drivers and small vehicles.
        pass

    @unittest.skip("Test assertions are not implemented yet")
    def test_competing_donations(self):
        # TODO: Assert capacity is not reused after an assignment.
        pass

    @unittest.skip("Test assertions are not implemented yet")
    def test_empty_input(self):
        # TODO: Assert behavior for empty lists, empty files, and zero denominators.
        pass

    @unittest.skip("Test assertions are not implemented yet")
    def test_fifo_and_greedy_differ(self):
        # TODO: Assert different expected outcomes on the same original data.
        pass

    @unittest.skip("Test assertions are not implemented yet")
    def test_fairness_or_starvation(self):
        # TODO: Assert which donation is deferred and document why.
        pass
