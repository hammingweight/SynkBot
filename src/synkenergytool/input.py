import json
import subprocess
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, Union
from .errors import Error


class Input(BaseModel):
    power: int = Field(description="The power being produced by the input source")
    peakPower: int = Field(description="The peak power that the input can produce")


@tool(parse_docstring=True)
def input_state(inverter_serial_number: Optional[int] = 0) -> Union[Input, Error]:
    """
    Retrieves the current input state (e.g. for solar panels) for a specified inverter.

    Executes shell commands to fetch input power and peak power values for the inverter
    identified by the given serial number. If no serial number is provided, defaults to 0.

    Args:
        inverter_serial_number (Optional[int]): The serial number of the inverter. Defaults to 0.

    Returns:
        Union[Input, Error]: Either an Input object or an Error if the request failed. An Input
        object contains the current power and peak power values.
    """
    cmd = "synkctl input get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        message = res.stderr.split("\n")[0]
        return Error(message=message)

    input = {}
    input["power"] = json.loads(res.stdout)["pac"]

    cmd = "synkctl plant get"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        message = res.stderr.split("\n")[0]
        return Error(message=message)

    input["peakPower"] = int(json.loads(res.stdout)["totalPower"] * 1000)
    return Input(**input)
