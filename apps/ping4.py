from subprocess import call
import numpy as np
from time import sleep
import sys

slot_time = 60

slots = np.array([
		[0, 4   + 1],
		[3, 15  + 1],
		[4, 10  + 1],
		[10, 14 + 1],
		[5, 12  + 1],
		[4, 10  + 1],
		[1, 4   + 1],
		[10, 15 + 1],
		[12, 15 + 1]
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
