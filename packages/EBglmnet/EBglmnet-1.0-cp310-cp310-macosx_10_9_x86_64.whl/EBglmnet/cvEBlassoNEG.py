import numpy as np
from lambdaMax import lambdaMax
from CVonePair import CVonePair
import pandas as pd


def EBlassoNEG_GaussianCV(X, y, kFolds =5, foldId = None, verbose=0):
    """
    This is the CV function for EBlasso NEG (Normal + Exponential + Gamma hierarchical prior) linear model.
    :param x: The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.
    :param y: The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.
    :param kFolds: k -fold CV
    :param foldId: optional parameter that assign each row of X and y into k-folds
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: dict of the CV results

    Note: the optimal (gamma_a, gamma_b) is set at  the min MSE + 1*ste.
    This is arbitrary, and users are free to use the cv output to set the optimal  (gamma_a, gamma_b)  at min MSE.

    CV function has an early stop mechanism assuming that from low degree of shrinkage to high, cv will be stopped when no
    MSE decreases(defined as current  (gamma_a, gamma_b)  results in MSE larger than 1*ste more of prev_MSE.
    i.e., current MSE > (prev_MSE + prev_ste) )
    """

    if verbose >1:
        print("Empirical Bayes LASSO Linear Model (Normal + Exponential + Gamma prior)", kFolds,
          "-fold cross-validation")
    N = X.shape[0]

    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(
                np.concatenate([np.repeat(np.arange(1, kFolds + 1), N // kFolds), np.arange(1, N % kFolds + 1)]),
                size=N, replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), N // kFolds), size=N, replace=False)

    a_r1 = np.array([0.01, 0.05, 0.1, 0.5, 1])
    b_r1 = a_r1
    N_step1 = len(a_r1)
    a_r2 = np.array([1, 0.5, 0.1, 0.05, 0.01, -0.01, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9])
    b_r2 = np.array([0.01, 0.05, 0.1, 0.5, 1])
    N_step2 = len(a_r2) - 1
    N_step3 = len(b_r2)
    N_step = N_step1 + N_step2 + N_step3

    MeanSqErr = np.zeros((N_step, 4))
    SSE = np.zeros((kFolds, 1))
    stp = 1

    nLogL = np.zeros(4)
    pr = "lasso"  # 1: LassoNEG, 2: lasso, 3: EN
    model = "gaussian"  # 0: linear, 1: binomial

    # ------------------------------------------ step one ----------------------------------
    for i_s1 in range(N_step1):
        a_gamma = a_r1[i_s1]
        b_gamma = b_r1[i_s1]
        if verbose > 2:
            print("Testing step", stp, "\t\ta:", a_gamma, "b:", b_gamma, "\t", end="")

        hyperpara = np.array([a_gamma, b_gamma])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)

        if verbose >2 :
            print("sum squre error", logL[2])

        MeanSqErr[stp - 1] = logL
        stp += 1

    index = np.argmin(MeanSqErr[:N_step1, 2])
    previousL = MeanSqErr[index, 2] + MeanSqErr[index, 3]
    previousMin = MeanSqErr[index, 2]
    b_gamma = b_r1[index]
    index = np.where(a_r2 >= b_gamma)[0]
    a_rS2 = a_r2[np.setdiff1d(np.arange(len(a_r2)), index)]
    N_step2 = len(a_rS2)

    # ------------------------------------------ step two ----------------------------------
    for i_s2 in range(N_step2):
        a_gamma = a_rS2[i_s2]
        if verbose >2:
            print("Testing step", stp, "\t\ta:", a_gamma, "b:", b_gamma, "\t", end="")

        hyperpara = np.array([a_gamma, b_gamma])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)

        if verbose >2:
            print("sum squre error", logL[2])

        MeanSqErr[stp - 1] = logL
        currentL = MeanSqErr[stp - 1, 2]
        stp += 1

        # break out of 2nd step
        if currentL - previousL > 0 and a_gamma < 0:
            break

        if currentL < previousMin:
            preStp = stp - 1
            previousL = MeanSqErr[preStp - 1, 2] + MeanSqErr[preStp - 1, 3]
            previousMin = MeanSqErr[preStp - 1, 2]

    nStep = stp - 1
    index = np.argmin(MeanSqErr[:nStep, 2])
    a_gamma = MeanSqErr[index, 0]
    previousL = MeanSqErr[index, 2] + MeanSqErr[index, 3]
    previousMin = MeanSqErr[index, 2]
    bstep2 = MeanSqErr[index, 1]
    b_rS2 = b_r2.copy()
    index = np.where(b_r2 == bstep2)[0]
    Nbcut = len(index)
    b_rS2 = np.delete(b_rS2, index)
    N_step3 = N_step3 - Nbcut

    # ------------------------------------------ step three ----------------------------------
    for i_s3 in range(N_step3):
        b_gamma = b_rS2[i_s3]
        if verbose >2:
            print("Testing step", stp, "\t\ta:", a_gamma, "b:", b_gamma, "\t", end="")

        hyperpara = np.array([a_gamma, b_gamma])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)

        if verbose >2:
            print("sum squre error", logL[2])

        MeanSqErr[stp - 1] = logL
        currentL = MeanSqErr[stp - 1, 2]
        stp += 1

        # break out of 3rd step
        if currentL - previousL > 0:
            break

        if currentL < previousMin:
            preStp = stp - 1
            previousL = MeanSqErr[preStp - 1, 2] + MeanSqErr[preStp - 1, 3]
            previousMin = MeanSqErr[preStp - 1, 2]

    nStep = stp - 1
    index = np.argmin(MeanSqErr[:nStep, 2])
    a_gamma = MeanSqErr[index, 0]
    b_gamma = MeanSqErr[index, 1]
    opt_para = np.array([a_gamma, b_gamma])

    MSEcv_cols = ["a", "b", "Mean Square Error", "standard error"]
    MSEcv = MeanSqErr[:nStep]
    cv_MSE = pd.DataFrame(MSEcv, columns=MSEcv_cols);

    result = {"CrossValidation": cv_MSE, "optimal": opt_para}
    return result


