from datetime import datetime


def parse_coffee_command(text: str, default_time: str, default_place: str):
    """
    Возвращает:
        (time: str, place: str)

    Поддерживает:

    /coffee
    /coffee 20:30
    /coffee 20:30 Парнас
    """

    parts = text.split(maxsplit=2)

    time = default_time
    place = default_place

    if len(parts) >= 2:
        try:
            datetime.strptime(parts[1], "%H:%M")
        except ValueError:
            raise ValueError(
                "Неверный формат времени."
            )

        time = parts[1]

    if len(parts) == 3:
        place = parts[2].strip()

    return time, place
