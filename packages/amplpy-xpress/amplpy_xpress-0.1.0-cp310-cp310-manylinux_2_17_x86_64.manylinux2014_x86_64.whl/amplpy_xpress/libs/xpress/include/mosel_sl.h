/************************/
/*         Mosel        */
/*                      */
/* File  mosel_sl.h     */
/************************/
/* (c) Copyright Fair Isaac Corporation 2008 */

#define MM_MPNAM_COL	0
#define MM_MPNAM_ROW	1
#define MM_MPNAM_SOS	2

#define MM_MAT_FORCE	1
#define MM_MAT_HUGE	2
#define MM_MAT_CHOBJ	4

#define MM_FREE_LOBND	(-DBL_MAX/10)

/*
   The structure Matrix is used by Mosel to send the problem to a module
   [x]   : the array contains 'x' values
   (NULL): the pointer may be NULL if the feature is not used
*/
struct Matrix
	{
	 int ncol;		/* Number of columns */
	 int nrow;		/* Number of rows */
	 int nzr;		/* Number of non-zero elements in the matrix */
	 double fixobj;		/* Fix part of the objective */
	 double *obj;		/* Objective coeffs [ncol] */
	 char *qrtype;		/* Row types [nrow] */
	 			/* Values from mipsolver.ctypecode[1-4] */
	 double *rhs;		/* RHS values [nrow] */
	 double *range;		/* Range values [nrow] (NULL) */
	 int *mstart;		/* Start index for each column [ncol+1] */
	 int *mnel;		/* Number of elts per column [ncol] */
	 int *mrwind;		/* Row reference [nzr] */
	 double *dmatval;	/* Coeff [nzr] */
	 double *dlb;		/* Lower bounds [ncol] */
	 double *dub;		/* Upper bounds [ncol] */

	 int ngents;		/* Number of int/PI/SI/bin/SC entities (glb) */
	 char *qgtype;		/* Type for each glb [ngents] (NULL) */
	 			/* Values from mipsolver.vtypecode[1-5] */
	 int *mgcols;		/* Column of each glb [ngents] (NULL) */
	 double *mplim;		/* Real bound for PI/SI/SC [ngents] (NULL) */

	 int nsos;		/* Number of SOS */
	 int nzrsos;		/* Number of non-zero elements for SOS */
	 char *qstype;		/* Type of each SOS [nsos] (NULL) */
	 			/* Values from mipsolver.ctypecode[5,6] */
	 int *msstart;		/* Start point for each SOS [nsos+1] (NULL) */
	 int *mscols;		/* Columns (=> SOS) [nzrsos] (NULL) */
	 double *dref;		/* Weights (=> SOS) [nzrsos] (NULL) */

	/* Following entries defined if MAT_HUGE is in use (nzr=nzrsos=-1) */
	 size_t nzr_l;		/* Number of non-zero elements in the matrix */
	 size_t *mstart_l;	/* Start index for each column [ncol+1] */
	 size_t nzrsos_l;	/* Number of non-zero elements for SOS */
	 size_t *msstart_l;	/* Start point for each SOS [nsos+1] (NULL) */
	};

struct Vimactx;

/*
   A module requiring a matrix has to provide the following structure
   and implement the functions loadmatrix, delmatrix and getsol_var.
   The last function is optional.
*/
struct Mipsolver
	{
	 char ctypecode[7];	/* uncons, >=,<=,=,R,sos1,sos2 */
	 char vtypecode[6];	/* cont,int,bin,pint,semcont,semint */
	 int (*loadmatrix)(struct Vimactx *,void *,struct Matrix *);
	 void (*delmatrix)(struct Vimactx *,void *);
	 double (*getsol_var)(struct Vimactx *,void *,int,int);
	 double (*getsol_ctr)(struct Vimactx *,void *,int,int);  /* (NULL) */
	};
