from pydantic import condecimal
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING, List, Optional

from .sa_helpers import ForeignKeyConstraint


if TYPE_CHECKING:  # pragma: no cover
    from . import ResultsSet  # noqa: F401


"""
Results set segment-level details

"""


class SegmentDetails(SQLModel, table=True):
    """
    Contians the segment level details associated with the results set.

    """

    __tablename__ = "segment_details"

    results_set_id: Optional[int] = Field(
        default=None,
        foreign_key="results_set.id",
    )
    segment_id: int = Field(
        primary_key=True,
    )
    wav_path: str = Field(
        nullable=False,
        description=(
            "path to the wav file associated with the segment result "
            "(relative to the SharePoint measurement files folder)"
        ),
    )
    run_number: int = Field(
        nullable=False,
        description=(
            "run number as per the measurement files. This cannot be relied "
            "on when determining the number of runs across a given road "
            "segment. Instead, count the number of unique "
            "road_id/start_m/end_m/lane_number combinations assocated with "
            "the results set."
        ),
    )
    run_segment_count: int = Field(
        nullable=False,
        description=(
            "the run segment counter as per the measurement files. This "
            "is used to indicate a pause in a run. This cannot be relied "
            "on when determining the number of runs across a given road "
            "segment. Instead, count the number of unique "
            "road_id/start_m/end_m/lane_number combinations assocated with "
            "the results set."
        ),
    )
    road_id: int = Field(
        nullable=False,
        description="RAMM road ID",
    )
    start_m: float = Field(
        nullable=False,
        description=(
            "start position of the road segment in metrers (RAMM route " "position)"
        ),
    )
    end_m: float = Field(
        nullable=False,
        description=(
            "end position of the road segment in metres (RAMM route position)"
        ),
    )
    length_m: float = Field(
        nullable=False,
        description="length of the road segment in metres",
    )
    lane: str = Field(
        nullable=False,
        description="RAMM lane number (e.g. 'L1', 'L2', 'R1', 'R2', etc)",
    )
    start_sample: int = Field(
        nullable=False,
        description=(
            "wav sample number corresponding to the start of the road segment"
        ),
    )
    end_sample: int = Field(
        nullable=False,
        description=("wav sample number corresponding to the end of the road segment"),
    )
    speed_kph: float = Field(
        nullable=False,
        description="average speed across the road segment in km/h",
    )
    air_temperature: float = Field(
        nullable=False,
        description=("average air temperature across the road segment in degrees C"),
    )
    speed_correction_db: float = Field(
        nullable=False,
        description="speed correction in dB",
    )
    temperature_correction_db: float = Field(
        nullable=False,
        description="temperature correction in dB",
    )
    start_latitude: float = Field(
        nullable=False,
        description="latitude of segment start point",
    )
    start_longitude: float = Field(
        nullable=False,
        description="longitude of segment start point",
    )
    end_latitude: float = Field(
        nullable=False,
        description="latitude of segment end point",
    )
    end_longitude: float = Field(
        nullable=False,
        description="longitude of segment end point",
    )
    passing_truck_flag: Optional[bool] = Field(
        default=False,
        description="passing truck",
    )
    other_flag: Optional[bool] = Field(
        default=False,
        description="other flag",
    )
    valid: bool = Field(
        nullable=False,
        description=(
            "indicated whether the road segment results are valid or not, "
            "based on the speed and any event flags"
        ),
    )
    wheel_bay_details: List["SegmentWheelBayDetails"] = Relationship()


class SegmentWheelBayDetails(SQLModel, table=True):
    """
    Wheel bay details for a given road segment.
    """

    __tablename__ = "segment_wheel_bay_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "segment_id"],
            ["segment_details.results_set_id", "segment_details.segment_id"],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    segment_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: str = Field(
        primary_key=True,
        description="wheel_bay name ('left' or 'right')",
    )
    ir_temperatures: List["IRTemperature"] = Relationship()
    microphone_details: List["SegmentMicrophoneDetails"] = Relationship()
    wheel_bay_third_octave_levels: List["WheelBayThirdOctaveLevels"] = Relationship()
    laeq_db: Optional[float] = Field(
        default=None,
        description="LAeq for the wheel bay in dB (no CPX corrections applied)",
    )
    lcpx_db: Optional[float] = Field(
        default=None,
        description="LCPX for the wheel bay in dB",
    )


