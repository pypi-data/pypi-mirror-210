"""

--------------------------------------------------------------------------
EmpBayesGlmnet.py:
    EmpBayesGlmnet is the main function to fit a generalized linear model via the empirical Bayesian methods
    with lasso and elastic net hierarchical priors.
	It features with `p>>n` capability, produces a sparse outcome for the
	regression coefficients, and performs significance test for nonzero effects
	in both  linear and logistic regression models.
			}
--------------------------------------------------------------------------

FUNCTION INTERFACE:
-----------
    import EBglmnet
    fit = EmpBayesGlmnet(X, Y, family = 'gaussian', prior = 'lassoNEG', hyperparameters, verbose = 1);


INPUT ARGUMENTS:
---------------
    X           The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.

    Y           The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.

    family      Model type taking values of "gaussian" (default) or "binomial".

    prior       Prior distribution to be used. It takes values of "lassoNEG"(default), "lasso", and "elastic net".
                All priors will produce a sparse outcome of the regression coefficients; see Details for choosing priors.

    hyperparameters
                the optimal hyperparameters in the prior distribution. Similar as \eqn{\lambda} in lasso
                method, the hyperparameters control the number of nonzero elements in the regression coefficients. Hyperparameters
                are most oftenly determined by CV. See `cv.EBglmnet` for the method in determining their values.
                While cv.EBglmnet already provides the model fitting results using the hyperparameters determined in CV,
                users can use this function to obtain the results under other parameter selection criteria such as Akaike information criterion
                (AIC) or Bayesian information criterion (BIC).

    verbose     parameter that controls the level of message output from EBglment. It takes values from 0 to 5; larger
                verbose displays more messages. small values are recommended to avoid excessive outputs. Default value
                for `verbose` is minimum message output.


OUTPUT ARGUMENTS:
---------------
    Function output is a dictionary with the following keys:
    fit         the model fit using the hyperparameters provided. EBglmnet selects the variables having nonzero regression
	            coefficients and estimates their posterior distributions. With the posterior mean and variance, a \code{t-test}
	            is performed and the \code{p-value} is calculated. Result in fit is a matrix with rows corresponding to the
	            variables having nonzero effects, and columns having the following values: \cr\cr
	            column1: (predictor index in X) denoting the column number in the input matrix \code{x}. \cr\cr
                column2: beta. It is the posterior mean of the nonzero regression coefficients. \cr\cr
                column3: posterior variance.  It is the diagonal element of the posterior covariance matrix among the nonzero regression coefficients. \cr\cr
                column4: t-value calculated using column 3-4. \cr\cr
                column5: p-value from t-test.

	\item{WaldScore}{
                the Wald Score for the posterior distribution. It is computed as \eqn{\beta^T\Sigma^{-1}\beta}.
                See (Huang A, 2014b) for using Wald Score to identify significant effect set.
        }
	\item{Intercept}{
	            the intercept in the linear regression model. This parameter is not shrunk.
	            }
	\item{residual variance}{
	            the residual variance if the Gaussian family is assumed in the GLM
	            }
	\item{logLikelihood}{
	            the log Likelihood if the Binomial family is assumed in the GLM
	            }
	\item{hyperparameters}{
	            the hyperparameter used to fit the model
	            }
	\item{family}{
	            the GLM family specified in this function call
	            }
	\item{prior}{
	            the prior used in this function call
	            }
	\item{call}{
	            the call that produced this object
	            }
	\item{nobs}{
	            number of observations
	            }




Hyperparameters:
--------
    Cross - Validation:
                hyperparameters are recommended to be selected by cross validation
                (CV) using function `cv.EBglmnet`

    Stability Selection
                Stability Selection (Meinshausen and Buhlmann 2010) can be an alternative approach to the cross
                validation.

    Random Seed
                User is responsible to set the random seed before calling this function.

LICENSE:
-------
    GPL-2 | GPL-3
AUTHORS:
-------
    C code, R package (EBglmnet: https://cran.r-project.org/web/packages/EBglmnet/index.html)
    and this Python package were written by Anhui Huang (anhuihuang@gmail.com)

REFERENCES:
----------
            Cai, X., Huang, A., and Xu, S. (2011). Fast empirical Bayesian LASSO for multiple quantitative trait locus mapping. BMC Bioinformatics 12, 211.\cr\cr
	        Huang A, Xu S, Cai X. (2013). Empirical Bayesian LASSO-logistic regression for multiple binary trait locus mapping. BMC genetics  14(1):5. \cr\cr
	        Huang, A., Xu, S., and Cai, X. (2014a). Empirical Bayesian elastic net for multiple quantitative trait locus mapping. Heredity 10.1038/hdy.2014.79 \cr
            Meinshausen, N. and P. Buhlmann, 2010 Stability selection. J. R. Stat. Soc. Series B. Stat. Methodol. 72: 417-473.

"""

