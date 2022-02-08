import re

# function that will be used to figure out what type of data format is in the input file
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

    # read a sample from input file
    with open(inputfile, "r") as f:
        # this will make a list of first n lines and store it in the sample variable (list), where n = sample_size
        sample = [next(f) for _ in range(sample_size)]

    # inside function that can only be used in the analize_file() function - it will do the test against type 1 format
    def test_format_1(test_sample):
        # counts how many lines passed the test so far
        count_true = 0
        # regular expression for type 1 format that will be stored in variable p:
        # r - raw string (easier to use in regular expressions)
        # ^{ - line starts with {
        # then we have 2 parts:
        # Part 1: [\w":{},]+ - there can be 1 or more signs: small letters, big letters, numbers, and signs: _ " : { } ,
        # + - one or more things that are before it
        # [] - means that any character can be used that is between these brackets
        # \w - small letters a-z, big letters A-Z, numbers 0-9, sign: _
        # ":{}, - just these signs
        # Part 2: (\\"[\w":{},]+)+ - there can be one or more combination/s of characters where first one is \" and after
        #                            that there will be one or more characters from Part 1
        # () - characters in these brackets need to have the same order as they are writen
        # \\ - escaped character \ (because \ is special character)
        # " - just this sign
        # [\w":{},]+ - the same as in Part 1
        # }$ - line needs to end with } sign
        p = re.compile(r'^{[\w":{},]+(\\"[\w":{},]+)+}$')
        # simple for loop where test_sample is a list of lines from input file and s is just one line from this list
        for s in test_sample:
            # this will return True if regular expression will be matched for a line
            if p.match(s):
                # if there is a match counter of valid lines will go up
                count_true += 1
        # here we check if the ratio of valid lines to all lines is higher or equal to accuracy we want (where 1.0 is 100%)
        if count_true / len(test_sample) >= accuracy:
            print(f'Format 1: detected.')
            # if the ratio is higher or equal we return True (type 1 was confirmed)
            return True
        # if the ratio is lower we return False (this data is not of type 1)
        return False

    # inside function that can only be used in the analize_file() function - it will do the test against type 2 format
    def test_format_2(test_sample):
        # counts how many lines passed the test so far
        count_true = 0
        # regular expression for type 2 format that will be stored in variable p:
        # r - raw string (easier to use in regular expressions)
        # ^{ - line starts with {
        # then we have 2 parts:
        # Part 1: [\w":{},\\\[\]]+ - there can be 1 or more signs: small letters, big letters, numbers,
        #                            and signs: _ " : { } , \ [ ]
        # + - one or more things that are before it
        # [] - means that any character can be used that is between these brackets
        # \w - small letters a-z, big letters A-Z, numbers 0-9, sign: _
        # ":{}, - just these signs
        # \\ - escaped sign \
        # \[ - escaped sign [
        # \] - escaped sign ]
        # Part 2: ([ ]+[\w":{},\\\[\]]+)+ - there can be one or more combination/s of characters where first one
        #                                   is one or more space/s and after that there will be one or more
        #                                   characters from Part 1
        # () - characters in these brackets need to have the same order as they are writen
        # [ ]+ - one or more space/s
        # [\w":{},\\\[\]]+)+ - the same as in Part 1
        # }$ - line needs to end with } sign
        p = re.compile(r'^{[\w":{},\\\[\]]+([ ]+[\w":{},\\\[\]]+)+}$')
        # simple for loop where test_sample is a list of lines from input file and s is just one line from this list
        for s in test_sample:
            # this will return True if regular expression will be matched for a line
            if p.match(s):
                # if there is a match counter of valid lines will go up
                count_true += 1
        # here we check if the ratio of valid lines to all lines is higher or equal to accuracy we want (where 1.0 is 100%)
        if count_true / len(test_sample) >= accuracy:
            print(f'Format 2: detected.')
            # if the ratio is higher or equal we return True (type 2 was confirmed)
            return True
        # if the ratio is lower we return False (this data is not of type 2)
        return False

    # inside function that can only be used in the analize_file() function - it will do the test against type 3 format
    def test_format_3(test_sample):
        # counts how many lines passed the test so far
        count_true = 0
        # regular expression for type 3 format that will be stored in variable p:
        # r - raw string (easier to use in regular expressions)
        # | - this is OR so there can be something or something else and it will be valid
        # There are 5 possible valid lines types:
        # Option 1: (^("{)$) - the line that has only "{ is valid
        # () - characters in these brackets need to have the same order as they are writen
        # ^" - line starts with " sign
        # {$ - line needs to end with { sign
        # Option 2: (^}"$) - the line that has only }" is valid
        # () - characters in these brackets need to have the same order as they are writen
        # ^} - line starts with } sign
        # "$ - line needs to end with " sign
        # Option 3: (^[ ]+({|])$) - line needs to start with one or more space/s and ends with { or } sign
        # () - characters in these brackets need to have the same order as they are writen
        # ^[ ]+ - starts with one or more space/s
        # ({|])$ - ends with { or ] sign
        # Option 4: (^[ ]+},?$) - line needs to start with one or more space/s and ends with } or }, sign/s
        # () - characters in these brackets need to have the same order as they are writen
        # ^[ ]+ - starts with one or more space/s
        # } - just the } sign
        # ? - zero or one things that are before it
        # ,?$ - ends with zero or one , sign
        # Option 5: (^[ ]+[\w":]+[ ](\[|[\w"]+,?)$) - line needs to start with one or more space/s, after that
        #                                             there are one or more signs: small letters, big letters, numbers,
        #                                             and signs: _ " :, after that there is space, after that either
        #                                             [ sign or one or more signs: small letters, big letters, numbers,
        #                                             and signs: _ ", and it will ends with zero or one , sign
        # () - characters in these brackets need to have the same order as they are writen
        # ^[ ]+ - starts with one or more space/s
        # [] - means that any character can be used that is between these brackets
        # \w - small letters a-z, big letters A-Z, numbers 0-9, sign: _
        # ": - just signs " and :
        # [ ] - just space
        # \[ - escaped [ sign
        # | - OR
        # [\w"]+ - one or more small letters a-z, big letters A-Z, numbers 0-9, signs: _ and "
        # ? - zero or one things that are before it
        # ,?$ - ends with zero or one , sign
        p = re.compile(r'(^("{)$)|(^}"$)|(^[ ]+({|])$)|(^[ ]+},?$)|(^[ ]+[\w":]+[ ](\[|[\w"]+,?)$)')
        # simple for loop where test_sample is a list of lines from input file and s is just one line from this list
        for s in test_sample:
            # this will return True if regular expression will be matched for a line
            if p.match(s):
                # if there is a match counter of valid lines will go up
                count_true += 1
        # here we check if the ratio of valid lines to all lines is higher or equal to accuracy we want (where 1.0 is 100%)
        if count_true / len(test_sample) >= accuracy:
            print(f'Format 3: detected.')
            # if the ratio is higher or equal we return True (type 3 was confirmed)
            return True
        # if the ratio is lower we return False (this data is not of type 3)
        return False

    # inside function that can only be used in the analize_file() function - it will do the test against type 4 format
    def test_format_4(test_sample):
        # counts how many lines passed the test so far
        count_true = 0
        # regular expression for type 4 format that will be stored in variable p:
        # r - raw string (easier to use in regular expressions)
        # ^" - line starts with "
        # + - one or more things that are before it
        # [] - means that any character can be used that is between these brackets
        # \w - small letters a-z, big letters A-Z, numbers 0-9, sign: _
        # ":,{} - just these signs
        # "$ - ends with sign "
        p = re.compile(r'^"[\w":,{}]+"$')
        # simple for loop where test_sample is a list of lines from input file and s is just one line from this list
        for s in test_sample:
            # this will return True if regular expression will be matched for a line
            if p.match(s):
                # if there is a match counter of valid lines will go up
                count_true += 1
        # here we check if the ratio of valid lines to all lines is higher or equal to accuracy we want (where 1.0 is 100%)
        if count_true / len(test_sample) >= accuracy:
            print(f'Format 4: detected.')
            # if the ratio is higher or equal we return True (type 4 was confirmed)
            return True
        # if the ratio is lower we return False (this data is not of type 4)
        return False

    # test sample from input file agains type 1 syntax
    if test_format_1(sample):
        # type 1 confirmed return 1
        return 1
    # test sample from input file agains type 2 syntax
    if test_format_2(sample):
        # type 2 confirmed return 2
        return 2
    # test sample from input file agains type 3 syntax
    if test_format_3(sample):
        # type 3 confirmed return 3
        return 3
    # test sample from input file agains type 4 syntax
    if test_format_4(sample):
        # type 4 confirmed return 4
        return 4
    # unknown data type return None
    return None

