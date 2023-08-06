from datetime import date
from pydantic import condecimal
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING, List, Optional

from .sa_helpers import ForeignKeyConstraint


if TYPE_CHECKING:  # pragma: no cover
    from . import ResultsSet  # noqa: F401


"""
Results set session-level details

The models related to all road segment results from a measurement session. The
top-level model is the ResultsSetSessionDetails model.

"""


class SessionDetails(SQLModel, table=True):
    """
    Contains the measurement session level details associated with the results
    set.
    """

    __tablename__ = "session_details"

    results_set_id: int = Field(
        default=None,
        foreign_key="results_set.id",
        primary_key=True,
    )
    wheel_bay_details: List["SessionWheelBayDetails"] = Relationship()


class SessionWheelBayDetails(SQLModel, table=True):
    """
    Session-level wheel bay details for a given results set. Each results set
    can have up to two wheel bay entries.
    """

    __tablename__ = "session_wheel_bay_details"

    results_set_id: Optional[int] = Field(
        default=None,
        foreign_key="session_details.results_set_id",
        primary_key=True,
    )
    wheel_bay_name: str = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    wheel_bay_configuration_details: str = Field(
        nullable=False,
        description="description of the wheel bay configuration",
    )
    wheel_bay_calibration_date: date = Field(
        nullable=False, description="wheel bay / device correction calibration date"
    )
    microphone_details: List["SessionMicrophoneDetails"] = Relationship()
    accelerometer_details: List["SessionAccelerometerDetails"] = Relationship()
    tyre_details: "TyreDetails" = Relationship(
        sa_relationship_kwargs={"uselist": False},
    )
    device_corrections: List["DeviceCorrection"] = Relationship()


class SessionMicrophoneDetails(SQLModel, table=True):
    """
    Session-level microphone details.

    """

    __tablename__ = "session_microphone_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "wheel_bay_name"],
            [
                "session_wheel_bay_details.results_set_id",
                "session_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: str = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    microphone_position: int = Field(
        primary_key=True,
        description="microphone position (1-6) as per ISO 11819-2:2017",
    )
    microphone_serial_number: str = Field(
        nullable=False,
        description="microphone serial number",
    )
    microphone_sensitivity_mv_pa: condecimal(
        max_digits=4,
        decimal_places=2,
    ) = Field(
        nullable=False,
        description="microphone sensitivity in mV/Pa",
    )
    microphone_calibration_date: date = Field(
        nullable=False,
        description="microphone calibration date",
    )
    wav_file_channel_number: int = Field(
        nullable=False,
        description=(
            "channel number in the wav file corresponding to the microphone " "position"
        ),
    )
    used_in_wheel_bay_results: bool = Field(
        nullable=False,
        description=(
            "whether the microphone position was used when calculating the "
            "wheel bay results"
        ),
    )


class SessionAccelerometerDetails(SQLModel, table=True):
    __tablename__ = "session_accelerometer_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "wheel_bay_name"],
            [
                "session_wheel_bay_details.results_set_id",
                "session_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: str = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    accelerometer_position: str = Field(
        primary_key=True,
        description="accelerometer position ('chassis' or 'axle')",
    )
    accelerometer_sensitivity_mv_g: condecimal(
        max_digits=5,
        decimal_places=2,
    ) = Field(
        nullable=False,
        description="accelerometer sensitivity in mV/g",
    )
    wav_file_channel_number: int = Field(
        nullable=False,
        description=(
            "channel number in the wav file corresponding to the accelerometer"
        ),
    )


class TyreDetails(SQLModel, table=True):
    """
    Tyre details for a given wheel bay. Sub-model of the SessionWheelBayDetails
    model.

    """

    __tablename__ = "tyre_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "wheel_bay_name"],
            [
                "session_wheel_bay_details.results_set_id",
                "session_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: str = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    tyre: str = Field(
        nullable=False,
        description="tyre name/type (e.g. 'P1', 'H1', etc.)",
    )
    tyre_purchase_date: date = Field(
        nullable=False,
        description="tyre purchase date",
    )
    reference_hardness: int = Field(
        nullable=False,
        description="reference tyre hardness in Shore A",
    )
    hardness: condecimal(max_digits=3, decimal_places=1) = Field(
        nullable=False,
        description="tyre hardness in Shore A",
    )
    hardness_date: date = Field(
        nullable=False,
        description="tyre hardness measurement date",
    )
    hardness_correction_coefficient: condecimal(
        max_digits=3,
        decimal_places=2,
    ) = Field(
        nullable=False,
        description="tyre hardness correction coefficient",
    )
    hardness_correction_db: float = Field(
        nullable=False,
        description="tyre hardness correction value in dB",
    )


class DeviceCorrection(SQLModel, table=True):
    """
    Device corrections used when calculating LCPX (as per ISO 11819-2:2017
    A.2). Each row represents a single wheel bay / frequency combination, so
    there will be multiple rows that apply to each wheel bay.
    """

    __tablename__ = "device_correction"
    __table_args__ = (
        ForeignKeyConstraint(
            ["results_set_id", "wheel_bay_name"],
            [
                "session_wheel_bay_details.results_set_id",
                "session_wheel_bay_details.wheel_bay_name",
            ],
        ),
    )

    results_set_id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    wheel_bay_name: str = Field(
        primary_key=True,
        description="wheel bay name ('left' or 'right')",
    )
    frequency_hz: condecimal(max_digits=6, decimal_places=1) = Field(
        primary_key=True,
        description="one-third octave band centre frequency in Hz",
    )
    correction_db: float = Field(
        description="device correction in dB",
    )