def EBlassoNEG_BinomialCV(X, y, kFolds =5, foldId = None, verbose=0):
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

    Note: the optimal (alpha, lambda) is set at  the min MSE + 1*ste.
    This is arbitrary, and users are free to use the cv output to set the optimal (alpha, lambda) at min MSE.

    CV function has an early stop mechanism assuming that from high degree of shrinkage to low, cv will be stopped when no
    logL decreases(defined as current  (gamma_a, gamma_b)  results in logL smaller than 1*ste more of prev_lgoL.
    i.e., current logL < (prev_logL - prev_ste) )


    """

    if verbose > 1:
        print("Empirical Bayes LASSO Logistic Model (Normal + Exponential + Gamma prior)", kFolds,
              "-fold cross-validation")
    N = X.shape[0]

    if foldId is None:
        if N % kFolds != 0:
            foldId = np.random.choice(
                np.concatenate([np.repeat(np.arange(1, kFolds + 1), N // kFolds), np.arange(1, N % kFolds + 1)]),
                size=N, replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), N // kFolds), size=N, replace=False)

    a_r1 = np.array([0.01, 0.05, 0.1, 0.5, 1])
    b_r1 = a_r1
    N_step1 = len(a_r1)

    a_r2 = np.array([1, 0.5, 0.1, 0.05, 0.01, -0.01, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9])
    b_r2 = np.array([0.01, 0.05, 0.1, 0.5, 1])
    N_step2 = len(a_r2) - 1

    N_step3 = len(b_r2)
    N_step = N_step1 + N_step2 + N_step3
    Likelihood = np.zeros((N_step, 4))
    logL = np.zeros(kFolds)
    stp = 1

    nLogL = np.zeros(4)
    pr = "lassoNEG"  # 1: LassoNEG, 2: lasso, 3: EN
    model = "binomial"  # 0: linear, 1: binomial alpha

    # ------------------------------------------ step one ----------------------------------
    for i_s1 in range(N_step1):
        a_gamma = a_r1[i_s1]
        b_gamma = b_r1[i_s1]

        if verbose >2:
            print("Testing step", stp, "\t\ta:", a_gamma, "b:", b_gamma, "\t", end="")

        hyperpara = np.array([a_gamma, b_gamma])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)
        logL[2] = -logL[2]  # C produces negative logL

        if verbose >2:
            print("log likelihood:", logL[2])

        Likelihood[stp - 1] = logL
        stp += 1

    index = np.argmax(Likelihood[:N_step1, 2])
    previousL = Likelihood[index, 2] - Likelihood[index, 3]
    previousMax = Likelihood[index, 2]
    b_gamma = b_r1[index]
    index = np.where(a_r2 >= b_gamma)[0]
    a_rS2 = a_r2[np.setdiff1d(np.arange(len(a_r2)), index)]
    N_step2 = len(a_rS2)

    # ------------------------------------------ step two ----------------------------------
    for i_s2 in range(N_step2):
        a_gamma = a_rS2[i_s2]

        if verbose >2:
            print("Testing step", stp, "\t\ta:", a_gamma, "b:", b_gamma, "\t", end="")

        hyperpara = np.array([a_gamma, b_gamma])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)
        logL[2] = -logL[2]  # C produces negative logL

        if verbose >2:
            print("log likelihood:", logL[2])

        Likelihood[stp - 1] = logL
        currentL = Likelihood[stp - 1, 2]
        stp += 1

        # break out of 2nd step
        if (currentL - previousL) < 0 and a_gamma < 0:
            break
        if currentL > previousMax:
            preStp = stp - 1
            previousL = Likelihood[preStp - 1, 2] - Likelihood[preStp - 1, 3]
            previousMax = Likelihood[preStp - 1, 2]

    nStep = stp - 1
    index = np.argmax(Likelihood[:nStep, 2])
    a_gamma = Likelihood[index, 0]
    previousL = Likelihood[index, 2] - Likelihood[index, 3]
    previousMax = Likelihood[index, 2]
    bstep2 = Likelihood[index, 1]
    b_rS2 = b_r2.copy()
    index = np.where(b_r2 == bstep2)[0]
    Nbcut = len(index)
    b_rS2 = np.delete(b_rS2, index)
    N_step3 = N_step3 - Nbcut

    # ------------------------------------------ step three ----------------------------------
    for i_s3 in range(N_step3):
        b_gamma = b_rS2[i_s3]

        if verbose >2:
            print("Testing step", stp, "\t\ta:", a_gamma, "b:", b_gamma, "\t", end="")

        hyperpara = np.array([a_gamma, b_gamma])
        logL = CVonePair(X, y, kFolds, foldId, hyperpara, pr, model, verbose)

        if verbose >2:
            print("log likelihood:", logL[2])

        Likelihood[stp - 1] = logL
        currentL = Likelihood[stp - 1, 2]
        stp += 1

        # break out of 3rd step
        if (currentL - previousL) < 0:
            break
        if currentL > previousMax:
            preStp = stp - 1
            previousL = Likelihood[preStp - 1, 2] - Likelihood[preStp - 1, 3]
            previousMax = Likelihood[preStp - 1, 2]

    nStep = stp - 1
    index = np.argmax(Likelihood[:nStep, 2])
    a_gamma = Likelihood[index, 0]
    b_gamma = Likelihood[index, 1]
    opt_para = np.array([a_gamma, b_gamma])

    Likelihood = Likelihood[:nStep]
    Likelihood_names = ["a", "b", "logLikelihood", "standard error"]

    Likelihood= pd.DataFrame(Likelihood, columns=Likelihood_names);
    result = {"CrossValidation": Likelihood, "optimal": opt_para}
    return result
