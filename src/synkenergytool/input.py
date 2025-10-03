import json
import subprocess
from pydantic import BaseModel, Field
from typing import Optional


class Input(BaseModel):
    power: int = Field(description="The power being produced by the input source")
    peakPower: int = Field(description="The peak power that the input can produce")


def input_state(inverter_serial_number: Optional[int] = 0) -> Input:
    """
    Retrieves the current input state (e.g. for solar panels) for a specified inverter.

    Executes shell commands to fetch input power and peak power values for the inverter
    identified by the given serial number. If no serial number is provided, defaults to 0.

    Args:
        inverter_serial_number (Optional[int]): The serial number of the inverter. Defaults to 0.

    Returns:
        Input: An Input object containing the current power and peak power values.
    """
    cmd = "synkctl input get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    input = {}
    input["power"] = json.loads(res.stdout)["pac"]

    cmd = "synkctl plant get"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    input["peakPower"] = int(json.loads(res.stdout)["totalPower"] * 1000)

    return Input(**input)
