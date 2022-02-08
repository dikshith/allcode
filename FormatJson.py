
import re


def analize_file(inputfile, sample_size, accuracy):
    """
    This function classify input file format as one of few types accepted based on the sample from the input file.

    :param inputfile: name or path+name of the input file.
    :return: Format type.

    Format types sample:

    1:  {"preview":false,"result":{"Req":"{\"sourceSystemId\":\"STAR\",\"mbrUid\":\"56D24C5E5C1668C37C6F1E916EA55E9B\",\"marketSegment\":\"IND\"}"}}

    2:  {"preview":false,"result":{"Req":"{\n  \"clientId\": \"L00797\",\n  \"sourceSystemId\": \"WGS20\",\n  \"product\": [\n    {\n      \"productType\": \"MED\",\n      \"subgroupId\": \"L00797MC01\"\n    },\n    {\n      \"productType\": \"MED\",\n      \"subgroupId\": \"L00797M001\"\n    },\n    {\n      \"productType\": \"MED\",\n      \"subgroupId\": \"L00797MS01\"\n    }\n  ]\n}"}}

    3:  "{
          ""mbrUid"": ""43BBB068D754FD2D8711802EFF96B414"",
          ""sourceSystemId"": ""MEDISYS"",
          ""product"": [
            {
              ""productType"": ""MED""
            }
          ]
        }"

    4:  "{""groupId"":""507145"",""sourceSystemId"":""CS90"",""marketSegment"":""SM""}"

    """

    with open(inputfile, "r") as f:
        sample = [next(f) for _ in range(sample_size)]

    def test_format_1(test_sample):
        count_true = 0
        p = re.compile(r'^{[\w":{},]+(\\"[\w":{},]+)+}$')
        for s in test_sample:
            if p.match(s):
                count_true += 1
                # print(f'{s}')
                # print(f'OKAY')
        if count_true / len(test_sample) > accuracy:
            print(f'Format 1: detected.')
            return True
        return False

    def test_format_2(test_sample):
        count_true = 0
        p = re.compile(r'^{[\w":{},\\\[\]]+([ ]+[\w":{},\\\[\]]+)+}$')
        for s in test_sample:
            if p.match(s):
                count_true += 1
                # print(f'{s}')
                # print(f'OKAY')
        if count_true / len(test_sample) > accuracy:
            print(f'Format 2: detected.')
            return True
        return False

    def test_format_3(test_sample):
        count_true = 0
        p = re.compile(r'(^("{)$)|(^}"$)|(^[ ]+({|])$)|(^[ ]+},?$)|(^[ ]+[\w":]+[ ](\[|[\w"]+,?)$)')
        for s in test_sample:
            if p.match(s):
                count_true += 1
                # print(f'{s}')
                # print(f'OKAY')
        if count_true / len(test_sample) > accuracy:
            print(f'Format 3: detected.')
            return True
        return False

    def test_format_4(test_sample):
        count_true = 0
        p = re.compile(r'^"[\w":,{}]+"$')
        for s in test_sample:
            if p.match(s):
                count_true += 1
                # print(f'{s}')
                # print(f'OKAY')
        if count_true / len(test_sample) > accuracy:
            print(f'Format 4: detected.')
            return True
        return False

    if test_format_1(sample):
        return 1
    if test_format_2(sample):
        return 2
    if test_format_3(sample):
        return 3
    if test_format_4(sample):
        return 4


def transform_type_1(inputfile, outputfile):
    """
    This function will change type 1 input data to desired output data syntax.

    :param inputfile: input data file
    :param outputfile: output data file

    Type 1 input data sample:
    {"preview":false,"result":{"Req":"{\"sourceSystemId\":\"STAR\",\"mbrUid\":\"56D24C5E5C1668C37C6F1E916EA55E9B\",\"marketSegment\":\"IND\"}"}}

    Desired output data syntax sample:
    "{"groupId": "W42172","sourceSystemId": "WGS20","product": [{"productType": "MED","subgroupId": "W42172M001"},{"productType": "MED","subgroupId": "W42172MC01"},{"productType": "MED","subgroupId": "W42172M002"}]}"
    """

    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        line = f.readline()
        # p = re.compile(r'^{[\w":{},]+(\\"[\w":{},]+)+}$')
        while line:
            # if not p.match(line):
            #     # repair line
            #     pass
            # print(line)
            txt = line.replace("\\", "")\
                .replace("\"{", "{")\
                .replace("}\"", "}")\
                .replace("false", '"false"')\
                .replace("true", '"true"')\
                .replace(":", ": ")\
                .replace('""', '","')\
                .replace('"false"', "false")\
                .replace('"true"', "true")\
                .strip()
            txt = "".join(['"', txt, '"'])

            # g.write(f'{line.strip()}\n')
            g.write(f'{txt}\n')

            # print(txt)
            line = f.readline()


