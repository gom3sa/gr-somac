
# coding: utf-8

# In[9]:


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
from pathlib import Path


# In[10]:


home = str(Path.home())

f_csma_list = [
    home + "/UFMG/SOMAC-ML/data/_BKP/29092018/csma/round2/backlog_file.npy", # RUN
    home + "/UFMG/SOMAC-ML/data/10102018/round1/csma/backlog_file.npy",      # RUN3
    home + "/UFMG/SOMAC-ML/data/06102018/run4/5/csma/backlog_file.npy",       # RUN4
    home + "/UFMG/SOMAC-ML/data/16102018/csma/csma/backlog_file.npy",       # RUN2 (CSMA)
    home + "/UFMG/SOMAC-ML/data/16102018/tdma/csma/backlog_file.npy"       # RUN2 (TDMA)
]

f_tdma_list = [
    home + "/UFMG/SOMAC-ML/data/_BKP/29092018/tdma/round2/backlog_file.npy", # RUN
    home + "/UFMG/SOMAC-ML/data/10102018/round1/tdma/backlog_file.npy",      # RUN3
    home + "/UFMG/SOMAC-ML/data/06102018/run4/5/tdma/backlog_file.npy",       # RUN4
    home + "/UFMG/SOMAC-ML/data/16102018/csma/tdma/backlog_file.npy",       # RUN2 (CSMA)
    home + "/UFMG/SOMAC-ML/data/16102018/tdma/tdma/backlog_file.npy"       # RUN2 (TDMA)
]


# In[11]:


y = "hit_rate"

def calc_heatmap(df):
    arr_avg = np.zeros((11, 11))
    arr_var = np.zeros((11, 11))
    
    for i in range(11):
        for j in range(11):

            arr_avg[i, j] = df[y].where((df["learn_rate"] == i/10.) & (df["discount"] == j/10.)).mean()
            arr_var[i, j] = df[y].where((df["learn_rate"] == i/10.) & (df["discount"] == j/10.)).var()
              
    return arr_avg, arr_var

def plot_heatmap(arr, fig_name, save_fig = False):
    xlabels = [i for i in range(11)]
    ylabels = [i for i in range(11)]

    sns.heatmap(
        arr, vmin = 60, vmax = 80, annot = True, linewidths = 0., xticklabels = xlabels, yticklabels = ylabels
        #arr, annot = True, linewidths = 0., xticklabels = xlabels, yticklabels = ylabels
    )
    plt.title("(%)")
    plt.ylabel(r'$\alpha$' + " (x10)")
    plt.xlabel(r'$\gamma$' + " (x10)")

    if save_fig == True:
        plt.savefig(fig_name, bbox_inches='tight')
    
    #plt.show()
    plt.clf()
    
    return

def run(f_name, fig_name, save_fig = False):
    # Return an array with heatmap values
    # arr: arr[learn_rate * 10, discount * 10]
    
    arr_avg = np.zeros((11, 11))
    arr_var = np.zeros((11, 11))

    for f in f_name:

        dic_data = np.load(f, encoding = "latin1").item()
        df = pd.DataFrame.from_dict(dic_data)

        temp_avg, temp_var = calc_heatmap(df)

        arr_avg = arr_avg + temp_avg
        arr_var = arr_var + temp_var

    arr_avg = (arr_avg / (len(f_name) * 1.)) * 100.
    arr_var = (arr_var / (len(f_name) * 1.)) * 1000.
    
    plot_heatmap(arr_avg, fig_name, save_fig = save_fig)
    #plt.figure(2)
    #arr = np.divide(arr_avg, arr_var)
    #plot_heatmap(arr, fig_name, save_fig = save_fig)
    
    return arr_avg


# In[26]:


def calc_reward(curr, prev):
    # Positive reward
    if 0.95 * curr < prev < 1.05 * curr or 0.95 * prev < curr < 1.05 * prev:
        reward = 0.
    else:
        if curr > prev:
            reward = curr / prev - 1. if prev > 0. else 0.
        else:
            reward = - (prev / curr - 1.) if curr > 0. else 0.
    if reward > 1. or reward < -1:
        reward = 1 if reward > 1 else -1

    return reward * 5.

