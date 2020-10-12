# config.py

## What config.py Does

The config.py file allows the Lambda School Labs 26 Citrics Team A Data Scientist to choose whether to build the team Docker image and deploy to the team AWS application or build his personal Docker image and deploy to his own application.

## Using config.py

The simplest part of this;
in command line or terminal, simply type:

```
python preroutes_and_utilities/config.py
```

You should see a message in command line or terminal prompting you to enter your Docker ID:

```
Docker ID:
```

Simply input your Docker ID if building and pushing to your personal AWS app. If building and pushing to the team app, use *Aaron Watkins'* Docker ID **ekselan**.  In the former case, you'll be greeted with the following in command line or terminal:

```
Docker ID: YOUR_DOCKER_ID
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "YOUR_DOCKER_ID/labs26-citrics-ds-teama_web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ],
  "Command": "uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000"
}
writing to ./Dockerrun.aws.json
```

Double check that the Dockerrun.aws.json file is up to date, and you can proceed with pushing to docker and deploying to AWS.

### Resetting config.py

Two reset options are built into the config.py script, reset and reset team.

The former resets the DOCKER_ID parameter to the default, like so:

```
Docker ID: reset
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "DOCKER_ID/labs26-citrics-ds-teama_web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ],
  "Command": "uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000"
}
```

The latter resets the DOCKER_ID parameter to the team Docker ID, *ekselan*:

```
Docker ID: reset team
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "ekselan/labs26-citrics-ds-teama_web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ],
  "Command": "uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000"
}
```

### Exiting the program:

When prompted for the Docker ID, the following inputs will close the program without altering the .json file.

```
Docker ID: exit
```

or

```
Docker ID: quit
```

or 

```
Docker ID: q
```
```

# insert.py

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

# weather.py

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
python preroutes_and_utilities/weather.py 10007 90012 60602
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

# walk.py
The `walk.py` file is used to pull addresses from the Yelp API, and make fetches to the Walk Score API using these addresses. In order to gain a degree of generalization, this file fetches the maximum addresses from Yelp (50). Due to the Walk Score API having a 5,000 a day free API call limit, it was chosen to use a timer to maximize how many cities could be fetched in a day, and populates the database.

## Setup Instructions
Open accounts for Yelp API and Walk Score API. Ensure their API keys are stored in your environment variables.

### Dependencies
Ensure the following dependencies are installed, as listed in requirements.txt:
```
pandas
psycopg2
python-dotenv
```

## Running the walk.py file.

The esiest part of this README; ensure your database credentials as well as API keys are stored in environment variables, and just let the file run with:
```
python preroutes_and_utilities/walk.py
```