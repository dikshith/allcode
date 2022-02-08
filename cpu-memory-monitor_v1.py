#!/usr/bin/env python

"""
Process Monitor

Monitors the Processes of given PIDs or command names.

Install
-------
Copy this script to /usr/local/bin and make it executable.

    chmod +x cpu-memory-monitor.py

Usage
-----
View this help message

    cpu-memory-monitor.py --help
    cpu-memory-monitor.py -h

View Version information

    cpu-memory-monitor.py --version

Run metrics collection for the given PIDs

    cpu-memory-monitor.py --pids "53009,53073,53397,53411"

Run metrics collection for the given commands

    cpu-memory-monitor.py --commands "python,java"

Configure the metrics collection interval (Seconds). The default
value is 30 seconds.

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        --interval 10

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        -i 10

Configure the metrics collection duration (Minutes). The default
value is 120 minutes.

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        --interval 10 --duration 5

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        -i 10 -d 5

Configure the timestamp format in the CSV output(Default is
"%Y-%m-%d %H:%M:%S")

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        --interval 10 --duration 5 --timestamp-format "%H-%M-%S"

If outfile is not provided, by default it will create output file
as `out.<timestamp>.csv`.

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        --interval 10 --duration 5                         \\
        --output-file /home/reports/java-profile-20210620.csv

    cpu-memory-monitor.py --pids "53009,53073,53397,53411" \\
        --interval 10 --duration 5                         \\
        -o /home/reports/java-profile-20210620.csv

CSV format is

    TIMESTAMP,PID,COMMAND,%CPU,%MEM,UPTIME

Example:

    2021-06-20 05:23:44,53541,python,0.3,0.6,210

Use it as Pipe

    ps ax | grep python | grep -v grep | python cpu-memory-monitor.py \
        --interval 10 --duration 5
"""

# Library to parse the Command line arguments
from argparse import ArgumentParser, RawDescriptionHelpFormatter

# Library to call external process(In this file ps command)
import subprocess

# System libraries to get input arguments and to control exit
import sys

# To get Unix timestamps and Sleep/wait functionality
import time

# Date time library
from datetime import datetime


def parse_to_csv(args, data, outfile):
    """
    Parse the output of ps command and generate CSV file
    """
    # Timestamp in the required format
    ts = datetime.now().strftime(args.timestamp_format)

    # Read each line of command output and split to get
    # each values.
    for line in data.split("\n"):
        pid, pcpu, pmem, uptime, cmd = line.split(None, 4)
        # Write the parsed values to csv file
        outfile.write(
            "%s,%s,%s,%s,%s,%s\n" % (ts, pid, cmd, pcpu, pmem, uptime)
        )


def collect_metrics(args, outfile):
    # Prepare the command
    # "ps --no-header -ww -o pid,pcpu,pmem,etimes,comm"
    cmd = [
        "ps",
        "--no-header",  # No header in the output
        "-ww",          # To set unlimited width to avoid crop
        "-o",           # Output Format
        # PID,%CPU,%MEM,Uptime,Command
        "pid,pcpu,pmem,etimes,comm",
    ]

    if args.pids != "":
        # Add pids list to the ps command
        # -p "pid1,pid2,pid3.."
        cmd += ["-p", args.pids]

    if args.commands != "":
        # Add commands list to the ps command
        # -C "cmd1,cmd2,cmd3.."
        cmd += ["-C", args.commands]

    # Run the ps command and validate for return code as zero
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the command to complete
    out, err = proc.communicate()
    if proc.returncode != 0:
        print("Failed to run ps command. Return code=%s" % proc.returncode)
        print(err)
        sys.exit(1)

    parse_to_csv(args, out.strip(), outfile)


