import json
import subprocess
from pydantic import BaseModel, Field
from typing import Optional


class Inverter(BaseModel):
    ratedPower: int = Field(description="The maximum power (W) that the inverter can supply")
    power: int = Field(description="The power being supplied by the inverter")
    batteryMinimumSoCLimit: int = Field(description="The battery discharge limit")
    powerEssentialOnly: bool = Field(description="True if the inverter powers only non-essential loads")
    gridCharge: bool = Field(description="True if the battery can be recharged from the grid")


def inverter_settings(inverter_serial_number: Optional[int] = 0) -> Inverter:
    """
    Retrieves inverter load settings using the synkctl CLI tool.

    Args:
        inverter_serial_number (Optional[int], optional): Serial number of the inverter to query. Defaults to 0.

    Returns:
        Inverter: An Inverter object containing the following fields:
            - ratedPower (int): The maximum power (in watts) that the inverter can supply.
            - power (int): The current power being supplied by the inverter.
            - batteryMinimumSoCLimit (int): The minimum state of charge limit for battery discharge.
            - powerEssentialOnly (bool): Indicates if the inverter is powering only essential loads.
              Non-essential loads are typically hot water cyclinders/geysers and stoves and ovens.
            - gridCharge (bool): Indicates if the battery can be recharged from the grid.
    """
    cmd = "synkctl inverter settings"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    res = json.loads(res.stdout)

    inverter = {}
    inverter["batteryMinimumSoCLimit"] = res["battery-capacity"]
    inverter["powerEssentialOnly"] = res["essential-only"] == "on"
    inverter["gridCharge"] = res["grid-charge"] == "on"

    cmd = "synkctl inverter details"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    res = json.loads(res.stdout)

    inverter["ratedPower"] = res["ratePower"]
    inverter["power"] = res["pac"]

    return Inverter(**inverter)
