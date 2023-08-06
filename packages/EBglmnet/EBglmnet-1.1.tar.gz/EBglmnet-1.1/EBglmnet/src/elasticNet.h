#ifndef ELASTICNET_H
#define ELASTICNET_H

#include "Binary.h"
#include "Linear.h"

void fEBDeltaML_EN(double *DeltaML, int *Action, double *AlphaRoot, int *anyToDelete,
                   int *Used, int * Unused, double * S_out, double * Q_out, double *Alpha,
                   double *a_lmabda,double *b_Alpha, int m, int mBar);


// linear
void elasticNetLinear(double *BASIS, double *y, double *a_lambda, double *b_Alpha,
				double *Beta,
				double *wald, double *intercept, int *n, int *kdim, int *verb,double *residual);

void LinearFastEmpBayes_EN(int *Used, double *Mu, double *SIGMA, double *H, double *Alpha, double *PHI,
				double *BASIS, double * Targets, double *Scales, double *a_lambda, double *b_Alpha,
				int *iteration, int *n, int *kdim, int *m,int basisMax,double *b,double *beta,double * C_inv,
				int verbose);

//binary
void fEBBinary_EN(int *Used, double *Mu2, double *SIGMA2, double *H2, double *Alpha, double *PHI2,
				double *BASIS, double * Targets, double *Scales, double *a_lambda, double *b_Alpha,
				int *iteration,
				int *n, int *kdim, int *m,double * LOGlikelihood,int basisMax);

void ElasticNetBinary(double *BASIS, double * Targets, double *a_Lambda,double *b_Alpha,
				double * logLIKELIHOOD, double * Beta, double *wald,double *intercept, int *n, int *kdim);

#endif
