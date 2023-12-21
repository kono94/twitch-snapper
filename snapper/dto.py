from pydantic import BaseModel


class StreamActiveUpdate(BaseModel):
    is_active: bool


class ClipRatingUpdate(BaseModel):
    rating: float
