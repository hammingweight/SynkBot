import json
import subprocess
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class Battery(BaseModel):
    bmsSoc: int = Field(description="The battery's state of charge as a percentage")
    bmsVolt: float = Field(
        description="The battery voltage according to the battery management system (BMS)"
    )
    isCharging: bool = Field(
        description="True if the battery is charging; False if discharging"
    )
    power: int = Field(
        description="""
                       The power flowing into or out of the battery in Watts.
                       If positive, power is flowing into the battery; i.e. charging.
                       If negative, power is flowing from the battery; i.e. discharging.
                       """
    )
    temp: float = Field(description="The battery temperature in Celsius")
    voltage: float = Field(description="The battery voltage according to the inverter")


@tool(parse_docstring=True)
def battery_state(inverter_serial_number: Optional[int] = 0) -> Battery:
    """
    Gets the state of a battery including the battery state of charge, temperature, voltage, whether the battery is
    charging or discharging and the power flow into the battery or the power flow from the battery.

    Args:
        inverter_serial_number (Optional[str]): The serial number of an inverter that the battery to is connected to.
        If not provided, returns the battery state for the default inverter.

    Returns:
        Battery: A Battery object containing the following fields:
            - bmsSoc (int): Battery state of charge as a percentage (0-100%)
            - bmsVolt (float): Battery voltage measured by the BMS in Volts
            - power (int): Power flow in Watts. Positive implies that the battery is charging (power flows into
                           the battery), negative implies the battery is discharging (power flows from the battery).
            - temp (float): Battery temperature in Celsius
            - voltage (float): Battery voltage measured by the inverter in Volts
    """
    cmd = "synkctl battery get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    b = json.loads(res.stdout)
    battery = {}
    for k in b.keys():
        if k in Battery.model_fields.keys():
            battery[k] = b[k]
    battery["isCharging"] = b["power"] < 0
    battery["power"] = -b["power"]

    return Battery(**battery)
