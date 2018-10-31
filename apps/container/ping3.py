from subprocess import call
import numpy as np
from time import sleep
import sys

slot_time = 360

slots = np.array([
		[4, 9 + 1],
		[0, 4 + 1],
		[1, 5 + 1],
		[5, 9 + 1],
		[2, 6 + 1],
		[3, 7 + 1],
		[6, 9 + 1],
		[7, 9 + 1],
		[7, 9 + 1]
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
call(["timeout", str(int(run_time)), "ping", "-i 0.01", "192.168.123.1"], stdout = f)

####################
# Make sure ping is dead
####################
call(["pkill", "ping"], stdout = f)
sleep(10)

f.close()

print("Done!")
