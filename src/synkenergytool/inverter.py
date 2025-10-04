import json
import subprocess
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional


class Inverter(BaseModel):
    ratedPower: int = Field(
        description="The maximum power (W) that the inverter can supply"
    )
    loadPower: int = Field(
        description="The power being supplied by the inverter to the load, e.g. the home"
    )
    batteryPower: int = Field(description="The power flowing to or from the inverter")
    inputPower: int = Field(
        description="The power coming from the inputs (e.g. solar panels)"
    )
    gridPower: int = Field(description="The power flowing to or from the grid")
    batteryMinimumSoCLimit: int = Field(description="The battery discharge limit")
    powerEssentialOnly: bool = Field(
        description="True if the inverter powers only non-essential loads"
    )
    gridCharge: bool = Field(
        description="True if the battery can be recharged from the grid"
    )


@tool(parse_docstring=True)
def inverter_settings(inverter_serial_number: Optional[int] = 0) -> Inverter:
    """
    Retrieves inverter load settings using the synkctl CLI tool.

    Args:
        inverter_serial_number (Optional[int], optional): Serial number of the inverter to query. Defaults to 0.

    Returns:
        Inverter: An Inverter object containing the following fields:
            - ratedPower (int): The maximum power (in watts) that the inverter can supply.
            - loadPower (int): The current power being supplied by the inverter to the load, e.g. the home.
            - batteryPower(int): The power flowing to or from the battery.
            - inputPower(int): The power coming from the inputs, e.g. solar panels.
            - gridPower(int): The power flowing to or from the grid.
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
    inverter["inputPower"] = res["pac"]

    cmd = "synkctl load get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    res = json.loads(res.stdout)
    inverter["loadPower"] = res["totalPower"]

    cmd = "synkctl battery get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    res = json.loads(res.stdout)
    inverter["batteryPower"] = res["power"]

    cmd = "synkctl grid get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    res = json.loads(res.stdout)
    inverter["gridPower"] = res["pac"]

    return Inverter(**inverter)


@tool(parse_docstring=True)
def inverter_update(
    inverter_serial_number: Optional[int] = 0,
    minimum_battery_soc: Optional[int] = None,
    essential_only: Optional[bool] = None,
    grid_charge: Optional[bool] = None,
):
    """
    Updates inverter settings.

    Args:
        inverter_serial_number (Optional[int], optional): Serial number of the inverter. Defaults to 0.
        minimum_battery_soc (Optional[int], optional): Minimum battery state of charge (SOC) to set. If None, this
                                                       option is omitted.
        essential_only (Optional[bool], optional): If True, enables essential-only mode; if False, disables it; if
                                                   None, this option is omitted.
        grid_charge (Optional[bool], optional): If True, enables grid charging; if False, disables it; if None, this
                                                option is omitted.
    """
    cmd = "synkctl inverter update"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)

    if minimum_battery_soc is not None:
        cmd += " --battery-capacity " + str(minimum_battery_soc)

    if essential_only is not None:
        cmd += " --essential-only "
        if essential_only:
            cmd += "on"
        else:
            cmd += "off"

    if grid_charge is not None:
        cmd += " --grid-charge "
        if grid_charge:
            cmd += "on"
        else:
            cmd += "off"

    subprocess.run(cmd, shell=True, capture_output=True, text=True)
