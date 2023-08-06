import numpy as np
import pandas as pd
import polars as pl

from camminapy import logger


def resample_dataframe_polars(
    df: pl.DataFrame,
    interpolation_column: str,
    interpolation_step: float,
    to_log: bool = False,
) -> pl.DataFrame:
    """Resamples a dataframe to obtain data at interpolation points.

    Parameters
    ----------
    df : pl.DataFrame
        The dataframe to interpolate.
    interpolation_column : str
        Which numeric column to use for the interpolation points.
    interpolation_step : float
        Steps for the newly create interpolation points
    to_log : bool
        Whether or not to show additional logging info.

    Returns
    -------
    pl.DataFrame
        A dataframe with the same columns as the input dataframe and where
        `interpolation_column` is spaced as `interpolation_step` and all other
        data is interpolated onto that timeline.
    """
    # Get the x-values onto which we want to interpolate the data.
    interpolation_points = pl.DataFrame(
        {
            interpolation_column: np.arange(
                start=df.min()[0, interpolation_column],
                stop=df.max()[0, interpolation_column] + interpolation_step,
                step=interpolation_step,
            )
        }
    )
    # Add the new interpolation points to the input dataframe and interpolate the
    # data onto those new interpolation points.
    df_with_data_at_additional_interpolation_points = (
        interpolation_points.join(df, on=[interpolation_column], how="outer")
        .sort(interpolation_column)
        .interpolate()
    )

    # After interpolation, we now have data at the new nodes. What's left is
    # to only select those new interpolation nodes and the new data.
    df_with_data_only_at_interpolation_points = interpolation_points.join(
        df_with_data_at_additional_interpolation_points,
        on=[interpolation_column],
        how="left",
    ).sort(interpolation_column)

    if to_log:
        n_input = len(df)
        n_output = len(df_with_data_only_at_interpolation_points)
        logger.info(f"Resampled from {n_input} rows to {n_output} rows.")

    return df_with_data_only_at_interpolation_points


#######################################################################################
#                       Everything below is just wrappers.                            #
#######################################################################################


def resample_dataframe_grouped_polars(
    df: pl.DataFrame,
    interpolation_column: str,
    interpolation_step: float,
    group_column: str,
) -> pl.DataFrame:
    """Groupwise resamples a dataframe to obtain data at interpolation points.

    Parameters
    ----------
    df : pl.DataFrame
        The dataframe to interpolate.
    interpolation_column : str
        Which numeric column to use for the interpolation points.
    interpolation_step : float
        Steps for the newly create interpolation points
    group_column:str
        The column over which to group

    Returns
    -------
    pl.DataFrame
        A dataframe with the same columns as the input dataframe and where
        `interpolation_column` is spaced as `interpolation_step` and all other
        data is interpolated onto that timeline.
    """
    return pl.concat(
        [
            resample_dataframe_polars(
                groupdf,
                interpolation_column=interpolation_column,
                interpolation_step=interpolation_step,
            )
            for _, groupdf in df.groupby(group_column, maintain_order=True)
        ]
    )


def resample_dataframe_pandas(
    df: pd.DataFrame,
    interpolation_column: str,
    interpolation_step: float,
) -> pd.DataFrame:
    """
    Pandas wrapper for resampling.

    See `resample_dataframe_polars` for details.
    """
    return resample_dataframe_polars(
        pl.DataFrame(df), interpolation_column, interpolation_step
    ).to_pandas()


def resample_dataframe_grouped_pandas(
    df: pd.DataFrame,
    interpolation_column: str,
    interpolation_step: float,
    group_column: str,
) -> pd.DataFrame:
    """
    Pandas wrapper for groupwise resampling.

    NOTE: This does alter the index!

    See `resample_dataframe_grouped_polars` for details.
    """
    return resample_dataframe_grouped_polars(
        pl.DataFrame(df),
        interpolation_column,
        interpolation_step,
        group_column,
    ).to_pandas()
