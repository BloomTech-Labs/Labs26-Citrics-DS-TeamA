# Using the weather.py file

## PLEASE READ BEFORE TOUCHING THE weather.py FILE

The weather.py file is setup to pull data from the [World Weather Online API](https://www.worldweatheronline.com/developer/). The data from the API itself are stored in the data\weather directory along with information on the zipcodes of which locations statistics have already been pulled from the API.

## Instructions

Before attempting to use the weather.py file, make sure to check that you have the correct versions of **python-dotenv** and **wwo_hist** as listed in the global requirements.txt file (wwo-hist==0.0.5).

If not using a virtual environment or if using conda:
```
pip list
```

If using Pipenv

```
pipenv run pip list

python -m pipenv run pip list (if the former does not work.)
```

Before pulling any new data, PLEASE CONSULT THE LEXICON, lexicon.txt, in the data\weather directory to ensure that you do not duplicate a call which has been already made.