import logging
from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ForceParameters(BaseModel):
    """Pydantic model of force supported parameters."""

    input_files: list[str]
    user_workspace: Path
    dem_file: str
    dem_nodata: int = Field(default=-9999)
    do_atmo: Union[str, bool] = Field(default="TRUE", regex=r"(?i)(TRUE|FALSE)")
    do_topo: Union[str, bool] = Field(default="TRUE", regex=r"(?i)(TRUE|FALSE)")
    do_brdf: Union[str, bool] = Field(default="TRUE", regex=r"(?i)(TRUE|FALSE)")
    adjacency_effect: Union[str, bool] = Field(
        default="TRUE", regex=r"(?i)(TRUE|FALSE)"
    )
    multi_scattering: Union[str, bool] = Field(
        default="TRUE", regex=r"(?i)(TRUE|FALSE)"
    )
    erase_clouds: Union[str, bool] = Field(default="TRUE", regex=r"(?i)(TRUE|FALSE)")
    max_cloud_cover_frame: int = Field(default=90, ge=0, le=100)
    max_cloud_cover_tile: int = Field(default=100, ge=0, le=100)
    cloud_buffer: float = Field(default=300, ge=0, le=10000)
    cirrus_buffer: float = Field(default=0, ge=0, le=10000)
    shadow_buffer: float = Field(default=90, ge=0, le=10000)
    snow_buffer: float = Field(default=30, ge=0, le=1000)
    cloud_threshold: float = Field(default=0.225, ge=0, le=1)
    shadow_threshold: float = Field(default=0.02, ge=0, le=1)
    res_merge: str = Field(
        default="IMPROPHE", regex=r"(?i)(REGRESSION|IMPROPHE|STARFM|NONE)"
    )
