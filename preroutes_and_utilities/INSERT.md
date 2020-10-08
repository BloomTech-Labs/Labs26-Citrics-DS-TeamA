# Using the insert.py file

## Please read before using the insert.py file:)

The *insert.py* file is setup to insert data pulled from the [World Weather Online API](https://www.worldweatheronline.com/developer/) into the project's PostgreSQL database.

## Instructions

### Packages

Before attempting to use the *insert.py* file, make sure to check you have downloaded the correct version of **psycopg2**.

If not using a virtual environment or if using conda:
```
pip list
```

If using Pipenv

```
pipenv run pip list

python -m pipenv run pip list (if the former does not work)
```

As of the time of this writing the correct version of the package is

```
psycopg2-binary==2.8.5
```

#### Installing Packages from requirements.txt file

If you using a Conda environment, entering

```
conda install --yes --file requirements.txt
```

in command line will ensure that the appropriate version of both packages
are installed on your local machine.

#### Individual Package Installation

If they are not installed and you are not using a virtual environment or are using Conda:
```
pip install psycopg2==2.8.5
```

If the dependencies are already installed, and you are using Pipenv, simply activating the environment should do the trick.

Otherwise enter:

```
pipenv install psycopg2==2.8.5
```

### Using insert.py

Unlike, the *weather.py* script, *insert.py* takes command-line input after running

```
python preroutes_and_utilities/insert.py
```

as opposed to command-line arguments.

The *insert.py* script also features instructions in the form of input prompts, like the one generated when running the program:

```
    Welcome to the Historical Weather Database Insertion Utility!

    If you would like to insert a city, simply type 'insert' in the prompt
    below, then type the city name and state abbreviation when prompted.

    If you would like to repopulate the database with all the historic data
    found in the data/weather directory, type 'populate'

    If you would like to reset the entire Historic Weather Database, simply
    type 'reset'.

    If you would like to reset only those data for a single city, type
    'reset city', then type the desired city name and state abbreviation
    when prompted.

    If you would like to retrieve data for a specific city, type 'retrieve'.
```

or the prompt shown when typing *'retrieve'*:

```
        Would you like to retrieve the records by city name, or by zipcode?
        For the former, type 'city';
        for the latter, type 'location'.
```

In order to leave the program, type, *'exit'*, *'quit'*, or  *'q'*, but be advised, your command line terminal window may close depending on which terminal you use.

**NOTE:** There is currently no way of directly exiting the program when prompted for a city name, state abbreviation, or location zip code, so if you desire to exit the program without querying the database or altering any of the data therein, simply type an invalid value in both boxes and the built in error messages will prevent the query from being executed.

**Important!**: Please be very, very cautious when using *'populate'*, *'reset'*, and  *'reset city'* commands as they may affect your fellow data scientists and the web development team who may be attempting to call information from the API, and by extension, the database. As an act of ettiquite, please inform your DS colleagues and, if relevant, the web team, whenever using any of these three commands.