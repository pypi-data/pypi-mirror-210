import os
import unittest
import pandas as pd
from pers import PersistentResults

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        results = PersistentResults(
            'test_exists.pickle', # storage for results
            interval=1,           # how often dump the results
            load=False,           # False means we will overwrite the results
        )

        fun = lambda x, y, a, b: x**2 + y
        for x in range(10):
            for y in range(11):
                results.append(fun, x, y, a=x, b=y)
        results.save()
        self.results = results

    def tearDown(self):
        os.remove(self.results.filename)

    def test_exist1(self):
        # Check if results for product of all below arguments exist:
        # arg1: [4]
        # arg2: [3]
        # a: [4]
        # b: [3]
        self.assertTrue(self.results.all(
            [4], [3],         # args
            a = [4], b = [3], # kwargs
        ))


    def test_exist2(self):
        # Similar test as above, but for arguments where at least one result does not exist
        self.assertFalse(self.results.all(
            [4], [1, 3, 5, 7],
            a = [4], b = [1, 3, 5, 7],
        ))


    def test_exist3(self):
        # Similar test as above, but checks if at least one argument exists
        self.assertTrue(self.results.any(
            [4, 20], [1, 3, 5, 7],
            a = [4, 20], b = [1, 3, 5, 7],
        ))


    def test_exist4(self):
        # Similar test as above, but should return False
        self.assertFalse(self.results.any(
            [20], [1, 3, 5, 7],
            a = [20], b = [1, 3, 5, 7],
        ))

    def test_missing(self):
        # Checks if missing correctly returns missing results
        # print(
        #     self.results.missing(
        #         [4], [1, 3, 5, 7], # add 20
        #         a = [4], b = [1, 3, 5, 7],
        #     ))
        self.assertSequenceEqual(
            [
                ((4, 1), {'a': 4, 'b': 3}), 
                ((4, 1), {'a': 4, 'b': 5}), 
                ((4, 1), {'a': 4, 'b': 7}), 
                ((4, 3), {'a': 4, 'b': 1}), 
                ((4, 3), {'a': 4, 'b': 5}), 
                ((4, 3), {'a': 4, 'b': 7}), 
                ((4, 5), {'a': 4, 'b': 1}), 
                ((4, 5), {'a': 4, 'b': 3}),
                ((4, 5), {'a': 4, 'b': 7}), 
                ((4, 7), {'a': 4, 'b': 1}), 
                ((4, 7), {'a': 4, 'b': 3}), 
                ((4, 7), {'a': 4, 'b': 5})
            ],
            self.results.missing(
                [4], [1, 3, 5, 7], # add 20
                a = [4], b = [1, 3, 5, 7],
            )
        )

    def test_duplicate_entry(self):
        results = PersistentResults(
            self.results.filename
        )

        # This function should never be executed as all results are already collected
        fun = lambda x, y, a, b: {'x': 'DUPLICATE', 'y': 'DUPLICATE'}
        for x in range(10):
            for y in range(11):
                results.append(fun, x, y, a=x, b=y)
        # It means there should be no records with 'DUPLICATE' value
        self.assertEqual(len([x for x in results.data if 'DUPLICATE' in x.values()]), 0)


if __name__ == '__main__':
    unittest.main()



