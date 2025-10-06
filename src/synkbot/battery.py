import json
import subprocess
from typing import Optional, Union
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from .errors import Error
from .power import Power

class Battery(BaseModel):
    bmsSoc: int = Field(description="The battery's state of charge as a percentage")
    bmsVolt: float = Field(
        description="The battery voltage according to the battery management system (BMS)"
    )
    isCharging: bool = Field(
        description="True if the battery is charging; False if discharging"
    )
    power: Power = Field(description="The power flowing into or out of the battery in Watts.")
    temp: float = Field(description="The battery temperature in Celsius")
    voltage: float = Field(description="The battery voltage according to the inverter")


@tool(parse_docstring=True)
def battery_state(
    inverter_serial_number: Optional[int] = 0,
) -> Union[Battery, Error]:
    """
    Gets the state of a battery including the battery state of charge, temperature, voltage, whether the battery is
    charging or discharging and the power flow into the battery or the power flow from the battery.

    Args:
        inverter_serial_number (Optional[str]): The serial number of an inverter that the battery to is connected to.
        If not provided, returns the battery state for the default inverter.

    Returns:
        Union[Battery, Error]: Either a Battery object containing the battery state information, or an Error object
        if the request failed. The Battery object contains the following fields::
            - bmsSoc (int): Battery state of charge as a percentage (0-100%)
            - bmsVolt (float): Battery voltage measured by the BMS in Volts
            - power (Power): Power flow in Watts and the direction that the power is flowing.
            - temp (float): Battery temperature in Celsius
            - voltage (float): Battery voltage measured by the inverter in Volts
    """
    cmd = "synkctl battery get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        message = res.stderr.split("\n")[0]
        return Error(message=message)

    b = json.loads(res.stdout)
    battery = {}
    for k in b.keys():
        if k in Battery.model_fields.keys():
            battery[k] = b[k]
    if b["power"] < 0:
        battery["power"] = Power(power=-b["power"], direction="Power is flowing into the battery")
    else:
        battery["power"] = Power(power=b["power"], direction="Power is flowing from the battery")

    return Battery(**battery)
