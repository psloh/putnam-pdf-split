#!/usr/bin/env python3

import argparse
import requests
import getpass
import sys
import os
import shutil
import json
import csv
import re
import time
from datetime import datetime

AOPS_CONTEST_ID = "50"
AOPS_PROBLEM_ID_A1 = 1273
AOPS_ROUND_ID = "62"

PAUSE_AFTER_UPLOAD_SEC = 0.1

AOPS_LOGIN_URL = "https://artofproblemsolving.com/ajax.php"
AOPS_UPLOAD_URL = "https://artofproblemsolving.com/m/contests/dropzone_problem_upload.php"

AOPS_HEADERS = {
        "origin": "https://artofproblemsolving.com",
        "pragma": "no-cache",
        "referer": "https://artofproblemsolving.com/",
        }

REGEX_SUBMIT_FILENAME = r"^(\d+)([AB])(\d+).pdf$"

argParser = argparse.ArgumentParser()
argParser.add_argument("aopsUserIdCsvFilename")
argParser.add_argument("inputDir")
argParser.add_argument("outputDir")
args = argParser.parse_args()

sess = requests.Session()

### Log in to AoPS

aopsUser = input("Enter Supervisor's AoPS Username: ")
aopsPassword = getpass.getpass(prompt="Enter Supervisor's AoPS Password: ")

response = sess.post(AOPS_LOGIN_URL, data={
    "a": "login",
    "username": aopsUser,
    "password": aopsPassword,
    "stay": "false"})

if response.status_code != 200:
    print(f"ERR: AoPS login URL returned {response.status_code}")
    sys.exit(1)

responseDict = json.loads(response.content.decode("utf-8"))
try:
    userId = responseDict["response"]["user_id"]
    print(f"Supervisor AoPS user id = {userId}")
except:
    print(f"ERR: Failed to log in: {responseDict}")
    sys.exit(1)


### Load the mapping from PIN -> user_id

pinToUserId = {}

with open(args.aopsUserIdCsvFilename) as csvFile:
    csvReader = csv.reader(csvFile, delimiter=",")
    for row in csvReader:
        if row[0] != "PIN":  # skip header
            pin = int(row[0])
            user_id = int(row[1])
            pinToUserId[pin] = user_id


### Now go through every file in the directory to upload

directory = os.fsencode(args.inputDir)
if not os.path.exists(args.outputDir):
    os.mkdir(args.outputDir)

for f in sorted(os.listdir(directory)):
    filename = os.fsdecode(f)

    if not re.match(REGEX_SUBMIT_FILENAME, filename):
        print(f"ERR: {filename} has wrong format")
        sys.exit(1)

    m = re.match(REGEX_SUBMIT_FILENAME, filename)
    (pin, ab, probNum) = m.groups()

    pin = int(pin)
    if pin not in pinToUserId:
        print(f"ERR: {filename} is foreign PIN")
        sys.exit(1)
    user_id = pinToUserId[pin]

    ab = ab.upper()
    if ab == "A":
        segment_id = 1
    elif ab == "B":
        segment_id = 2
    else:
        print(f"ERR: {filename} has no A/B part")
        sys.exit(1)

    probNum = int(probNum)
    problem_id = AOPS_PROBLEM_ID_A1 - 1 + probNum + 6*(segment_id - 1)
    
    files = {
            "client_updated_at": (None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "contest_id": (None, AOPS_CONTEST_ID),
            "segment_id": (None, str(segment_id)),
            "problem_id": (None, str(problem_id)),
            "round_id": (None, AOPS_ROUND_ID),
            "display_problem_id": (None, f"{ab}{probNum}"),
            "registration_id": (None, str(pin)),
            "user_id": (None, str(user_id)),
            "force_create_grading_rows": (None, "true"),
            "file": (filename, open(f"{args.inputDir}/{filename}", "rb"), "application/pdf")
            }

    response = sess.post(AOPS_UPLOAD_URL, headers=AOPS_HEADERS, files=files)

    if response.status_code != 200:
        print(f"ERR: upload failed for {filename}: {response.status_code}")
        sys.exit(1)

    try:
        responseDict = json.loads(response.content.decode("utf-8"))
        responseResponseDict = json.loads(responseDict["response"])
        file_path = responseResponseDict[str(problem_id)]["file_path"]
        print(f"{filename} uploaded to {file_path}")
    except:
        print(f"ERR: upload failed for {filename}: {responseDict}")
        sys.exit(1)
        
    # Move this file to the done area
    shutil.move(f"{args.inputDir}/{filename}", f"{args.outputDir}/{filename}")
    time.sleep(PAUSE_AFTER_UPLOAD_SEC)
