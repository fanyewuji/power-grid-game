import unittest
from logic.Cities import Cities

class TestCities(unittest.TestCase):
    def setUp(self):
        self.cities = Cities()

    def test_get_connection_cost_empty(self):
        self.assertEqual(self.cities.get_connection_cost('Hamburg', []), 0)

    def test_get_connection_cost_direct_neighbor(self):
        # Hamburg neighbors Lubeck (6) and Kiel (8)
        cost = self.cities.get_connection_cost('Hamburg', ['Kiel', 'Lubeck'])
        self.assertEqual(cost, 6)

    def test_get_connection_cost_indirect(self):
        # Dresden -> Fulda (32), Munster -> Fulda (28), Trier -> Fulda (26), Saarbrucken -> Fulda (18)
        cost = self.cities.get_connection_cost('Fulda', ['Dresden', 'Munster', 'Trier', 'Saarbrucken'])
        self.assertEqual(cost, 18)

    def test_get_build_cost(self):
        # First build cost = 10, then 15, then 20
        self.assertEqual(self.cities.get_build_cost('Lubeck'), 10)
        self.cities.build_house('Lubeck', 'Bob', 4)
        self.assertEqual(self.cities.get_build_cost('Lubeck'), 15)
        self.cities.build_house('Lubeck', 'Cody', 4)
        self.assertEqual(self.cities.get_build_cost('Lubeck'), 20)

if __name__ == '__main__':
    unittest.main()