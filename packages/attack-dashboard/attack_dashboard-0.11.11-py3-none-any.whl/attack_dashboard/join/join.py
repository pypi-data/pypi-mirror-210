# import modin.pandas as pd
# import pandas as pd

# Check if cuDF is available
from pandas import Timestamp
from tqdm import tqdm

try:
    import cudf as pd
except ImportError:
    import pandas as pd

from attack_dashboard.join.join_helpers import (
    drop_cols,
    replace_cols,
    prep_join,
    merge_duplicate_cols,
    drop_sub_techniques,
    get_join_key,
    get_mitre_data,
    get_args,
    cuda_apply,
)
import os
import logging
import re

# # --- Start Config ---
# matrix_name = "mobile-attack"
# matrix_name = "ics-attack"
# matrix_name = "enterprise-attack"
# include_sub_techniques = True
# include_descriptions = False
# include_detection = False
# output_dir = "output"
# # --- End Config ---


def join_op():
    """Join the MITRE ATT&CK data into a single csv file."""
    args = get_args("join")
    matrix_name = args.matrix_name
    include_sub_techniques = args.include_sub_techniques
    include_descriptions = args.include_descriptions
    include_detection = args.include_detection
    output_dir = args.output_dir
    pbar = tqdm(total=5, desc="Joining the latest MITRE ATT&CK data", colour="cyan")

    pbar.display("Getting the MITRE ATT&CK data", pos=1)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = "{}_{}_{}{}_{}".format(
        matrix_name,
        "all" if include_sub_techniques else "tech",
        "" if include_detection else "super",
        "" if include_descriptions else "lean",
        # Current month and year
        Timestamp.now().strftime("%Y%m"),
    )
    output_file = os.path.join(output_dir, output_file)

    dict_all = get_mitre_data(matrix_name=matrix_name)

    pbar.update(1)
    pbar.display("Joining techniques and mitigations", pos=1)

    df_m = pd.DataFrame(dict_all["mitigations"]["mitigations"])
    df_m = drop_cols(df_m)
    df_m = replace_cols(
        "mitigation",
        ["ID", "name", "description"],
        df_m,
        include_descriptions=include_descriptions,
    )

    df_mjt = prep_join(
        df_m,
        dict_all["mitigations"]["techniques addressed"],
        "mitigation_id",
        "technique_id",
    )

    df_t = pd.DataFrame(dict_all["techniques"]["techniques"])
    df_t = drop_cols(df_t)
    df_t = replace_cols(
        "technique",
        ["ID", "name", "description"],
        df_t,
        include_descriptions=include_descriptions,
    )
    df_tm = df_t.merge(
        df_mjt,
        on="technique_id",
        how="left",
    )
    df_tm = merge_duplicate_cols(df_tm)
    df_tm = drop_sub_techniques(df_tm, include_sub_techniques)

    pattern = re.compile(r"\w+\s?\w*:\s")
    if "data sources" in df_tm.columns:
        ds_shortener = lambda x: pattern.sub("", str(x))
        df_tm["data sources"] = cuda_apply(df_tm["data sources"], ds_shortener)

    df_sgc = pd.DataFrame()
    previous_key = None

    # for key in ["groups", "campaigns", "software"]:
    for key in ["groups", "software"]:
        pbar.update(1)
        pbar.display("Processing {}".format(key), pos=1)

        df_key = pd.DataFrame(dict_all[key][key])
        df_key = drop_cols(df_key)
        links = dict_all[key].keys()
        replace_key = key[:-1] if key[-1] == "s" else key
        df_key = replace_cols(
            replace_key,
            ["ID", "name", "description"],
            df_key,
            include_descriptions=include_descriptions,
        )

        for link in links:
            if link not in [key, "citations"]:
                source_id = replace_key + "_id"
                target_id = get_join_key(link)
                # Inconsistency in the data mapping.
                if key == "software" and target_id in ["group_id", "campaign_id"]:
                    flip_key = True
                elif key == "groups" and target_id == "campaign_id":
                    flip_key = True
                else:
                    flip_key = False
                df_link = pd.DataFrame(dict_all[key][link])
                df_key = prep_join(
                    df_key,
                    df_link,
                    source_id,
                    target_id,
                    flip_key,
                )
        if "technique_id" in df_key.columns:
            df_key = drop_sub_techniques(df_key, include_sub_techniques)

        if len(df_sgc) == 0:
            df_sgc = pd.DataFrame(df_key)
        else:
            if previous_key not in df_key.columns:
                df_key[previous_key] = None

            logging.debug(
                "Joining {} to {} with {} outcasts".format(
                    previous_key,
                    replace_key,
                    str(len(df_key[df_key[previous_key].isna()])),
                )
            )
            df_sgc = df_sgc.merge(
                df_key,
                on=previous_key,
                how="outer",
            )
            df_sgc = merge_duplicate_cols(df_sgc)

        previous_key = replace_key + "_id"

    pbar.update(1)
    pbar.display("Processing final data-join", pos=1)
    logging.debug("----end run----")
    logging.debug(
        "Final table join with {} left and {} right rows.".format(
            len(df_tm), len(df_sgc)
        )
    )
    df_all = df_tm.merge(
        df_sgc,
        on="technique_id",
        how="left",
    )

    # Drop the obsolete type column
    if "type" in df_all.columns:
        df_all.drop(columns=["type"], inplace=True)

    df_all = merge_duplicate_cols(df_all)
    # Set the matrix name
    df_all["matrix"] = matrix_name

    # clean up column names
    df_all.columns = (
        df_all.columns.str.replace(" ", "_").str.replace("-", "").str.lower()
    )

    # Map the column names to the names used in the HELK
    col_map = {
        "technique_name": "technique",
        "tactics": "tactic",
        "supports_remote": "remote_support",
        "software_name": "software",
        "platforms": "platform",
        "group_name": "group",
        "mitigation_name": "mitigation",
    }
    df_all = df_all.rename(columns=col_map)

    # More hacqs to match the HELK format
    # True where a detection is present otherwise False
    df_all["detectable_by_common_defenses"] = df_all[
        df_all["detection"].isna() == False
    ]["detection"].astype(bool)
    df_all["detectable_by_common_defenses"].fillna(False, inplace=True)

    if not include_detection:
        for col in ["detection", "system_requirements"]:
            if col in df_all.columns:
                df_all.drop(columns=[col], inplace=True)

    all_headers = [
        "aliases",
        "campaign_id",
        "data_sources",
        "defenses_bypassed",
        "detectable_by_common_defenses",
        "detection",
        "effective_permissions",
        "group",
        "group_description",
        "group_id",
        "impact_type",
        "is_subtechnique",
        "matrix",
        "mitigation",
        "mitigation_description",
        "mitigation_id",
        "mtc_id",
        "permissions_required",
        "platform",
        "remote_support",
        "software",
        "software_description",
        "software_id",
        "subtechnique_of",
        "system_requirements",
        "tactic",
        "tactic_type",
        "technique",
        "technique_description",
        "technique_id",
        "type",
    ]
    all_headers = set(all_headers + list(df_all.columns))
    all_headers = list(all_headers)
    all_headers.sort()

    # Add missing columns
    for col in all_headers:
        if col not in df_all.columns:
            df_all[col] = None

    # Reorder columns alphabetically
    df_all = df_all[all_headers]

    # Save full df and sample
    pbar.update(1)
    pbar.display("Saving data to csv", pos=1)
    logging.debug("Writing {} rows to csv file ...".format(len(df_all)))
    df_all.to_csv(f"{output_file}.csv", index=False, sep="|")
    df_all.sample(111).to_csv(f"{output_file}_sample.csv", index=False, sep="|")

    # Save headers as txt
    with open(f"{output_file}_headers.txt", "w") as f:
        f.write('["')
        f.write('","'.join(df_all.columns))
        f.write('"]')
    pbar.display("Done! 🎉", pos=1)
    pbar.close()
    logging.info("Done! 🎉")
