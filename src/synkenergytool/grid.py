import json
import subprocess
from pydantic import BaseModel, Field
from typing import Optional


class Grid(BaseModel):
    power: int = Field(description="The power being supplied from the electricity grid")
    isUp: bool = Field(description="Whether the electricity grid is up")


def grid_state(inverter_serial_number: Optional[int] = 0) -> Grid:
    """
    Retrieves the current grid state for a specified inverter.

    Args:
        inverter_serial_number (Optional[int], optional): The serial number of the inverter to query.
            Defaults to 0, which queries the default inverter.

    Returns:
        Grid: An instance of the Grid class containing the grid power (`power`) and relay status (`isUp`).
    """
    cmd = "synkctl grid get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    grid = {}
    grid["power"] = json.loads(res.stdout)["pac"]
    grid["isUp"] = json.loads(res.stdout)["acRealyStatus"] == 1

    return Grid(**grid)