import numpy as np
import warnings
from EBelasticNet import EBelasticNet_Gaussian, EBelasticNet_Binomial
from EBlassoNEG import EBlassoNEG_Gaussian, EBlassoNEG_Binomial

def EmpBayesGlmnet(x, y, family="gaussian", prior = "lassoNEG", hyperparameters = None,  verbose = 0):
    """

    :param x: The input matrix of dimension `n x p`; each row is an
                observation vector, and each column is a variable.
    :param y: The response variable. Continuous for `family="gaussian"`, and binary for
                `family="binomial"`. For binary response variable, y can be a Boolean or numeric vector, or factor type
                array.
    :param family: Model type taking values of "gaussian" (default) or "binomial".
    :param prior: Prior distribution to be used. It takes values of "lassoNEG"(default), "lasso", and "elastic net".
                All priors will produce a sparse outcome of the regression coefficients; see Details for choosing priors.
    :param hyperparameters: the hyperparameters in the prior distribution.
    :param verbose: parameter that controls the level of message output from EBglment.
    :return: the model fit using the hyperparameters provided.

    See the function script file EmpBayesGelmnet.py for more details.
    """
    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
    if not isinstance(y, np.ndarray):
        y = np.asarray(y)
    if hyperparameters is None:
        warnings.warn(
            "hyperparameters controlling the number of nonzero effects need to be specified; run cv.EBglmnet to determine the parameters")
        hyperparameters = np.array([0.5, 0.5])

    this_call = locals()  # Get the local variables as a dictionary

    if family not in ("gaussian", "binomial"):
        raise ValueError("Invalid family value. Allowed values are 'gaussian' and 'binomial'.")
    if prior not in ("lassoNEG","lasso","elastic net"):
        raise ValueError(f"Invalid prior value. Allowed values are 'lassoNEG', 'lasso', and 'elastic net'.")
    y = np.squeeze(y)  # Convert y to a 1D array

    np_dim = x.shape
    if np_dim[1] <= 1:
        raise ValueError("x should be a matrix with 2 or more columns")
    nobs = np_dim[0]

    dim_y = y.shape
    nrowy = dim_y[0] if len(dim_y) > 1 else len(y)
    if nrowy != nobs:
        raise ValueError(f"number of observations in y ({nrowy}) not equal to the number of rows of x ({nobs})")

    if family == "binomial":
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

        nc = len(ntab)
        y0 = np.eye(nc)[y.astype(int) - 1]
        y = y0[:, 1]

    if prior == "elastic net":
        alpha = hyperparameters[0]
        lamda = hyperparameters[1]

        if alpha > 1 or alpha < 0:
            warnings.warn("Empirical Bayes Elastic Net: alpha not in the range of [0,1]; set to 1")
            alpha = 1

        if lamda < 0:
            warnings.warn("Empirical Bayes Elastic Net: lambda should be a positive number; set lambda = 0.1")
            lamda = 0.1

        if family == "gaussian":
            fit = EBelasticNet_Gaussian(x, y, lamda, alpha, verbose)
        elif family == "binomial":
            fit = EBelasticNet_Binomial(x, y, lamda, alpha, verbose)

    elif prior == "lasso":
        alpha = 1
        lamda = hyperparameters[0]

        if lamda < 0:
            warnings.warn("Empirical Bayes Elastic Net: lambda should be a positive number; set lambda = 0.1")
            lamda = 0.1

        if family == "gaussian":
            fit = EBelasticNet_Gaussian(x, y, lamda, alpha, verbose)
        elif family == "binomial":
            fit = EBelasticNet_Binomial(x, y, lamda, alpha, verbose)

    else:
        a = hyperparameters[0]
        b = hyperparameters[1]

        if a <= -1.5:
            warnings.warn("EBlassoNEG has support of a > 1.5 and b > 0, set  a = 0.1 " )
            a = 0.1

        if b <= 0:
            warnings.warn("EBlassoNEG has support of a > 1.5 and b > 0, set b = 0.1")
            b = 0.1

        if family == "gaussian":
            fit = EBlassoNEG_Gaussian(x, y, a, b, verbose)
        elif family == "binomial":
            fit = EBlassoNEG_Binomial(x, y, a, b, verbose)

        del this_call['hyperparameters']
        del this_call['x']
        del this_call['y']
        fit["call"] = this_call
        fit["n-obs"] = nobs
        fit["n-vars"] = np_dim[1]
        return fit





