from enum import Enum
import pandas as pd
from logging import *


class _ColorType(Enum):
    COLOR_HEX = 1
    COLOR_EN = 2
    COLOR_CN = 3
    COLOR_OCT = 4


def __parse_color_df():
    import os
    folder_path = os.path.dirname(__file__)
    color_csv_file_path = os.path.join(folder_path, "color.csv")
    global __COLOR_DF
    __COLOR_DF = pd.read_csv(color_csv_file_path, index_col=None, header=0)


def __guess_color_type_and_value(color_value: str, color_df: pd.DataFrame) -> (_ColorType, str):
    if "" == color_value.strip():
        return None, None
    # guess Hex
    if color_value.startswith("#"):
        if len(color_value) != 7:
            raise ValueError("IllegalFormatColor" + color_value)
        for char in color_value[1:]:
            if char.lower() not in '0123456789abcdef':
                raise ValueError("IllegalFormatColor " + color_value)
        return _ColorType.COLOR_HEX, str(color_value)

    # try color_en
    color_en_filtered = color_df.loc[color_df['color_en'] == color_value]['color_hex']
    if len(color_en_filtered) > 0:
        return _ColorType.COLOR_EN, color_en_filtered.tolist()[0]

    # try color_cn
    color_cn_filtered = color_df.loc[color_df['color_cn'] == color_value]['color_hex']
    if len(color_cn_filtered) > 0:
        return _ColorType.COLOR_CN, color_cn_filtered.tolist()[0]

    # try oct_values color
    if ',' in color_value:
        try:
            parts = color_value.split(",")
            if len(parts) != 3:
                raise ValueError("IllegalFormatColor " + color_value)

            parsed_int_color = [int(p.strip()) for p in parts]
            if all([0 <= p <= 255 for p in parsed_int_color]):
                return _ColorType.COLOR_OCT, "#" + "".join([hex(p)[2:].upper().zfill(2) for p in parsed_int_color])
            else:
                raise ValueError("IllegalFormatColor " + color_value)

        except Exception as e:
            error(e)
            raise ValueError("IllegalFormatColor " + color_value)

    raise ValueError("Unknown color value: " + color_value)


__COLOR_DF = pd.DataFrame(None, columns=['color_en', 'color_cn', 'color_hex', 'color_oct'])


def translate_color(color_value: str) -> str:
    if len(__COLOR_DF) < 2:
        return color_value
    color_type, translated_color_value = __guess_color_type_and_value(color_value, __COLOR_DF)
    debug("Translate Color Vale " + color_value + " Got Type " + str(color_type) + " Value " + translated_color_value)
    return translated_color_value


init = __parse_color_df
