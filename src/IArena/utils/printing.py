from typing import List, Any

def matrix_map_to_str(
        matrix_map: List[List[Any]],
        add_coordinates: bool = True) -> str:
    """Convert a matrix map to a string representation.

    Args:
        matrix_map: The matrix map to convert.
        add_coordinates: Whether to add coordinates to the string representation.

    Returns:
        The string representation of the matrix map.
    """

    st = ""

    n_rows = len(matrix_map)
    n_cols = len(matrix_map[0]) if n_rows > 0 else 0

    elem_width = max(
        len(str(matrix_map[i][j]))
        for i in range(n_rows)
        for j in range(n_cols)
    ) + 1

    coor_width = max(len(str(n_rows)), len(str(n_cols))) + 1

    cell_width = max(elem_width, coor_width)

    if add_coordinates:
        st += " " * coor_width
        for j in range(n_cols):
            st += f"{j:>{cell_width}}"
        st += "\n"
    for i in range(n_rows):
        if add_coordinates:
            st += f"{i:>{coor_width}}"
        for j in range(n_cols):
            st += f"{str(matrix_map[i][j]):>{cell_width}}"
        st += "\n"
    return st


COLOR_CODES = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
}

def color_text(
            text: str,
            color_code: int = None,
            color_name: str = None
        ) -> str:
    """Color the given text with the given color code.

    Args:
        text: The text to color.
        color_code: The color code to use.

    Returns:
        The colored text.
    """

    if color_name is not None:
        if color_name.lower() in COLOR_CODES:
            color_code = COLOR_CODES[color_name.lower()]
        else:
            raise ValueError(f"Invalid color name: {color_name}")

    return f"\033[{color_code}m{text}\033[0m"


def green_tick() -> str:
    """Return a green tick character."""
    return color_text("✔", color_name="green")

def red_cross() -> str:
    """Return a red cross character."""
    return color_text("✘", color_name="red")
