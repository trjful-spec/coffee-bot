from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Config:
    bot_token: str

    default_place: str

    default_time: str


config = Config(
    bot_token=os.getenv(
        "BOT_TOKEN",
        "",
    ),
    default_place=os.getenv(
        "DEFAULT_PLACE",
        "Мега",
    ),
    default_time=os.getenv(
        "DEFAULT_TIME",
        "21:00",
    ),
)

if not config.bot_token:
    raise RuntimeError(
        "BOT_TOKEN is not configured"
    )