from math import floor
from typing import Union


def get_arrow(arrow_length: Union[int, float], arrow_left=True, strip=False):
    """
    Includes a space for the text immediately preceding
    :param arrow_length:
    :param arrow_left:
    :param strip: Set true if you don't want a space on the tail side of the arrow
    :return:
    """
    if arrow_length == 1:
        arrow = " \u2192" if not arrow_left else "\u2190 "
        return arrow.strip() if strip else arrow

    arrow_body = "\U0001F89C"
    arrow_body_half = "\U0001F89E"
    if not arrow_left:
        arrow_tail = " \u250F"
        arrow_head = "\u2B95"
    else:
        arrow_tail = "\u2513 "
        arrow_head = "\u2B05"

    if 1 < arrow_length < 2:
        arrow_length = 2
        print(
            "Invalid arrow length - due to limitations in the font, arrow lengths "
            "between 1 and 2 are impossible. Rounded up to length 2. Sorry!"
        )

    if arrow_length <= 2:
        arrow = arrow_tail + arrow_head if not arrow_left else arrow_head + arrow_tail
        return arrow.strip() if strip else arrow

    arrow_length = arrow_length - 2
    middle = ""
    if arrow_length % 1 != 0:
        middle += arrow_body_half
        arrow_length = floor(arrow_length)

    arrow = (
        arrow_tail + arrow_body * arrow_length + middle + arrow_head
        if not arrow_left
        else arrow_head + arrow_body * arrow_length + middle + arrow_tail
    )

    return arrow.strip() if strip else arrow
