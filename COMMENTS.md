# EXERCISE INSTRUCTIONS AND INFORMATION

This file provides additional instructions and details for getting setup to run
the script and/or its tests, and explains the rationale behind the approach
taken along with specific implementation notes.


## DETAILED PREREQUISITE SETUP INSTRUCTIONS

For this script to work, you must have Python version 3.7+ installed on your
computer.

You can download Python from https://www.python.org/downloads/ or by following
your operating system's package manager instructions if it has one.  If you
download Python from the Python homepage, please follow the setup instructions
in the documentation (https://docs.python.org/3/using/index.html) for the
version you downloaded for your specific operating system.

You can also leverage a tool like PyEnv (https://github.com/pyenv/pyenv) - or
pyenv-win for Windows (https://github.com/pyenv-win/pyenv-win) - to help manage
Python versions on your system without disrupting your operating system's
default installation.  Please see the respective repositories for installation
and usage instructions of these tools.

Once you have Python installed, there is no other setup needed.  This script is
entirely self-contained and uses modules only found in the standard library.
There are no external dependencies to download and manage and no virtual
environments to configure and manage.


## DETAILED SCRIPT SETUP AND USAGE INSTRUCTIONS

To run this script, open a console/terminal/shell window and navigate to the
directory you downloaded or cloned this repository into.  For example, if you
downloaded this repository into your `C:\Downloads` folder on a Windows machine,
open a PowerShell window and run the following command:

```
cd C:\Downloads\slcsp
```

If you are working in MacOS or any other UNIX-style machine and you downloaded
this repository to your `~/Downloads` directory, open a Terminal
window or load your command prompt and run the following command:

```
cd ~/Downloads/slcsp
```

Depending on how you retrieved the files, you may have to also unzip them.  Use
your operating systems unarchiving utility to do this and extract the files in
the same directory.  This will preserve the directory structure needed to
properly run everything.

With everything in place in the directory you have copied everything to, you can
now run the script with the following command:

```
python slcsp.py
```

_NOTE: `python` may be called something else on your machine, e.g., `python3`,
depending on how you have it installed and configured; please be sure to use the
`python` command that corresponds to your particular setup._

If you would like to run the tests, you can do so with this command:

```
python tests.py
```

The tests are configured to run with verbose output automatically.


## IMPLEMENTATION NOTES AND DETAILS

For the purposes of this assignment and exercise, there was an explicit
requirement for code brevity.  With this in mind, I opted to keep everything as
bare bones and simple as possible, and thankfully Python provides all of the
tools to do this out of the box.

I deliberately chose not to pull in any external dependencies to keep the setup
and usage as simple as possible, as I had everything I needed with just a few
modules.

If this were a script being created for a production use-case or integrated into
a larger production system, I may have reached for a couple of other things to
bolster its robustness, particularly with testing.

Additionally, I may have implemented this a little differently, such as creating
classes for data objects where state needed to be managed if necessary and
providing more flexibility for customization and accounting for a more general
use case: e.g., allowing a user to provide one or more plan levels to calculate
different kinds of plan rates for a zipcode, or writing the output to a file or
somewhere else.

In the case of what is essentially an ETL (Extract-Transform-Load) exercise
though, I felt that a few hardcoded values based on the specific exercise
requirements and simple, well-composed functions called in a specific order was
the quickest and most concise way to implement a solution for this exercise and
fulfill the desired requirements.


### Retrieving and setting the header row fields in the original slcsp.csv input

The `csv.DictReader.fieldnames` public property
(https://docs.python.org/3/library/csv.html#csv.DictReader)
has a weird quirk with it (at least when working with a CSV file in a context
manager on Windows) where you cannot copy and store its values, even when
leveraging `copy.deepcopy()`.

In the `load_slcsp_csv()` method, all I wanted to do is this before looping
through each record in the file:

```python
SLCSP_OUTPUT_FIELD_NAMES = slcsp_reader.fieldnames
```

Or at least this:

```python
SLCSP_OUTPUT_FIELD_NAMES = copy.deepcopy(slcsp_reader.fieldnames)
```

Neither of those will store the header fields, though, as the list will end up
being empty once the function finishes executing. There is a scoping issue where
the `fieldname` property gets cleared out that I have never been able track down
the details for, but I have come across this particular behavior in previous
work that involved CSV parsing.

Seeing as how this didn't work as I expected or desired, I opted to hardcode the
field names from the input file instead to match them for the output as the
simplest solution I could think of.  For a more robust solution, this could be
made configurable by adding support for a command line argument to take in a
header row or a list of field names.
