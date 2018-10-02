from subprocess import call
import numpy as np
from time import sleep
import sys

slot_time = 360

slots = np.array([
		[0, 2  + 1],
		[9, 15 + 1],
		[9, 14 + 1],
		[0, 9  + 1],
		[0, 4  + 1],
		[0, 6  + 1],
		[2, 13 + 1],
		[3, 9  + 1],
		[5, 10 + 1]
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

f.close()

print("Done!")
