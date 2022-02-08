import sys  # standard library
import os  # standard library
import argparse  # to parse arguments
import operator  # to sort list of classes objects by argument
import csv  # to write csv file
from datetime import datetime  # to get current time


# small class to keep Transaction object values (it can be moved to other file or be here)
class Transaction:
    # class constructor without arguments - just to initiate variables
    def __init__(self):
        # initialize arguments of Transaction class with initial values
        self.id = 0
        self.name = ""
        self.request_timestamp = 0
        self.response_timestamp = 0
        self.response_time = 0
        self.response_time_avg = 0.0
        self.response_time_avg_all = 0.0

    # simple function to calculate response_time value
    def calc_response_time(self):
        self.response_time = self.response_timestamp - self.request_timestamp


start = 0  # 0  - start of file
end = -1  # -1 - end of file
duration = 0
avg_start_index = 10
avg_end_index = 60
input_file = None
output_log_file = None
output_csv_file = None
second_factor = 60
round_float = 2
ext_script_cmd = None
# getting script name from args
script_name = str(sys.argv[0])
# initialize parser
parser = argparse.ArgumentParser(prog=script_name,
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 add_help=False)
# parse each argument - action='store_true' says that it is a flag and there is no value after argument
parser.add_argument('-i', help='Specify input file.')
parser.add_argument('-o', help='Specify output file.')
parser.add_argument('-s', help='Specify the start time for splitting in minutes.')
parser.add_argument('-e', help='Specify the end time for splitting in minutes.')
parser.add_argument('-d', help='Specify the duration for splitting in minutes.')
parser.add_argument('-ast', help='Specify the start index to calculate the average response time.')
parser.add_argument('-ae', help='Specify the end index to calculate the average response time.')
parser.add_argument('-ext', help='Specify name/path of external script/tool.')
parser.add_argument('-arg', help='Specify command line arguments for external script/tool.')
parser.add_argument('-r', help='Specify the number digits after decimal point for floating point numbers.')
parser.add_argument('-sec', action='store_true', help='Switch to seconds for -s/-e/-d. Default is minutes.')
parser.add_argument('-h', action='store_true', help='Show helps.')

args = parser.parse_args()


def show_help():
    print("""
log_split.py
Version:    1.0
Author:     dixit

Usage:
    log_split.py -i <input_log_file> [options]

Command line options:
    -i	Specify input file.
    -o	Specify output file.
    -s	Specify the start time for splitting in minutes.
    -e	Specify the end time for splitting in minutes.
    -d	Specify the duration for splitting in minutes.
    -ast	Specify the start index to calculate the average response time.
    -as	Specify the end index to calculate the average response time.
    -ext	Specify name/path of external script/tool.
    -arg	Specify command line arguments for external script/tool.
    -r	Specify the number digits after decimal point for floating point numbers.
    -sec	Switch to seconds for -s/-e/-d.
    -h	Show helps.

Notes:
    1. If you are not specify an output file name, log_split.py will use
    <input_log_file>.csv and <input_log_file>.log as the default output
    file name.

    2. Default start index and end index to calculate the average response
    time is 10 and 60 respectively.""")


# -h argument
# display helps
if args.h:
    show_help()
    sys.exit(0)

# -i argument
# if input file not specified
if args.i is None:
    print(f'No input fileError: No input file specified\n')
    sys.exit(0)
# if input file not exist
elif not os.path.isfile(f'./{args.i}'):
    print(f'Error: No such file {args.i}\n')
    sys.exit(0)
else:
    input_file = args.i

# -o argument
# if output files name not specified use input file name
if args.o is None:
    output_log_file = f'{input_file.split(".")[0]}_split.log'  # e.g test.log -> test_split.log
    output_csv_file = f'{input_file.split(".")[0]}_split.csv'  # e.g test.log -> test_split.csv
else:
    output_log_file = f'{args.o.split(".")[0]}.log'
    output_csv_file = f'{args.o.split(".")[0]}.csv'

# -sec
# if -sec flag specified
if args.sec:
    second_factor = 1

# -s argument
if args.s is None:
    print(f'Error: No start time specified\n')
    sys.exit(0)
# if specified and less than zero
if args.s and int(args.s) < 0:
    print(f'Error: Start time must be larger than zero\n')
    sys.exit(0)
else:
    # convert start time to seconds if needed
    start = int(args.s) * second_factor

# -d argument
# if duration time is specified
if args.d:
    duration = int(args.d)

# -e argument
# check if end time is not specified
if args.e is None:
    # check if duration is not specified
    if args.d is None:
        duration = 30 * 24 * 60
    # convert duration to seconds if needed
    duration *= second_factor
    # calculate end time based on start time and duration
    end = start * duration
else:
    # convert time to seconds if needed
    end = int(args.e) * second_factor

# check if start time and end time are valid
if start > end:
    print(f'Error: End time must larger than start time\n')
    sys.exit(0)

