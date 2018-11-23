from subprocess import call
import numpy as np
from time import sleep
import sys
import time

nodeid = -1

print("Starting ping")

nodeid = arg_id = int(sys.argv[1]) - 1

assert nodeid >= 0, "Error! Invalid nodeid"

profile = np.load("/tmp/profile.npy", encoding = "latin1").item()

n = len(profile[nodeid]["tx"])
f = open("/dev/null", "w")

_tic = time.time()

for i in range(n):
	t0 = profile[nodeid]["t0"][i]
	sleeptime = profile[nodeid]["sleep"][i]
	txtime = profile[nodeid]["tx"][i]

	print("t0 = {} min,\t sleep time = {} min,\t tx time = {} min".format(t0, sleeptime, txtime))

	# minutes to seconds
	sleeptime, txtime = sleeptime * 60, txtime * 60

	sleep(sleeptime)
	call(["timeout", str(txtime), "ping", "-i 0.01", "192.168.123.1"], stdout = f)
	call(["pkill", "ping"], stdout = f)

f.close()

_toc = time.time()

print("Total execution time: {} min".format(round((_toc - _tic)/60, 2)))
print("Done!")