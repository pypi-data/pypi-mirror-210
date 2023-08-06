import numpy as np
import pandas as pd
import string
from itertools import product
from sklearn.linear_model import Lasso, OrthogonalMatchingPursuit
import multiprocessing as mp
from itertools import repeat

def getX(dims, pools):
    """
    Generate design matrix of combinatorial pooling. Columns corresponds to 
    wells on the grid and the rows to the pools. Entries with 1 indicate that 
    a well is part of a pool. 

    Parameters
    ----------
    dims :  dict
        indicating which  pool belongs to which dimension
    pools : list of str
        holding names of pools
    Returns
    -------
    X : pandas dataframe
        Pooling design matrix

    """
    # build design matrix
    colnames = []
    
    for i in product(*dims.values()):
        colnames.append("_".join(i))
    X = pd.DataFrame(0, index=pools, columns = colnames)
    for i in colnames:
        idx = i.split("_")
        X.loc[idx,i] = 1
    return X



def fit(mut, X, dims):
    """
    Fit regularized linear model for a given mutant given the pooling design
    matrix X and return predicted and possible well locations

    Parameters
    ----------
    mut : numpy array
        row of the mutant count matrix, holding the read counts for all pools 
        for a given mutant
    X : pandas dataframe
        Pooling design matrix
    dims : dict
        indicating which  pool belongs to which dimension

    Returns
    -------
    pred: list of str
        predicted wells
    possible: list of str
        possible wells

    """
    nonzero = []
    for j in dims:
        nonzero.append(np.intersect1d(mut.index[mut != 0] , dims[j]))
    
    red = max([len(i) for i in nonzero])
    mut_ = mut[mut!=0]
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=red, fit_intercept=False)
    possible = ["_".join(i) for i in product(*nonzero)]
    X_  = X.loc[mut_.index , possible]
    omp = omp.fit(X_, mut_)
    pred = X_.columns[omp.coef_ !=0].tolist()
    return pred, possible


def predict_ambiguous_locations(data, experiment):
    """
    Wrapper to run predictions for ambiguous mutants.

    Parameters
    ----------
    data : pandas dataframe
        count matrix of ambiguous mutants
    experiment : LibraryExperiment
        Object holding input parameters.

    Returns
    -------
    locations : pandas dataframe
        holding the predicted locations of mutants and properties 
        (genomic coordinates, tn orientation, ambiguity etc.)

    """
    dims = experiment.pool_dims
    pools = experiment.pools
    pool_reads = data[pools].astype(int)
    X = getX(dims, pools)
    
    pred = []
    possible = []
    for i in range(pool_reads.shape[0]):
        res = fit(pool_reads.iloc[i], X, dims)
        pred.append(res[0])
        possible.append(res[1])
    
    pred = np.array([";".join(i) for i in pred])
    possible = np.array([";".join(i) for i in possible])
    amb = np.array(["Ambiguous" for i in range(data.shape[0])])
    
    if "Barcode" in data.columns:
        outcols = ["Reference","Feature", "Orientation", "Barcode",
                  "Predicted_wells", "Possible_wells", "Ambiguity"]
        locations = np.vstack((data["Reference"], data["Feature"], data["Orientation"], data["Barcode"], 
                  pred, possible, amb)).T
        locations = pd.DataFrame(locations, columns =outcols)
    else:
        outcols = ["Reference", "Feature", "Orientation",
                  "Predicted_wells", "Possible_wells", "Ambiguity"]
        locations = np.vstack((data["Reference"], data["Feature"], data["Orientation"], 
                  pred, possible, amb)).T
        locations = pd.DataFrame(locations, columns =outcols)
    return locations