# convert start/end time from minutes to milliseconds
start *= 1000
end *= 1000

# check if start/end index is specified to calculate average response time
# default is set to 10 and 59 for start index and end index respectively
# -ast argument
if args.ast is None:
    avg_start_index = 1
else:
    avg_start_index = int(args.ast)

# -ae argument
if args.ae is None:
    avg_end_index = 2
else:
    avg_end_index = int(args.ae)

if avg_start_index > avg_end_index:
    print(f'Error: Start index -ast must be less than end index -ae\n')
    sys.exit(0)

# -r argument
# check if floating point rounding is specified or not - default is 2
if args.r is None:
    round_float = 2
else:
    round_float = int(args.r)

# -ext argument
# build external script command
if args.ext:
    ext_script_cmd = f'{args.ext}'
    # -arg argument
    if args.arg:
        ext_script_cmd = f'{args.ext} {args.arg}'

transaction = None  # Variable holds the current transaction data
transaction_found = True
transactions = []  # Array holds all the transactions
first_timestamp = 0  # The first timestamp found in the log file
first_timestamp_found = False  # Flag indicating that the first timestamp is found
collect_start_timestamp = 0  # The timestamp of the first transaction that will be split
collect_end_timestamp = 0  # The timestamp of the last transaction that will be split
collect_start = False  # Flag indicating that the splitting has started
collect_end = False  # Flag indicating that the splitting has finished
line_no = 0  # The line number of the current line in the log file. It's used for debugging only.

# display the current time
time = datetime.now()
print(f'Start: {time}')

# try except block - will go to except part if will not be able to read file
try:
    # opens input and output files and close it when not need it anymore - no need to close files by hand
    with open(input_file, "r") as in_log, open(output_log_file, "w") as out_log:
        # read first line
        line = in_log.readline()

        while line:
            # calculate the line number
            line_no += 1

            # Check if the current line has word REQUEST and OK
            if "REQUEST" in line and "OK" in line:
                # new Transaction object
                transaction = Transaction()

                # Split the current line by while space and tab.
                # The 3rd word should be the start timestamp and the 4th word should be
                # the end timestamp. For example:
                # REQUEST	3			GetOfferDetailsKnownUser	1582040099351	1582040099386	OK
                # $words[0]	$words[1]	$words[2]					$words[3]		$words[4]		$words[5]
                words = line.split()
                transaction.name = words[2]
                transaction.request_timestamp = int(words[3])
                transaction.response_timestamp = int(words[4])
                transaction.calc_response_time()
                transaction_found = True

            # Look for the first timestamp in the log file
            if not first_timestamp_found and transaction:
                # Record the first timestamp found, calculate the timestamp that we
                # should start to collect data
                first_timestamp = transaction.request_timestamp
                first_timestamp_found = True
                collect_start_timestamp = first_timestamp + start
                collect_end_timestamp = first_timestamp + end

            # Check if the current timestamp is larger than collect_start_timestamp
            if first_timestamp_found and not collect_start:
                # If it's larger than collect_start_timestamp then we should
                # start to collect data
                if transaction.request_timestamp > collect_start_timestamp:
                    collect_start = True

            # Check if the current timestamp is larger than collect_end_timestamp
            if collect_start and not collect_end:
                # If it's larger than collect_end_timestamp then we should
                # stop collecting data
                if transaction.request_timestamp > collect_end_timestamp:
                    collect_end = True
            # Save the current line from the original log file into the split log file
            # until the $collectEnd flag is set.
            if collect_start or line_no == 1:
                if not collect_end:
                    # write line to output file
                    out_log.write(line)
                    # Store the current transaction into the transactions list
                    if transaction_found:
                        # append transaction to the list
                        if transaction is not None:
                            transactions.append(transaction)
                        transaction_found = False
                else:
                    break

            # read next line
            line = in_log.readline()
# throw exception and handle it if there is problem with reading input file
except EnvironmentError:
    print(f'Error: Cannot read file {input_file} because $!\n')
    sys.exit(0)

temp_transactions = []  # list of transactions that has the same name
temp_start_index_exceed_limit = False  # Flag indicating that the number specified by option -ast is exceed the upper limit index of the current transaction
temp_end_index_exceed_limit = False  # Flag indicating that the number specified by option -ae is exceed the upper limit index of the current transaction
temp_sum = 0.0  # Variable holds the sum of the temporary transactions
temp_avg = 0.0  # Variable holds the average response time of the temporary transactions
temp_sum_all = 0.0
temp_avg_all = 0.0
transaction_id = 0  # Variable holds the ID of the current transaction
avg_transactions = []  # the final list of transactions after calculating the average response time

# Sort the transactions in place by response name and calculate the average response
# time for each transaction
transactions.sort(key=operator.attrgetter('name'))