def run_boltz(init_prot = 0, learn_rate = 0.3, discount = 0.8, dic = {}, T = 1.0):
    somac = boltz(prot = init_prot, learn_rate = learn_rate, discount = discount, T = T)
    backlog, metric = test(init_prot = init_prot, learn_rate = learn_rate, discount = discount, dic = dic, alg = somac)
    return backlog, metric

def run_egreedy(init_prot = 0, learn_rate = 0.3, discount = 0.8, dic = {}, epsilon = 1.0):
    somac = egreedy(prot = init_prot, learn_rate = learn_rate, discount = discount, epsilon = epsilon)
    backlog, metric = test(init_prot = init_prot, learn_rate = learn_rate, discount = discount, dic = dic, alg = somac)
    return backlog, metric

def run_ucb(init_prot = 0, learn_rate = 0.3, discount = 0.8, dic = {}, c = 1.0):
    somac = ucb(prot = init_prot, learn_rate = learn_rate, discount = discount, c = c)
    backlog, metric = test(init_prot = init_prot, learn_rate = learn_rate, discount = discount, dic = dic, alg = somac)
    return backlog, metric

def test(init_prot = 0, learn_rate = 0.3, discount = 0.8, dic = {}, alg = {}):
    logging.basicConfig(filename="/tmp/out.log", level = logging.INFO)
    
    dic["learn_rate"].append(learn_rate)
    dic["discount"].append(discount)
    
    prot   = init_prot
    somac  = alg
    metric = {}
    t      = 0
    dt     = -1

    decision = prot
    backlog  = {}
    
    while t < n:
        metric[t] = t_csma[t] if prot == 0 else t_tdma[t]
        
        alpha = 0.5
        if t > 0:
            metric[t] = (1. - alpha) * metric[t-1] + alpha * metric[t]

        backlog[t] = prot
        
        logging.info("Metric = {}".format(metric[t]))

        if dt > 1:
            if dt == 2:
                reward = calc_reward(metric[t], metric[t-2])
            elif dt == 3:
                reward = calc_reward(metric[t], metric[t-3])
            else:
                reward = calc_reward(metric[t], metric[t-1])
                if reward > 0:
                    reward = 0.
                elif reward < 0:
                    reward = reward

            somac.update_qtable(reward, dt)

            if dt == 2 and reward >= 0:
                #decision = somac.decision(prot, keep = True)
                decision = somac.decision(prot, keep = True)
            elif dt == 2 and reward < 0.:
                decision = somac.decision(prot, force_switch = True)
                #decision = somac.decision(prot)
            else:
                #decision = somac.decision(prot, keep = False)
                decision = somac.decision(prot)

            if decision != prot:
                dt = 0

        t = t + 1
        dt = dt + 1

        prot = decision
        
    return backlog, metric
        
        
def calc_stats(backlog, metric, dic = {}):
    n_csma  = 0
    n_tdma  = 0
    n_somac = 0
    n_changes = 0
    
    per_threshold = 1.
    dic["threshold"].append(per_threshold)
    
    for t in range(n):
        if t_csma[t] >= per_threshold * t_tdma[t]:
            n_csma = n_csma + 1

            if backlog[t] == 0:
                n_somac = n_somac + 1

        if t_tdma[t] >= per_threshold * t_csma[t]:
            n_tdma = n_tdma + 1

            if backlog[t] == 1:
                n_somac = n_somac + 1

    for t in range(1, n, 1):
        if backlog[t-1] != backlog[t]:
            n_changes = n_changes + 1
    
    #########################################################################

    norm = np.max([
        round(np.mean(t_csma), 2),
        round(np.mean(t_tdma), 2),
        round(np.mean([metric[t] for t in range(n)]), 2)
    ])
    
    dic["csma_count"].append(round(n_csma * 1. / n, 2))
    dic["tdma_count"].append(round(n_tdma * 1. / n, 2))
    dic["hit_rate"].append(round(n_somac * 1. / n, 2))
    dic["n_switches"].append(n_changes)
    dic["n_tot"].append(n)
    dic["csma_performance"].append(round(np.mean(t_csma), 2))
    dic["tdma_performance"].append(round(np.mean(t_tdma), 2))
    dic["somac_performance"].append(round(np.mean([metric[t] for t in range(n)]), 2))
    dic["csma_per_performance"].append(round(np.mean(t_csma) / norm, 2))
    dic["tdma_per_performance"].append(round(np.mean(t_tdma) / norm, 2))
    dic["somac_per_performance"].append(round(np.mean([metric[t] for t in range(n)]) / norm, 2))


