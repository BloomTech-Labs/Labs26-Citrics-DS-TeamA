from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import (
    adv_search,
    bls_jobs1,
    bls_viz,
    bls_viz_view,
    census,
    census_pred,
    current,
    rent_city_states,
    rental1,
    rental_pred,
    rentviz2,
    static,
    viz,
    walkability,
    weather_pred
)

# Description Text
DESC_TEXT = "Finding a place to live is hard! Nomads struggle with finding the right city for them. Citrics is a city comparison tool that allows users to compare cities and find cities based on user preferences."

app = FastAPI(
    title='Citrics API',
    description=DESC_TEXT,
    version='2.9',
    docs_url='/',
)

app.include_router(adv_search.router)
app.include_router(bls_jobs1.router)
app.include_router(bls_viz.router)
app.include_router(bls_viz_view.router)
app.include_router(census.router)
app.include_router(census_pred.router)
app.include_router(current.router)
app.include_router(rent_city_states.router)
app.include_router(rental1.router)
app.include_router(rental_pred.router)
app.include_router(rentviz2.router)
app.include_router(static.router)
app.include_router(viz.router)
app.include_router(walkability.router)
app.include_router(weather_pred.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)
