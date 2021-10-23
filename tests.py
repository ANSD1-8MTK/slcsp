#!/env/python

"""
A Python test suite to test the functionality of the corresponding slcsp.py
script for the SLCSP Ad Hoc homework exercise found here:
https://homework.adhoc.team/slcsp/

REQUIREMENTS:
- Python 3.7+

There is no need to install any additional modules or setup a virtual
environment.  This test suite is entirely self-contained and contains zero
external dependencies.

HOW TO USE THIS TEST SUITE:

Run "python tests.py" (or whatever your Python executable is called - sometimes
it might be "python3") in a command line/terminal window within the same
directory that you have placed the slcsp.py script.

The test suite is configured to display verbose test output by default.
"""


import unittest

from collections import OrderedDict


# Import all of the necessary data processing methods, configuration, and
# defaults in the slcsp.py script required for testing.
from slcsp import (
    clean_plan_rates,
    clean_zipcode_rate_areas,
    filter_plan_metal_level,
    prepare_slcsp_output,
    retrieve_slcsp_for_zipcode,

    SLCSP_OUTPUT_FIELD_NAMES,
    DESIRED_METAL_LEVEL
)


class TestCSVFileLoadMethods(unittest.TestCase):
    """
    Test suite for checking that the data is loaded properly from the given
    input sources.
    """

    def test_filtering_plans_by_metal_level_matches_only_silver(self):
        """
        Tests the filtering for a plan by its metal level to only match silver
        level plans.
        """

        silver_plan_inputs = [
            {
                'plan_id': '05276NA2900195',
                'state': 'MI',
                'metal_level': 'Silver',
                'rate': '283.39',
                'rate_area': '1'
            },
            {
                'plan_id': '05276NA2900195',
                'state': 'MI',
                'metal_level': 'silver',
                'rate': '283.39',
                'rate_area': '1'
            }
        ]

        non_silver_plan_inputs = [
            {
                'plan_id': '68493CI1477769',
                'state': 'SC',
                'metal_level': 'Bronze',
                'rate': '214.57',
                'rate_area': '21'
            },
            {
                'plan_id': '09812TP4606635',
                'state': 'NV',
                'metal_level': 'Platinum',
                'rate': '331.363599',
                'rate_area': '1'
            },
            {
                'plan_id': '11698OD6718414',
                'state': 'SC',
                'metal_level': 'Gold',
                'rate': '269.54',
                'rate_area': '8'
            },
            {
                'plan_id': '70547DK6596753',
                'state': 'FL',
                'metal_level': 'Catastrophic',
                'rate': '241.1',
                'rate_area': '57'
            }
        ]

        for silver_plan in silver_plan_inputs:
            result = filter_plan_metal_level(silver_plan, DESIRED_METAL_LEVEL)
            self.assertEqual(True, result)

        for non_silver_plan in non_silver_plan_inputs:
            result = filter_plan_metal_level(
                non_silver_plan,
                DESIRED_METAL_LEVEL
            )
            self.assertEqual(False, result)


