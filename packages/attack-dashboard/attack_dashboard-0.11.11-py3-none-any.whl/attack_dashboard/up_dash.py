# upload the Mitre ATT&CK dashboard to the Kibana instance
import logging
import os
import sys
from typing import Dict, List, Tuple
from addict import Dict as ADict
import shlex
import getpass


def promt_args() -> Dict:
    """Promt the user for the Kibana instance host-address and credentials.

    Returns:
        Dict: return args.
    """
    args = ADict()
    args.kibana_host = input("Kibana host-address: ")
    username = shlex.quote(input("Username: "))
    password = shlex.quote(
        getpass.getpass(
            "Password: ",
        )
    )
    args.elasticsearch_creds = f"{username}:{password}"
    return args


def run_upload_sh(args: Dict) -> None:
    """Run the upload.sh script with the given arguments.
    The script is located inside this python package.

    Args:
        args (Dict): the arguments to pass to the script
    """
    # get the path to the upload.sh script
    upload_sh_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dashboard_data/mitre_dashboards.sh"
    )
    # run the script and print the output
    # file deepcode ignore CommandInjection: <please specify a reason of ignoring this>
    script_out = os.system(
        f"bash {upload_sh_path} {args.kibana_host} {args.elasticsearch_creds}"
    )
    logging.info(script_out)


def main() -> None:
    """Main function."""
    # set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # get the arguments
    args = promt_args()
    logging.info("Running upload.sh script...", args)
    # run the upload script
    run_upload_sh(args)


if __name__ == "__main__":
    main()
