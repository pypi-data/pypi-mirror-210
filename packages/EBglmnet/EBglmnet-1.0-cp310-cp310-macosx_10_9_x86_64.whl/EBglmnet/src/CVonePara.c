
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "mkl.h"

#include "Linear.h"
#include "Binary.h"
#include "elasticNet.h"
#include "NEG.h"

// no explicit blas.h included; implicitly included in lapack.h

double stdTargets(double* Targets,int N)
{
	int i;
	double meanT			= 0;
	double stdT				= 0;
	double varT;
	for(i=0;i<N;i++) meanT	= meanT + Targets[i];
	meanT					= meanT/N;
	for(i=0;i<N;i++) stdT	= stdT + pow((Targets[i] - meanT),2);
	varT					= stdT/(N-1);
	stdT					= sqrt(varT);
	return stdT;
}

//version Note: block coordinate ascent: after each block updated: update IBinv before next iteration

//transpose a matrix;
void transposeB(double *B, int M, int N) //MxN input
{
	int MN = M*N;
	double *tB,*readPtr1,*readPtr2;
	tB 	= (double* ) calloc(MN,sizeof(double)); 
	
	int i,inci,incj;
	inci = 1;
	incj = N;
	for(i=0;i<N;i++)
	{
		readPtr1 = &tB[i];
		readPtr2 = &B[i*M];
		dcopy(&M,readPtr2,&inci,readPtr1,&incj);
	}
	
	dcopy(&MN,tB,&inci,B,&inci);
	free(tB);
}

//input X, y, 
//		grid: the grid point for prior 1: after grid 1, early stop to grid 2; so on so forth
//prior 1: lassoNEG
//prior 2: lasso
//prior 3: elastic net
//internal function for cvFunc: compute nFold cv for one hyperparameter
//return negative logL c(mean(ml), sd(ml);
// the creating Xtrain, Xtest have to be repeated to allow early stop;
//API
void cvOnePara(double *BASIS, double *y, int *foldId, int *nfolds, 
				int *n, int *k,int *VB,
				double *hyperpara,double *nLogL,
				int *epistasis, int *pr, int *glm,
				int *group)
{
	//initialize 
	int N = *n;
	int p = *k;
	int verbose = *VB;
	int prior = *pr;
	int epis = *epistasis;
	int Kcv = *nfolds;
	int GLM = *glm;
	//transpose BASIS to avoid memory allocation repeation
	int MN = N*p;
	double *X 	= (double* ) calloc(MN,sizeof(double)); 
	double *readPtr1,*readPtr2;
	int i,j,jj,kk,cv,inci,incj;
	int loc1, loc2;
	inci = 1;
	incj = 1;
	dcopy(&MN,BASIS,&inci,X,&incj);
	transposeB(X,N,p);
	double *Xtrain = (double* ) calloc(MN,sizeof(double));  
	double *Xtest  = (double* ) calloc(MN,sizeof(double)); 
	double *Ytrain = (double* ) calloc(N,sizeof(double)); 
	double *Ytest = (double* ) calloc(N,sizeof(double)); 
	double *SSE = (double* ) calloc(N,sizeof(double)); 
	//for each fold of cv, read Xtrain, Xtest from X; 
	//						transpose Xtrain, Xtest to function.
	
	int indTr, indTe, nTr, nTe;
	double *Beta;
	double a_gamma, b_gamma;
	double wald,intercept,Mu0,residual,logLIKELIHOOD;
	double *Intercept = (double* ) calloc(2,sizeof(double)); 
	int nEff  = p;
	if(epis ==1) nEff = p*(p+1)/2;
	Beta = (double* ) calloc(nEff*5,sizeof(double)); 
	jj = 0;
	double temp, meanSE;
	meanSE = 0;
	for(cv=1;cv<=Kcv;cv++)
	{
		//step 1: get X, Y ready		
		indTr = 0;
		indTe = 0;
		for(i =0;i<N;i++)
		{
			if(foldId[i] ==cv)//copy to Xtest
			{
				readPtr1 = &X[i*p];
				readPtr2 = &Xtest[indTe*p];
				dcopy(&p,readPtr1,&inci,readPtr2,&incj);
				Ytest[indTe] = y[i];				
				indTe++;

			}else//copy to Xtrain;
			{
				readPtr1 = &X[i*p];
				readPtr2 = &Xtrain[indTr*p];
				dcopy(&p,readPtr1,&inci,readPtr2,&incj);
				Ytrain[indTr] = y[i];				
				indTr++;				
			}//endif

		}//end for
		nTr = indTr;
		nTe = indTe;
		transposeB(Xtrain,p,nTr);
		transposeB(Xtest,p,nTe);	
		
		//step2: call the function;
		a_gamma = hyperpara[0];
		b_gamma = hyperpara[1];	
			
		if(prior ==1)//lassoNEG
		{
	
			if(epis == 0)
			{
				if(GLM==0)//0: linear; 1: logistic
				{
fEBLinearMainEff(Xtrain,Ytrain, &a_gamma, &b_gamma,Beta, 
				&wald, &intercept, &nTr, &p,&verbose,&residual);
				
				}else
				{
fEBBinaryMainEff(Xtrain,Ytrain, &a_gamma, &b_gamma,
				&logLIKELIHOOD, Beta, &wald, Intercept, &nTr, &p,&verbose);
					
				}
			}

		}else//lassoNE, EBEN
		{
			if(epis == 0)
			{
				if(GLM==0)
				{
elasticNetLinear(Xtrain, Ytrain, &b_gamma, &a_gamma,
				Beta, &wald, &intercept, &nTr, &p, &verbose,&residual);
					
				}else
				{
ElasticNetBinary(Xtrain,Ytrain, &b_gamma, &a_gamma,
				&logLIKELIHOOD, Beta, &wald, Intercept, &nTr, &p);
					
				}				
			}
		}// end of prior
		
		//step3: compute prediction in Ytest;
		int M = 0;
		for(i=0;i<nEff;i++)
		{
			if(Beta[nEff*2+i]!=0) M++;
		}
		double *PHI = (double* ) calloc(nTe*M,sizeof(double));
		double *beta = (double* ) calloc(M,sizeof(double));
		double *PHI_Mu = (double* ) calloc(nTe,sizeof(double));
		kk = 0;
		for(i=0;i<nEff;i++)
		{
			loc1 = (int)Beta[i] -1;
			loc2 = (int)Beta[nEff+i] -1;
			if(Beta[nEff*2+i]!=0)
			{
				beta[kk] = Beta[nEff*2+i];
				if(loc1 == loc2)
				{
					//copy loc1
					readPtr1 = &PHI[kk*nTe];
					readPtr2 = &Xtest[loc1*nTe];
					dcopy(&nTe,readPtr2,&inci,readPtr1,&incj);
				}else
				{
					for(j=0;j<nTe;j++) PHI[kk*nTe + j] = Xtest[loc1*nTe+j]*Xtest[loc2*nTe+j];
				}
				kk++;
			}
		}//end for
		for(i = 0;i<nTe;i++)
		{
			PHI_Mu[i]			= 0;
			for(j = 0;j<M;j++)	PHI_Mu[i]	= PHI_Mu[i] + PHI[j*nTe+i]*beta[j];
		}
	
	// 1) prediction error -->gaussian;
	// 2) likelihood; --> logistic;
		if(GLM==0) //MSE
		{
			for(i = 0;i<nTe;i++)
			{
				temp = Ytest[i] - intercept -PHI_Mu[i];
				SSE[jj] = temp*temp;
				meanSE = meanSE + SSE[jj];
				jj++;
			}
		}else//-logL
		{
			Mu0 = Intercept[0];
			for(i = 0;i<nTe;i++)
			{
				SSE[jj] = Ytest[i]*log(exp(Mu0+PHI_Mu[i])/(1+exp(Mu0+PHI_Mu[i]))) + 
						(1-Ytest[i])*log(1/(1+exp(Mu0+PHI_Mu[i])));
				SSE[jj] = -SSE[jj];
				meanSE = meanSE + SSE[jj];
				jj++;
			}
		}	
	free(PHI);
	free(beta);
	free(PHI_Mu);
	
	}//end of for CV
	//mean sde for this hyperparameter;
	nLogL[0] = a_gamma;
	nLogL[1] = b_gamma;
	nLogL[2] = meanSE/N;
	nLogL[3] = stdTargets(SSE,N)/sqrt(Kcv);
	free(X);
	free(Xtrain);
	free(Xtest);
	free(Ytrain);
	free(Ytest);
	free(SSE);
	free(Intercept);
	free(Beta);
}
			

