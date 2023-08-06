# import modin.pandas as pd
# import pandas as pd
# Check if cuDF is available
try:
    import cudf as pd
    import pandas

    is_cuda = True
except ImportError:
    import pandas as pd

    is_cuda = False

import mitreattack.attackToExcel.attackToExcel as attackToExcel
from typing import Dict, List

import pickle
import os
import argparse
import logging


def cuda_apply(series: pd.Series, func: callable, *args, **kwargs) -> pd.Series:
    """Apply a function to a series using cuDF if available.

    Args:
        series (pd.Series): The series to apply the function to.
        func (callable): The callable function.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        pd.Series: The series with the function applied.
    """
    if is_cuda:
        # cuDF doesn't support apply yet -> copy the series to a pandas series
        pd_series = pandas.Series(series.to_arrow().to_pylist())
        pd_series = pd_series.apply(func, *args, **kwargs)
        return pd_series
    else:
        return series.apply(func, *args, **kwargs)


def split_literals_cols(df: pd.DataFrame, cols: List, sep: str = ",") -> pd.DataFrame:
    """Split the given columns from strings into an array of
    strings on the given separator.

    Args:
        df (pd.DataFrame): the host dataframe
        cols (List): the columns with strings to split
        sep (str, optional): the separator to split on. Defaults to ",".

    Returns:
        pd.DataFrame: the dataframe with the split columns
    """
    lit_splitter = lambda x: x.split(sep) if isinstance(x, str) else x
    for col in cols:
        if col in df.columns:
            df[col] = cuda_apply(df[col], lit_splitter)
    return df


def get_args(op_name: str) -> argparse.Namespace:
    """Parse the arguments for the given operation.

    Args:
        op_name (str): the name of the operation

    Returns:
        argparse.Namespace: the parsed arguments
    """
    if op_name not in ["join"]:
        raise ValueError("Invalid operation name: {}".format(op_name))

    parser = argparse.ArgumentParser(
        description="Run the {} operation.".format(op_name)
    )
    if op_name == "join":
        parser.add_argument(
            "--matrix_name",
            type=str,
            default="enterprise-attack",
            help="The name of the matrix to use.",
        )
        parser.add_argument(
            "--include_sub_techniques",
            action="store_true",
            help="Whether to include sub-techniques.",
        )
        parser.add_argument(
            "--include_descriptions",
            action="store_true",
            help="Whether to include descriptions.",
        )
        parser.add_argument(
            "--include_detection",
            action="store_true",
            help="Whether to include detection.",
        )
        parser.add_argument(
            "--output_dir",
            type=str,
            default="output",
            help="The directory to output the results to.",
        )
        args = parser.parse_args()
        return args


def replace_cols(
    prefix: str, cols: List, df: pd.DataFrame, include_descriptions: bool = False
) -> pd.DataFrame:
    """
    Replaces the given column names by adding the given prefix.

    Parameters:
        prefix (str): the prefix to add to the column names
        cols (List): the list of column names to replace
        df (pd.DataFrame): the dataframe to replace the columns in
        include_description (bool): whether to include the description column. Defaults to False.

    Returns:
        pd.DataFrame: the dataframe with replaced columns
    """
    for col in cols:
        new_col = prefix + "_" + col.lower()
        df[new_col] = df[col]
        del df[col]
    if not include_descriptions:
        del df[prefix + "_description"]
    return df