class TestCleanDataMethods(unittest.TestCase):
    """
    Test suite for testing and validating that the clean methods are functioning
    properly and producing the expected output.
    """

    def test_clean_zipcode_data_is_unique(self):
        """
        Test that the zipcode data is cleaned properly and contains only unique
        rate areas.
        """

        input = {
            '11111': [('NY', '5')],
            '22222': [('WI', '2')],
            '33333': [('WI', '2'), ('NY', '5')],
            '44444': [('WI', '2'), ('WI', '2')],
            '55555': [('WI', '2'), ('WI', '2'), ('NY', '5')],
            '66666': [('WI', '2'), ('WI', '2'), ('NY', '5'), ('NY', '5')],
            '77777': [
                ('WI', '2'),
                ('WI', '2'),
                ('NY', '5'),
                ('NY', '5'),
                ('CA', '7')
            ]
        }

        expected = {
            '11111': [('NY', '5')],
            '22222': [('WI', '2')],
            '33333': [('WI', '2'), ('NY', '5')],
            '44444': [('WI', '2')],
            '55555': [('WI', '2'), ('NY', '5')],
            '66666': [('WI', '2'), ('NY', '5')],
            '77777': [('WI', '2'), ('NY', '5'), ('CA', '7')]
        }

        cleaned_rate_areas = clean_zipcode_rate_areas(input)

        # Compare each set of rate areas for every zipcode; sort the values to
        # make sure we're comparing the data correctly.
        for zipcode, rate_areas in cleaned_rate_areas.items():
            self.assertEqual(sorted(rate_areas), sorted(expected[zipcode]))

    
    def test_clean_plan_rates_sorts_and_makes_data_unique(self):
        """
        Tests the plan ratea data is cleaned properly and is returned with
        sorted unique values for each rate area.
        """

        input = {
            ('IN', '1'): [
                '304.5',
                '422.28',
                '386.79',
                '382.7',
                '332.21',
                '422.28',
                '382.7'
            ],
            ('SD', '2'): [
                '279.4',
                '250.14',
                '270.13',
                '274.56',
                '247.67',
                '279.4',
                '270.13'
            ],
            ('FL', '63'): [
                '398.14',
                '330.9',
                '324.61',
                '398.14',
                '345.91',
                '214.32',
                '330.9'
            ],
            ('FL', '54'): [
                '428.03',
                '294.87',
                '339.6',
                '409.72',
                '294.44'
            ]
        }

        expected = {
            ('IN', '1'): [
                '304.5',
                '332.21',
                '382.7',
                '386.79',
                '422.28'
            ],
            ('SD', '2'): [
                '247.67',
                '250.14',
                '270.13',
                '274.56',
                '279.4'
            ],
            ('FL', '63'): [
                '214.32',
                '324.61',
                '330.9',
                '345.91',
                '398.14'
            ],
            ('FL', '54'): [
                '294.44',
                '294.87',
                '339.6',
                '409.72',
                '428.03'
            ]
        }

        cleaned_plan_data = clean_plan_rates(input)
        self.assertEqual(expected, cleaned_plan_data)


class TestRetrievingSLCSPForZipcode(unittest.TestCase):
    """
    Test suite for testing and validating that we properly retrieve a second
    lowest cost silver plan rate and properly handle the cases when we cannot.
    """

    def test_zipcode_is_successfully_mapped(self):
        """
        Tests that when the conditions are right, a zipcode is properly mapped
        to a rate.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'11111': [('NY', '5')]}
        cleaned_plan_data_input = {('NY', '5'): ['294.44', '294.87', '339.6']}

        expected = '294.87'

        slcsp_rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data_input,
            cleaned_plan_data_input
        )

        self.assertEqual(expected, slcsp_rate)


    def test_no_rate_found_is_empty_string(self):
        """
        Tests that if no matching rate is found for a zipcode, an empty string
        is returned instead per the exercise instructions.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'22222': [('NH', '12')]}
        cleaned_plan_data_input = {('NY', '5'): ['294.44', '294.87', '339.6']}

        expected = ''

        slcsp_rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data_input,
            cleaned_plan_data_input
        )

        self.assertEqual(expected, slcsp_rate)

    
    def test_only_five_digit_zipcodes_match(self):
        """
        Tests that a rate is not returned when a zipcode is given in a format
        that is not 5 digits.
        """

        incorrect_zipcodes = ['1', 'abcdef', '123ab', '12345-6789', 'abc-def']
        non_string_zipcodes = [1, [123, 143], {'test': '123'}, 344.234, True]
        cleaned_zipcode_data_input = {'11111': [('NY', '5')]}
        cleaned_plan_data_input = {('NY', '5'): ['294.44', '294.87', '339.6']}

        expected = ''

        for incorrect_zipcode in incorrect_zipcodes:
            slcsp_rate = retrieve_slcsp_for_zipcode(
                incorrect_zipcode,
                cleaned_zipcode_data_input,
                cleaned_plan_data_input
            )

            self.assertEqual(expected, slcsp_rate)

        for non_string_zipcode in non_string_zipcodes:
            slcsp_rate = retrieve_slcsp_for_zipcode(
                non_string_zipcode,
                cleaned_zipcode_data_input,
                cleaned_plan_data_input
            )

            self.assertEqual(expected, slcsp_rate)

    
    def test_empty_string_returned_if_no_plan_areas_exist(self):
        """
        Tests that an empty string is returned if no plan areas exist for a
        given zipcode.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'11111': []}
        cleaned_plan_data_input = {('NY', '5'): ['294.44', '294.87', '339.6']}

        expected = ''

        slcsp_rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data_input,
            cleaned_plan_data_input
        )

        self.assertEqual(expected, slcsp_rate)


    def test_empty_string_returned_if_too_many_plan_areas_exist(self):
        """
        Tests that an empty string is returned if more than one plan area exists
        for a given zipcode.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'11111': [('WI', '9'), ('NY', '5')]}
        cleaned_plan_data_input = {('NY', '5'): ['294.44', '294.87', '339.6']}

        expected = ''

        slcsp_rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data_input,
            cleaned_plan_data_input
        )

        self.assertEqual(expected, slcsp_rate)
    

    def test_empty_string_returned_if_no_plans_are_found(self):
        """
        Tests that an empty string is returned if no plans can be found for a
        rate area for the given zipcode.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'11111': [('WI', '9')]}
        cleaned_plan_data_input = {('WI', '9'): []}

        expected = ''

        slcsp_rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data_input,
            cleaned_plan_data_input
        )

        self.assertEqual(expected, slcsp_rate)

    
    def test_empty_string_returned_if_too_few_plans_are_found(self):
        """
        Tests that an empty string is returned if no plans can be found for a
        rate area for the given zipcode.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'11111': [('WI', '9')]}
        cleaned_plan_data_input = {('WI', '9'): []}
        cleaned_plan_data_input = {('WI', '9'): ['324.6']}

        expected = ''

        slcsp_rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data_input,
            cleaned_plan_data_input
        )

        self.assertEqual(expected, slcsp_rate)


    def test_rate_always_formatted_to_two_decimal_places(self):
        """
        Tests that if a rate can be returned, it is always formatted to two
        decimal places.
        """

        zipcode = '11111'
        cleaned_zipcode_data_input = {'11111': [('NY', '5')]}
        cleaned_plan_data_inputs = [
            {('NY', '5'): ['294.24', '294']},
            {('NY', '5'): ['294.24', '294.7']},
            {('NY', '5'): ['294.24', '294.3452']},
            {('NY', '5'): ['294.24', '294.24']}
        ]

        # NOTE:  Formatting a decimal.Decimal value will result in rounding.
        expected_results = ['294.00', '294.70', '294.35', '294.24']

        for i, cleaned_plan_data_input in enumerate(cleaned_plan_data_inputs):
            slcsp_rate = retrieve_slcsp_for_zipcode(
                zipcode,
                cleaned_zipcode_data_input,
                cleaned_plan_data_input
            )

            self.assertEqual(expected_results[i], slcsp_rate)


