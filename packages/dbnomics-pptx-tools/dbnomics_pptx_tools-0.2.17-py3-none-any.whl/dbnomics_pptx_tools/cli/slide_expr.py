from typing import Iterator


def check_slide_number(slide_number: int, *, slide_ids: list[str | None]) -> None:
    if slide_number > len(slide_ids):
        raise ValueError(
            f"Invalid slide number: {slide_number} (there are only {len(slide_ids)} slide in the presentation)"
        )


def parse_range_expr(value: str) -> Iterator[int | str]:
    range_parts = value.split("-")
    if len(range_parts) != 2:
        raise ValueError(f"Invalid range: {value!r}")

    try:
        a = parse_slide_number(range_parts[0])
        b = parse_slide_number(range_parts[1])
    except ValueError as exc:
        raise ValueError(f"Invalid range: {value!r}") from exc

    yield from range(a, b + 1)


def parse_slide_expr(value: str) -> int | str:
    try:
        return parse_slide_number(value)
    except ValueError:
        return value


def parse_slide_number(value: str) -> int:
    slide_number = int(value)
    if slide_number < 1:
        raise ValueError(f"Invalid slide number: {slide_number}")
    return slide_number


def parse_slides_expr(value: str) -> Iterator[int | str]:
    """Parse slide expression like "1-10,3,slide_x,4,23-47"."""
    for part in value.split(","):
        if "-" in value:
            yield from parse_range_expr(part)
        else:
            yield parse_slide_expr(part)


def slide_id_to_number(slide_id: str, *, slide_ids: list[str | None]) -> int:
    if slide_id not in slide_ids:
        raise ValueError(f"Invalid slide ID: {slide_id!r}")

    slide_number = slide_ids.index(slide_id) + 1
    return slide_number


def slide_to_number(slide: str | int, *, slide_ids: list[str | None]) -> int:
    slide_number = slide_id_to_number(slide, slide_ids=slide_ids) if isinstance(slide, str) else slide
    check_slide_number(slide_number, slide_ids=slide_ids)
    return slide_number
