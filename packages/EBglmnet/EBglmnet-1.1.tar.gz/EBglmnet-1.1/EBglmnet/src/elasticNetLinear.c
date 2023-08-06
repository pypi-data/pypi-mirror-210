
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "mkl.h"

#include "Linear.h"
#include "elasticNet.h"
//G: gauss; m:main; Ne: normal exp


// API:
void elasticNetLinear(double *BASIS, double *y, double *a_lambda, double *b_Alpha,
				double *Beta, 
				double *wald, double *intercept, int *n, int *kdim, int *verb,double *residual)
{
	int N					= *n;
	int K					= *kdim;
	int verbose 				= *verb;

	int M_full = K;
	const int iter_max		= 50;
	const double err_max	= 1e-8;
	// set a limit for number of basis
	
	int basisMax			= 1e7/M_full;
	if (basisMax>M_full)	basisMax = M_full;
	if(verbose>2) printf("basisMax: %d \n",basisMax);
	if(verbose >1) printf("start EB-elasticNet with alpha: %f, lambda: %f\n",*b_Alpha, *a_lambda);
	double vk				= 1e-30;
	double vk0				= 1e-30;
	double temp				= 0;
	int i;
	double *Scales			= (double * ) calloc(M_full,sizeof(double));
	//lapack
	int inci 				=1;
	int incj 				=1;
	double *readPtr1, *readPtr2;
	int inc0 				= 0;
	double a_blas 			= 1;
	double b_blas 			= 1;
	double zero_blas 		= 0;
	//lapack end
	
	for (i					=0;i<K;i++)
	{
		Beta[i]				= i + 1;
		Beta[M_full + i]	= i + 1;

		temp				= 0;

		readPtr1  			= &BASIS[i*N];
		temp  				= ddot(&N, readPtr1, &inci,readPtr1, &incj);
		if(temp ==0) temp	= 1;
		Scales[i]			=sqrt(temp);
	}
	readPtr1 				= &Beta[K*2];
	dcopy(&K,&zero_blas,&inc0,readPtr1,&inci);  //dcopy(n, x, incx, y, incy) ---> y = x
	readPtr1 				= &Beta[K*3];
	dcopy(&K,&zero_blas,&inc0,readPtr1,&inci);  //dcopy(n, x, incx, y, incy) ---> y = x
		

	//
	int iter				= 0;
	double err				= 1000;
	double *Mu, *SIGMA, *H, *Alpha, *PHI,*Targets,*C_inv;
	int * Used,*iteration, *m;
	
	Used					= (int* ) calloc(basisMax, sizeof(int));
	Mu						= (double * ) calloc(basisMax,sizeof(double));							  
	SIGMA					= (double * ) calloc(basisMax*basisMax,sizeof(double));
	H						= (double * ) calloc(basisMax*basisMax,sizeof(double));
	Alpha					= (double * ) calloc(basisMax,sizeof(double));
	PHI						= (double * ) calloc(N*basisMax,sizeof(double));
	Targets					= (double * ) calloc(N,sizeof(double));
	iteration				= (int* ) calloc(1, sizeof(int));
	m						= (int* ) calloc(1, sizeof(int));
	C_inv					= (double * ) calloc(N*N,sizeof(double));
	if(verbose>2) printf("outer loop starts\n");
	m[0]			= 1;
	int M					= m[0];	
	//Fixed Effect
	double b				= 0;
	daxpy(&N, &a_blas,y, &inci,&b, &inc0); //daxpy(n, a, x, incx, y, incy) y := a*x + y

	b						= b/N;
	double beta;
	double *Csum			= (double *) calloc(N,sizeof(double));
	double Cinv,Cinvy;
	while (iter<iter_max && err>err_max)
	{
		iter				= iter + 1;
		
		vk0					= vk;
		iteration[0]		= iter;
		b_blas = -b;
		dcopy(&N,&b_blas,&inc0,Targets,&inci);  //dcopy(n, x, incx, y, incy) ---> y = x
		daxpy(&N, &a_blas,y, &inci,Targets, &incj); //daxpy(n, a, x, incx, y, incy) y := a*x + y
		
//
		LinearFastEmpBayes_EN(Used, Mu, SIGMA, H, Alpha,PHI,	BASIS, Targets,Scales, a_lambda,b_Alpha,
						iteration, n, kdim, m,basisMax,&b,&beta,C_inv,verbose);

		 for(i=0;i<N;i++)
		 {
			 Csum[i]	= 0;
			 readPtr1 		= &Csum[i];
			 readPtr2 		= &C_inv[i*N];
			daxpy(&N, &a_blas,readPtr2, &inci,readPtr1, &inc0); //daxpy(n, a, x, incx, y, incy) y := a*x + y

		 }
		 Cinv = 0;
		daxpy(&N, &a_blas,Csum, &inci,&Cinv, &inc0); //daxpy(n, a, x, incx, y, incy) y := a*x + y
	
		 Cinvy = 0;
		 Cinvy 				= ddot(&N, Csum, &inci,y, &incj);
		 b		= Cinvy/(Cinv+ 1e-10);
		vk					= 0;
		M 					= m[0];
		daxpy(&M, &a_blas,Alpha, &inci,&vk, &inc0); //daxpy(n, a, x, incx, y, incy) y := a*x + y
	
		err					= fabs(vk - vk0)/m[0];
		if(verbose >2) printf("Iteration number: %d, err: %f;\t mu: %f.\n",iter,err,b);
	}

	// wald score
	M					= m[0];	
	double *tempW			= (double * ) calloc(M,sizeof(double));

	wald[0]					= 0;
	int index = 0;
	if(verbose >1) printf("EBLASSO Finished, number of basis: %d\n",M);
	for(i=0;i<M;i++)
    {

        tempW[i]      		= 0;
		readPtr1 			= &H[i*M];		
        tempW[i] 			= ddot(&M, Mu, &inci,readPtr1, &incj);     
	}
	wald[0] 				= ddot(&M, tempW, &inci,Mu, &incj);	
	for(i=0;i<M;i++)
	{
		index				= Used[i] - 1;
		Beta[M_full*2 + index]	= Mu[i]/Scales[index];
		Beta[M_full*3 + index]  = SIGMA[i*M + i]/(Scales[index]*Scales[index]);
	}
	//

	intercept[0]	= b;
	residual[0] 	= 1/(beta + 1e-10);

	free(Scales);
	free(Used);	
	free(Mu);
	free(SIGMA);	
	free(H);
	free(Alpha);	
	free(PHI);
	free(Targets);	
	free(iteration);	
	free(m);
	free(C_inv);	
	free(tempW);
	free(Csum);
}


