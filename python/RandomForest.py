# André Gomes <andre.gomes@dcc.ufmg.br>
# The Federal University of Minas Gerais <ufmg.br>

import numpy as np
from sklearn.ensemble import RandomForestRegressor

class RandomForest:
    # This class implements the ensemble ML method Random Forest
    # This is part of the SOMAC framework
    # The forest is continuously evaluated and post prunned when it is necessary
    # Trees that are inaccurate by some extent are removed and brand new ones are added
    # There 2 regressors implemented withing this class, 1 for CSMA and another for TDMA

    def __init__(self, n_estimators = 100, max_depth = 2, max_features = "log2"):
        
        self.reg = RandomForestRegressor(
            max_depth = max_depth, random_state = 0, n_estimators = n_estimators,
            warm_start = False, bootstrap = True, max_features = max_features
        )
        
        return
    
    def feature_scaling_trainingset(self, x):
        # Feature scaling based on (x - x_avg) / x_avg
        # This is related to the training set, so it returns x_avg
        
        _x         = np.zeros(x.shape)
        self.x_avg = np.zeros(x.shape[1])
        
        for col in range(x.shape[1]):
            self.x_avg[col] = np.mean(x[:, col])

            if self.x_avg[col] != 0:
                _x[:, col] = (x[:, col] - self.x_avg[col]) * 1. / self.x_avg[col]
            else:
                _x[:, col] = (x[:, col] - self.x_avg[col])

        return _x
    
    def feature_scaling(self, x):
        # Feature scales the input data according to self.x_avg (training set)
        
        _x = np.zeros(x.shape)
        
        for col in range(x.shape[1]):
            if self.x_avg[col] != 0:
                _x[:, col] = (x[:, col] - self.x_avg[col]) * 1. / self.x_avg[col]
            else:
                _x[:, col] = (x[:, col] - self.x_avg[col])
                
        return _x      

    def fit(self, x, y):
        # Fits the training set data and enables warm_start for following updates on the model
        
        _x = self.feature_scaling_trainingset(x)
        
        self.reg.fit(_x, y)
        
        self.reg.set_params(warm_start = True)
        
        return
    
    def predict(self, x):
        # Final prediction, based on the entire set of estimators
        
        _x = self.feature_scaling(x)
        
        y_hat = self.reg.predict(_x)
        
        return y_hat
    
    def nrmse(self, y, y_hat):
        # Computes the normalized root mean square error
        
        nrmse = 0
        y_avg = np.mean(y)
        n     = len(y)
        
        assert(n > 0), "len(y) must be greater than 0"
        
        if y_avg != 0:
            nrmse = np.sqrt(np.sum((y - y_hat)**2) / n) / y_avg
        else:
            nrmse = np.sqrt(np.sum((y - y_hat)**2) / n)
            
        return nrmse
    
    def rmse(self, y, y_hat):
        # Computes the root mean square error
        
        rmse = 0
        n    = len(y)
        
        assert(n > 0), "len(y) must be greater than 0"
        
        rmse = np.sqrt(np.sum((y - y_hat)**2) / n)
        
        return rmse
        
    def post_prunning(self, x, y, threshold):
        # This method removes trees less accurate than a give threshold
        # The threshold should be based on NRMSE
        # This does NOT update the model with new trees
        
        _x = self.feature_scaling(x)
        
        err = np.array([self.nrmse(y, e.predict(_x)) for e in self.reg.estimators_])
        
        n_estimators = len(self.reg.estimators_)
        estimators_  = [
            self.reg.estimators_[i] for i in range(n_estimators) if err[i] < threshold
        ]
        
        self.reg.estimators_ = estimators_
        
        return
    
    def update(self, x, y):
        # Given a pruned forest, it inserts new trees based on new data
        
        _x = self.feature_scaling(x)
        
        if len(self.reg.estimators_) < self.reg.n_estimators:
            self.reg.fit(_x, y)
        else:
            print("No update. Forest is already full.")
            
        return

