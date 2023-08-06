/************************/
/*         Mosel        */
/*                      */
/* File  mmnl.h         */
/************************/
/* (c) Copyright Fair Isaac Corporation 2007-2018. All rights reserved */

#ifndef _MMNL_H
#define _MMNL_H

#define NL_FREE_LOBND (-DBL_MAX/10)

#define NLOPT_VERBOSE	1
#define NLOPT_SPRSOBJ	2	/* Sparse objective */
#define NLOPT_FULLJAC	4	/* Allocate full Jacobian (or: linear only) */
#define NLOPT_COLWJAC	8	/* Jacobian coded columnwise */
#define NLOPT_UPTRHES	16	/* Need Hessian Upper Triangle */
#define NLOPT_LOTRHES	32	/* Need Hessian Lower Triangle */
#define NLOPT_FULLHES	(NLOPT_UPTRHES|NLOPT_LOTRHES)	/* Full Hessian */
#define NLOPT_SPHES	64	/* Hessian provided in sparse form */
#define NLOPT_CTRBNDS	128	/* Constraint types as bounds */
#define NLOPT_RAWBNDS	256	/* Do not default lower bounds to 0 */
#define NLOPT_QUADLIN	512	/* Need accurate JAC for QP expressions */
#define NLOPT_NAMES	1024	/* Generate names for nlctrs */
#define NLOPT_NOAD	2048	/* AD routines are not required */
#define NLOPT_HAVENLVS	4096	/* NLVS provided (in place of extravars) */

/* Warnings:
  option NLOPT_COLWJAC disables evaluation of linear constraints
  option NLOPT_QUADLIN disables NLOPT_*HESS if no NL ctr/obj
*/

		/* Possible values for 'strip' */
#define NLSTRIP_VBNDS	1	/* variables data */
#define	NLSTRIP_CBNDS	2	/* constraints bounds */
#define	NLSTRIP_CJAC	4	/* Jacobian colomnwise */
#define	NLSTRIP_HESS	8	/* Hessian data */
#define	NLSTRIP_MAT	16	/* matrix data */
#define	NLSTRIP_WKA	32	/* working arrays */
#define	NLSTRIP_NAMES	64	/* names */
#define	NLSTRIP_ALL	0xFF

#define NLEVAL_OBJ	-1
#define NLEVAL_ALL	-2
#define NLEVAL_NL	-3
#define NLEVAL_LIN	-4

struct NlCtx;
struct NlCtr;
union NlExpr;
struct NLVS;

typedef struct
	{
	 int code;
	 void *(*duptok)(mm_context ctx,void *libctx,int code,void *tok);
	 void (*deltok)(mm_context ctx,void *libctx,int code,void *tok);
	 double (*evaltok)(mm_context ctx,void *libctx,int code,void *tok,int *status);
	 int (*countvars)(mm_context ctx,void *libctx,struct NLVS *nlvs,int code,void *tok,int where,int lev);
	} s_deftok;

typedef struct
	{
	 double coeff;
	 mm_mpvar v1;
	 mm_mpvar v2;
	} s_nlqterm;

typedef struct NLVS			/* used & populated by nlstore */
	{
	 int needhess;		/* <>0 if structures for Hessian are required */
	 int nbnlctr;		/* nb of NL constraints (quadratic included) */
	 int nbqctr;		/* nb of quadratic constraints */
	 int objtype;		/* 1 if objective is NL; 2 if quadratic */
	 int nb_nlctrs;		/* nb of constraints handled by mmnl */
	 void *htdata;		/* ht for nlstore (deleted by mkextravar) */
	 int nzro;		/* nb of non zero in objective gradient */
	 int n_var;		/* nb of vars (size of lsvars/prvars/mnel) */
	 int tapesize;		/* nb of doubles required for AD_rev */
	 mm_mpvar *lsvars;	/* list of vars for 'loadmat' */
	 int *prvars;		/* properties of each variable */
	 int *mnel;		/* nb of element / column */
	 int use_exttok;	/* 1 if exttok in obj; 2 if exttok in ctrs */
	} s_nlvstore;

