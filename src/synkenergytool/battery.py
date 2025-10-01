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
    power: int = Field(
        description="""
                       The power flowing into or out of the battery in Watts.
                       If positive, power is flowing from the battery; i.e. discharging.
                       If negative, power is flowing into the battery; i.e. charging.
                       """
    )
    temp: float = Field(description="The battery temperature in Celsius")
    voltage: float = Field(description="The battery voltage according to the inverter")


@tool(parse_docstring=True)
def battery_state(inverter_serial_number: Optional[int] = 0) -> Battery:
    """
    Gets the state of a battery.

    Args:
        inverter_serial_number (Optional[str]): The serial number of an inverter that the battery to is connected to. 
        If not provided, returns the battery state for the default inverter.

    Returns:
        Battery: A Battery object containing the following fields:
            - bmsSoc (int): Battery state of charge as a percentage (0-100%)
            - bmsVolt (float): Battery voltage measured by the BMS in Volts
            - power (int): Power flow in Watts. Positive means discharging (power flows from the battery),
                           negative means charging (power flows into the battery)
            - temp (float): Battery temperature in Celsius
            - voltage (float): Battery voltage measured by the inverter in Volts

    Example:
        >>> battery = mocked_battery_state(12345)
        >>> print(battery.bmsSoc)
        84
    """
    cmd = "synkctl battery get --short"
    if inverter_serial_number:
        cmd += " -i " + str(inverter_serial_number)
    #print(cmd)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #print(res.stdout)
    b = json.loads(res.stdout)
    b_clean = {}
    for k in b.keys():
        if k in Battery.model_fields.keys():
            b_clean[k] = b[k]
    #print(b_clean)
    #if inverter_serial_number:
    #    return Battery(serialNumber=inverter_serial_number, bmsSoc=84, bmsVolt=53, power=-100, temp=30, voltage=53.1)
    #return Battery(serialNumber=123, bmsSoc=94, bmsVolt=53.2, power=-62, temp=23.9, voltage=53.3)
    return Battery(**b_clean)
