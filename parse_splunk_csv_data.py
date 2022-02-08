# Author : dixit.ac@legatohealth.com
# About the program - This program reads the CSV file exported from SPLUNK.
# writes the following information into any format file(output csv).
# Pre-Requisite :
# Install PYTHON runtime or PyCharm IDE
# The CSV generated from SPUNK has REQ and double quotes "" for all fields, script does remove and formats.
# Supply input filename and output filename

# How to Run : python3 Scriptfilename.py
# ============================================================================


import os
import re


def one_line(inputfile, outputfile):
    output = []
    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        line = f.readline()
        counter = 0
        temp = []
        while line:
            if "{" in line:
                counter += 1
            elif "}" in line:
                counter -= 1

            temp.append(line)
            if counter == 0:
                output.append(temp)
                temp = []
            line = f.readline()
        # result = []
        for o in output:
            txt = "".join(o).replace("\n", "").replace(" ", "").replace(":", ": ").replace('"{', '{').replace('}"',
                                                                                                              '}').replace(
                "Req", "").replace('""', '"').replace('"', '\\"')
            g.write(txt)
            g.write("\n")
    #     result.append(txt)
    #
    # return "\n".join(result)


if __name__ == "__main__":
    infile = "C_coverageinfoJSON.json"
    outfile = "outputC_coverageinfoJSON.txt"
    one_line(infile, outfile)
