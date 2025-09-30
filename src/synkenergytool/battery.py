from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class Battery(BaseModel):
    bmsSoc: int = Field(description="The battery's state of charge as a percentage")
    bmsVolt: float = Field(
        description="The batter voltage according to the battery management system (BMS)"
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


@tool
def mocked_battery_state(serial_number: Optional[int] = 0) -> Battery:
    """
    Gets the state of a battery.
    """
    if serial_number:
        return Battery(bmsSoc=84, bmsVolt=49, power=100, temp=30, voltage=48.9)
    return Battery(bmsSoc=94, bmsVolt=53.2, power=61, temp=23.9, voltage=53.3)