class TestSLCSPOutputMatchesInput(unittest.TestCase):
    """
    Test suite for testing and validating that the output we produce matches the
    format and structure of the input given.
    """

    def test_output_matches_structure_of_input(self):
        """
        Tests that the prepared output matches the structure of the input with
        the given sample data.

        This test simulates the data having already been loaded from the source
        CSV files.
        """

        input_header = ['zipcode', 'rate']
        input_slcsp_zipcodes = ['11111', '22222', '33333', '44444', '55555']
        input_zipcode_data = {
            '11111': [('NY', '5')],
            '22222': [('WI', '2')],
            '33333': [('WI', '2'), ('NY', '5')],
            '55555': [('FL', '63')]
        }
        input_plan_data = {
            ('NY', '5'): [
                '304.5',
                '422.28',
                '386.79',
                '382.7',
                '332.21',
                '422.28',
                '382.7'
            ],
            ('WI', '2'): [
                '279.4',
                '250.14',
                '270.13',
                '274.56',
                '247.67',
                '279.4',
                '270.13'
            ],
            ('FL', '63'): [
                '398.14'
            ]
        }

        expected_output = OrderedDict({
            '11111': '332.21',  # Rate found
            '22222': '250.14',  # Rate found
            '33333': '',        # Rate not found - too many rate areas
            '44444': '',        # Rate not found - zipcode wasn't found
            '55555': ''         # Rate not found - too few rates
        })

        # Check that the header row default is set properly.
        self.assertEqual(input_header, SLCSP_OUTPUT_FIELD_NAMES)

        # Clean the data to prepare it for calculating the second lowest cost
        # silver plan for a given zipcode.
        cleaned_zipcode_data = clean_zipcode_rate_areas(input_zipcode_data)
        cleaned_plan_data = clean_plan_rates(input_plan_data)

        # Prepare the data for final output.
        prepared_slcsp_output = prepare_slcsp_output(
            input_slcsp_zipcodes,
            cleaned_zipcode_data,
            cleaned_plan_data
        )

        # Check that the expected output matches what was produced with the
        # prepared output.
        self.assertEqual(expected_output, prepared_slcsp_output)


# Execute the test suite when run from the command line.
if __name__ == '__main__':
    unittest.main(verbosity=2)
