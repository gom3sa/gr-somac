from subprocess import call
import numpy as np
from time import sleep
import sys

slot_time = 360

slots = np.array([
		[0, 1 + 1],
		[0, 6 + 1],
		[1, 6 + 1],
		[5, 9 + 1],
		[3, 8 + 1],
		[4, 8 + 1],
		[7, 9 + 1],
		[8, 9 + 1],
		[9, 9 + 1]
	]) * slot_time

arg_id = int(sys.argv[1]) - 1

####################
# Ping
####################

sleep_time = slots[arg_id, 0]
print("Sleeping time = {} min".format(sleep_time / 60))
sleep(sleep_time)

run_time = slots[arg_id, 1] - slots[arg_id, 0]
print("Running time = {} min".format(run_time / 60))
f = open("/dev/null", "w")
call(["sudo", "timeout", str(int(run_time)), "ping", "-i 0.01", "192.168.123.1"], stdout = f)

####################
# Make sure ping is dead
####################
call(["sudo", "pkill", "ping"], stdout = f)
sleep(10)

f.close()

print("Done!")