# ### Number of repetitions

# In[23]:


n_reptitions = 4


# ### Softmax / Boltzmann

# In[17]:


fname_list = [
    "../tmp/run_boltz.npy",
    "../tmp/run3_boltz.npy",
    "../tmp/run4_boltz.npy",
    "../tmp/run2_0_boltz.npy",
    "../tmp/run2_1_boltz.npy"
]

T_list = [i/10. for i in range(1, 20, 1)]

for T in T_list:

    for fname, f_csma, f_tdma in (zip(fname_list, f_csma_list, f_tdma_list)):

        d_csma = np.load(f_csma, encoding = "latin1").item()
        d_tdma = np.load(f_tdma, encoding = "latin1").item()

        n = np.min([len(d_csma), len(d_tdma)]) - 10

        t_csma = np.array([d_csma[t]["metrics"][0, 1] for t in range(n)])
        t_tdma = np.array([d_tdma[t]["metrics"][0, 1] for t in range(n)])

        results = {
            "learn_rate":            [],
            "discount":              [],
            "threshold":             [],
            "csma_count":            [],
            "tdma_count":            [],
            "hit_rate":              [],
            "n_switches":            [],
            "n_tot":                 [],
            "csma_performance":      [],
            "tdma_performance":      [],
            "somac_performance":     [],
            "csma_per_performance":  [],
            "tdma_per_performance":  [],
            "somac_per_performance": []
        }

        count = 0

        for step in range(n_reptitions):

            prot = 0 if step % 2 == 0 else 1

            #if step % 5 == 0:
            #    print("file: {},\tstep: {}".format(fname, step))

            learn_rate_list = [i/10. for i in range(11)]
            discount_list = [i/10. for i in range(11)]

            for learn_rate in learn_rate_list:
                for discount in discount_list:
                    backlog, metric = run_boltz(
                        init_prot = prot, learn_rate = learn_rate, discount = discount, dic = results, T = T
                    )
                    calc_stats(backlog, metric, dic = results)

                    #plt.subplot(2, 1, 1)
                    #plt.plot(t_csma); plt.plot(t_tdma); plt.legend(["CSMA", "TDMA"])

                    #plt.subplot(2, 1, 2)
                    #x = list(backlog.keys())
                    #y = [backlog[t] for t in x]
                    #plt.plot(x, y)

                    #plt.savefig("./_tmp/figs/file={},alpha={},gamma={}.pdf".format(fname[13:] + "_" + str(count), learn_rate, discount), bbox_inches='tight')

                    #count = count + 1
                    #plt.clf()
        np.save(fname, results)

    print("T = {}".format(T))
    
    _ = run(fname_list, "../heatmaps/boltz_heatmap_T={}.pdf".format(T), save_fig = True)


# ### Egreedy

# In[24]:


fname_list = [
    "../tmp/run_egreedy.npy",
    "../tmp/run3_egreedy.npy",
    "../tmp/run4_egreedy.npy",
    "../tmp/run2_0_egreedy.npy",
    "../tmp/run2_1_egreedy.npy"
]

epsilong_list = [i/10. for i in range(0, 11, 1)]

