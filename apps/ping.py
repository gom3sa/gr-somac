from subprocess import call
import numpy as np
from time import sleep
import sys

time_list = [t for t in range(0, 3600, 360)]
n = len(time_list) - 1

t_id_0 = int(sys.argv[1]) - 1
t_id_1 = int(sys.argv[2]) - 1

####################
# 1st round
####################

print("Sleeping time = {} min".format(time_list[t_id_0] / 60))
sleep(time_list[t_id_0])

print("Running time = {} min".format(time_list[n - t_id_0] / 60))
f = open("/dev/null", "w")
call(["sudo", "timeout", str(time_list[n - t_id_0]), "ping", "-i 0.01", "192.168.123.1"], stdout = f)

####################
# Interval
####################
call(["sudo", "pkill", "ping"], stdout = f)
sleep(30)

####################
# 2nd round
####################
print("Sleeping time = {} min".format(time_list[t_id_1] / 60))
sleep(time_list[t_id_1])

print("Running time = {} min".format(time_list[n - t_id_1] / 60))
call(["sudo", "timeout", str(time_list[n - t_id_1]), "ping", "-i 0.01", "192.168.123.1"], stdout = f)

f.close()

print("Done!")