def drop_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops unnecessary columns from the dataframe.

    Parameters:
        df (pd.DataFrame): the dataframe to drop columns from

    Returns:
        pd.DataFrame: the dataframe with dropped columns
    """
    cols = [
        "url",
        "created",
        "last modified",
        "version",
        "contributors",
        "relationship citations",
        "associated groups",
        "associated groups citations",
        "associated campaigns",
        "associated campaigns citations",
    ]
    for col in cols:
        if col in df.columns:
            del df[col]
    return df


def prep_join(
    df_main: pd.DataFrame,
    df_j: pd.DataFrame,
    source_id: str,
    target_id: str,
    flip: bool = False,
) -> pd.DataFrame:
    """
    Prepare and join two dataframes.
    The dataframes are joined on the source ID.
    Flip indicates whether the source and target IDs should be flipped on the second dataframe.

    Parameters:
        df_main (pd.DataFrame): the main dataframe
        df_j (pd.DataFrame): the dataframe to join
        source_id (str): the column name of the source ID
        target_id (str): the column name of the target ID
        flip (bool): whether to flip the source and target IDs on the second dataframe

    Returns:
        pd.DataFrame: the joined dataframe
    """
    df_temp = pd.DataFrame()
    df_temp[source_id] = df_j["source ID"]
    df_temp[target_id] = df_j["target ID"]
    if flip:
        df_temp[source_id], df_temp[target_id] = (
            df_temp[target_id],
            df_temp[source_id],
        )
    len_before = len(df_main)
    df_ret = df_main.merge(
        df_temp,
        on=source_id,
        how="left",
    )
    logging.debug("Rows:\n Before:\t{}\n  After:\t{}\n".format(len_before, len(df_ret)))
    return df_ret


def get_join_key(key_text) -> str:
    """
    Returns the standardized column name for the given column name.
    Accounts for inconsistencies in the MITRE data.

    Parameters:
        key_text (str): the inconsistent column name.

    Returns:
        str: the standardized column name.
    """

    if key_text in [
        "associated groups",
        "attributed groups",
    ]:
        return "group_id"
    elif key_text in ["associated software"]:
        return "software_id"
    elif key_text in [
        "associated campaigns",
        "attributed campaigns",
    ]:
        return "campaign_id"
    elif key_text in [
        "techniques addressed",
        "techniques used",
    ]:
        return "technique_id"
    else:
        raise ValueError("Unknown key text: " + key_text)


def get_mitre_data(matrix_name: str) -> Dict:
    """
    Fetch and save the MITRE data for the given matrix name.
    If the data has already been downloaded, it will be loaded from disk.

    Parameters:
        matrix_name (str): the att&ck matrix to fetch

    Returns:
        Dict: the MITRE data
    """
    # Sanitize the matrix name against path traversal
    matrix_name = matrix_name.replace("/", "_")
    path_pkl = "./mitre_data"
    name_pkl = f"{matrix_name}.pkl"
    name_pkl = os.path.join(path_pkl, name_pkl)
    if not os.path.exists(path_pkl):
        os.makedirs(path_pkl)

    if os.path.exists(name_pkl):
        with open(name_pkl, "rb") as f:
            return pickle.load(f)
    else:
        # download the data
        attackdata = attackToExcel.get_stix_data(matrix_name)
        dict_all = attackToExcel.build_dataframes(
            attackdata,
            matrix_name,
        )
        # save the data
        with open(name_pkl, "wb") as f:
            pickle.dump(dict_all, f)
        return dict_all


def merge_duplicate_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Looks for columns which end in _x and _y and merges them into a single column

    Parameters:
        df (pd.DataFrame): the dataframe to merge

    Returns:
        pd.DataFrame: the merged dataframe
    """
    cols = df.columns
    cols_x = [col for col in cols if col.endswith("_x")]
    cols_y = [col for col in cols if col.endswith("_y")]
    cols_to_merge = list(zip(cols_x, cols_y))
    for col_x, col_y in cols_to_merge:
        col = col_x[:-2]
        logging.debug(
            "Merging x/y column: {}\nNaNs on x:\t\t{}\nNaNs on y:\t\t{}\nOverlapping:\t{}\n".format(
                col,
                df[col_x].isna().sum(),
                df[col_y].isna().sum(),
                df[df[col_x].isna() & df[col_y].isna()].shape[0],
            )
        )
        if df[col_x].isna().sum() == 0:
            df.rename(columns={col_x: col}, inplace=True)
            del df[col_y]
        elif df[col_y].isna().sum() == 0:
            df.rename(columns={col_y: col}, inplace=True)
            del df[col_x]
        else:
            df[col] = df[col_x].fillna(df[col_y])
            del df[col_x]
            del df[col_y]
    # remove duplicate rows
    len_before = len(df)
    df = df.drop_duplicates()
    logging.debug(
        "Dropped {} duplicate rows".format(len_before - len(df)),
    )
    return df


def drop_sub_techniques(
    df: pd.DataFrame, include_sub_techniques: bool = False
) -> pd.DataFrame:
    """Drop all rows which are sub-techniques.
    We use the column `technique_id` to determine
    if a row is a sub-technique.

    Args:
        df (pd.DataFrame): Input dataframe
        include_sub_techniques (bool, optional): Whether to actually drop the sub-techniques. Defaults to False.

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    if include_sub_techniques:
        return df
    # drop rows which have the field subtechnique_of
    if "subtechnique_of" in df.columns:
        df = df[df["subtechnique_of"].isna()]
    return df
