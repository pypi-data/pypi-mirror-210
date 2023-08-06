from datetime import date
from pydantic import condecimal
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING, List, Optional

from . import session, segment  # noqa: F401

if TYPE_CHECKING:  # pragma: no cover
    from .session import SessionDetails
    from .segment import SegmentDetails


class MeasurementDetails(SQLModel, table=True):
    __tablename__ = "measurement_details"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    location: str
    purpose: str
    operator_name: str
    tow_vehicle: str
    target_speed_kph: int
    wheel_track: str
    hours_since_last_rain: int
    wav_scale: float = Field(
        default=None,
        description=(
            "scale factor to apply to the raw wav file data (-1 to + 1 range) "
            "to convert the data back into volts."
        ),
    )
    notes: str

    results_sets: List["ResultsSet"] = Relationship()


class ResultsSet(SQLModel, table=True):
    __tablename__ = "results_set"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="unique identifier for the results set",
    )
    measurement_details_id: int = Field(
        default=None,
        foreign_key="measurement_details.id",
    )
    software_version: str = Field(
        description=("processing software version used to generate the results set"),
    )
    segment_length_m: Optional[float] = Field(
        default=None,
        description=(
            "length of the road segment in metres. Set to None if results use "
            "a variable segment length."
        ),
    )
    reference_speed_kph: int = Field(
        nullable=False,
        description="reference speed in km/h",
    )
    speed_correction_coefficient: condecimal(max_digits=5, decimal_places=3) = Field(
        nullable=False,
        description="speed constant used to calculate speed correction",
    )
    reference_temperature: float = Field(
        nullable=False,
        description="reference temperature in degrees C",
    )
    temperature_correction_type: str = Field(
        nullable=False,
        description="temperature correction basis ('air', 'tyre' or 'road')",
    )
    temperature_correction_coefficient: condecimal(
        max_digits=5,
        decimal_places=4,
    ) = Field(
        nullable=False,
        description="temperature correction coefficient",
    )
    gps_acceleration_threshold_kph_sec: float = Field(
        description=(
            "threshold for determining if the GPS acceleration is valid in " "km/h/sec"
        ),
    )
    rsrp_database: str = Field(
        description="name of the RSRP database used to generate the results set",
    )
    rsrp_date: date = Field(
        description="date that the RSRP database was accessed",
    )
    notes: Optional[str] = Field(
        default=None,
        description="reason for the results set being generated",
    )
    include_in_map_service: bool = Field(
        default=True,
        description=("whether or not to include the results set in the map service"),
    )
    session_details: "SessionDetails" = Relationship(
        sa_relationship_kwargs={"uselist": False},
    )
    segment_details: List["SegmentDetails"] = Relationship()
