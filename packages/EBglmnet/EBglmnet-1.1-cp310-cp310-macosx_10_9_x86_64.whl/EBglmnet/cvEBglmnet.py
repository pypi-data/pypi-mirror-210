"""

--------------------------------------------------------------------------
cvEBglmnet.py

Cross Validation (CV) Function to Determine Hyperparameters of the EBglmnet Algorithms
The degree of shrinkage, or equivalently, the number of non-zero effects selected by EBglmnet are
				controlled by the hyperparameters in the prior distribution, which can be obtained
				via Cross Validation (CV). This function performs k-fold CV for hyperparameter selection, and
				outputs the model fit results using the optimal parameters. Therefore, this function runs
				\code{EBglmnet} for (\code{k x n_parameters + 1}) times. By default, EBlasso-NE tests 20
				\eqn{\lambda}s , EBEN tests an additional 10 \eqn{\alpha}s (thus a total of 200 pair of
				hyperparameters), and EBlasso-NEG tests up to 25 pairs of (a,b).

\details{
  The three priors in EBglmnet all contain hyperparameters that control how heavy the tail probabilities are.
  Different values of the hyperparameters will yield different number of non-zero effects retained in the model.
  Appropriate selection of their values is required to obtain optimal results, and CV is the most
  oftenly used method. For Gaussian model, CV determines the optimal hyperparameter values that yield
  the minimum square error. In Binomial model, CV calculates the mean logLikelihood in each of
  the left out fold, and chooses the values that yield the maximum mean logLikelihood value of the k-folds.
  See \code{EBglmnet} for the details of hyperparameters in each prior distribution. \cr \cr

}

--------------------------------------------------------------------------


cvEBglmnet(x, y, family=("gaussian","binomial"),
		prior= ("lassoNEG","lasso","elastic net"), kFolds=5,
		foldId, verbose = 0)


INPUT ARGUMENTS:
---------------
- x             {input matrix of dimension \code{n} x \code{p}; each row is an
                observation vector, and each column is a candidate variable. When epistasis is considered, users do not need
                to create a giant matrix including both main and interaction terms. Instead, \code{x} should always be
                the matrix corresponding to the \code{p} main effects, and \code{cv.EBglmnet} will generate the interaction terms
                dynamically during running time.}

- y             {response variable. Continuous for \code{family="gaussian"}, and binary for
                \code{family="binomial"}. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.}

- family        {model type taking values of "gaussian" (default) or "binomial". }

- prior         {prior distribution to be used. Taking values of "lassoNEG"(default), "lasso", and "elastic net".
                All priors will produce a sparse outcome of the regression coefficients; see Details for choosing priors. }

- kFolds
                {number of n-fold CV. \code{kFolds} typically >=3. Although \code{kFolds}
                can be as large as the sample size (leave-one-out CV), it will be computationally intensive for large datasets. Default value is \code{kFolds=5}.}

- foldId        {an optional vector of values between 1 and \code{kFolds}
                identifying which fold each observation is assigned to. If not supplied, each of the \code{n} samples will be
                assigned to the \code{kFolds} randomly.}

- verbose       {parameter that controls the level of message output from EBglment. It takes values from 0 to 5;
                larger verbose displays more messages. 0 is recommended for CV to avoid excessive outputs. Default value for \code{verbose} is minimum message output.}





OUTPUT ARGUMENTS:
---------------
  CrossValidation
              {matrix of CV result with columns of: \cr
                column 1: hyperparameter1 \cr
                column 2: hyperparameter2 \cr
                column 3: prediction metrics/Criteria\cr
                column 4: standard error in the k-fold CV. \cr

                Prediction metrics is the mean square error (MSE) for Gaussian model and mean log likelihood (logL) for the binomial model.	}

  optimal hyperparameter
                {the hyperparameters that yield the smallest MSE or the largest logL.}


fit             {model fit using the optimal parameters computed by CV. See \code{EBglmnet} for values in this item. }

WaldScore       {the Wald Score for the posterior distribution.	See (Huang A., Martin E., et al., 2014b) for using Wald Score to identify significant  effect set.}

Intercept       {model intercept. This parameter is not shrunk (assumes uniform prior).}

residual variance
                {the residual variance if the Gaussian family is assumed in the GLM}

logLikelihood
                {the log Likelihood if the Binomial family is assumed in the GLM}

hyperparameters
                {the hyperparameter(s) used to fit the model}

family
                {the GLM family specified in this function call}

 prior          {the prior used in this function call}


  nobs          {number of observations}

kFolds          {number of folds in CV}



LICENSE:
-------
    GPL-2 | GPL-3
AUTHORS:
-------
    C code, R package (EBglmnet: https://cran.r-project.org/web/packages/EBglmnet/index.html)
    and this Python package were written by Anhui Huang (anhuihuang@gmail.com)

REFERENCES:
----------


- Cai, X., Huang, A., and Xu, S. (2011). Fast empirical Bayesian LASSO for multiple quantitative trait locus mapping. BMC Bioinformatics 12, 211.\cr\cr
- Huang A, Xu S, Cai X. (2013). Empirical Bayesian LASSO-logistic regression for multiple binary trait locus mapping. BMC genetics  14(1):5. \cr\cr
- Huang, A., Xu, S., and Cai, X. (2014a). Empirical Bayesian elastic net for multiple quantitative trait locus mapping. Heredity 10.1038/hdy.2014.79 \cr\cr
- Huang, A., E. Martin, et al. (2014b). Detecting genetic interactions in pathway-based genome-wide association studies. Genet Epidemiol 38(4): 300-309.
  \cr	}



"""