for i in range(len(transactions)):

    # If the temporary transactions list is empty then initialize the temporary
    # transactions list
    if not temp_transactions:
        # Store the current transaction into the temporary transactions list
        temp_transactions.append(transactions[i])
        # Reset flags
        temp_start_index_exceed_limit = False
        temp_end_index_exceed_limit = False
        # Calculate new ID for the next transaction
        transaction_id += 1
        # Continue with the next transaction in the original transactions list
        continue

    # Check if the current transaction in the original list is the same with
    # the current transaction in the temporary list.
    if transactions[i].name == temp_transactions[0].name:
        # Store the current transaction into the temporary list
        temp_transactions.append(transactions[i])

    # The current transaction is different from the current transaction in the
    # temporary list. At this point, the temporary transactions list contains
    # transactions that has the same name. These transactions are belong to an
    # unique transaction. It's time to calculate the average response time for
    # the current transaction.
    if transactions[i].name != temp_transactions[0].name or i == len(transactions) - 1:
        # Check if the start index is exceed the upper index limit
        if avg_start_index > len(temp_transactions) - 1:
            # Set the exceed limit flag
            temp_start_index_exceed_limit = True
            # Display a warning message
            print(f"""
Warning: The start index to calculate average response time is exceeding the upper
limit index of transaction {temp_transactions[0].name}. The average response time for this
transaction will be set to zero.""")

        # Check if the end index is exceed the upper index limit
        elif avg_end_index > len(temp_transactions) - 1:
            # Set the exceed limit flag
            temp_end_index_exceed_limit = True
            # Display a warning message
            print(f"""
Warning: The end index to calculate average response time is exceeding the upper
limit index of transaction {temp_transactions[0].name}. The average response time for this
transaction will be calculated base on the transactions between the start
index and the last index.""")
        # do nothing
        else:
            pass

        temp_sum_all = 0.0
        temp_avg_all = 0.0

        # Calculate the average response time for all transactions of the
        # current request
        for trans in temp_transactions:
            temp_sum_all += trans.response_time
        temp_avg_all = float(temp_sum_all) / float(len(temp_transactions))

        temp_sum = 0.0
        temp_avg = 0.0

        # Sort in place the temporary transactions list by Response time by ascending order
        temp_transactions.sort(key=operator.attrgetter('response_time'))

        # Calculate the average response time for the current transaction in
        # the temporary transactions list only if the start index is not exceed
        # the upper limit index
        temp_end = avg_end_index
        if not temp_start_index_exceed_limit:
            if temp_end_index_exceed_limit:
                temp_end = len(temp_transactions) - 1
            for j in range(avg_start_index, temp_end + 1):
                temp_sum += temp_transactions[j].response_time

        # If the start index is exceed the upper limit then the tempSum = 0,
        # then the average response time in this case is zero.
        temp_avg = float(temp_sum) / float(temp_end - avg_start_index + 1)

        # Set the current transaction response time to the calculated average
        # response time and then store the current transaction into the average
        # transaction list
        temp_transactions[0].response_time_avg = float(temp_avg)
        temp_transactions[0].response_time_avg_all = float(temp_avg_all)
        temp_transactions[0].id = transaction_id
        avg_transactions.append(temp_transactions[0])

        # Empty the temporary transactions list to prepare for the next round
        temp_transactions.clear()

        if i < len(transactions) - 1:
            # Store the current transaction into the temporary list
            temp_transactions.append(transactions[i])
            # reset flags
            temp_start_index_exceed_limit = 0
            temp_end_index_exceed_limit = 0  # Bug_01052020: In the last version, this flag reset was missing
            # Calculate new ID for the next transaction
            transaction_id += 1

# Save the calculated data to the CSV file
# open csv file
with open(output_csv_file, 'w') as out_csv:
    header_avg_start_index = f'M{avg_start_index + 1}'
    header_avg_end_index = f'M{avg_end_index + 1}'
    col_1 = "No."
    col_2 = "Transaction name"
    col_3 = "Average total"
    col_4 = f'{header_avg_start_index} - {header_avg_end_index}'
    # make list of columns names
    fieldnames = [col_1, col_2, col_3, col_4]
    # write column names to the csv file
    writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
    writer.writeheader()
    # write data to each row by column name position
    for trans in avg_transactions:
        writer.writerow({col_1: trans.id,
                         col_2: trans.name,
                         col_3: '{:.2f}'.format(trans.response_time_avg_all),
                         col_4: '{:.2f}'.format(trans.response_time_avg)})

# write end time on the screen
end_time = datetime.now()
print(f'Finish: {end_time}')
print(f'Output: {output_log_file}')
print(f'Output: {output_csv_file}')

# call external script
if ext_script_cmd:
    print(f'Warning: External script/tool is about to be called: {ext_script_cmd}\n')
    os.system(ext_script_cmd)

if __name__ == "__main__":
    pass