# function that will do the parsing of input data type 1 to desired output format
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
    # we open input file in read mode and output file in write mode
    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        # we read first line from input file
        line = f.readline()
        # while loop that will end if the line variable will be empty
        while line:
            # in the line variable we do series of replaces to get desired format of data and we store it in txt variable
            txt = line.replace("\\", "")\
                .replace("\"{", "{")\
                .replace("}\"", "}")\
                .replace("false", '"false"')\
                .replace("true", '"true"')\
                .replace(":", ": ")\
                .replace('""', '","')\
                .replace('"false"', "false")\
                .replace('"true"', "true")\
                .strip()        # at the end we remove all white signs and newlines from start and end of the data
            # we add " sign at the start and end of the txt string
            txt = "".join(['"', txt, '"'])
            # we write txt variable data with newline at the end to the output file
            g.write(f'{txt}\n')
            # we read another line from the input file and jump to the start of while loop
            line = f.readline()

# function that will do the parsing of input data type 2 to desired output format
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
    # we open input file in read mode and output file in write mode
    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        # we read first line from input file
        line = f.readline()
        # while loop that will end if the line variable will be empty
        while line:
            # in the line variable we do series of replaces to get desired format of data and we store it in txt variable
            txt = line.replace(" ", "")\
                .replace("\\n", "")\
                .replace("\\", "")\
                .replace('"{', "{")\
                .replace('}"', "}")\
                .replace(":", ": ")\
                .strip()        # at the end we remove all white signs and newlines from start and end of the data
            # we add " sign at the start and end of the txt string
            txt = "".join(['"', txt, '"'])
            # we write txt variable data with newline at the end to the output file
            g.write(f'{txt}\n')
            # we read another line from the input file and jump to the start of while loop
            line = f.readline()

