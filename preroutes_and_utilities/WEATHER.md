# Using the weather.py file

## Please read before using the weather.py file:)

The *weather.py* file is setup to pull data from the [World Weather Online API](https://www.worldweatheronline.com/developer/). The data from the API itself are stored in the data\weather directory along with information on the zipcodes of which locations statistics have already been pulled from the API.

## Instructions

### Open an Account for the API

Follow the instructions in the following [link](https://www.worldweatheronline.com/developer/) in order to create an account for use with the World Weather Online API.

### Packages

Before attempting to use the *weather.py* file, make sure to check that you have the correct versions of **python-dotenv** and **wwo_hist** as listed in the global requirements.txt file.

If not using a virtual environment or if using conda:
```
pip list
```

If using Pipenv

```
pipenv run pip list

python -m pipenv run pip list (if the former does not work)
```

As of the time of this writing the correct versions of these are

```
python-dotenv                      0.14.0
wwo-hist                           0.0.5
```

#### Installing Packages from requirements.txt file

If you using a Conda environment, entering

```
conda install --yes --file requirements.txt
```

in command line will ensure that the appropriate version of both packages
are installed on your local machine.

#### Individual Package Installation

If you are not installed and you are not using a virtual environment or are using Conda:
```
pip install python-dotenv==0.14.0
pip install wwo-hist==0.0.5
```

If the dependencies are already installed, and you are using Pipenv, simply activating the environment should do the trick.

Otherwise enter:

```
pipenv install python-dotenv==0.14.0
pipenv install wwo-hist==0.0.5
```

### Running the weather.py file

Before pulling any new data, PLEASE CONSULT THE LEXICON, lexicon.txt, in the data\weather directory to ensure that you do not duplicate a call which has been already made.

Assuming you have not opened your wallet and are just using the trial version of API, you will be limited to 500 API calls per day which adds up to data for three cities. The weather.py file is set up to ask if you choose to include more than three cities, but leaves the option open in case you did open your wallet.

The weather.py file is setup to take the zip codes of the given locale as system arguments.
For example, if I wanted to pull data for New York, Los Angeles, and Chicago I would run the file with the zip codes for each respective city as additional arguments like so:

```
python utilities/weather.py 10007 90012 60602
```

The script would then ask to input the names of each location IN ORDER. These inputs are then used to update the lexicon.

Let's see this in action:

```
10007 : location {user input}
```

Enter the name of the city

```
10007 : location New York
```

The script repeats this with each of the cities entered, appends them to the lexicon file, then proceeds to pull the data from the API.

**Important!** When the data are first pulled, they will be stored in the following format:

{zip code}.csv.
 
It is important for readability and consistency that these be changed to reflect the natural language name of the city in the following format:

{cityname}_{state id}.csv

For example: New York would initally read out as 10007.csv, but would need to be manually changed to new_york_ny.csv

**Also Important!** Even after following the steps above to retrieve data from the API, your job in still not done yet! These data you just pulled now exist in the data/weather directory as csv files, but in order for any files in the project directory to be able to recognize them when the DS API is deployed online, they need to be inserted into the database. To do this, follow the instructions for using the *insert.py* file in [its README](INSERT.md)