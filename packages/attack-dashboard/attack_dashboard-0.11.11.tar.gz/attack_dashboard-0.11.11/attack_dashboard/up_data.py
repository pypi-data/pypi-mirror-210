# create a folder with the logstash config and docker-compose file and run docker-compose up

import typing
import os
import sys
import subprocess
import getpass
import shlex
import socket
import time
from tqdm import tqdm
from threading import Thread

# TODO: get data folder as optional argument

# TODO: optionally delete the logstash folder after successful completion or abortion.


def mk_logstash_dir():
    """
    Create a folder with the logstash config and docker-compose file.
    """
    # create the folder
    if not os.path.exists("logstash"):
        os.mkdir("logstash")
    # create the logstash config file

    base_path = os.path.dirname(os.path.abspath(__file__))
    logstash_config_path = os.path.join(base_path, "logstash/logstash.conf")
    # copy to local dir
    os.system(f"cp {logstash_config_path} logstash/logstash.conf")
    # same for docker-compose
    docker_compose_path = os.path.join(base_path, "logstash/docker-compose.yml")
    os.system(f"cp {docker_compose_path} logstash/docker-compose.yml")


def mk_dotenv():
    """Make a .env file with the prompted Elastic and credentials."""
    elastic_host = input("Elasticsearch host-address: ")
    elastic_username = shlex.quote(input("Elastic user: "))
    elastic_pwd = getpass.getpass("Elastic password: ")
    # create the .env file
    with open("logstash/.env", "w") as f:
        f.write(f"ELASTIC_HOST={elastic_host}\n")
        f.write(f"ELASTIC_USER={elastic_username}\n")
        f.write(f"ELASTIC_PWD={elastic_pwd}\n")


def netcat(host: str, port: int, content_path: str) -> bool:
    """Netcat for python.

    Args:
        host (str): The host to netcat to.
        port (int): Which port to use.
        content_path (str): The path to the content to send.

    Returns:
        bool: Success or failure.
    """
    try:
        # read the content line by line
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        with open(content_path, "r") as f:
            # with tqsm
            pbar = tqdm(total=os.path.getsize(content_path), colour="cyan")
            for line in f:
                pbar.update(len(line.encode()))
                s.sendall(line.encode())
        # Wait and close the socket
        time.sleep(1)
        s.shutdown(socket.SHUT_WR)
        s.close()
        return True
    except Exception as e:
        print(e)
        return False


def wrapper_nc(file_path: str, port: int = 32173):
    """Wrapper for nc_logstash to run it in a thread.

    Args:
        port (int, optional): the port to netcat to. Defaults to 32173.
        file_path (str): the path to the file to send.
    """
    file_name = os.path.basename(file_path)
    print(f"Sending {file_name} to logstash...")
    if netcat("localhost", port, file_path):
        print(f"Successfully sent {file_name} to logstash. 🚀 ")
    else:
        print(f"Failed to send {file_name} to logstash. ☠️ ")


def get_filepath() -> typing.List[str]:
    """Get the file path to the generated mitre csv files.

    Returns:
        typing.List[str]: List of file paths.
    """
    # Get all cvs files in output folder
    file_paths = []
    for file in os.listdir("./output"):
        if file.endswith(".csv"):
            # Remove sample data
            if not file.endswith("sample.csv"):
                # Get the absolute path
                file_path = os.path.abspath(os.path.join("./output", file))
                file_paths.append(file_path)

    return file_paths


def main():
    """
    Main function.
    """
    # create the logstash dir
    mk_logstash_dir()
    # create the .env file
    mk_dotenv()
    # run docker-compose up
    p_logstash = subprocess.Popen(
        ["docker-compose", "up"],
        cwd="logstash",
        bufsize=1,
        universal_newlines=True,
        stdout=subprocess.PIPE,
    )
    t_start = time.time()
    # wait for stdout to print:  Pipelines running
    while True:
        line = p_logstash.stdout.readline()
        if "pipeline" in line.lower().split():
            print(line)

        if "Pipelines running" in line:
            print("Logstash is up. 🚀 ")
            break

        if p_logstash.poll() is not None:
            print("Logstash failed to start. ☠️ ")
            sys.exit(1)
        # timeout after 3 minutes
        if time.time() - t_start > 180:
            print(
                "Logstash is taking too long to start, better restart the script. ♻️ "
            )
            sys.exit(1)

    file_paths = get_filepath()
    t_pool = []
    for file_path in file_paths:
        t = Thread(target=wrapper_nc, args=(file_path,))
        t.start()
        t_pool.append(t)
    # wait for all threads to finish
    for t in t_pool:
        t.join()
    # Kill the logstash process
    p_logstash.kill()
    # print done
    print("Done. 🐈‍⬛ ")


if __name__ == "__main__":
    main()
