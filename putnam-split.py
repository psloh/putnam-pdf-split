#!/usr/bin/env python3

import collections
import os
import re
import argparse
import sys
import csv

REGEX_SPEC_FULL = r"^(\d+)([AaBb])(\d)-(\d+)$"
REGEX_SPEC_FROM_AB = r"^([AaBb])(\d)-(\d+)$"
REGEX_SPEC_FROM_PROB_NUM = r"^(\d)-(\d+)$"
REGEX_SPEC_PAGE_NUM = r"^(\d+)$"
REGEX_SPEC_DROP = r"^x$"
REGEX_PDF_FILENAME = r"^.*\.pdf$"

argParser = argparse.ArgumentParser()
argParser.add_argument("controlFilename")
argParser.add_argument("registrantsCsvFilename")
argParser.add_argument("outputPrefix")
args = argParser.parse_args()

# Global variables
# Make sure we don't have typos in our PIN's, and that we don't overwrite
# the same PIN again later.
pinsSet = set()
currentPinPart = ""  # e.g., "123456A"
pinPartsSeenSet = set()


def readPins(pinsSet, registrantsCsvFilename):
    with open(registrantsCsvFilename) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=",")
        for row in csvReader:
            try:
                pin = int(row[0])
            except:
                print(f"ERR in {registrantsCsvFilename}: invalid {','.join(row)}")
                sys.exit(1)
            pinsSet.add(pin)


def pdfNumPages(pdfFilename):
    cmd = "pdfinfo -enc ASCII7 " + pdfFilename + " | grep Pages | awk '{print $2}'"
    numPagesStr = os.popen(cmd).read().strip()
    try:
        numPagesInt = int(numPagesStr)
        return numPagesInt
    except:
        print(f"ERR: {pdfFilename} is not a PDF file")
        sys.exit(1)


def processCommand(pinProbPageToPdfPage, controlLineNum, pdfFilename, pdfPageNum, 
        pin, ab, probNum, solPageNum):
    global pinsSet
    global currentPinPart
    global pinPartsSeenSet

    # Since we got here from a regex, integers should be legit integers,
    # and parts should be uppercase; parse them all accordingly.
    pin = int(pin)
    ab = ab.upper()
    probNum = int(probNum)
    solPageNum = int(solPageNum)

    if pdfFilename == "":
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: No PDF filename yet for command: {command}")
        sys.exit(1)

    if pin == 0:
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: No PIN yet for command: {command}")
        sys.exit(1)

    if pin not in pinsSet:
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: Foreign PIN {pin} in command: {command}")
        sys.exit(1)

    if ab == "":
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: No A/B yet for command: {command}")
        sys.exit(1)

    pinPart = f"{pin}{ab}"

    if pinPart != currentPinPart:
        if pinPart in pinPartsSeenSet:
            print(f"ERR on line {controlLineNum} of {args.controlFilename}: Already-handled PIN part {pin}{ab} in command: {command}")
            sys.exit(1)
        else:
            currentPinPart = pinPart
            pinPartsSeenSet.add(pinPart)

    if probNum == 0:
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: No problem number yet for command: {command}")
        sys.exit(1)

    if solPageNum == 0:
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: No page number yet for command: {command}")
        sys.exit(1)

    # Now record this new entry
    pinProbPage = (pin, ab, probNum, solPageNum)
    if pinProbPage in pinProbPageToPdfPage:
        print(f"ERR on line {controlLineNum} of {args.controlFilename}: repeated entry for {pin}{ab}{probNum}-{solPageNum}: {command}")
        sys.exit(1)
    pinProbPageToPdfPage[pinProbPage] = pdfPageNum
    #print(f"{pdfFilename}:p{pdfPageNum} {pin} {ab}{probNum}-{solPageNum}")


