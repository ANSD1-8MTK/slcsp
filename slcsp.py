#!/env/python

"""
A Python script to retrieve the second lowest cost silver plan for a set of
zipcodes based on the SLCSP Ad Hoc homework exercise found here:
https://homework.adhoc.team/slcsp/

REQUIREMENTS:
- Python 3.7+

There is no need to install any additional modules or setup a virtual
environment.  This script is entirely self-contained and contains zero external
dependencies.

HOW TO USE THIS SCRIPT:

Run "python slcsp.py" (or whatever your Python executable is called - sometimes
it might be "python3") in a command line/terminal window within the same
directory that you have placed this script.
"""


import csv
import decimal
import re
import sys

from collections import OrderedDict


# Set the files that we need to load for the script to work; all files are
# expected to be in a "slcsp" subdirectory found in the same directory as this
# script.
PLAN_CSV_FILE = 'slcsp/plans.csv'
SLCSP_CSV_FILE = 'slcsp/slcsp.csv'
ZIPCODE_CSV_FILE = 'slcsp/zips.csv'


# Set some default values based on the data and exercise instructions:
# - A header row of "zipcode,rate"
# - Only Silver plans need to be accounted for and processed
# - If a rate cannot be found, use an empty string
# - Rates should always be displayed as a number with two decimal places
# - Zipcodes must be in a five digit format
SLCSP_OUTPUT_FIELD_NAMES = ['zipcode', 'rate']
DESIRED_METAL_LEVEL = re.compile('^silver$', re.IGNORECASE)
NO_RATE_VALUE = ''
FORMATTED_RATE = lambda rate: f'{decimal.Decimal(rate):.2f}'
EXPECTED_ZIPCODE_FORMAT = re.compile('^\d{5}$')


def filter_plan_metal_level(plan, desired_metal_level):
    """
    Checks to see if the given insurance plan matches the desired metal level.

    Requires the following:
    - An insurance plan dictionary
    - A desired metal level to check for

    Returns True if the insurance plan matches the desired metal level, False if
    not.
    """

    if desired_metal_level.fullmatch(plan['metal_level']) is not None:
        return True

    return False


def load_plans_csv(csv_file_path):
    """
    Load the plans CSV file into a dictionary.
    
    Requires a valid path to a CSV file.

    Returns a dictionary of plan data.
    
    This only retrieves silver level plans as the exercise specifically desires
    these rates only, so this helps keep the dictionary as small as possible.
    We do not need the Plan ID for this, either, so that information is
    ignored as well.

    During the initial load, we simply take in all of the data that we do need.
    There is a separate method to clean the data and remove duplicate values to
    simplify the checks for a second lowest cost rate.
    
    Dictionary structure:

    {
        (State, Rate Area): [
            silver rate,
            silver rate,
            silver rate,
            ...
        ],
        (State, Rate Area): [
            silver rate,
            silver rate,
            silver rate,
            ...
        ],
        ...
    }
    """

    plan_data = {}

    with open(csv_file_path, 'r') as plans:
        plan_reader = csv.DictReader(plans)

        # Loop through each insurance plan and check if the metal level is
        # Silver, as that is all that is desired for this exercise.  If it is,
        # set the rate area for the plan as the dictionary key and append the
        # rate to a list of silver plan rates for that key.
        for plan in plan_reader:
            if filter_plan_metal_level(plan, DESIRED_METAL_LEVEL):
                plan_key = (plan['state'], plan['rate_area'])

                # Check to see if the plan key already exists; if not, set it
                # and create a new empty list for it first.
                if plan_key not in plan_data.keys():
                    plan_data[plan_key] = []
            
                plan_data[plan_key].append(plan['rate'])

    return plan_data


