"""Stream the mouse position to a PowerBI streaming dataset"""


import asyncio
import datetime
import os
from dataclasses import dataclass, field
from typing import TypedDict

import httpx
import pyautogui
from dotenv import find_dotenv, load_dotenv


class PositionDict(TypedDict):
    time: str
    x: float  # noqa
    y: float  # noqa


@dataclass(slots=True, frozen=True)
class Position:
    """The position of the mouse at a specific time"""

    x: float  # noqa
    y: float  # noqa
    time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> PositionDict:
        return {
            "time": self.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "x": self.x,
            "y": self.y,
        }


async def send_position(position: Position, url: str) -> None:
    """Send the position to the API"""
    payload = position.to_dict()
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


def _get_mouse_position() -> Position:
    mouse_coords = pyautogui.position()
    position = Position(mouse_coords[0], mouse_coords[1])
    return position


async def get_mouse_position() -> Position:
    """Get the current mouse position"""
    position = await asyncio.to_thread(_get_mouse_position)
    return position


async def stream(url: str) -> None:
    """Continously stream the mouse position to the API"""
    while True:
        position = await get_mouse_position()
        await send_position(position, url)
        await asyncio.sleep(0.4)


def main() -> None:
    load_dotenv(find_dotenv())
    url = os.getenv("URL")
    if url is None:
        raise ValueError("Please provide a .env file with your API URL.")
    asyncio.run(stream(url))


if __name__ == "__main__":
    main()
