# API Directory

## Route Referencing

### Route Referencing Explained

Each route in the API is essentially a function. Since well written code often uses functions which reference other functions, enhancing readability, and often improving performance, the [weather_pred.py script](weather_pred.py) has implemented *route referencing* as explained in the schema below.

![API Schema](https://raw.githubusercontent.com/Lambda-School-Labs/Labs26-Citrics-DS-TeamA/master/data/whimsical/APISchema.png)

### Route Referencing Example

In order to help the  understand how to build his or her own script incorporating route referencing, below is a simple example with two routes in a single script.

```python
# project/app/api/routing_example.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/do_one_thing/{thing}")
async def do_one_thing(thing):
    return thing

@router.get("do_two_things/{thing1}_{thing2}")
async def do_two_things(thing1, thing2):
    thing1 = (await do_one_thing(thing1))
    thing2 = (await do_one_thing(thing2))
    return thing1, thing2
```

All the programmer need to to implement the route referencing example shown above, is to add ```await``` prior to the function being referenced from another route.

FastAPI is also rather efficient in that the *main.py* file where the API is actually run only requires the *router* for the entire script to be stated rather than a router for each individual route. In the example above, if your API consisted solely of the two routes contained in the *routing_example.py* script, the *main.py* file would look something like this.

```python
# project/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import routing_example

DESC_TEXT = "SOME DESCRIPTION"

app = FastAPI(
    title='SOME API',
    description=DESC_TEXT,
    version='3.0',
    docs_url='/',
)

app.include_router(routing_example.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)
```

**It's two for the price of one!**

## Pickling Predictive Models

Up to this point in the project, the Data Science Team had decided not to Pickle any of the predictive routes due to the fact that each model was for a completely different subset of data and corrosponding to a different city found in the found in the database. 

This is illustrated in the section of the [rental_pred.py] script where the model, *Exponential Smoothing*, is declared five times, once for each category of housing.

```python
for col in df.columns:
    s = ExponentialSmoothing(
        df[col].astype(np.int64),
            trend="add",
            seasonal="add",
            seasonal_periods=12
        ).fit().forecast(30)
```

Due to the fact that each data source used contained several hundered to several thousand cities each, pickling each model individually would prove to be a daunting task. Due to the potential for memory issues to occure, the **Labs 28 DS Team** taking over this project will likely need to find a scalable way to pickle and store these [**time series**](https://github.com/Lambda-School-Labs/Labs26-Citrics-DS-TeamA/blob/master/development/notebooks/tsa.ipynb) models. A slight modification to the API's predictive route schema would be in order, with a *pickle route*. These *pickle routes* would most likely involve using a third-party file-hosting service given their size.

![Pickle](https://raw.githubusercontent.com/Lambda-School-Labs/Labs26-Citrics-DS-TeamA/master/data/whimsical/Pickling.png)

### Potential Problems

Theoretically, the *pkl* files could be stored in a directory listed in the *.ebignore* in order to avoid memory issues, but this may make them inaccessable to the API itself.

Using *GitHub* and [*GitHub Large File Storage*](https://git-lfs.github.com/) as the third-party hosting service is an option, but Amazon Web Service may not recognize *LFS* - *Heroku doesn't.*

At this point, we are not certain whether the ElasticBeanstalk service is even capable of dealing with interfacing with third-party file-storage services (other than GitHub and Amazon RDS).