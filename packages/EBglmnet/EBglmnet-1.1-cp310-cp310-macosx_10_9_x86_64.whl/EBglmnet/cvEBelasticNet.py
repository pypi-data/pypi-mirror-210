import numpy as np
from lambdaMax import lambdaMax
from CVonePair import CVonePair
import pandas as pd


def EBelasticNet_GaussianCV(X, y, kFolds =5, foldId = None, verbose=0):
    """
    This is the CV function for EB elastic net Gaussian model.
    :param x: The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.
    :param y: The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.
    :param kFolds: k -fold CV
    :param foldId: optional parameter that assign each row of X and y into k-folds
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: dict of the CV results

    Note: the optimal (alpha, lambda) is set at  the min MSE .

    CV function has an early stop mechanism assuming that from lambda_max to lambda_min, cv will be stopped when no
    MSE decreases(defined as current (alpha, lambda) results in MSE larger than 1*ste more of prev_MSE.
    i.e., current MSE > (prev_MSE + prev_ste) )
    """

    nStep = 19
    if verbose>0:
        print("Empirical Bayes Elastic Net Linear Model:", kFolds, "fold cross-validation")
    N , K = X.shape
    Epis = False

    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(
                np.concatenate([np.repeat(np.arange(1, kFolds + 1), N // kFolds), np.arange(1, N % kFolds + 1)]),
                size=N, replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), N // kFolds), size=N, replace=False)
    lambda_Max = lambdaMax(X, y, Epis)
    lambda_Min = np.log(0.0001 * lambda_Max)
    step = (np.log(lambda_Max) - lambda_Min) / nStep
    Lambda = np.exp(np.arange(np.log(lambda_Max), lambda_Min - step, -step))
    N_step = len(Lambda)

    Alpha = np.arange(0.9, 0, -0.1)
    nAlpha = len(Alpha)

    MSEcv = np.zeros((N_step * nAlpha, 4))
    MSEeachAlpha = np.zeros((nAlpha, 4))
    MeanSqErr = np.zeros((kFolds, 1))
    SSE1Alpha = np.full((N_step, 2), 1e10)

    nLogL = np.zeros(4)
    pr = "elastic net"
    model = "gaussian"

    step = 1
    for i_alpha in range(nAlpha):
        alpha = Alpha[i_alpha]
        SSE1Alpha = np.full((N_step, 2), 1e10)
        if verbose > 1:
            print("Testing alpha", i_alpha + 1, "/", nAlpha, ":   alpha:", alpha, "\t", end="")
        for i_s in range(N_step):
            lambda_ = Lambda[i_s]
            min_index = np.argmin(SSE1Alpha[:(i_s+1), 0])
            previousL = SSE1Alpha[min_index, 0] + SSE1Alpha[min_index, 1]
            hyperpara = [alpha, lambda_]
            logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose) #logL is numpy arrary
            SSE1Alpha[i_s] = logL[2:4]
            MSEcv[step - 1] = logL
            currentL = MSEcv[step - 1, 2]
            step += 1
            if currentL - previousL > 0:
                break
        index = np.argmin(SSE1Alpha[:, 0])
        lambda_ = Lambda[index]
        if verbose > 1:
            print("lambda:", lambda_, "   minimum square error:", SSE1Alpha[index, 0])
        MSEeachAlpha[i_alpha] = np.concatenate(([alpha, lambda_], SSE1Alpha[index]))


    MSEcv_cols = ["alpha", "lambda", "Mean Square Error", "standard error"]
    index = np.argmin(MSEeachAlpha[:, 2])
    Res_lambda = MSEeachAlpha[index, 1]
    Res_alpha = MSEeachAlpha[index, 0]
    opt_para = [Res_alpha, Res_lambda]

    cv_MSE = pd.DataFrame(MSEcv, columns=MSEcv_cols);
    result = {"CrossValidation": cv_MSE, "optimal": opt_para}

    return result



def EBelasticNet_BinomialCV(X, y, kFolds =5, foldId = None, verbose=0):
    """
    This is the CV function for EB elastic net Binomial model.
    :param x: The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.
    :param y: The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.
    :param kFolds: k -fold CV
    :param foldId: optional parameter that assign each row of X and y into k-folds
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: dict of the CV results

    Note: the optimal (alpha, lambda) is set at  the max logL.

    CV function has an early stop mechanism assuming that from lambda_max to lambda_min, cv will be stopped when no
    logL increases (defined as current (alpha, lambda) results in logL smaller than 1*ste less of prev_logL.
    i.e., current logL < (prev_logL - prev_ste) )
    """

    nStep = 19
    print("Empirical Bayes Elastic Net Binomial Model:", kFolds, "fold cross-validation")
    N , K = X.shape
    Epis = False

    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(
                np.concatenate([np.repeat(np.arange(1, kFolds + 1), N // kFolds), np.arange(1, N % kFolds + 1)]),
                size=N, replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), N // kFolds), size=N, replace=False)

    lambda_Max = lambdaMax(X, y, Epis)
    lambda_Min = np.log(0.0001 * lambda_Max)
    step = (np.log(lambda_Max) - lambda_Min) / nStep
    Lambda = np.exp(np.arange(np.log(lambda_Max), lambda_Min - step, -step))
    N_step = len(Lambda)

    Alpha = np.arange(0.9, 0, -0.1)
    nAlpha = len(Alpha)

    MSEcv = np.zeros((N_step * nAlpha, 4))
    MSEeachAlpha = np.zeros((nAlpha, 4))
    MeanSqErr = np.zeros((kFolds, 1))
    SSE1Alpha = np.full((N_step, 2), 1e10)

    nLogL = np.zeros(4)
    pr = "elastic net"
    model = "binomial"

    step = 1
    for i_alpha in range(nAlpha):
        alpha = Alpha[i_alpha]
        SSE1Alpha = np.full((N_step, 2), 1e10)
        if verbose > 1:
            print("Testing alpha", i_alpha + 1, "/", nAlpha, ":   alpha:", alpha, "\t", end="")
        for i_s in range(N_step):
            lambda_ = Lambda[i_s]
            min_index = np.argmin(SSE1Alpha[:(i_s+1), 0])
            previousL = SSE1Alpha[min_index, 0] + SSE1Alpha[min_index, 1]
            hyperpara = [alpha, lambda_]
            logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose) #logL is numpy arrary
            #logL[2] = -logL[2] # C produce negative logL
            SSE1Alpha[i_s] = logL[2:4]
            MSEcv[step - 1] = logL
            currentL = MSEcv[step - 1, 2]
            step += 1
            if currentL - previousL > 0:
                break
        index = np.argmin(SSE1Alpha[:, 0])
        lambda_ = Lambda[index]
        if verbose > 1:
            print("lambda:", lambda_, "   negative logL:", SSE1Alpha[index, 0])
        MSEeachAlpha[i_alpha] = np.concatenate(([alpha, lambda_], SSE1Alpha[index]))


    MSEcv_cols = ["alpha", "lambda", "logL", "standard error"]
    index = np.argmin(MSEeachAlpha[:, 2])
    Res_lambda = MSEeachAlpha[index, 1]
    Res_alpha = MSEeachAlpha[index, 0]
    opt_para = [Res_alpha, Res_lambda]

    cv_MSE = pd.DataFrame(MSEcv, columns=MSEcv_cols);
    cv_MSE["logL"] = -cv_MSE["logL"]
    result = {"CrossValidation": cv_MSE, "optimal": opt_para}

    return result
