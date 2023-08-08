from django.test import SimpleTestCase
from app.calc import subtract

from app.calc import addexample

class CalcTest(SimpleTestCase):
    def test_add_numbers(self):
        """Test that two numbers are added together"""

        self.assertEqual(addexample(3, 8), 11)
        print("Test 1 passed")

    def subtract_test(self):
        """Test that values are subtracted and returned"""
        self.assertEqual(subtract(11, 5), 6)
        print("Test 2 passed")