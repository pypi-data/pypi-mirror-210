import numpy as np
from lambdaMax import lambdaMax
from CVonePair import CVonePair
import pandas as pd

def EBlassoNE_GaussianCV(X, y, kFolds=5, foldId = None, verbose=0):
    """
    This is the CV function for EB-lasso Gaussian model.
    :param x: The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.
    :param y: The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.
    :param kFolds: k -fold CV
    :param foldId: optional parameter that assign each row of X and y into k-folds
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: dict of the CV results

    Note:
    EBlasso with NE (Normal + Exponential) hierarch equivalent with alpha = 1 in EB-elastic net. Similar as
    in EB-elastic net:
    The optimal (lambda) is set at  the min MSE.

    CV function has an early stop mechanism assuming that from lambda_max to lambda_min, cv will be stopped when no
    MSE decreases(defined as current (lambda) results in MSE larger than 1*ste more of prev_MSE.
    i.e., current MSE > (prev_MSE + prev_ste) )

    """


    nStep = 19
    # early stop: for each alpha, if next lambda > SSEmin, then stop.
    if verbose >1:
        print("Empirical Bayes LASSO Linear Model (Normal + Exponential prior):", kFolds, "fold cross-validation")
    N = X.shape[0]
    K = X.shape[1]
    Epis = False

    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(np.concatenate(
                [np.repeat(np.arange(1, kFolds + 1), np.floor(N / kFolds).astype(int)), np.arange(1, N % kFolds + 1)]),
                                      N, replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), np.floor(N / kFolds).astype(int)), N,
                                      replace=False)

    lambda_Max = lambdaMax(X, y, Epis)
    lambda_Min = np.log(0.0001 * lambda_Max)
    step = (np.log(lambda_Max) - lambda_Min) / nStep
    Lambda = np.exp(np.arange(np.log(lambda_Max), lambda_Min - step, -step))
    N_step = len(Lambda)

    step = 1
    nAlpha = 1
    alpha = 1
    MSEcv = np.zeros((N_step * nAlpha, 4))
    MSEeachAlpha = np.zeros((nAlpha, 4))  # minimum MSE for each alpha
    MeanSqErr = np.zeros((kFolds, 1))
    SSE1Alpha = np.full((N_step, 2), 1e10)  # temp matrix to keep MSE + std in each step

    nLogL = np.zeros(4)
    pr = "lasso"  # 1: LassoNEG; 2: lasso; 3: EN
    model = "gaussian"  # 0: linear; 1: binomial

    for i_s in range(N_step):
        lambda_val = Lambda[i_s]
        min_index = np.argmin(SSE1Alpha[:(i_s+1), 0])
        previousL = SSE1Alpha[min_index, 0] + SSE1Alpha[min_index, 1]

        if verbose >2:
            print("\tTesting step", step, "\t\tlambda:", lambda_val, "\t", end="")

        hyperpara = np.array([alpha, lambda_val])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)

        SSE1Alpha[i_s] = logL[2:4]

        if verbose >2:
            print("sum square error:", logL[2])

        MSEcv[step - 1] = logL
        currentL = MSEcv[step - 1, 2]
        step += 1

        # break out of 2nd for loop
        if currentL - previousL > 0:
            break

    index = np.argmin(SSE1Alpha[:, 0])
    Res_lambda = Lambda[index]

    colnames = ["alpha", "lambda", "Mean Square Error", "standard error"]
    cv_MSE = pd.DataFrame(MSEcv, columns=colnames);

    result = {"CrossValidation": cv_MSE, "optimal": Res_lambda}
    return result




def EBlassoNE_BinomialCV(X, y, kFolds=5, foldId = None, verbose=0):
    """
    This is the CV function for EB-lasso Binomial model.
    :param x: The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.
    :param y: The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.
    :param kFolds: k -fold CV
    :param foldId: optional parameter that assign each row of X and y into k-folds
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: dict of the CV results

    Note:
    EBlasso with NE (Normal + Exponential) hierarch equivalent with alpha = 1 in EB-elastic net. Similar as
    in EB-elastic net:
        Note: the optimal (alpha, lambda) is set at  the max logL.

    CV function has an early stop mechanism assuming that from lambda_max to lambda_min, cv will be stopped when no
    logL increases (defined as current (alpha, lambda) results in logL smaller than 1*ste less of prev_logL.
    i.e., current logL < (prev_logL - prev_ste) )

    """


    nStep = 19
    # early stop: for each alpha, if next lambda > SSEmin, then stop.
    if verbose >1:
        print("Empirical Bayes LASSO Binomial Model (Normal + Exponential prior):", kFolds, "fold cross-validation")
    N , K = X.shape
    Epis = False

    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(np.concatenate(
                [np.repeat(np.arange(1, kFolds + 1), np.floor(N / kFolds).astype(int)), np.arange(1, N % kFolds + 1)]),
                                      N, replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), np.floor(N / kFolds).astype(int)), N,
                                      replace=False)

    lambda_Max = lambdaMax(X, y, Epis)
    lambda_Min = np.log(0.0001 * lambda_Max)
    step = (np.log(lambda_Max) - lambda_Min) / nStep
    Lambda = np.exp(np.arange(np.log(lambda_Max), lambda_Min - step, -step))
    N_step = len(Lambda)

    step = 1
    nAlpha = 1
    alpha = 1
    MSEcv = np.zeros((N_step * nAlpha, 4))
    MSEeachAlpha = np.zeros((nAlpha, 4))  # minimum MSE for each alpha
    MeanSqErr = np.zeros((kFolds, 1))
    SSE1Alpha = np.full((N_step, 2), 1e10)  # temp matrix to keep MSE + std in each step

    nLogL = np.zeros(4)
    pr = "lasso"  # 1: LassoNEG; 2: lasso; 3: EN
    model = "binomial"  # 0: linear; 1: binomial

    for i_s in range(N_step):
        lambda_val = Lambda[i_s]
        min_index = np.argmin(SSE1Alpha[:(i_s+1), 0])
        previousL = SSE1Alpha[min_index, 0] + SSE1Alpha[min_index, 1]

        if verbose >2:
            print("\tTesting step", step, "\t\tlambda:", lambda_val, "\t", end="")

        hyperpara = np.array([alpha, lambda_val])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)

        SSE1Alpha[i_s] = logL[2:4]

        if verbose >2:
            print("sum square error:", logL[2])

        MSEcv[step - 1] = logL
        currentL = MSEcv[step - 1, 2]
        step += 1

        # break out of 2nd for loop
        if currentL - previousL > 0:
            break

    index = np.argmin(SSE1Alpha[:, 0])
    Res_lambda = Lambda[index]

    colnames = ["alpha", "lambda", "logL", "standard error"]
    cv_MSE = pd.DataFrame(MSEcv, columns=colnames);
    cv_MSE["logL"] = -cv_MSE["logL"]
    result = {"CrossValidation": cv_MSE, "optimal": Res_lambda}
    return result