double norm(double*X,int N)
{
	int inci = 1;
	int incj = 1;
	double *readPtr1, *readPtr2,temp;
	readPtr1 = &X[0];
	readPtr2 = &X[0];
	temp = ddot(&N,readPtr1,&inci,readPtr2,&incj);	//res = ddot(n, x, incx, y, incy)
	temp = sqrt(temp);
	return temp;
}

//Projection function
void ProjectCorr(int *n, int *p,double*y0,double*BASIS,
		double*lambdaMax, int *epistasis)
{
	int N 				= n[0];
	int K 				= p[0];	
	int epis 			= *epistasis;
	double *y			= (double * ) calloc(N,sizeof(double));
	double *z 			= (double * ) calloc(N,sizeof(double));

	int i,j,l;	
	double normY, normX;
	normY = norm(y0,N);
	for(i=0;i<N;i++) y[i]	= y0[i]/normY;
	//compute abscor vector
	double *readPtr1,*readPtr2, corXY;
	int inci 				= 1;
	int incj 				= 1;
	lambdaMax[0] 			= 0;
	for(i =0;i<K;i++)
	{
		//1. center x;
		readPtr1 			= &BASIS[i*N];
		normX = norm(readPtr1,N);
		for(l=0;l<N;l++) z[l] = readPtr1[l]/normX;
		//2. compute corr;
		corXY = ddot(&N,z,&inci,y,&incj);
		if(corXY>lambdaMax[0]) lambdaMax[0] = corXY;
		
		//interactions
		if(epis!=0 && i<(K-1))
		{
			for(j=(i+1);j<K;j++)
			{
				readPtr2 	= &BASIS[j*N];
				//1.
				for(l=0;l<N;l++) z[l] 	= readPtr1[l]*readPtr2[l];
				normX = norm(z,N);				
				for(l=0;l<N;l++) z[l] = z[l]/normX;
				//2. 
				corXY = ddot(&N,z,&inci,y,&incj);
				if(corXY>lambdaMax[0]) lambdaMax[0] = corXY;		
			}//j<K			
		}//if i<(K-1)		
	}//i
	//free memory
	free(y);
	free(z);
}
