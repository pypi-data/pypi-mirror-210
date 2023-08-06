import simple_matrix_api
from simple_matrix_api.client import Client
import argparse
import json
from os import path

READ_SIZE = 50_000_000


def upload_large_file(
    username: str,
    password: str,
    file_path: str,
    matrix_url: str,
):
    if not path.isfile(file_path):
        print("Argument file_path doesn't represent a file.")
        return

    client: Client = simple_matrix_api.login(username, password, matrix_url)
    urls: list[str] = []

    with open(file_path, "rb") as input:
        while True:
            content = input.read(READ_SIZE)
            if (len(content) == 0):
                break
            urls.append(client.upload("_", content))

    file_name = path.basename(file_path)
    json_path = f"{file_name}.json"
    with open(json_path, "w") as output:
        json.dump({"file_name": file_name, "urls": urls}, output)


def download_large_file(
    username: str,
    password: str,
    file_path: str,
    matrix_url: str,
):
    if not path.isfile(file_path):
        print("Argument 'file_path' doesn't represent a file.")
        return

    if not file_path.endswith(".json"):
        print(
            "Warning: file_path expects json, but file doesn't end with '.json'."
        )

    client: Client = simple_matrix_api.login(username, password, matrix_url)

    with open(file_path, "r") as input:
        json_data = json.load(input)
        with open(json_data["file_name"], "wb") as output:
            for url in json_data["urls"]:
                content_part = client.get_file(url)
                if content_part != None:
                    output.write(content_part)


parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("file_path")
parser.add_argument("-m", "--matrix")
parser.add_argument("-d", "--download", action='store_true')
args = parser.parse_args()

matrix_address = args.matrix if args.matrix != None else "matrix.org"

if args.download:
    print("Downloading")
    download_large_file(args.username, args.password, args.file_path,
                        matrix_address)

else:
    print("Uploading")
    upload_large_file(args.username, args.password, args.file_path,
                      matrix_address)