typedef struct NLPdata
	{
	 struct NlCtx *nlctx;
	 int options;
	 int nbvar;		/* nb of variables */
	 int nbctr;		/* nb of constraints */
	 int nb_nlctrs;		/* nb of constraints handled by mmnl */
	 int nbnlctr;		/* nb of NL constraints (quadratic included) */
	 int nbqctr;		/* nb of quadratic constraints */

	 void *fctctx;		/* Context for user functions */
	 double (*getsol_v)(mm_context ctx,void *fctctx,int what,int colndx);
	 			/* what=0 => var sol */
	 			/* what=1 => var reduced cost */
	 double (*getsol_c)(mm_context ctx,void *fctctx,int what,int rowndx);
	 			/* what=0 => ctr slack */
	 			/* what=1 => ctr dual sol */
	 void (*delmat)(mm_context ctx,void *fctctx);
	 			/* Called before releasing this structure */

	 int objtype;		/* 1 if objective is NL; 2 if quadratic */
	 struct NlCtr *nlobj;	/* if objtype>=1: the objective */
	 int nzrobj;		/* nb of non zero in objective gradient */
	 int *vrefobj;		/* var ref in grdobj [nzrobj] */
	 double *grdobj;	/* Gradient of the objective
	 			   [nbvar] or [nzrobj] if NLOPT_SPRSOBJ */
	 double fixobj;		/* constant term in the linear objective */

	 struct NlCtr **nlctr;	/* NL constraints [nb_nlctrs] */

	 int nzr;		/* nb of non zero in Jacobian */
	 int nzr_lin;		/* nb of non zero in linear part of Jacobian */
	 int *ctrstart;		/* start index of each ctr in jac
	 			   [nbctr+1] or [nbnlctr+1] if NLOPT_COLWJAC */
	 int *vref;		/* var ref in jac
	 			   [nzr] or [nzr-nzr_lin] if NLOPT_COLWJAC */
	 int *colstart;		/* NLOPT_COLWJAC: start index of columns in jac
	 			   [nbvar+1] */
	 int *cref;		/* NLOPT_COLWJAC: constraint ref in jac [nzr] */
	 double *jac;		/* Jacobian 
	 			   [nzr_lin] or [nzr] if FULLJAC|COLWJAC: */

	 		/* Following defined if ! NLOPT_CTRBNDS */
	 char *ctrtype;		/* constraint types [nbctr] */
	 double *rhs;		/* RHS values [nbctr] */
	 double *range;		/* range values [nbctr] (NULL) */
	 		/* Following defined if NLOPT_CTRBNDS */
	 double *clb;		/* Constraints lower bounds [nbctr] */
	 double *cub;		/* Constraints upper bounds [nbctr] */

	 double *dlb;		/* Variables lower bounds [nbvar] */
	 double *dub;		/* Variables upper bounds [nbvar] */

	 int ngents;		/* number of int/PI/SI/bin/SC entities (glb) */
	 char *qgtype;		/* type for each glb [ngents] (NULL) */
	 			/* 'I','B','P','S','R' */
	 int *mgcols;		/* column of each glb [ngents] (NULL) */
	 double *mplim;		/* real bound for PI/SI/SC [ngents] (NULL) */

	 int nsos;		/* Number of SOS */
	 int nzrsos;		/* Number of non-zero elements for SOS */
	 char *qstype;		/* Type of each SOS [nsos] (NULL) */
	 			/* '1' for SOS1 and '2' for SOS2 */
	 int *msstart;		/* Start point for each SOS [nsos+1] (NULL) */
	 int *mscols;		/* Columns (=> SOS) [nzrsos] (NULL) */
	 double *dref;		/* Weights (=> SOS) [nzrsos] (NULL) */

	 int tapesize;
	 double *wcval;		/* work array [ncol] */
	 double *tape;		/* work array [tapesize] */
	 int *wcref;		/* work array [ncol] (=tape!) */

	 double *wcp;		/* direction for Hessian [ncol] */
	 int *cstarth;		/* start index (Hess) [nbnlctr+2] */
	 int *vrefh;		/* var ref (Hess) [cstarth[nbnlctr+1]] */
	 int nzrsh;		/* nb of non zero in Hessian */
	 int *histart;		/* start index of each line in shes [nbvar+1] */
	 int *hiref;		/* var ref in sphes [nzrsh] */

	 struct NLVS *nlvs;	/* for internal use */
	 void *baseadr;		/* for internal use */
	 void *baseadr1;	/* for internal use */
	 double *linjac;	/* for internal use */

	 		/* Following defined if NLOPT_NAMES */
	 char **names;		/* NL constraints names [nb_nlctrs] */
	} s_nlpdata;

typedef struct NlCtr* mm_nlctr;
typedef mm_nlctr XPRMnlctr;
typedef s_nlpdata *XPRMnlpdata;
typedef s_nlqterm *XPRMnlqterm;

/* if NLOPT_SPRSOBJ && !NLOPT_COLWJAC :
     if objtype jac=grdobj+nzrobj  vref=vrefobj+nzrobj
     else       grdobj=jac+nzr     vrefobj=vref+nzr    */
struct Matrix;