# function that will do the parsing of input data type 3 to desired output format
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
    # inside function that will store transformed data to the output file (data is a list of strings)
    def save_data(data, g):
        # we join all strings in the data to one string and do series of replaces to get desired format
        txt = "".join(data)\
            .replace("\n", "")\
            .replace(" ", "")\
            .replace('""', '"')\
            .replace(":", ": ")\
            .strip()        # at the end we remove all white signs and newlines from start and end of the data
        # we write txt variable data with newline at the end to the output file
        g.write(f'{txt}\n')

    # we open input file in read mode and output file in write mode
    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        # here we will store all data before write it to the output file
        temp = list()
        # the flag if the data started to being collected or not (False is set after data was writen to the output file)
        data_started = False
        # we read first line from input file
        line = f.readline()
        # while loop that will end if the line variable will be empty
        while line:
            # we check is the line without white signs equal to "{ and was the previous data writen to the output file
            if line.strip() == '"{' and not data_started:
                data_started = True     # change flag
                temp.append(line)       # add line to temporary list of data
                line = f.readline()     # read another line
                continue                # jump to the start of while loop
            # we check is the line without white signs equal to }" and was the current temporary data not yet writen to the output file
            if line.strip() == '}"' and data_started:
                data_started = False    # change flag
                temp.append(line)       # add line to temporary list of data
                line = f.readline()     # read another line
                save_data(temp, g)      # we save all temporary data from temp to output file
                temp.clear()            # remove all data from temporary list of data
                continue                # jump to the start of while loop
            # here we check if there wa an error in the data and new data is starting before the previous one was saved
            if line.strip() == '"{' and data_started:
                data_started = False    # change flag
                temp.append('}"')       # add }" at the end of the previous data
                save_data(temp, g)      # we save all temporary data from temp to output file
                temp.clear()            # remove all data from temporary list of data
                continue                # jump to the start of while loop
            # here we just add data to the temporary list of data
            if data_started:
                temp.append(line)       # add line to temporary list of data
                line = f.readline()     # read another line
                continue                # jump to the start of while loop

# function that will do the parsing of input data type 4 to desired output format
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
    # we open input file in read mode and output file in write mode
    with open(inputfile, "r") as f, open(outputfile, "w") as g:
        # we read first line from input file
        line = f.readline()
        # while loop that will end if the line variable will be empty
        while line:
            # in the line variable we do series of replaces to get desired format of data and we store it in txt variable
            txt = line.replace('""', '"')\
                .replace(":", ": ")\
                .strip()        # at the end we remove all white signs and newlines from start and end of the data
            # we write txt variable data with newline at the end to the output file
            g.write(f'{txt}\n')
            # we read another line from the input file and jump to the start of while loop
            line = f.readline()


if __name__ == "__main__":

    # input and output files
    inputfile = "input.txt"
    outputfile = "output.txt"

    # how many lines should be used from input file to determine what type of data in inside
    sample_size = 10            # recommended value is 10
    # how many lines (percent) from sample should pass the test of data type
    accuracy = 0.7              # recommend value is 0.7 (70% - so 7 out of 10 should be correct)

    # output is 1 or 2 or 3 or 4 or None - In the analize_file() function description are writen data examples of each type
    type_data = analize_file(inputfile=inputfile, sample_size=sample_size, accuracy=accuracy)

    print(f'Data type: {type_data}')

    # use parse function designed for specific type of data
    if type_data == 1:
        # function to parse type 1 data
        transform_type_1(inputfile=inputfile, outputfile=outputfile)
    elif type_data == 2:
        # function to parse type 2 data
        transform_type_2(inputfile=inputfile, outputfile=outputfile)
    elif type_data == 3:
        # function to parse type 3 data
        transform_type_3(inputfile=inputfile, outputfile=outputfile)
    elif type_data == 4:
        # function to parse type 4 data
        transform_type_4(inputfile=inputfile, outputfile=outputfile)
    else:
        # data in the input file didn't pass the test for known data formats
        print('ERROR: Unknown input data format.')
