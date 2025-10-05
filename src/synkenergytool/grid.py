import json
import subprocess
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, Union
from .errors import Error


class Grid(BaseModel):
    power: int = Field(description="The power being supplied from the electricity grid")
    isUp: bool = Field(description="Whether the electricity grid is up")


@tool(parse_docstring=True)
def grid_state(inverter_serial_number: Optional[int] = 0) -> Union[Grid, Error]:
    """
    Retrieves the current grid state for a specified inverter.

    Args:
        inverter_serial_number (Optional[int], optional): The serial number of the inverter to query.
            Defaults to 0, which queries the default inverter.

    Returns:
        Union[Grid, Error]: Either a Grid object containing the grid state information, or an Error object
        if the request failed. A  Grid object contains the grid power (`power`) and relay status (`isUp`).
    """
    cmd = "synkctl grid get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        message = res.stderr.split("\n")[0]
        return Error(message=message)

    grid = {}
    grid["power"] = json.loads(res.stdout)["pac"]
    grid["isUp"] = json.loads(res.stdout)["acRealyStatus"] == 1

    return Grid(**grid)
