import os

import altair as alt
import toolz

from camminapy.plot.altair_theme import (
    altair_theme_gray,
)


def altair_theme() -> None:
    for _ in range(2):
        alt.themes.register("theme_gray", altair_theme_gray)
        alt.themes.enable("theme_gray")


def altair_setup(csv_or_json: str = "json") -> None:
    alt.data_transformers.register("csv_dir", csv_dir)
    alt.data_transformers.register("json_dir", json_dir)
    for _ in range(2):  # For some reason I need to run this twice for it to work.
        alt.data_transformers.enable(
            f"{csv_or_json}_dir", data_dir="./.temporary_altair_data/"
        )


def csv_dir(data, data_dir="altairdata") -> None:
    return generic_dir(data, alt.to_csv, data_dir)


def json_dir(data, data_dir="altairdata") -> None:
    return generic_dir(data, alt.to_json, data_dir)


def generic_dir(data, to_disk: toolz.functoolz.curry, data_dir="altairdata") -> None:
    os.makedirs(data_dir, exist_ok=True)
    return toolz.curried.pipe(
        data, to_disk(filename=data_dir + "/{prefix} -{hash}.{extension}")
    )
