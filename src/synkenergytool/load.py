import json
import subprocess
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional


class Load(BaseModel):
    power: int = Field(description="The power being consumed")


@tool(parse_docstring=True)
def load_state(inverter_serial_number: Optional[int] = 0) -> Load:
    """
    Retrieves the load connected to a specified inverter.

    Args:
        inverter_serial_number (Optional[int], optional): The serial number of the inverter to query.
            Defaults to 0, which queries the default inverter.

    Returns:
        Load: An instance of the Load class containing the load power (`power`).
    """
    cmd = "synkctl load get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    load = {}
    load["power"] = json.loads(res.stdout)["totalPower"]

    return Load(**load)
