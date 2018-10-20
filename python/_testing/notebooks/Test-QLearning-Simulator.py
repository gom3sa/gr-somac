
# coding: utf-8

# In[357]:


import sys # in order to import QLearning* modules
sys.path.append('../..')

import numpy as np
import matplotlib.pyplot as plt
import logging
from QLearningBoltzmann import QLearningBoltzmann as boltz
from QLearningEGreedy import QLearningEGreedy as egreedy
from QLearningUCB import QLearningUCB as ucb
import pandas as pd
import seaborn as sns
import scipy.stats as st
from pathlib import Path

from threading import Thread
from threading import RLock as lock
import time


# In[358]:


home = str(Path.home())

f_csma_list = [
    home + "/Temp/SOMAC-ML/data/_BKP/29092018/csma/round2/backlog_file.npy", # RUN
    home + "/Temp/SOMAC-ML/data/10102018/round1/csma/backlog_file.npy",      # RUN3
    home + "/Temp/SOMAC-ML/data/06102018/run4/5/csma/backlog_file.npy",      # RUN4
    home + "/Temp/SOMAC-ML/data/16102018/csma/csma/backlog_file.npy",        # RUN2 (CSMA)
    home + "/Temp/SOMAC-ML/data/16102018/tdma/csma/backlog_file.npy"         # RUN2 (TDMA)
]

f_tdma_list = [
    home + "/Temp/SOMAC-ML/data/_BKP/29092018/tdma/round2/backlog_file.npy", # RUN
    home + "/Temp/SOMAC-ML/data/10102018/round1/tdma/backlog_file.npy",      # RUN3
    home + "/Temp/SOMAC-ML/data/06102018/run4/5/tdma/backlog_file.npy",      # RUN4
    home + "/Temp/SOMAC-ML/data/16102018/csma/tdma/backlog_file.npy",        # RUN2 (CSMA)
    home + "/Temp/SOMAC-ML/data/16102018/tdma/tdma/backlog_file.npy"         # RUN2 (TDMA)
]


# In[359]:


class Simulator:
    
    def __init__(self, f_csma = "", f_tdma = "", somac = {}, init_prot = 0, alpha = 0.75):
        
        self.dic_csma = np.load(f_csma, encoding = "latin1").item()
        self.dic_tdma = np.load(f_tdma, encoding = "latin1").item()
        
        n = np.min([len(self.dic_csma), len(self.dic_tdma)])
        self.arr_csma = np.array([self.dic_csma[t]["metrics"][0, 1] for t in range(n)])
        self.arr_tdma = np.array([self.dic_tdma[t]["metrics"][0, 1] for t in range(n)])
        
        self.somac = somac
        
        self.init_prot = init_prot
        self.alpha = alpha
        
        logging.basicConfig(filename = "/tmp/out.log", level = logging.INFO)
        
        return
    
    def calc_reward(self, backlog, t, dt):
        if dt == 2:
            reward = self._reward(backlog["metric"][t], backlog["metric"][t-2])
        elif dt == 3:
            reward = self._reward(backlog["metric"][t], backlog["metric"][t-3])
        else:
            reward = self._reward(backlog["metric"][t], backlog["metric"][t-1])

            if reward >= 0:
                reward = 0.
            else:
                reward = reward

        return reward
    
    def _reward(self, curr, prev):
        if curr > prev:
            reward = curr / prev - 1. if prev > 0. else 0.
        else:
            reward = - (prev / curr - 1.) if curr > 0. else 0.

        if reward > 1. or reward < -1:
            reward = 1 if reward > 1 else -1

        return reward * 5.
    
    def run(self):
        
        n = len(self.arr_csma)

        prot = self.init_prot
        decision = prot
        backlog = {"metric": {}, "prot": {}}
        _backlog = {"metric": {}, "prot": {}}
        dt = -1
        
        for t in range(n):
            backlog["metric"][t] = self.arr_csma[t] if prot == 0 else self.arr_tdma[t]
            backlog["prot"][t] = prot
            
            _backlog["metric"][t] = self.arr_csma[t] if prot == 0 else self.arr_tdma[t]
            _backlog["prot"][t] = prot
            
            if dt == 1:
                backlog["metric"][t] = (backlog["metric"][t] + backlog["metric"][t-1]) / 2.
                _backlog["metric"][t] = (_backlog["metric"][t] + _backlog["metric"][t-1]) / 2.
            
            if t > 0:
                _backlog["metric"][t] = (
                    (1. - self.alpha) * _backlog["metric"][t - 1] + self.alpha * _backlog["metric"][t]
                )
                
            logging.info("Metric = {}, Protocol = {}".format(backlog["metric"][t], backlog["prot"][t]))
            
            if dt > 1:
                reward = self.calc_reward(_backlog, t, dt)
                
                self.somac.update_qtable(reward, dt)
                
                if dt == 2 and reward >= 0:
                    decision = self.somac.decision(prot, keep = True)
                elif dt == 2 and reward < 0:
                    decision = self.somac.decision(prot, force_switch = True)
                else:
                    decision = self.somac.decision(prot)
                    
                if decision != prot:
                    dt = 0
                    
                    logging.info("Protocol switch: {} => {}".format(prot, decision))
                    
            dt = dt + 1
            prot = decision
            
        self.backlog = backlog
        
        return
    
    def get_results(self):
        
        n = len(self.backlog["metric"])
        performance = np.array([self.backlog["metric"][t] for t in range(n)])
        
        n = len(self.backlog["prot"])
        protocol = np.array([self.backlog["prot"][t] for t in range(n)])
        
        return performance, protocol
    
    def get_network_scenario(self):
        
        return self.arr_csma, self.arr_tdma


