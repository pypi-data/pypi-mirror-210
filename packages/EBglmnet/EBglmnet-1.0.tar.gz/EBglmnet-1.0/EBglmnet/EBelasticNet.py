import ctypes
import numpy as np
from loadEBglmnetLib import loadEBglmnetLib
from scipy.stats import t as ttest
import pandas as pd



def EBelasticNet_Gaussian(BASIS, Target, Lambda, Alpha, verbose=0):
    n, k = BASIS.shape
    epis = False
    if verbose > 0:
        print("Empirical Bayes Elastic Net Gaussian Model")

    if not epis:
        N_effect = k
        Beta = np.zeros(N_effect * 4)

    WaldScore = np.zeros(1)
    intercept = np.zeros(1)
    residual = np.zeros(1)

    X = np.asfortranarray(BASIS);
    X = X.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    Y = np.asfortranarray(Target);
    Y = Y.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    alpha_factors = np.asarray(Alpha);
    lambda_factors = np.asarray(Lambda);
    alpha_factors = alpha_factors.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    lambda_factors = lambda_factors.ctypes.data_as(ctypes.POINTER(ctypes.c_double));

    Beta = np.asfortranarray(Beta);
    Beta = Beta.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    WaldScore = np.asfortranarray(WaldScore);
    WaldScore = WaldScore.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    intercept = np.asfortranarray(intercept);
    intercept = intercept.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    N = np.asarray(n);
    N = N.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    K = np.asarray(k);
    K = K.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    verbose = np.asarray(verbose);
    verbose = verbose.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    residual = np.asfortranarray(residual);
    residual = residual.ctypes.data_as(ctypes.POINTER(ctypes.c_double) );

    '''
    void elasticNetLinear(double * BASIS, double * y, double * a_lambda, double * b_Alpha,
    double * Beta,
    ouble * wald, double * intercept, int * n, int * kdim, int * verb, double * residual)
    
    EBglmnetLib.elasticNetLinear(X,Y,lambda_factors, alpha_factors,Beta,WaldScore,intercept,N,K,verbose,residual)
    '''
    EBglmnetLib = loadEBglmnetLib()

    EBglmnetLib.elasticNetLinear(X,
                                 Y,
                                 lambda_factors, alpha_factors,
                                 Beta,
                                 WaldScore,
                                 intercept,
                                 N,
                                 K,
                                 verbose,
                                 residual)

    result  = np.ctypeslib.as_array(Beta, shape=(4, k)); # the array is row based, need to manually convert to column based
    result = result.T.reshape(k, 4)
    ToKeep = np.where(result[:, 3] != 0)[0]

    if len(ToKeep) == 0:
        Blup = np.zeros((1, 4))
    else:
        nEff = len(ToKeep)
        Blup = result[ToKeep]

    t = np.abs(Blup[:, 2]) / (np.sqrt(Blup[:, 3]) + 1e-20)
    pvalue = 2 * (1 - ttest.cdf(t, df=(n - 1)))

    blup = np.hstack((Blup[:, 1:4], t.reshape(-1, 1), pvalue.reshape(-1, 1)))
    colnames = ["predictor", "beta", "posterior variance", "t-value", "p-value"]
    fit_blup = pd.DataFrame(blup, columns=colnames);

    waldScore = np.ctypeslib.as_array(WaldScore, shape=(1, 1));
    intercept = np.ctypeslib.as_array(intercept, shape=(1, 1));
    residual = np.ctypeslib.as_array(residual, shape=(1, 1));


    hyperparameters = [Alpha, Lambda]
    output = {
        "fit": fit_blup,
        "WaldScore": waldScore[0][0],
        "Intercept": intercept[0][0],
        "residual variance": residual[0][0],
        "prior": "elastic net",
        "model": "EBelasticNet Gaussian Model",
        "hyperparameters": hyperparameters
    }

    return output





def EBelasticNet_Binomial(BASIS, Target, Lambda, Alpha, verbose=0):
    n, k = BASIS.shape
    epis = False
    if verbose > 0:
        print("Empirical Bayes Elastic Net Logistic Regression Model")

    if not epis:
        N_effect = k
        Beta = np.zeros(N_effect * 4)

    WaldScore = np.zeros(1)
    intercept = np.zeros(1)
    logLikelihood = np.zeros(1)

    X = np.asfortranarray(BASIS);
    X = X.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    Y = np.asfortranarray(Target);
    Y = Y.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    alpha_factors = np.asarray(Alpha);
    lambda_factors = np.asarray(Lambda);
    alpha_factors = alpha_factors.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    lambda_factors = lambda_factors.ctypes.data_as(ctypes.POINTER(ctypes.c_double));

    Beta = np.asfortranarray(Beta);
    Beta = Beta.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    WaldScore = np.asfortranarray(WaldScore);
    WaldScore = WaldScore.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    intercept = np.asfortranarray(intercept);
    intercept = intercept.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    N = np.asarray(n);
    N = N.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    K = np.asarray(k);
    K = K.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    verbose = np.asarray(verbose);
    verbose = verbose.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    logL = np.asfortranarray(logLikelihood);
    logL = logL.ctypes.data_as(ctypes.POINTER(ctypes.c_double));


    EBglmnetLib = loadEBglmnetLib()

    EBglmnetLib.ElasticNetBinary(X,
                                 Y,
                                 lambda_factors, alpha_factors,
                                 logL,
                                 Beta,
                                 WaldScore,
                                 intercept,
                                 N,
                                 K)

    result = np.ctypeslib.as_array(Beta,
                                   shape=(4, k));  # the array is row based, need to manually convert to column based
    result = result.T.reshape(k, 4)
    ToKeep = np.where(result[:, 3] != 0)[0]

    if len(ToKeep) == 0:
        Blup = np.zeros((1, 4))
    else:
        nEff = len(ToKeep)
        Blup = result[ToKeep]

    t = np.abs(Blup[:, 2]) / (np.sqrt(Blup[:, 3]) + 1e-20)
    pvalue = 2 * (1 - ttest.cdf(t, df=(n - 1)))

    blup = np.hstack((Blup[:, 1:4], t.reshape(-1, 1), pvalue.reshape(-1, 1)))
    colnames = ["predictor", "beta", "posterior variance", "t-value", "p-value"]
    fit_blup = pd.DataFrame(blup, columns=colnames);

    waldScore = np.ctypeslib.as_array(WaldScore, shape=(1, 1));
    intercept = np.ctypeslib.as_array(intercept, shape=(1, 1));
    residual = np.ctypeslib.as_array(logL, shape=(1, 1));

    hyperparameters = [Alpha, Lambda]
    output = {
        "fit": fit_blup,
        "WaldScore": waldScore[0][0],
        "Intercept": intercept[0][0],
        "logLikelihood": residual[0][0],
        "prior": "elastic net",
        "model": "EBelasticNet Binomial Model",
        "hyperparameters": hyperparameters
    }

    return output

