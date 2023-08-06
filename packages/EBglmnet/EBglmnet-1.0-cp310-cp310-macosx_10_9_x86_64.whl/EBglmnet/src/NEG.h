#ifndef NEG_H
#define NEG_H

#include "Binary.h"
#include "Linear.h"

void fEBDeltaML_NEG(double *DeltaML, int *Action, double *AlphaRoot, int *anyToDelete,
                     int *Used, int * Unused, double * S_out, double * Q_out, double *Alpha,
                     double *a_gamma, double *b_gamma, int m, int mBar);


//linear
void LinearFastEmpBayes_NEG(int *Used, double *Mu, double *SIGMA, double *H, double *Alpha, double *PHI,
                            double *BASIS, double * Targets, double *Scales, double *a_gamma, double *b_gamma,
                            int *iteration, int *n, int *kdim, int *m,int basisMax,double *b,double *beta,double * C_inv,int verbose);

void fEBLinearMainEff(double *BASIS, double *y, double *a_gamma, double *b_gamma,double *Beta,
				double *wald, double *intercept, int *n, int *kdim,int *VB,double *residual);

//binary
void fEBBinary_NEG(int *Used, double *Mu2, double *SIGMA2, double *H2, double *Alpha, double *PHI2,
                       double *BASIS, double * Targets, double *Scales, double *a_gamma, double *b_gamma,
                       int *iteration, int *n, int *kdim, int *m,double * LOGlikelihood,int basisMax,int verbose);


void fEBBinaryMainEff(double *BASIS, double * Targets, double *a_gamma, double * b_gamma,
				double * logLIKELIHOOD, double * Beta, double *wald,double *intercept, int *n, int *kdim,int *VB);
#endif