def main(input_args):
    # Argument parser is a library that helps to create Command
    # line programs. Define the Parser and then define all the flags
    parser = ArgumentParser(
        prog="cpu-memory-monitor.py",
        formatter_class=RawDescriptionHelpFormatter,
        description=__doc__, version="1.2.0"
    )

    # --pids <pid1,pid2..> or --pids=<pid1,pid2..> both
    # the syntax are supported
    parser.add_argument(
        "--pids", default="",
        help="List of Pids comma separated. Example: --pids=\"50368,41284\""
    )

    # --commands <cmd1,cmd2..> or --commands=<cmd1,cmd2..> both
    # the syntax are supported
    parser.add_argument(
        "--commands",
        default="",
        help=("List of commands comma separated. "
              "Example: --commands=\"python,java\"")
    )

    # --interval <num> or --interval=<num> or -i<num> are
    # supported.
    parser.add_argument(
        "--interval", "-i",
        type=int,
        help="Interval in seconds(Default: 30)",
        default=30
    )

    # --duration <num> or --duration=<num> or -d<num> are
    # supported.
    parser.add_argument(
        "--duration", "-d",
        type=int,
        help="Duration in minutes(Default: 120)",
        default=120
    )

    # --output-file <file> or --output-file=<file> or
    # -o <file> are supported.
    parser.add_argument(
        "--output-file", "-o",
        default="out.%s.csv" % datetime.now().strftime("%Y%m%d%H%M%S"),
        help="Output CSV file"
    )

    # --timestamp-format <format> or --timestamp-format=<format>
    parser.add_argument(
        "--timestamp-format",
        help="Timestamp Format",
        default="%Y-%m-%d %H:%M:%S"
    )

    # Note the start time in Unix Epoch format(In seconds)
    start_time = int(time.time())

    # Parse the arguments as args object. All the above defined flags will
    # be accessible as args. For example, args.duration, args.interval,
    # args.output_file etc
    args = parser.parse_args(input_args)

    # If this script is called as Pipe
    # ps ax | grep python | grep -v grep | \
    #   python cpu-memory-monitor.py
    if not sys.stdin.isatty():
        pids = []
        for line in sys.stdin:
            # Split the line, first element is PID
            pids.append(line.split()[0].strip())

        args.pids = ",".join(pids)

    # Validation: If nothing is provided
    if args.pids == "" and args.commands == "":
        print("--pids or --commands are not specified")
        sys.exit(1)

    # Validation: If both are specified
    if args.pids != "" and args.commands != "":
        print("--pids and --commands are not allowed to use together.")
        sys.exit(1)

    # Validation: If duration is zero
    if args.duration < 1:
        print("Duration should be not be less than 1 minute")
        sys.exit(1)

    # Validation: If interval is zero
    if args.interval < 1:
        print("Interval should not be less than 1 seconds")
        sys.exit(1)

    # Remove spaces in between
    # Convert "1,2, 3 , 4" into "1,2,3,4"
    args.pids = ",".join([pid.strip() for pid in args.pids.split(",")])

    # Convert "python, java,  systemd" into "python,java,systemd"
    args.commands = ",".join([cmd.strip() for cmd in args.commands.split(",")])

    # Print the Summary
    print("Summary\n-------------------")
    print("PIDs                 : %s" % ("-" if args.pids == "" else args.pids))
    print("Commands             : %s" % ("-" if args.commands == "" else args.commands))
    print("Interval             : %s seconds" % args.interval)
    print("Duration             : %s minutes" % args.duration)
    print("CSV Timestamp format : %s" % args.timestamp_format)
    print("Output file          : %s" % args.output_file)

    # Open output file and share with other functions
    outfile = open(args.output_file, "w")

    # Add CSV file heading
    outfile.write("Timestamp,PID,Command,%CPU,%MEM,Uptime\n")

    # Continues loop. Break only when running time exceeds
    # the given duration.
    while True:
        collect_metrics(args, outfile)

        # Break when this script is running more
        # than the duration specified
        if (int(time.time()) - start_time) >= args.duration*60:
            break

        # Wait till the next interval starts
        time.sleep(args.interval)

    print("Completed")


# Starting point of the Program. Below code will not
# be triggered if this is imported as a library.
# Runs only when this file is directly called.
if __name__ == "__main__":
    try:
        # sys.argv will have all the arguments passed to this script
        # First argument is file name itself. Skip the first argument
        # and pass all other arguments to the parser.
        # Example: If this file called as
        # python cpu-memory-monitor.py --pids 12,26 --interval 2
        # Then sys.argv will contain
        # ["cpu-memory-monitor.py", "--pids", "12,26", "--interval", "2"]
        # Pass all the arguments except the first argument to main function.
        # main(["--pids", "12,26", "--interval", "2"])
        main(sys.argv[1:])
    except KeyboardInterrupt:
        # Catches this exception is Control+C is pressed
        print("Exiting..")
        sys.exit(1)
