from datetime import date as date_
import json
from typing import Literal, Optional
from pydantic import BaseModel, Field


class MicrophoneDetails(BaseModel):
    microphone_position: int = Field(
        description="microphone position (1-6) as per ISO 11819-2:2017",
    )
    microphone_serial_number: str = Field(
        description="microphone serial number",
    )
    microphone_sensitivity_mv_pa: float = Field(
        description="microphone sensitivity in mV/Pa",
    )
    microphone_calibration_date: date_ = Field(
        description="microphone calibration date",
    )
    wav_file_channel_number: int = Field(
        description=(
            "channel number in the wav file corresponding to the microphone " "position"
        ),
    )


class AccelerometerDetails(BaseModel):
    accelerometer_position: Literal["chassis", "axle"] = Field(
        description="accelerometer position ('chassis' or 'axle')",
    )
    accelerometer_sensitivity_mv_g: float = Field(
        description="accelerometer sensitivity in mV/g",
    )
    wav_file_channel_number: int = Field(
        description=(
            "channel number in the wav file corresponding to the accelerometer"
        ),
    )


class TyreDetails(BaseModel):
    tyre: str = Field(
        description="tyre name/type (e.g. 'P1', 'H1', etc.)",
    )
    tyre_purchase_date: date_ = Field(
        description="tyre purchase date",
    )
    hardness: float = Field(
        description="tyre hardness in Shore A",
    )
    hardness_date: date_ = Field(
        description="tyre hardness measurement date",
    )


class DeviceCorrections(BaseModel):
    frequency_hz: list[float] = Field(
        description="list third-octave band centre frequencies in Hz",
    )
    correction_db: list[float] = Field(
        description="list of device corrections in dB",
    )


class MeasurementDetails(BaseModel):
    date: date_ = Field(
        description="date of measurement",
    )
    location: str = Field(
        description="location of measurement",
    )
    purpose: str = Field(
        description="purpose of measurement",
    )
    operator_name: str = Field(
        description="name of CPX trailer operator",
    )
    tow_vehicle: str = Field(
        description="tow vehicle details and licence plate number",
    )
    target_speed_kph: int = Field(
        description="target speed in km/h",
    )
    wheel_track: Literal["left", "right", "both"] = Field(
        description="wheel track being measured (left, right, or both)",
    )
    hours_since_last_rain: int = Field(
        description="hours since last rain",
    )
    wav_scale: float = Field(
        description=(
            "scale factor to apply to the raw wav file data (-1 to + 1 range) "
            "to convert the data back into volts."
        ),
    )
    notes: str = Field(
        description="any additional notes",
    )


class WheelBayDetails(BaseModel):
    wheel_bay_name: Literal["left", "right"] = Field(
        description="wheel bay name ('left' or 'right')",
    )
    wheel_bay_configuration_details: str = Field(
        description="description of the wheel bay configuration",
    )
    wheel_bay_calibration_date: date_ = Field(
        description="wheel bay / device correction calibration date"
    )
    microphone_details: list["MicrophoneDetails"]
    accelerometer_details: Optional[list["AccelerometerDetails"]]
    tyre_details: "TyreDetails"
    device_corrections: "DeviceCorrections"


class Metadata(BaseModel):
    measurement_details: "MeasurementDetails"
    wheel_bay_details: list["WheelBayDetails"]

    def write(self, path: str):
        with open(path, "w") as f:
            f.write(self.json(indent=4))

    @staticmethod
    def read(path: str):
        with open(path, "r") as f:
            return Metadata.validate(json.load(f))