def load_zips_csv(csv_file_path):
    """
    Load the zipcodes CSV file into a dictionary.

    Requires a valid path to a CSV file.
    
    Returns a dictionary of zipcode data.

    Zipcodes may appear in more than one rate area, and they may also appear in
    more than one county as well.  Neither the county codes or names are needed
    for this exercise to determine the rate areas or rates, so we ignore those
    to keep the dictionary as small as possible.

    During the initial load we take in all of the data that we do need.  There
    is a separate method to clean the data and remove duplicate rate areas for
    each zipcode to make sure we're accurately counting how many rate areas a
    zipcode appears in.

    Dictionary structure:

    {
        zipcode: [
            (State, Rate Area),
            (State, Rate Area),
            (State, Rate Area),
            ...
        ],
        zipcode: [
            (State, Rate Area),
            (State, Rate Area),
            (State, Rate Area),
            ...
        ],
        ...
    }
    """
   
    zipcode_data = {}

    with open(csv_file_path, 'r') as zipcodes:
        zipcode_reader = csv.DictReader(zipcodes)

        # Loop through each zipcode, set the zipcode as the dictionary key, and
        # append all rate areas that match the zipcode to its corresponding
        # list as tuples of state and rate area - (state, rate area).
        for zipcode in zipcode_reader:
            zipcode_key = zipcode['zipcode']

            # Check to see if the zipcode already exists; if not, set it and
            # create a new empty list for it first.
            if zipcode_key not in zipcode_data.keys():
                zipcode_data[zipcode_key] = []

            # Create the rate area tuple and then appened it to the list
            # associated with the matching zipcode.
            rate_area_tuple = (zipcode['state'], zipcode['rate_area'])
            zipcode_data[zipcode_key].append(rate_area_tuple)

    return zipcode_data


def load_slcsp_csv(csv_file_path):
    """
    Load the SLCSP CSV file into a list.

    Requires a valid path to a CSV file.

    Returns a list of zipcodes.

    This is the file that is used to drive the processing for all of the second
    lowest cost silver plan that are desired with its given zipcodes.  It also
    provides the structure and order we need to use when outputting the final
    result back to STDOUT (the console/shell).

    We only retrieve the zipcodes since there are no rates in the input file,
    and we store them in a list to preserve the order they are in so it can be
    matched in the output at the end.

    List structure:

    [
        zipcode,
        zipcode,
        zipcode,
        ...
    ]
    """

    slcsp_zipcodes = []

    with open(csv_file_path, 'r') as slcsp:
        slcsp_reader = csv.DictReader(slcsp)

        for data in slcsp_reader:
            slcsp_zipcodes.append(data['zipcode'])

    return slcsp_zipcodes


def clean_zipcode_rate_areas(zipcode_data = {}):
    """
    Cleans the rate areas in zipcodes to ensure that only unique values are
    present for each zipcode.  This makes it very easy to determine if a zipcode
    is present in a single rate area.

    Requires a dictionary of zipcode data.

    Returns the cleaned zipcode data in a dictionary that matches the original
    structure.
    """

    cleaned_zipcode_data = {}

    for zipcode, rate_areas in zipcode_data.items():
        cleaned_zipcode_data[zipcode] = list(set(rate_areas))

    return cleaned_zipcode_data


def clean_plan_rates(plan_data = {}):
    """
    Cleans the plan rates so that only unique values are present, and those
    values are sorted from smallest to largest.  This makes it easy to determine
    if there are enough silver plan rates to retrieve a second lowest cost rate.

    Requires a dictionary of plan data.

    Returns the cleaned plan rates in a dictionary that matches the original
    structure.
    """

    cleaned_plan_data = {}

    for rate_area, rates in plan_data.items():
        cleaned_plan_data[rate_area] = sorted(list(set(rates)))

    return cleaned_plan_data