class RandomForestSOMAC:
    
    def __init__(self, n_post_prunning = 10):

        print("hello there")

        # Variables:
        #   1. n_post_prunning: number of samples no 
        self.n_post_prunning = n_post_prunning
        
        self.csma = RandomForest(n_estimators = 150, max_depth = 5)
        self.tdma = RandomForest(n_estimators = 150, max_depth = 5)
        
        # Mapping metrics names to ids
        self.map_metric = {
            'thr': 0, 'lat': 1, 'jit': 2, 'rnp': 3, 'interpkt': 4, 'snr': 5, 'contention': 6, 'non': 7, 'bsz': 8
        }
        self.map_aggr = {
            'sum': 0, 'avg': 1, 'max': 2, 'min': 3, 'var': 4, 'count': 5
        }
        
        # Metrics that will be used by the ML algorithm
        self.in_metric = [
            "interpkt", "interpkt", "interpkt", "snr", "snr", "snr", "bsz", "bsz"
        ]

        self.in_aggr = [
            "avg", "sum", "max", "min", "avg", "max", "avg", "sum"
        ]
        
        self.out_metric = "thr"
        self.out_aggr   = "avg"
        
        # Data window
        # DWs are used for evaluation, post-prunning and training new trees to the model
        self.csma_dw_x = []
        self.csma_dw_y = []
        self.tdma_dw_x = []
        self.tdma_dw_y = []
        
        # UCB (Upper-Confidence-Bound) parameters
        # This first set of parameters are argument of log() and denominators, so must be > 0
        self.n_csma    = 1
        self.n_tdma    = 1
        self.t         = 1
        
        self.c         = 0.25 # this value should be evaluated
        
        self.rmse_csma = 0
        self.rmse_tdma = 0
        
        return
    
    def train(self, file):
        # Trains the regressors of both CSMA and TDMA
        
        self.data = np.load(file, encoding = "latin1").item()
        
        x_csma, y_csma = self._get_xy("CSMA")
        x_tdma, y_tdma = self._get_xy("TDMA")
        
        self.csma.fit(x_csma, y_csma)
        self.tdma.fit(x_tdma, y_tdma)
        
        return
        
    def _get_xy(self, prot):
        # Splits the training data set according to input metrics and protocol
        
        map_prot = lambda _p: 0 if _p == "CSMA" else 1
        
        tsteps = [t for t in self.data if self.data[t]["prot"] == map_prot(prot)]
        
        y = [
            self.data[t]["metrics"][self.map_metric[self.out_metric], self.map_aggr[self.out_aggr]]
            for t in tsteps
        ]
        
        x = []
        for t in tsteps:
            row = [
                self.data[t]["metrics"][self.map_metric[met], self.map_aggr[aggr]]
                for (met, aggr) in (zip(self.in_metric, self.in_aggr))
            ]
            
            # dt and transition seem not interfer a lot
            #row.extend([self.data[t]["dt"], self.data[t]["transition"] * 1.])
            
            x.append(row)
            
        return np.array(x), np.array(y)
    
    def decision(self, arr):
        # Decision made based on UCB (Upper-Confidence-Bound) principle
        # prot = argmax(CSMA, TDMA), thinking abouth throughput
        
        curr_prot = arr["prot"]
        x = np.array([[arr["metrics"][self.map_metric[met], self.map_aggr[aggr]]
             for (met, aggr) in (zip(self.in_metric, self.in_aggr))
        ]])
        y = arr["metrics"][self.map_metric["thr"], self.map_aggr["avg"]]
        
        y_hat_csma = self.csma.predict(x)
        y_hat_tdma = self.tdma.predict(x)
        
        print("Prot: {}, y = {}".format(arr["prot"], y))
        print("y_hat_CSMA = {}, y_hat_TDMA = {}".format(y_hat_csma, y_hat_tdma))
        
        # UCB based decision
        # 1st: CSMA parameters, idx 0
        # 2nd: TDMA parameters, idx 1
        prot = np.argmax([
            y_hat_csma - self.rmse_csma + self.c * np.sqrt(np.log(self.t) / self.n_csma),
            y_hat_tdma - self.rmse_tdma + self.c * np.sqrt(np.log(self.t) / self.n_tdma)
        ])
        
        # Update parameters of UCB
        self.t = self.t + 1
        if curr_prot == 0:   # CSMA
            self.n_csma = self.n_csma + 1
            
            self.csma_dw_x.extend([list(x[0])])
            self.csma_dw_y.extend([y])
            
        elif curr_prot == 1: # TDMA
            self.n_tdma = self.n_tdma + 1
            
            self.tdma_dw_x.extend([list(x[0])])
            self.tdma_dw_y.extend([y])
            
        # Evaluate regressors
        # If necessary, post-prunning and retraining is made
        self.eval_reg()
        
        return prot
    
    def eval_reg(self):
        # Check if it is time for prunning
        # if so, prunning & retraining is made
        
        if len(self.csma_dw_y) >= self.n_post_prunning:
            x = np.array(self.csma_dw_x)
            y = np.array(self.csma_dw_y)
            
            self.csma.post_prunning(x, y, 0.6)
            self.csma.update(x, y)
            
            self.csma_dw_x, self.csma_dw_y = [], []
            
        if len(self.tdma_dw_y) >= self.n_post_prunning:
            x = np.array(self.tdma_dw_x)
            y = np.array(self.tdma_dw_y)
            
            self.tdma.post_prunning(x, y, 0.6)
            self.tdma.update(x, y)
            
            self.tdma_dw_x, self.tdma_dw_y = [], []
            
        return      