typedef struct Mmnl_imci
	{
	 int (*loadprob)(mm_context ctx,struct NlCtx *nlctx,
	 	s_nlpdata **nlpd_prev,int options,mm_linctr obj,
		struct NlCtr *nlobj,mm_mpvar *extravars,
		int (*preproc)(mm_context ctx,void *lctx,struct Matrix *m),
		void *lctx);
	 void (*strip)(mm_context ctx,s_nlpdata *nlpdata,int what);
	 int (*eval)(mm_context ctx,s_nlpdata *nlpdata,int nb,const double *x,double *val);
	 int (*grad)(mm_context ctx,s_nlpdata *nlpdata,int nb,double *grad,const double *x,double *val,int dense);
	 int (*hess)(mm_context ctx,s_nlpdata *nlpdata,double *hess,double yobj,const double *y,const double *x);
	 int (*hessvect)(mm_context ctx,s_nlpdata *nlpdata,double *hv,const double *p,double yobj,const double *y,const double *x);
	 void (*setsolstat)(mm_context ctx,s_nlpdata *nlpdata,int status,double objval);
	 int (*getctrnum)(mm_context ctx,s_nlpdata *nlpdata,mm_linctr ctr);
	 int (*getnlctrnum)(mm_context ctx,s_nlpdata *nlpdata,struct NlCtr *nlctr);

	 struct NlCtr *(*getnextctr)(mm_context ctx,struct NlCtx *nlctx,void **ref);
	 void *(*getnextival)(mm_context ctx,struct NlCtx *nlctx,void *ref,mm_mpvar *v,double *coeff);
	 union NlExpr *(*getexpr)(struct NlCtr *ctr);
	 double (*evalexpr)(mm_context ctx,union NlExpr *toev,int *status, const char **fctnam);
	 mm_mpvar *(*mkvlist)(mm_context ctx,struct NlCtx *nlctx,struct NlCtr *nlobj,s_nlvstore *nlvs,int adopt,mm_mpvar *extravars);
	 void (*clsvstore)(mm_context ctx,s_nlvstore *nlvs);
	 double (*getcstterm)(union NlExpr *expr);
	 int (*getlinpart)(mm_context ctx,union NlExpr *expr,double *coeffs,char *colisnl,int *ndx,int maxvar);
	 void (*recvarref)(double *coeffs, int *ndx,int *nbvar,double coef,int var);
	 int (*buildqtls)(mm_context ctx,struct NlCtx *nlctx,struct NlCtr *qobj,int onlyqterms,int *nbterm,s_nlqterm **qtls,double *cstt);
	 void (*freeqtls)(mm_context ctx,struct NlCtx *nlctx,s_nlqterm *qtls);
	 int (*resetmodflag)(struct NlCtr *nlctr);
	 int (*getmodflag)(struct NlCtr *nlctr);
	 int (*regexttok)(mm_context ctx,struct NlCtx *nlctx,void *libctx,const s_deftok *df);
	 struct NlCtr *(*newextntok)(mm_context ctx,struct NlCtx *nlctx,int index,void *ref);
	 struct NlCtr *(*dupnlctr)(mm_context ctx,struct NlCtx *nlctx,struct NlCtr *nlsrc);
	 struct NlCtr *(*linctr2nlctr)(mm_context ctx,struct NlCtx *nlctx,mm_linctr ctr);
	 int (*countvars)(mm_context ctx,s_nlvstore *nlvs,union NlExpr *expr,int where,int lev);
	 int (*storvar)(mm_context ctx,s_nlvstore *nlvs,mm_mpvar v,int prop,int lev);
	 void (*defgetvsol)(mm_context ctx,struct NlCtx *nlctx,double(*getvsol)(void*,mm_mpvar),void *sctx);
	 int (*setinitsol)(mm_context ctx,void *nlctx);	/* Vima fct!!! */
	 int (*genautoname)(mm_context ctx,struct NlCtx *nlctx,const char *pref,int n,void *ref,char *buf,int buflen);
	 int (*setcallback_nlctrdefinition)(mm_context ctx,struct NlCtx* nlctx, void *nlctrdefinition, void* autoelimctx);
	 int (*setcallback_varequalnlctr)(mm_context ctx,struct NlCtx* nlctx, void *varequalnlctr, void* autoelimctx);
	 int (*getprobstat)(mm_context ctx,struct NlCtx* nlctx);
	 int (*gsetmodflag)(mm_context ctx,struct NlCtx* nlctx,struct NlCtr* nlctr,int how);
	 int (*getnlctrtype)(struct NlCtr *nlctr);
	 int (*setnlctrhidden)(mm_context ctx, struct NlCtx* nlctx,struct NlCtr* nlctr,int hidden);
	} *mmnl_imci;
#endif