/************** outputs are passed by COPY in R, cann't dynamic realloc memory **************************/
/************** Not a problem in C */
// function [Used,Mu2,SIGMA2,H2,Alpha,PHI2]=fEBBinaryMex(BASIS,Targets,PHI2,Used,Alpha,Scales,a,b,Mu2,iter)
void LinearFastEmpBayes_EN(int *Used, double *Mu, double *SIGMA, double *H, double *Alpha, double *PHI,
				double *BASIS, double * Targets, double *Scales, double *a_lambda, double *b_Alpha,
				int *iteration, int *n, int *kdim, int *m,int basisMax,double *b,double *beta,double * C_inv,
				int verbose)
{
    //basis dimension
   int N,K,M_full,N_unused,M,i,j,iter;
   	N					= *n;			// row number
    K					= *kdim;		// column number
	M_full = K;

	int *Unused				= (int *) calloc(M_full,sizeof(int));
    iter				= *iteration;
    const int	ACTION_REESTIMATE       = 0;			
	const int	ACTION_ADD          	= 1;
	const int 	ACTION_DELETE        	= -1;
    const int   ACTION_TERMINATE        = 10;    
    
	//
	const int		CNBetaUpdateStart	=10;
	const double	BetaMaxFactor		=1e6;
	const double	MinDeltaLogBeta		=1e-6;
    int *IniLogic;
	IniLogic				= (int*) calloc(1,sizeof(int));
    if (iter<=1)    
    {
        IniLogic[0]     = 0;
        m[0]            = 1;
		M				= m[0];
		N_unused		= M_full -1;

    }else
    {
		IniLogic[0]    = 1;
        M				= *m;          //Used + 1
		N_unused		= M_full - M;
    }
    //
	//lapack
	int inci 				=1;
	int incj 				=1;
	double *readPtr1;//, *readPtr2;
	int inc0 				= 0;
	double a_blas 			= 1;
	double b_blas 			= 1;
	double c_blas 			= 1;
	int MM;
	char transa 			= 'N';
	char transb 			= 'N';
	int lda,ldb,ldc,ldk;
	//lapack end

	fEBInitialization_Gauss(Alpha, PHI, Used, Unused, BASIS, Targets, Scales, IniLogic, N, m, K,beta);
	double *BASIS_Targets,**BASIS_PHI;
	BASIS_Targets		= (double *) calloc(M_full,sizeof(double));
	BASIS_PHI			= (double **) calloc(basisMax,sizeof(double));
	for(i=0;i<M;i++)
	{
		BASIS_PHI[i] 	= (double *) calloc(M_full,sizeof(double));
	}
	CacheBP(BASIS_PHI, BASIS_Targets, BASIS, PHI,	Targets,Scales,N,K,M,M_full);
	
	double *S_in, *Q_in, *S_out, *Q_out,*gamma;
	S_in				= (double *) calloc(M_full,sizeof(double));
	Q_in				= (double *) calloc(M_full,sizeof(double));
	S_out				= (double *) calloc(M_full,sizeof(double));
	Q_out				= (double *) calloc(M_full,sizeof(double));
	gamma				= (double *) calloc(basisMax,sizeof(double));

	int i_iter = 0;
	fEBLinearFullStat(beta,SIGMA, H, S_in, Q_in, S_out,Q_out,  BASIS, Scales, 
			PHI, BASIS_PHI,BASIS_Targets, Targets, Used, Alpha, Mu, 
				 gamma, n, m, kdim, iteration,&i_iter);

   double *DeltaML, *AlphaRoot,deltaLogMarginal,*phi,newAlpha,oldAlpha;
    double deltaInv,kappa,Mujj;
    //
	int *Action, *anyToDelete,selectedAction;
	anyToDelete			= (int*) calloc(1,sizeof(int));
	DeltaML				=	(double *) calloc(M_full,sizeof(double));
	AlphaRoot			=	(double *) calloc(M_full,sizeof(double));
	Action				= (int *) calloc(M_full,sizeof(int));
  	phi					= (double *) calloc(N,sizeof(double));

    int nu,jj,index;
    jj					= -1;
    int anyWorthwhileAction,UPDATE_REQUIRED;
  	//

    int LAST_ITERATION  = 0;
	//Gauss update
	double *PHI_Mu,*e;
	PHI_Mu				= (double*) calloc(N,sizeof(double));
	e					= (double*) calloc(N,sizeof(double));
	double betaZ1;
	double deltaLogBeta;
	double ee;
	double varT;
	
	
	double temp;			// for action_reestimate
	double * SIGMANEW	= (double * ) calloc(basisMax*basisMax,sizeof(double));
if(verbose>3) printf("check point 3: before loop \n");
   while(LAST_ITERATION!=1)
    {
        i_iter						= i_iter + 1;
		if(verbose >4) printf("\t inner loop %d \n",i_iter);

		fEBDeltaML_EN(DeltaML, Action, AlphaRoot,anyToDelete,Used, Unused, S_out, Q_out, Alpha,
				a_lambda, b_Alpha, M, N_unused);
		//
        deltaLogMarginal			= 0.001;
        nu							= -1;
        for(i=0;i<M_full;i++)
        {
            if(DeltaML[i]>deltaLogMarginal)
            {
                deltaLogMarginal    = DeltaML[i];
                nu                  = i;
            }
        }
		
        if(nu==-1)
		{		
			anyWorthwhileAction     = 0;
			selectedAction          = -10;
		}else
		{
			anyWorthwhileAction	= 1;
			selectedAction          = Action[nu];
			newAlpha                = AlphaRoot[nu];
		}
        if(selectedAction==ACTION_REESTIMATE || selectedAction==ACTION_DELETE)
        {
            index                   = nu + 1; 
            for(i=0;i<M;i++)
            {
                if (Used[i]==index)	
				{
						jj  = i;
						break;
				}
            }
        }

        //kk                          = K;                          
        for(i=0;i<K;i++)
        {
            if (i==nu)
            {
				readPtr1 		= &BASIS[i*N];
				dcopy(&N,readPtr1,&inci,phi,&incj);  //dcopy(n, x, incx, y, incy) ---> y = x
				b_blas 			= 1/Scales[i];
				dscal(&N,&b_blas,phi,&inci); 		//dscal(n, a, x, incx) x = a*x
				//break;
            }
			
        }

        if(anyWorthwhileAction==0)  selectedAction = ACTION_TERMINATE;
        if(selectedAction==ACTION_REESTIMATE)
        {
            if (fabs(log(newAlpha)-log(Alpha[jj]))<=1e-3 && anyToDelete[0] ==0)
            {	
                selectedAction		= ACTION_TERMINATE;
            }
        }
        //
        UPDATE_REQUIRED				= 0;
        if(selectedAction==ACTION_REESTIMATE)
        {
			if(verbose>4) printf("\t\t Action: Reestimate : %d \t deltaML: %f\n",nu + 1, deltaLogMarginal);
            oldAlpha				= Alpha[jj];
            Alpha[jj]				= newAlpha;

            deltaInv				= 1.0/(newAlpha-oldAlpha);
            kappa					= 1.0/(SIGMA[jj*M+jj] + deltaInv);
            Mujj					= Mu[jj];
			readPtr1 				= &SIGMA[jj*M];
			b_blas 					= -Mujj * kappa;
			daxpy(&M, &b_blas,readPtr1, &inci,Mu, &incj); //daxpy(n, a, x, incx, y, incy) y := a*x + y

			for(i=0;i<M;i++)
			{
				for(j=0;j<M;j++)	SIGMANEW[j*M + i] = SIGMA[j*M + i] - kappa * SIGMA[jj*M+i]*SIGMA[jj*M+j];
			}
			
			for(i=0;i<M_full;i++)
			{
				temp	= 0;
				for(j=0;j<M;j++) temp = temp + BASIS_PHI[j][i]*SIGMA[jj*M + j];
				S_in[i]				= S_in[i] +  pow(beta[0]*temp,2)*kappa;
				Q_in[i]				= Q_in[i] +  beta[0]*Mujj *kappa*temp;
			}

			UPDATE_REQUIRED			= 1;
        }
        /////////////////////////////////////////////////////////////////////////////////
        else if(selectedAction==ACTION_ADD)
        {
			if(verbose>4) printf("\t\t Action:add : %d \t deltaML: %f\n",nu + 1,deltaLogMarginal);

            index					= M + 1;
			if(index > (basisMax -10) && iter>1 && (N*K) > 1e7 && verbose > 0) {
				printf("bases: %d, warning: out of Memory!\n",index);
			}//return;
			if(index > (basisMax -1) && iter>1 && (N*K) > 1e7 && verbose > 0) {
				printf("bases: %d, out of Memory,exiting program!\n",index);
			}
			UPDATE_REQUIRED		= ActionAdd(BASIS_PHI, BASIS, Scales, PHI, phi, beta, Alpha,
				newAlpha, SIGMA, Mu, S_in, Q_in, nu, SIGMANEW, M_full, N, K, M);

            //			
            Used[M]			= nu + 1;						//new element

            //

			N_unused				= N_unused - 1;
			for(i=0;i<N_unused;i++)
            {                
                if(Unused[i]== (nu + 1))		Unused[i] =Unused[N_unused];
            }
			m[0]					= M + 1;
			M						= m[0];

        }
		//
        else if(selectedAction==ACTION_DELETE)
        {
			if(verbose>4) printf("\t\t Action: delete : %d deltaML: %f \n",nu + 1,deltaLogMarginal);
            UPDATE_REQUIRED = ActionDel(PHI, Alpha, SIGMA, SIGMANEW, BASIS_PHI,
				Mu, S_in, Q_in, beta, jj, N, M, M_full);
			index					= M -1;
			free(BASIS_PHI[index]);
            //Used; Unused;
            Used[jj]				= Used[index];

            //
			N_unused				= N_unused + 1;
			Unused[N_unused -1]		= nu + 1;

			m[0]					= M -1;
			M						= m[0];
		}

		if(UPDATE_REQUIRED==1)
        {
			dcopy(&M_full,S_in,&inci,S_out,&incj);  //dcopy(n, x, incx, y, incy) ---> y = x
			dcopy(&M_full,Q_in,&inci,Q_out,&incj); 
			for(i=0;i<M;i++)
		    {
				index					= Used[i] -1;
				S_out[index]			= Alpha[i]*S_in[index]/(Alpha[i]-S_in[index]);
				Q_out[index]			= Alpha[i]*Q_in[index]/(Alpha[i]-S_in[index]);
			}

			MM = M*M;			
			dcopy(&MM,SIGMANEW,&inci,SIGMA,&incj);  //dcopy(n, x, incx, y, incy) ---> y = x

			
			for(i=0;i<M;i++) gamma[i]		= 1- Alpha[i]*SIGMA[i*M+i];
        }

		if ((selectedAction==ACTION_TERMINATE)||(i_iter<=CNBetaUpdateStart)||(i_iter%5==0))
		{	
			ee					= 0;

			lda 				= N;
			b_blas 				= 0;
			dgemv(&transa, &N, &M,&a_blas, PHI, &lda, Mu, &inci, &b_blas,PHI_Mu, &incj); 
			dcopy(&N,Targets,&inci,e,&incj);  //dcopy(n, x, incx, y, incy) ---> y = x
			b_blas 				= -1;
			daxpy(&N, &b_blas,PHI_Mu, &inci,e, &incj);//daxpy(n, a, x, incx, y, incy) y := a*x + y
	
			 ee = ddot(&N, e, &inci,e, &incj);
			 betaZ1				= beta[0];
			 temp				= 0;
			daxpy(&M, &a_blas,gamma, &inci,&temp, &inc0);//daxpy(n, a, x, incx, y, incy) y := a*x + y
			
			 beta[0]			= (N-temp)/ee;
			 varT				= varTargets(Targets,N);
			 if(beta[0]>(BetaMaxFactor/varT))	beta[0] = BetaMaxFactor/varT;
			 deltaLogBeta			= log(beta[0]) - log(betaZ1);
			 //
			 if (fabs(deltaLogBeta)>MinDeltaLogBeta)
			 {
				FinalUpdate(PHI,H,SIGMA,Targets,Mu,Alpha,beta,N, M);
				if (selectedAction!=ACTION_TERMINATE)
				{
					fEBLinearFullStat(beta,SIGMA,H, S_in, Q_in, S_out,Q_out,  BASIS, Scales, 
							PHI, BASIS_PHI, BASIS_Targets, Targets, Used, Alpha, Mu, 
							gamma, n, m, kdim, iteration,&i_iter);
				}
			 }
        }

        if(selectedAction==ACTION_TERMINATE) LAST_ITERATION =1;
        if(i_iter==1000)   LAST_ITERATION = 1;
    }
	
	double*PHIsig	= (double *) calloc(N*M,sizeof(double)); // PHI *SIGMA
	transb = 'N';
	lda = N;
	ldb = M;
	ldc = N;
	ldk = M; //b copy
	b_blas = 1;
	c_blas = 0;
	dgemm(&transa, &transb,&N, &M, &ldk,&b_blas, PHI, &lda, SIGMA, &ldb, &c_blas, PHIsig, &ldc);

	transb = 'T';
	ldk = N;
	lda = N;
	ldb = N;
	ldc = N;
	b_blas = -beta[0]*beta[0];
	c_blas = 0;
	dgemm(&transa, &transb,&N, &ldk, &M,&b_blas, PHIsig, &lda, PHI, &ldb, &c_blas, C_inv, &ldc );

	 for(i=0;i<N;i++) C_inv[i*N+i]	=C_inv[i*N+i]	+ beta[0];
	free(Unused);	
	free(IniLogic);
	free(BASIS_Targets);
//free(BASIS_PHI);	
	for(i=0;i<M;i++)
	{
		free(BASIS_PHI[i]);
	}	
	free(BASIS_PHI);	
	free(S_in);
	free(Q_in);
	free(S_out);	
	free(Q_out);
	free(anyToDelete);	
	free(DeltaML);	
	free(AlphaRoot);
	free(Action);	
	free(phi);	
	free(PHI_Mu);
	free(e);
	free(SIGMANEW);
	free(PHIsig);
	free(gamma);
}

/****************************************************************************/