import numpy as np
import warnings
from EBelasticNet import EBelasticNet_Gaussian, EBelasticNet_Binomial
from EBlassoNEG import EBlassoNEG_Gaussian, EBlassoNEG_Binomial
from cvEBelasticNet import EBelasticNet_GaussianCV, EBelasticNet_BinomialCV
from cvEBlassoNEG import EBlassoNEG_GaussianCV,EBlassoNEG_BinomialCV
from cvEBlassoNE import EBlassoNE_GaussianCV, EBlassoNE_BinomialCV

def cv_EBglmnet(x, y, family="gaussian", prior="lassoNEG", kFolds=5,
                foldId=None, verbose=0):
    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
    if not isinstance(y, np.ndarray):
        y = np.asarray(y)

    if foldId is None:
        N = x.shape[0]
        if N % kFolds != 0:
            foldId = np.random.choice(
                np.concatenate((np.repeat(np.arange(1, kFolds + 1), N // kFolds), np.arange(1, N % kFolds + 1))), N,
                replace=False)
        else:
            foldId = np.random.choice(np.repeat(np.arange(1, kFolds + 1), N // kFolds), N, replace=False)

    # match the family, abbreviation allowed
    fambase = ['gaussian', 'binomial'];
    # find index of family in fambase
    indxtf = [x.startswith(family.lower()) for x in fambase]  # find index of family in fambase
    famind = [i for i in range(len(indxtf)) if indxtf[i] == True]
    if len(famind) == 0:
        raise ValueError(
            'Family should be one of ''gaussian'', ''binomial'' ')
    elif len(famind) > 1:
        raise ValueError('Family could not be uniquely determined : Use a longer description of the family string.')
    else:
        family = fambase[famind[0]]

    # match the prior, abbreviation not allowed
    priorBase = ['elastic net', 'lasso', 'lassoneg']
    prior = prior.lower()
    if prior not in priorBase:
        raise ValueError(
            'Prior should be one of ''elastic net'', ''lasso'',  and ''lassoNEG'', no abbreviation to avoid confusion ')

    this_call = locals()


    # Check parameters
    y = np.squeeze(y)
    np_x = x.shape
    if np_x[1] <= 1:
        raise ValueError("x should be a matrix with 2 or more columns")
    nobs = np_x[0]
    dim_y = y.shape
    nrow_y = dim_y[0] if dim_y else len(y)
    if nrow_y != nobs:
        raise ValueError(f"Number of observations in y ({nrow_y}) not equal to the number of rows of x ({nobs})")

    if family == "binomial":
        y = np.array(y)
        ntab = np.bincount(y)
        min_class = np.min(ntab)
        if min_class <= 1:
            raise ValueError("One binomial class has 1 or 0 observations; not allowed")
        if min_class < 8:
            print("One binomial class has fewer than 8 observations; dangerous ground")

        nc = len(ntab)
        y0 = np.eye(nc)[y]
        y = y0[:, 1]

    if prior == "elastic net":
        cv = {
            "gaussian": EBelasticNet_GaussianCV,
            "binomial": EBelasticNet_BinomialCV
        }[family](x, y, kFolds, foldId)

        opt_para = cv["optimal"]
        alpha = opt_para[0]
        lamda = opt_para[1]

        fit = {
            "gaussian": EBelasticNet_Gaussian,
            "binomial": EBelasticNet_Binomial
        }[family](x, y, lamda, alpha, verbose)

    elif prior == "lasso":
        cv = {
            "gaussian": EBlassoNE_GaussianCV,
            "binomial": EBlassoNE_BinomialCV
        }[family](x, y, kFolds, foldId, verbose)

        alpha = 1
        lamda = cv["optimal"]

        fit = {
            "gaussian": EBelasticNet_Gaussian,
            "binomial": EBelasticNet_Binomial
        }[family](x, y, lamda, alpha, verbose)

    else:
        cv = {
            "gaussian": EBlassoNEG_GaussianCV,
            "binomial": EBlassoNEG_BinomialCV
        }[family](x, y, kFolds, foldId, verbose)

        opt_para = cv["optimal"]
        a = opt_para[0]
        b = opt_para[1]

        fit = {
            "gaussian": EBlassoNEG_Gaussian,
            "binomial": EBlassoNEG_Binomial
        }[family](x, y, a, b, verbose)

    output = {**cv, **fit}

    del this_call['x']
    del this_call['y']
    del this_call['foldId']
    output["call"] = this_call
    output["nobs"] = nobs

    return output