class IRTemperature(SQLModel, table=True):
    """
    Average tyre or road temperature across a road segment for a wheel bay
    from the infrared temperature sensors.
    """

    __tablename__ = "ir_temperature"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "segment_id", "wheel_bay_name"],
            [
                "segment_wheel_bay_details.results_set_id",
                "segment_wheel_bay_details.segment_id",
                "segment_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    segment_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: Optional[str] = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    type: str = Field(
        primary_key=True,
        description="temperature type ('tyre' or 'road')",
    )
    temperature: float = Field(
        nullable=False,
        description="temperature in degrees C",
    )


class SegmentMicrophoneDetails(SQLModel, table=True):
    """
    Microphone details for a given road segment.
    """

    __tablename__ = "segment_microphone_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "segment_id", "wheel_bay_name"],
            [
                "segment_wheel_bay_details.results_set_id",
                "segment_wheel_bay_details.segment_id",
                "segment_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    segment_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: Optional[str] = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    microphone_position: int = Field(
        primary_key=True,
        description="microphone position (1-6) as per ISO 11819-2:2017",
    )
    laeq_db: float = Field(
        nullable=False,
        description="LAeq for the microphone position in dB (no CPX corrections applied)",
    )
    microphone_third_octave_levels: List["MicrophoneThirdOctaveLevels"] = Relationship()


class MicrophoneThirdOctaveLevels(SQLModel, table=True):
    """
    One-third octave band sound pressure levels for each microphone position
    in the wheel bay, measured across one road segment.
    """

    __tablename__ = "microphone_third_octave_levels"
    __table_args__ = (
        ForeignKeyConstraint(
            [
                "results_set_id",
                "segment_id",
                "wheel_bay_name",
                "microphone_position",
            ],
            [
                "segment_microphone_details.results_set_id",
                "segment_microphone_details.segment_id",
                "segment_microphone_details.wheel_bay_name",
                "segment_microphone_details.microphone_position",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    segment_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: Optional[str] = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    microphone_position: int = Field(
        primary_key=True,
        description="microphone position (1-6) as per ISO 11819-2:2017",
    )
    frequency_hz: condecimal(max_digits=6, decimal_places=1) = Field(
        primary_key=True,
        description="one-third octave band centre frequency in Hz",
    )
    leq_db: float = Field(
        nullable=False,
        description="microphone Leq in dB across the road segment",
    )
    laeq_db: float = Field(
        nullable=False,
        description="microphone LAeq in dB across the road segment",
    )


class WheelBayThirdOctaveLevels(SQLModel, table=True):
    __tablename__ = "wheel_bay_third_octave_levels"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "segment_id", "wheel_bay_name"],
            [
                "segment_wheel_bay_details.results_set_id",
                "segment_wheel_bay_details.segment_id",
                "segment_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    segment_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: Optional[str] = Field(
        primary_key=True,
        description="wheel_bay name ('left' or 'right')",
    )
    frequency_hz: condecimal(max_digits=6, decimal_places=1) = Field(
        primary_key=True,
        description="one-third octave band centre frequency in Hz",
    )
    leq_db: float = Field(
        nullable=False,
        description=(
            "energy-based average of the one-third octave Leq of all "
            "microphone positions within the enclosure in dB. Calculated by "
            "subtracting the A weighting from the one-third octave LAeq (see "
            "'laeq_db' field) for the wheel bay."
        ),
    )
    laeq_db: float = Field(
        nullable=False,
        description=(
            "energy-based average of the one-third octave LAeq of all "
            "microphone positions within the enclosure in dB (refer ISO "
            "11819-2:2017 Formula C.1 / C.7)"
        ),
    )
    lcpx_db: float = Field(
        nullable=False,
        description=(
            "one-third octave LCPX with all corrections applied (including "
            "the device-related correction) in dB (refer ISO 11819-2:2017 "
            "Formula C.8 and C.9)"
        ),
    )
