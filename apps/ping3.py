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

print("Sleeping time = {} min".format(slots[arg_id, 0] / 60))
sleep(slots[arg_id, 0])

print("Running time = {} min".format(slots[arg_id, 1] / 60))
f = open("/dev/null", "w")
call(["sudo", "timeout", str(slots[arg_id, 1]), "ping", "-i 0.1", "192.168.123.1"], stdout = f)

####################
# Make sure ping is dead
####################
call(["sudo", "pkill", "ping"], stdout = f)
sleep(10)


f.close()

print("Done!")
