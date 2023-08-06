import numpy as np
import ctypes
from loadEBglmnetLib import loadEBglmnetLib
import warnings

def CVonePair(X, y, kFolds = 5, foldId = None, hyperparameters=[1, 0.1], prior="lassoNEG", family="gaussian", verbose=0):
    """
    This function performs kFolds cross validation on the provided one pair of hyperameters and return the CV metrics of
    (MSE, ste) for gaussian model, and (logL, ste) for binomial model.

    :param X: The input matrix of dimension `n x p`;
    :param y: The response variable.
    :param kFolds: k -fold CV
    :param foldId: optional parameter that assign each row of X and y into k-folds
    :param hyperparameters:the hyperparameters in the prior distribution.
    :param prior:Prior distribution to be used. It takes values of "lassoNEG"(default), "lasso", and "elastic net".
    :param family:Model type taking values of "gaussian" (default) or "binomial".
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: numpy array for the CV metrics of:
    - Gaussian Model: (hyperapameter1, hyperparameter2, MSE, ste);
    - Binomial Model: (hyperapameter1, hyperparameter2, logL, ste).

    """
    if prior == "lassoNEG":
        pr = 1
    elif prior == "lasso":
        pr = 2
    else:
        pr = 3

    if family == "gaussian":
        model = 0
    else:
        model = 1

        if y.dtype != np.int64:
            y = np.asarray(y, dtype=np.int64)
        y_unique = np.unique(y)
        ntab = np.bincount(y)
        min_class = np.min(ntab)
        if len(y_unique) > 2:
            raise ValueError("multinomial distribution is currently not supported")
        if min_class <= 1:
            raise ValueError("one binomial class has 1 or 0 observations; not allowed")
        if min_class < 8:
            warnings.warn("one binomial class has fewer than 8 observations; dangerous ground")


    if verbose > 3:
        print("Empirical Bayes Lasso/Elastic Net Logistic Model:", kFolds, "fold cross-validation for parameters: ",hyperparameters)

    N , K = X.shape

    group = 0
    Epis = 0
    cv_metrics = np.zeros(4)
    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(
                np.concatenate((np.repeat(np.arange(1, kFolds + 1), N // kFolds), np.arange(1, N % kFolds + 1))), N,
                replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), N // kFolds), N, replace=False)



    X = np.asfortranarray(X);
    X = X.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    Y = np.asfortranarray(y);
    Y = Y.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    foldId = np.asfortranarray(foldId);
    foldId = foldId.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    kFolds = np.asarray(kFolds);
    kFolds = kFolds.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    n = np.asarray(N);
    n = n.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    k = np.asarray(K);
    k = k.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    verbose = np.asarray(verbose);
    verbose = verbose.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    hyperpara = np.asfortranarray(hyperparameters);
    hyperpara = hyperpara.ctypes.data_as(ctypes.POINTER(ctypes.c_double));

    cv = np.asfortranarray(cv_metrics);
    cv = cv.ctypes.data_as(ctypes.POINTER(ctypes.c_double));

    epistasis = np.asarray(Epis);
    epistasis = epistasis.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    pr = np.asarray(pr);
    pr = pr.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    model = np.asarray(model);
    model = model.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    group = np.asarray(group);
    group = group.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    EBglmnetLib = loadEBglmnetLib()

    EBglmnetLib.cvOnePara(X, Y, foldId, kFolds, n, k, verbose, hyperpara, cv, epistasis, pr, model, group)

    result = np.ctypeslib.as_array(cv, shape=(1, 4));


    return result[0]
