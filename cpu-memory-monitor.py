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

     cpu-memory-monitor.py --commands "python" --interval 10 --duration 2 --output-file /home/reports/java-profile-20210620.csv

CSV format is

    TIMESTAMP,PID,COMMAND,%CPU,%MEM,UPTIME

Example:

    2021-06-20 05:23:44,53541,python,0.3,0.6,210
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import subprocess
import sys
import time
from datetime import datetime


def parse_to_csv(args, data):
    """
    Parse the output of ps command and generate CSV file
    """
    ts = datetime.now().strftime(args.timestamp_format)
    with open(args.output_file, "a") as outfile:
        for line in data.split("\n"):
            pid, pcpu, pmem, uptime, cmd = line.split(None, 4)
            outfile.write(
                "%s,%s,%s,%s,%s,%s\n" % (ts, pid, cmd, pcpu, pmem, uptime)
            )


def collect_metrics(args):
    cmd = [
        "ps",
        "--no-header",  # No header in the output
        "-ww",  # To set unlimited width to avoid crop
        "-o",  # Output Format
        # PID,%CPU,%MEM,Uptime,Command
        "pid,pcpu,pmem,etimes,comm",
    ]

    if args.pids != "":
        cmd += ["-p", args.pids]

    if args.commands != "":
        cmd += ["-C", args.commands]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        print("Failed to run ps command. Return code=%s" % proc.returncode)
        print(err)
        sys.exit(1)

    parse_to_csv(args, out.strip())


# Main function
def main(input_args):
    parser = ArgumentParser(
        prog="cpu-memory-monitor.py",
        formatter_class=RawDescriptionHelpFormatter,
        # description=__doc__, version="1.0.0"
    )
    parser.add_argument(
        "--pids", default="",
        help="List of Pids comma separated. Example: --pids=\"50368,41284\""
    )
    parser.add_argument(
        "--commands",
        default="",
        help=("List of commands comma separated. "
              "Example: --commands=\"python,java\"")
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        help="Interval in seconds(Default: 30)",
        default=30
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        help="Duration in minutes(Default: 120)",
        default=120
    )
    parser.add_argument(
        "--output-file", "-o",
        default="out.%s.csv" % datetime.now().strftime("%Y%m%d%H%M%S"),
        help="Output CSV file"
    )
    parser.add_argument(
        "--timestamp-format",
        help="Timestamp Format",
        default="%Y-%m-%d %H:%M:%S"
    )

    start_time = int(time.time())
    args = parser.parse_args(input_args)

    if args.pids == "" and args.commands == "":
        print("--pids or --commands are not specified")
        sys.exit(1)

    if args.pids != "" and args.commands != "":
        print("--pids and --commands are not allowed to use together.")
        sys.exit(1)

    if args.duration < 1:
        print("Duration should be not be less than 1 minute")
        sys.exit(1)

    if args.interval < 1:
        print("Interval should not be less than 1 seconds")
        sys.exit(1)

    # Remove spaces in between
    args.pids = ",".join([pid.strip() for pid in args.pids.split(",")])
    args.commands = ",".join([cmd.strip() for cmd in args.commands.split(",")])

    print("Summary\n-------------------")
    print("PIDs                 : %s" % ("-" if args.pids == "" else args.pids))
    print("Commands             : %s" % ("-" if args.commands == "" else args.commands))
    print("Interval             : %s seconds" % args.interval)
    print("Duration             : %s minutes" % args.duration)
    print("CSV Timestamp format : %s" % args.timestamp_format)
    print("Output file          : %s" % args.output_file)

    while True:
        collect_metrics(args)

        # Break when this script is running more
        # than the duration specified
        if (int(time.time()) - start_time) >= args.duration * 60:
            break

        time.sleep(args.interval)

    print("Completed")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Exiting..")
        sys.exit(1)
