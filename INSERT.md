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