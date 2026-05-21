from django.test import SimpleTestCase

from notifications.action_priority import priority_from_days_until


class PriorityFromDaysUntilTests(SimpleTestCase):
    def test_overdue_is_critical(self):
        self.assertEqual(priority_from_days_until(-1), 'critical')

    def test_today_is_urgent(self):
        self.assertEqual(priority_from_days_until(0), 'urgent')

    def test_one_to_two_days_is_high(self):
        self.assertEqual(priority_from_days_until(1), 'high')
        self.assertEqual(priority_from_days_until(2), 'high')

    def test_three_to_four_days_is_medium(self):
        self.assertEqual(priority_from_days_until(3), 'medium')
        self.assertEqual(priority_from_days_until(4), 'medium')

    def test_five_plus_days_is_low(self):
        self.assertEqual(priority_from_days_until(5), 'low')
        self.assertEqual(priority_from_days_until(7), 'low')