def transform_type_2(inputfile, outputfile):
    """
    This function will change type 2 input data to desired output data syntax.

    :param inputfile: input data file
    :param outputfile: output data file

    Type 2 input data sample:
    {"preview":false,"result":{"Req":"{\n  \"clientId\": \"L00797\",\n  \"sourceSystemId\": \"WGS20\",\n  \"product\": [\n    {\n      \"productType\": \"MED\",\n      \"subgroupId\": \"L00797MC01\"\n    },\n    {\n      \"productType\": \"MED\",\n      \"subgroupId\": \"L00797M001\"\n    },\n    {\n      \"productType\": \"MED\",\n      \"subgroupId\": \"L00797MS01\"\n    }\n  ]\n}"}}

    Desired output data syntax sample:
    "{"groupId": "W42172","sourceSystemId": "WGS20","product": [{"productType": "MED","subgroupId": "W42172M001"},{"productType": "MED","subgroupId": "W42172MC01"},{"productType": "MED","subgroupId": "W42172M002"}]}"
    """

    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        line = f.readline()
        # p = re.compile(r'^{[\w":{},\\\[\]]+([ ]+[\w":{},\\\[\]]+)+}$')
        while line:
            # if not p.match(line):
            #     # repair line
            #     print(f'Line not match:\n{line}')
            #     pass
            # print(line)
            txt = line.replace(" ", "")\
                .replace("\\n", "")\
                .replace("\\", "")\
                .replace('"{', "{")\
                .replace('}"', "}")\
                .replace(":", ": ")\
                .strip()
            txt = "".join(['"', txt, '"'])

            # g.write(f'{line.strip()}\n')
            g.write(f'{txt}\n')

            # print(txt)
            line = f.readline()


def transform_type_3(inputfile, outputfile):
    """
    This function will change type 3 input data to desired output data syntax.

    :param inputfile: input data file
    :param outputfile: output data file

    Type 3 input data sample:
    "{
      ""mbrUid"": ""43BBB068D754FD2D8711802EFF96B414"",
      ""sourceSystemId"": ""MEDISYS"",
      ""product"": [
        {
          ""productType"": ""MED""
        }
      ]
    }"

    Desired output data syntax sample:
    "{"groupId": "W42172","sourceSystemId": "WGS20","product": [{"productType": "MED","subgroupId": "W42172M001"},{"productType": "MED","subgroupId": "W42172MC01"},{"productType": "MED","subgroupId": "W42172M002"}]}"
    """
    def save_data(data, g):
        # g.write(f'{"".join(data).strip()}\n')

        txt = "".join(data)\
            .replace("\n", "")\
            .replace(" ", "")\
            .replace('""', '"')\
            .replace(":", ": ")\
            .strip()

        # print(txt)

        # g.write(f'{line.strip()}\n')
        g.write(f'{txt}\n')

    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        temp = list()
        data_started = False
        line = f.readline()
        # p = re.compile(r'(^("{)$)|(^}"$)|(^[ ]+({|])$)|(^[ ]+},?$)|(^[ ]+[\w":]+[ ](\[|[\w"]+,?)$)')
        while line:
            # if not p.match(line):
            #     # repair line
            #     print(f'Line not match:\n{line}')
            #     pass
            if line.strip() == '"{' and not data_started:
                data_started = True
                temp.append(line)
                line = f.readline()
                continue
            if line.strip() == '}"' and data_started:
                data_started = False
                temp.append(line)
                line = f.readline()
                save_data(temp, g)
                temp.clear()
                continue
            if line.strip() == '"{' and data_started:
                data_started = False
                temp.append('}"')
                save_data(temp, g)
                temp.clear()
                continue
            if data_started:
                temp.append(line)
                line = f.readline()
                continue


def transform_type_4(inputfile, outputfile):
    """
    This function will change type 4 input data to desired output data syntax.

    :param inputfile: input data file
    :param outputfile: output data file

    Type 4 input data sample:
    "{""groupId"":""507145"",""sourceSystemId"":""CS90"",""marketSegment"":""SM""}"

    Desired output data syntax sample:
    "{"groupId": "W42172","sourceSystemId": "WGS20","product": [{"productType": "MED","subgroupId": "W42172M001"},{"productType": "MED","subgroupId": "W42172MC01"},{"productType": "MED","subgroupId": "W42172M002"}]}"
    """

    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        line = f.readline()
        # p = re.compile(r'^"[\w":,{}]+"$')
        while line:
            # if not p.match(line):
            #     # repair line
            #     print(f'Line not match:\n{line}')
            #     pass
            # print(line)
            txt = line.replace('""', '"')\
                .replace(":", ": ")\
                .strip()

            # g.write(f'{line.strip()}\n')
            g.write(f'{txt}\n')

            # print(txt)
            line = f.readline()


if __name__ == "__main__":

    inputfile = "input.txt"
    outputfile = "output.txt"

    sample_size = 3
    accuracy = 0.7

    type_data = analize_file(inputfile=inputfile, sample_size=sample_size, accuracy=accuracy)

    print(f'Data type: {type_data}')

    if type_data == 1:
        transform_type_1(inputfile=inputfile, outputfile=outputfile)
    elif type_data == 2:
        transform_type_2(inputfile=inputfile, outputfile=outputfile)
    elif type_data == 3:
        transform_type_3(inputfile=inputfile, outputfile=outputfile)
    elif type_data == 4:
        transform_type_4(inputfile=inputfile, outputfile=outputfile)
    else:
        print('ERROR: Unknown input data format.')
