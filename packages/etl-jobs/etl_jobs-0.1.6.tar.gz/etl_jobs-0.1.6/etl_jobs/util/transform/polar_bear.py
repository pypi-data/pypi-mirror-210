"""
fill in
"""

import polars as pl


def transform_machine_bronze(data_frame: pl.dataframe):
    """
    fill in
    :param data_frame:
    :return:
    """
    return data_frame.with_columns(
        (
            (pl.col("N8j2").round(0) * pl.col("N8j2").round(0))
            .cast(pl.Int64)
            .cast(pl.Utf8)
            + "_"
            + pl.col("6tk3").cast(pl.Utf8)
        ).alias("engine_type")
    )