for epsilon in epsilong_list:

    for fname, f_csma, f_tdma in (zip(fname_list, f_csma_list, f_tdma_list)):

        d_csma = np.load(f_csma, encoding = "latin1").item()
        d_tdma = np.load(f_tdma, encoding = "latin1").item()

        n = np.min([len(d_csma), len(d_tdma)]) - 10

        t_csma = np.array([d_csma[t]["metrics"][0, 1] for t in range(n)])
        t_tdma = np.array([d_tdma[t]["metrics"][0, 1] for t in range(n)])

        results = {
            "learn_rate":            [],
            "discount":              [],
            "threshold":             [],
            "csma_count":            [],
            "tdma_count":            [],
            "hit_rate":              [],
            "n_switches":            [],
            "n_tot":                 [],
            "csma_performance":      [],
            "tdma_performance":      [],
            "somac_performance":     [],
            "csma_per_performance":  [],
            "tdma_per_performance":  [],
            "somac_per_performance": []
        }

        count = 0

        for step in range(n_reptitions):

            prot = 0 if step % 2 == 0 else 1

            #if step % 5 == 0:
            #    print("file: {},\tstep: {}".format(fname, step))

            learn_rate_list = [i/10. for i in range(11)]
            discount_list = [i/10. for i in range(11)]

            for learn_rate in learn_rate_list:
                for discount in discount_list:
                    backlog, metric = run_egreedy(
                        init_prot = prot, learn_rate = learn_rate, discount = discount, dic = results, epsilon = epsilon
                    )
                    calc_stats(backlog, metric, dic = results)

                    #plt.subplot(2, 1, 1)
                    #plt.plot(t_csma); plt.plot(t_tdma); plt.legend(["CSMA", "TDMA"])

                    #plt.subplot(2, 1, 2)
                    #x = list(backlog.keys())
                    #y = [backlog[t] for t in x]
                    #plt.plot(x, y)

                    #plt.savefig("./_tmp/figs/file={},alpha={},gamma={}.pdf".format(fname[13:] + "_" + str(count), learn_rate, discount), bbox_inches='tight')

                    #count = count + 1
                    #plt.clf()
        np.save(fname, results)

    print("Epsilon = {}".format(epsilon))
    
    _ = run(fname_list, "../heatmaps/egreedy_heatmap_epsilon={}.pdf".format(epsilon), save_fig = True)


# ### UCB

# In[27]:


fname_list = [
    "../tmp/run_ucb.npy",
    "../tmp/run3_ucb.npy",
    "../tmp/run4_ucb.npy",
    "../tmp/run2_0_ucb.npy",
    "../tmp/run2_1_ucb.npy"
]

c_list = [i/10. for i in range(1, 50, 5)]

for c in c_list:

    for fname, f_csma, f_tdma in (zip(fname_list, f_csma_list, f_tdma_list)):

        d_csma = np.load(f_csma, encoding = "latin1").item()
        d_tdma = np.load(f_tdma, encoding = "latin1").item()

        n = np.min([len(d_csma), len(d_tdma)]) - 10

        t_csma = np.array([d_csma[t]["metrics"][0, 1] for t in range(n)])
        t_tdma = np.array([d_tdma[t]["metrics"][0, 1] for t in range(n)])

        results = {
            "learn_rate":            [],
            "discount":              [],
            "threshold":             [],
            "csma_count":            [],
            "tdma_count":            [],
            "hit_rate":              [],
            "n_switches":            [],
            "n_tot":                 [],
            "csma_performance":      [],
            "tdma_performance":      [],
            "somac_performance":     [],
            "csma_per_performance":  [],
            "tdma_per_performance":  [],
            "somac_per_performance": []
        }

        count = 0

        for step in range(n_reptitions):

            prot = 0 if step % 2 == 0 else 1

            #if step % 5 == 0:
            #    print("file: {},\tstep: {}".format(fname, step))

            learn_rate_list = [i/10. for i in range(11)]
            discount_list = [i/10. for i in range(11)]

            for learn_rate in learn_rate_list:
                for discount in discount_list:
                    backlog, metric = run_ucb(
                        init_prot = prot, learn_rate = learn_rate, discount = discount, dic = results, c = c
                    )
                    calc_stats(backlog, metric, dic = results)

                    #plt.subplot(2, 1, 1)
                    #plt.plot(t_csma); plt.plot(t_tdma); plt.legend(["CSMA", "TDMA"])

                    #plt.subplot(2, 1, 2)
                    #x = list(backlog.keys())
                    #y = [backlog[t] for t in x]
                    #plt.plot(x, y)

                    #plt.savefig("./_tmp/figs/file={},alpha={},gamma={}.pdf".format(fname[13:] + "_" + str(count), learn_rate, discount), bbox_inches='tight')

                    #count = count + 1
                    #plt.clf()
        np.save(fname, results)

    print("c = {}".format(c))
    
    _ = run(fname_list, "../heatmaps/ucb_heatmap_c={}.pdf".format(c), save_fig = True)