def retrieve_slcsp_for_zipcode(
    zipcode,
    cleaned_zipcode_data = {},
    cleaned_plan_data = {}
):
    """
    Retrieves the second lowest cost silver plan for a given zipcode, if one can
    be found.

    Requires the following:
    - A zipcode string in 5 digit format (e.g, "12345")
    - A dictionary of cleaned zipcode data
    - A dictionary of cleaned plan data

    Returns the rate if one is successfully found formatted to two decimal
    places, otherwise returns an empty string.
    """

    # Make sure the zipcode is a string.
    zipcode = str(zipcode)

    # Check that the zipcode is in the proper 5 digit format; if not, return an
    # empty string as we cannot lookup the zipcode.
    if EXPECTED_ZIPCODE_FORMAT.fullmatch(zipcode) is None:
        return NO_RATE_VALUE

    # Retrieve all of the rate areas for the given zipcode; default to an empty
    # list if no rate areas can be retrieved.
    zipcode_rate_areas = cleaned_zipcode_data.get(zipcode, [])

    # If the zipcode is present in no rate areas or more than 1 rate area, we
    # cannot accurately determine the rate area.  We must return an empty string
    # for the SLCSP rate in this case.
    if len(zipcode_rate_areas) != 1:
        return NO_RATE_VALUE

    # If a rate area for the zipcode could be found, retrieve all of the silver
    # plan rates for it; default to an empty string if no silver plan rates
    # could be retrieved for the zipcode.
    plan_rates = cleaned_plan_data.get(zipcode_rate_areas[0], [])

    # If less than 2 silver plan rates were found, there is no second lowest
    # cost rate available, so we must return an empty string for the SLCSP rate.
    if len(plan_rates) < 2:
        return NO_RATE_VALUE

    # If a matching set of silver plan rates were found for the zipcode and
    # there were at least 2 rates available, we can return the second lowest
    # cost silver plan rate.

    # The rates are unique and sorted from smallest to largest at this point, so
    # we can pull directly from the second spot in the list for this value.
    # Return the value formatted with two decimal places for the desired output.
    return FORMATTED_RATE(plan_rates[1])


def prepare_slcsp_output(
    slcsp_zipcodes = [],
    cleaned_zipcode_data = {},
    cleaned_plan_data = {}
):
    """
    Prepares the data for final output for the Second Lowest Cost Silver Plan
    exercise.

    Requires the following:
    - A list of zipcodes in 5 digit format (e.g., ['11111', '22222', ...])
    - A dictionary of cleaned zipcode data
    - A dictionary of cleaned plan data

    Returns an ordered dictionary of prepared output consisting of zipcodes
    mapped to rates in the same order as the original input.

    Dictionary structure:

    {
        zipcode: rate,
        zipcode: rate,
        zipcode: rate,
        ...
    }
    """

    prepared_slcsp_output = OrderedDict()

    # Retrieve the second lowest cost silver plan rates for each zipcode in the
    # original dataset and place it in a dictionary with its matching rate to
    # prepare it for final output.
    for zipcode in slcsp_zipcodes:
        rate = retrieve_slcsp_for_zipcode(
            zipcode,
            cleaned_zipcode_data,
            cleaned_plan_data
        )

        prepared_slcsp_output[zipcode] = rate

    return prepared_slcsp_output


def print_slcsp_for_zipcodes(prepared_slcsp_output = OrderedDict()):
    """
    Prints the Second Lowest Cost Silver Plan for a given zipcode to STDOUT as
    asked for by the exercise instructions.

    As a part of the output, the rates are formatted to two decimal places.

    Requires an ordered dictionary of prepared output.
    """

    # Prepare to write the CSV output to STDOUT by setting up the CSV writer and
    # writing the header row with the same fields as the input.
    slcsp_writer = csv.DictWriter(
        sys.stdout,
        fieldnames=SLCSP_OUTPUT_FIELD_NAMES
    )
    slcsp_writer.writeheader()

    # Retrieve the second lowest cost silver plan rates for each zipcode in the
    # original dataset and write the data to STDOUT.  For any zipcode where the
    # second lowest cost silver plan rate could not be found, print an empty
    # string.
    for zipcode, rate in prepared_slcsp_output.items():
        slcsp_writer.writerow({
            'zipcode': zipcode,
            'rate': rate
        })


# If run from the command line, execute the script.
if __name__ == '__main__':
    # Load all of the data from each file in the exercise for processing.
    plan_data = load_plans_csv(PLAN_CSV_FILE)
    zipcode_data = load_zips_csv(ZIPCODE_CSV_FILE)
    slcsp_zipcodes = load_slcsp_csv(SLCSP_CSV_FILE)

    # Clean the data to prepare it for calculating the second lowest cost silver
    # plan for a given zipcode.
    cleaned_zipcode_data = clean_zipcode_rate_areas(zipcode_data)
    cleaned_plan_data = clean_plan_rates(plan_data)

    # Prepare the data for final output.
    prepared_slcsp_output = prepare_slcsp_output(
        slcsp_zipcodes,
        cleaned_zipcode_data,
        cleaned_plan_data
    )

    # Output the results in the order and format asked for in the instructions
    # to STDOUT.
    print_slcsp_for_zipcodes(prepared_slcsp_output)
