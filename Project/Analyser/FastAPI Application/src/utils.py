import base64
import time

import requests
import json
import pandas


def upload_document():

    url = 'http://127.0.0.1:8000/documents'

    # Path to your CSV file
    file_path = 'src/out.csv'

    # Open and read the CSV file
    with open(file_path, 'rb') as file:
        file_content = file.read()

    file_content_base64 = base64.b64encode(file_content).decode('utf-8')

    # Create the payload dictionary
    payload = {
        "name": "Real Document",
        "csvFile": file_content_base64
    }

    # Send the POST request with the payload as JSON
    response = requests.post(url, json=payload)

    print(response.json())


def convert_to_csv():

    file_path = "src/points.txt"
    with open(file_path, 'r') as file:
        file_content = file.read()

    json_data = json.loads(file_content)

    count = 0
    csv_data = []
    for sk_id, skeleton in enumerate(json_data):
        datetime = skeleton.get("datetime")
        for part in skeleton.get("parts"):
            csv_data.append([count, sk_id + 1, datetime, part.get("part_type"), part.get("x"), part.get("y")])
            count += 1

    df = pandas.DataFrame(data=csv_data, columns=['count', 'id', 'datetime', 'part_type', 'x', 'y'])
    df.to_csv("out.csv", index=False)


def upload_skeleton_realtime():

    url = 'http://127.0.0.1:8000/skeleton'

    file_path = "src/points.txt"
    with open(file_path, 'r') as file:
        file_content = file.read()
    split_file = file_content.split("\n")

    for line in split_file:
        data = json.loads(line)
        payload = {
            k: v for k, v in data.items()
        }
        response = requests.post(url, json=payload)
        print(response.json())
        time.sleep(4)


if __name__ == '__main__':
    # upload_document()
    # convert_to_csv()
    upload_skeleton_realtime()
