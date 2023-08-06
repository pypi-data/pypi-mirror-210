import logging
from pathlib import Path
from typing import Optional

import pyproj
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


DEFAULT_CRS = pyproj.CRS.from_user_input("EPSG:4326").to_wkt()


def parse_crs(v) -> pyproj.CRS:
    if v is None or v.strip() == "":
        return DEFAULT_CRS
    else:
        try:
            # Check that the crs can be parsed and store as WKT
            crs_obj = pyproj.CRS.from_user_input(v)
            return crs_obj.to_wkt()
        except pyproj.exceptions.CRSError as e:
            logger.error(
                f"Provided CRS {v} could not be parsed, defaulting to EPSG:4326"
            )
            raise e


def crs_validator(field: str) -> classmethod:
    decorator = validator(field, allow_reuse=True, pre=True, always=True)
    validator_func = decorator(parse_crs)
    return validator_func


class BoundingBox(BaseModel, arbitrary_types_allowed=True):
    west: float
    east: float
    north: float
    south: float
    base: Optional[float]
    height: Optional[float]
    crs: Optional[str]

    # validators
    _parse_crs: classmethod = crs_validator("crs")


class sen2like_options(BaseModel):
    doGeometry: Optional[bool] = True
    doStitching: Optional[bool] = True
    doGeometryCheck: Optional[bool] = True
    doToa: Optional[bool] = True
    doInterCalibration: Optional[bool] = True
    doAtmcor: Optional[bool] = True
    doNbar: Optional[bool] = True
    doSbaf: Optional[bool] = True


class Sen2LikeParameters(BaseModel):
    """Pydantic model of sen2like supported parameters."""

    spatial_extent: BoundingBox
    temporal_extent: list
    user_workspace: Path
    target_resolution: Optional[int] = 10
    target_product: Optional[str] = Field(regex=r"L2F|L2H|l2f|l2h", default="L2F")
    options: Optional[sen2like_options] = None

    @validator("target_resolution")
    def check_resolution(cls, v):
        if v not in [10, 20, 60]:
            raise ValueError("Resolution must be set to 10, 20 or 60.")
        return v