# In[360]:


class Stats:
    
    def __init__(self, results, csma, tdma):
        
        self.csma = csma
        self.tdma = tdma
        self.results = results
        
        self._to_df()
        
        return
        
    def _to_df(self):
        
        n_rounds = len(self.results)
        n_steps = len(self.results[0]["performance"])
        
        tmp = {"x": [], "y": []}
        for i in range(n_rounds):
            tmp["x"].extend(list(np.arange(n_steps)))
            tmp["y"].extend(list(self.results[i]["performance"]))
            
        self.df = pd.DataFrame.from_dict(tmp)
        
        return
    
    def avg_ci(self, ci = 95):
        
        n_rounds = len(self.results)
        n_steps = len(self.results[0]["performance"])
        
        arr = np.zeros((n_rounds, ))
        
        for i in range(n_rounds):
            arr[i] = np.mean(self.results[i]["performance"])
        
        avg, ci = np.mean(arr), list(st.t.interval(ci/100., len(arr)-1, loc=np.mean(arr), scale=st.sem(arr)))
        
        ci[0], ci[1] = round(ci[0], 2), round(ci[1], 2)
        avg = round(avg, 2)
        avg_csma = round(np.mean(self.csma), 2)
        avg_tdma = round(np.mean(self.tdma), 2)
        
        return avg_csma, avg_tdma, avg, ci
    
    def plot(self, fig = 0, ci = 95, fig_name = ""):
        
        avg_csma, avg_tdma, avg_somac, ci_somac = self.avg_ci(ci = ci)
        avg_regret, ci_regret = self.calc_regret(ci = ci)
        
        plt.figure(fig)
        
        plt.plot(self.csma); plt.plot(self.tdma)
        
        ax = sns.lineplot(x = "x", y = "y", data = self.df, ci = ci)
        
        # Markers
        m_size = 5
        ax.lines[0].set_marker("x"); ax.lines[0].set_markersize(m_size)
        ax.lines[1].set_marker("s"); ax.lines[1].set_markersize(m_size)
        ax.lines[2].set_marker("o"); ax.lines[2].set_markersize(m_size)
        
        
        plt.title("CSMA = {}, TDMA = {}, SOMAC = {}, CI = {}\nRegret = {}, CI = {}".format(
            avg_csma, avg_tdma, avg_somac, ci_somac,
            avg_regret, ci_regret
        ))
        plt.legend(["CSMA", "TDMA", "SOMAC"], loc = "lower right")
        plt.grid(True)
        
        plt.savefig(fig_name, bbox_inches='tight')
        plt.clf()
        
        return
    
    def calc_regret(self, ci = 95):
        
        n_rounds = len(self.results)
        n_steps = len(self.results[0]["performance"])

        regret = []
        for i in range(n_rounds):
            
            tmp = []
            for t in range(n_steps):
                
                opt = self.csma[t] if self.csma[t] >= self.tdma[t] else self.tdma[t]
                
                r = opt - self.results[i]["performance"][t]
                
                tmp.append(r)
                
            regret.append(np.mean(tmp))
            
        _ci = list(st.t.interval(ci/100., len(regret)-1, loc=np.mean(regret), scale=st.sem(regret)))
        
        regret = round(np.mean(regret), 2)
        _ci[0], _ci[1] = round(_ci[0], 2), round(_ci[1], 2)
        
        return regret, _ci


