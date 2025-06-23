#!/bin/python3

import json
import sys

import requests


def upload_with_json(url: str, filepath: str):
    print(f"reading data from {filepath}")
    with open(filepath, mode="r") as file:
        payload = json.loads(file.read())
    print(f"receiving data: \n{payload}")
    print(f"sending to {url}")
    response = requests.post(url, json=payload)
    print(f"request completed, response status: {response.status_code}")
    print("response body: " + response.content.decode("UTF-8"))


if __name__ == "__main__":
    filepath = input("enter filepath to json data: ")
    handle = int(input("where do you want to upload? (1 - new, 2 - view, 3 - decide): "))
    host = input("enter host name: ")
    urls = {
        1: "/transaction/create",
        2: "/transaction/view",
        3: "/transaction/decide",
    }
    if handle not in urls:
        print("you entered wring option for handle.")
        sys.exit(1)
    upload_with_json(f"http://{host}{urls[handle]}", filepath)
