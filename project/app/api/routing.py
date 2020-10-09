from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/something")
async def get_something(
    something_id: int = Query(
        1,
        description="Some description"
    ),
    full: bool = Query(
        False,
        description="Some description"
    )
):
    # ... do some database queries or whatever
    return {"something_id": something_id, "full": full}

@router.get("/two_somethings")
async def get_two_somethings(
    something_id_1: int = Query(
        1,
        description="Some description"
    ),
    something_id_2: int = Query(
        2,
        description="Some description"
    ),
):
    one = await get_something(something_id_1)
    two = await get_something(something_id_2)
    return {"one": one, "two": two}