def processPinProbPageToPdfPage(execList, pinProbPageToPdfPage, pdfFilename, pdfPageNum):
    actualPdfNumPages = pdfNumPages(pdfFilename)
    if actualPdfNumPages != pdfPageNum:
        print(f"ERR {pdfFilename} has {actualPdfNumPages} pages but control file handles {pdfPageNum} pages")
        sys.exit(1)

    pinProbToMaxPage = {}
    for pinProbPage in sorted(pinProbPageToPdfPage.keys()):
        pdfPageNum = pinProbPageToPdfPage[pinProbPage]
        (pin, ab, probNum, solPageNum) = pinProbPage

        # Check for contiguous 1..N submission page ranges by just ensuring
        # that if we see solPageNum > 1, then we also have solPageNum-1
        # somewhere.
        if solPageNum > 1:
            if (pin, ab, probNum, solPageNum-1) not in pinProbPageToPdfPage:
                print(f"ERR {pdfFilename} spec has {pin}{ab}{probNum}-{solPageNum} but not {pin}{ab}{probNum}-{solPageNum-1}")
                sys.exit(1)

        # Keep track of the maximum solution page per problem
        pinProb = (pin, ab, probNum)
        if pinProbToMaxPage.get(pinProb, 0) < solPageNum:
            pinProbToMaxPage[pinProb] = solPageNum

    # Now generate the pdftk commands
    for pinProb in sorted(pinProbToMaxPage.keys()):
        (pin, ab, probNum) = pinProb
        maxPage = pinProbToMaxPage[pinProb]
        pdfPageNums = [str(pinProbPageToPdfPage[pinProb + (solPageNum, )]) for
                solPageNum in range(1, maxPage+1)]
        execList.append(f"pdftk {pdfFilename} cat {' '.join(pdfPageNums)} output {args.outputPrefix}/{pin}{ab}{probNum}.pdf")
        

    

### Main Program

readPins(pinsSet, args.registrantsCsvFilename)

pdfFilename = ""
pdfPageNum = 0
pin = 0
ab = ""
probNum = 0
solPageNum = 0

controlLineNum = 0

execList = []
pinProbPageToPdfPage = {}

with open(args.controlFilename) as controlFile:
    for command in controlFile:
        controlLineNum += 1
        command = command.strip()

        # Allow blank lines in control file for readability
        if command == "":
            continue

        # New PDF filename
        if re.match(REGEX_PDF_FILENAME, command):
            if pdfFilename != "":
                processPinProbPageToPdfPage(execList, pinProbPageToPdfPage, pdfFilename, pdfPageNum)
            pdfFilename = command
            pinProbPageToPdfPage = {}
            pdfPageNum = 0
            continue

        # Any command from here on down operates on some page of the PDF
        # file.
        pdfPageNum += 1
        if re.match(REGEX_SPEC_FULL, command):
            m = re.match(REGEX_SPEC_FULL, command)
            (pin, ab, probNum, solPageNum) = m.groups()
            processCommand(pinProbPageToPdfPage, controlLineNum, pdfFilename,
                    pdfPageNum, pin, ab, probNum, solPageNum)
        elif re.match(REGEX_SPEC_FROM_AB, command):
            m = re.match(REGEX_SPEC_FROM_AB, command)
            (ab, probNum, solPageNum) = m.groups()
            processCommand(pinProbPageToPdfPage, controlLineNum, pdfFilename,
                    pdfPageNum, pin, ab, probNum, solPageNum)
        elif re.match(REGEX_SPEC_FROM_PROB_NUM, command):

            m = re.match(REGEX_SPEC_FROM_PROB_NUM, command)
            (probNum, solPageNum) = m.groups()
            processCommand(pinProbPageToPdfPage, controlLineNum, pdfFilename,
                    pdfPageNum, pin, ab, probNum, solPageNum)
        elif re.match(REGEX_SPEC_PAGE_NUM, command):

            m = re.match(REGEX_SPEC_PAGE_NUM, command)
            (solPageNum, ) = m.groups()
            processCommand(pinProbPageToPdfPage, controlLineNum, pdfFilename,
                    pdfPageNum, pin, ab, probNum, solPageNum)
        elif re.match(REGEX_SPEC_DROP, command):
            pass  # drop the page
        else:
            print(f"ERR on line {controlLineNum} of {controlFile}: Invalid command: {command}")
            sys.exit(1)


if pdfFilename != "":
    processPinProbPageToPdfPage(execList, pinProbPageToPdfPage,
            pdfFilename, pdfPageNum)

# Now do all splitting, but first report about PIN's which are missing
missingSubmissions = collections.defaultdict(list)  # Dictionary from PIN -> list of missing parts
for pin in pinsSet:
    missingParts = []
    for part in ("A", "B"):
        pinPart = f"{pin}{part}"
        if pinPart not in pinPartsSeenSet:
            missingParts.append(part)
    #print(f"MISSING {pin} parts: {','.join(missingParts)}")


for execCmd in execList:
    print(execCmd)