# ### Number of repetitions

# In[361]:


n_repetition = 30
alpha = 1.


# ### Softmax / Boltzmann

# In[362]:


def run_softmax():
    fig = 0

    for f_csma, f_tdma in zip(f_csma_list, f_tdma_list):

        results = {}

        for i in range(n_repetition):
            somac = boltz(prot = 0, learn_rate = 0.5, discount = 0.9, T = 0.6)

            prot = 0 if i % 2 == 0 else 1
            sim = Simulator(f_csma = f_csma, f_tdma = f_tdma, somac = somac, init_prot = prot, alpha = alpha)

            sim.run()
            performance, protocol = sim.get_results()

            results[i] = {"performance": performance, "protocol": protocol}

        csma, tdma = sim.get_network_scenario()

        stats = Stats(results, csma, tdma)
        with my_lock:
            stats.plot(fig = fig, fig_name = "../graphs/boltz_" + str(fig) + ".pdf")

        fig = fig + 1
        
    return


# ### E-greedy

# In[363]:


def run_egreedy():
    fig = 0

    for f_csma, f_tdma in zip(f_csma_list, f_tdma_list):

        results = {}

        for i in range(n_repetition):
            somac = egreedy(prot = 0, learn_rate = 0.7, discount = 0.5, epsilon = 0.1)

            prot = 0 if i % 2 == 0 else 1
            sim = Simulator(f_csma = f_csma, f_tdma = f_tdma, somac = somac, init_prot = prot, alpha = alpha)

            sim.run()
            performance, protocol = sim.get_results()

            results[i] = {"performance": performance, "protocol": protocol}

        csma, tdma = sim.get_network_scenario()

        stats = Stats(results, csma, tdma)
        with my_lock:
            stats.plot(fig = fig, fig_name = "../graphs/egreedy_" + str(fig) + ".pdf")

        fig = fig + 1
        
    return


# ### UCB

# In[364]:


def run_ucb():
    fig = 0

    for f_csma, f_tdma in zip(f_csma_list, f_tdma_list):

        results = {}

        for i in range(n_repetition):
            somac = ucb(prot = 0, learn_rate = 0.4, discount = 0.8, c = 0.5)

            prot = 0 if i % 2 == 0 else 1
            sim = Simulator(f_csma = f_csma, f_tdma = f_tdma, somac = somac, init_prot = prot, alpha = alpha)

            sim.run()
            performance, protocol = sim.get_results()

            results[i] = {"performance": performance, "protocol": protocol}

        csma, tdma = sim.get_network_scenario()

        stats = Stats(results, csma, tdma)
        with my_lock:
            stats.plot(fig = fig, fig_name = "../graphs/ucb_" + str(fig) + ".pdf")

        fig = fig + 1
        
    return


# ### Execution

# In[365]:


my_lock = lock()

threads = []

try:
    threads.append(Thread(target = run_softmax, args = ()))
    threads.append(Thread(target = run_egreedy, args = ()))
    threads.append(Thread(target = run_ucb, args = ()))
    
    for thread in threads:
        thread.start()
        
    for thread in threads:
        thread.join()
    
    print("Done!")
    
except:
    print("Unable to start threads")

