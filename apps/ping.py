from subprocess import call
import numpy as np
from time import sleep
import sys

time_list = [t for t in range(0, 16200, 360)]
n = len(time_list) - 1

t_id = int(sys.argv[1]) - 1

print("Sleeping time = {} min".format(time_list[t_id] / 60))
sleep(time_list[t_id])

print("Running time = {} min".format(time_list[n - t_id] / 60))
f = open("/dev/null", "w")
call(["sudo", "timeout", str(time_list[n - t_id] + 1800), "ping", "-i 0.05", "192.168.123.1"], stdout = f)

print("Done!")
