/************************************************************************
  BCL: Xpress Builder Component Library
  =====================================

  File xprb.h
  ```````````
  -- C header file --

  (c) Copyright Fair Isaac Corporation 1999-2021. All rights reserved.
      rev. Aug. 2014
************************************************************************/

#ifndef _XPRB
#define _XPRB
#if defined(_WIN32) || defined(_WIN64)
#define XB_CC __stdcall
#ifdef _FILE_DEFINED
#define _STDIO_H
#endif
#define XB_EXTERN extern __declspec(dllimport)
#else
#define XB_CC
#if defined(_STDIO_INCLUDED) || defined (_H_STDIO)
#define _STDIO_H
#endif
#define XB_EXTERN extern
#endif

#ifndef xprb_deprecated
#  if defined(_WIN32)
#    define xprb_deprecated(msg) __declspec(deprecated(msg))
#  elif defined(__ICC)
#    define xprb_deprecated(msg) __attribute__((deprecated))
#  elif (defined(GNUC) && (GNUC > 4 || (GNUC == 4 && GNUC_MINOR >= 5))) || defined(clang)
#    define xprb_deprecated(msg) __attribute__((deprecated(msg)))
#  elif defined(__GNUC__) || defined(__INTEL_COMPILER) || defined(__clang__)
#    define xprb_deprecated(msg) __attribute__((deprecated))
#  else
#    define xprb_deprecated(msg)
#  endif
#endif /* !xprb_deprecated */

#define XB_INFINITY 1.0e+20

/* BCL version */
#define XB_VERSION "41.01.01"

/* Error types */
#define XB_ERR 1
#define XB_WAR 0

#define XB_FGETS (char*(*)(char*, int, void*))fgets

/* Variable types */
#define XB_PL  0
#define XB_BV  1
#define XB_UI  2
#define XB_PI  3
#define XB_SC  4
#define XB_SI  5

/* Constraint types */
#define XB_N   0
#define XB_L   1
#define XB_G   2
#define XB_E   3
#define XB_R   4

/* Sense of the objective function */
#define XB_MAXIM 1
#define XB_MINIM 0

/* SOS types */
#define XB_S1    0
#define XB_S2    1

/* Directive types */
#define XB_PR    1
#define XB_UP    2
#define XB_DN    3
#define XB_PU    4
#define XB_PD    5

/* Range types */
#define XB_UPACT 0
#define XB_LOACT 1
#define XB_UUP   2
#define XB_UDN   3
#define XB_UCOST 4
#define XB_LCOST 5

/* Dictionary types */
#define XB_VAR  1
#define XB_ARR  2
#define XB_CTR  3
#define XB_SOS  4
#define XB_IDX  5

/* Dictionaries */
#define XB_DICT_NAMES 0
#define XB_DICT_IDX   1

/* File formats */
#define XB_LP   1
#define XB_MPS  2

/* Synchronization */
#define XB_XO_SOL    1
#define XB_XO_PROB   2
#define XB_XO_SOLMIP 3

/* BCL problem status */
#define XB_GEN  1       /* Matrix has been generated */
#define XB_DIR  2       /* Directive added */
#define XB_MOD  4       /* Row/Col modification */
#define XB_SOL  8       /* Solution available */

/* LP status */
#define XB_LP_OPTIMAL        1
#define XB_LP_INFEAS         2
#define XB_LP_CUTOFF         3
#define XB_LP_UNFINISHED     4
#define XB_LP_UNBOUNDED      5
#define XB_LP_CUTOFF_IN_DUAL 6
#define XB_LP_UNSOLVED       7
#define XPRS_LP_NONCONVEX    8

/* MIP status */
#define XB_MIP_NOT_LOADED     0
#define XB_MIP_LP_NOT_OPTIMAL 1
#define XB_MIP_LP_OPTIMAL     2
#define XB_MIP_NO_SOL_FOUND   3
#define XB_MIP_SOLUTION       4
#define XB_MIP_INFEAS         5
#define XB_MIP_OPTIMAL        6
#define XB_MIP_UNBOUNDED      7

/* Objects of the modeling library */
typedef struct Xbprob xbprob;
typedef struct Xbvar xbvar;
typedef struct Xbvar * xbarrvar;
typedef struct Xbctr xbctr;
typedef struct Xbsos xbsos;
typedef struct Xbcut xbcut;
typedef struct Xbexpr xbexpr;
typedef struct Xbidxset xbidxset;
typedef struct Xbbasis xbbasis;
typedef struct Xbsol xbsol;

/****XPRB****/
#ifndef BCL_CPP
#ifndef _XPRBTYPES
typedef struct Xbprob *XPRBprob;
typedef struct Xbvar *XPRBvar;
typedef struct Xbvar **XPRBarrvar;
typedef struct Xbctr *XPRBctr;
typedef struct Xbsos *XPRBsos;
typedef struct Xbcut *XPRBcut;
typedef struct Xbidxset *XPRBidxset;
typedef struct Xbexpr *XPRBexpr;
typedef struct Xbbasis *XPRBbasis;
typedef struct Xbsol *XPRBsol;
#define _XPRBTYPES
#endif
#endif

#define XPRB_CC XB_CC

#define XPRB_INFINITY XB_INFINITY
#define XPRB_VERSION XB_VERSION

#define XPRB_ERR XB_ERR
#define XPRB_WAR XB_WAR

#define XPRB_FGETS XB_FGETS

#define XPRB_PL XB_PL
#define XPRB_BV XB_BV
#define XPRB_UI XB_UI
#define XPRB_PI XB_PI
#define XPRB_SC XB_SC
#define XPRB_SI XB_SI

#define XPRB_N XB_N
#define XPRB_L XB_L
#define XPRB_G XB_G
#define XPRB_E XB_E
#define XPRB_R XB_R

#define XPRB_MAXIM XB_MAXIM
#define XPRB_MINIM XB_MINIM

#define XPRB_S1 XB_S1
#define XPRB_S2 XB_S2

#define XPRB_UPACT XB_UPACT
#define XPRB_LOACT XB_LOACT
#define XPRB_UUP   XB_UUP
#define XPRB_UDN   XB_UDN
#define XPRB_UCOST XB_UCOST
#define XPRB_LCOST XB_LCOST

#define XPRB_PR XB_PR
#define XPRB_UP XB_UP
#define XPRB_DN XB_DN
#define XPRB_PU XB_PU
#define XPRB_PD XB_PD

#define XPRB_VAR XB_VAR
#define XPRB_ARR XB_ARR
#define XPRB_CTR XB_CTR
#define XPRB_SOS XB_SOS
#define XPRB_IDX XB_IDX

#define XPRB_DICT_NAMES XB_DICT_NAMES
#define XPRB_DICT_IDX   XB_DICT_IDX

#define XPRB_LP  XB_LP
#define XPRB_MPS XB_MPS

#define XPRB_XPRS_SOL    XB_XO_SOL
#define XPRB_XPRS_PROB   XB_XO_PROB
#define XPRB_XPRS_SOLMIP XB_XO_SOLMIP

#define XPRB_GEN XB_GEN
#define XPRB_DIR XB_DIR
#define XPRB_MOD XB_MOD
#define XPRB_SOL XB_SOL

#define XPRB_LP_OPTIMAL XB_LP_OPTIMAL
#define XPRB_LP_INFEAS XB_LP_INFEAS
#define XPRB_LP_CUTOFF XB_LP_CUTOFF
#define XPRB_LP_UNFINISHED XB_LP_UNFINISHED
#define XPRB_LP_UNBOUNDED XB_LP_UNBOUNDED
#define XPRB_LP_CUTOFF_IN_DUAL XB_LP_CUTOFF_IN_DUAL
#define XPRB_LP_UNSOLVED XB_LP_UNSOLVED
#define XPRB_LP_NONCONVEX XB_LP_NONCONVEX

#define XPRB_MIP_NOT_LOADED XB_MIP_NOT_LOADED
#define XPRB_MIP_LP_NOT_OPTIMAL XB_MIP_LP_NOT_OPTIMAL
#define XPRB_MIP_LP_OPTIMAL XB_MIP_LP_OPTIMAL
#define XPRB_MIP_NO_SOL_FOUND XB_MIP_NO_SOL_FOUND
#define XPRB_MIP_SOLUTION XB_MIP_SOLUTION
#define XPRB_MIP_INFEAS XB_MIP_INFEAS
#define XPRB_MIP_OPTIMAL XB_MIP_OPTIMAL
#define XPRB_MIP_UNBOUNDED XB_MIP_UNBOUNDED

/**************************** Function prototypes ****************************/

// Alternative spellings
#define XPRBlpoptimise     XPRBlpoptimize
#define XPRBmipoptimise    XPRBmipoptimize
#define XPRBgetmiis       XPRBgetmiiis

#ifdef __cplusplus
extern "C" {
#endif
int XB_CC XPRBinit(void);
int XB_CC XPRBfinish(void);
int XB_CC XPRBfree(void);
int XB_CC XPRBgettime(void);
struct Xbprob * XB_CC XPRBnewprob(const char *name);
int XB_CC XPRBsetprobname(struct Xbprob *  prob, const char *name);
int XB_CC XPRBresetprob(struct Xbprob *  prob);
int XB_CC XPRBdelprob(struct Xbprob *  prob);
struct xo_prob_struct* XB_CC XPRBgetXPRSprob(struct Xbprob *  prob);
struct Xbvar * XB_CC XPRBnewvar(struct Xbprob * prob, int type, const char *name, double bdl, double bdu);
struct Xbctr * XB_CC XPRBnewctr(struct Xbprob * prob, const char *name, int qrtype);
int XB_CC XPRBaddterm(struct Xbctr * ctr, struct Xbvar * var, double coeff);
int XB_CC XPRBsetsense(struct Xbprob * prob, int dir);
int XB_CC XPRBlpoptimize(struct Xbprob * prob, const char *alg);
double XB_CC XPRBgetobjval(struct Xbprob * prob);
double XB_CC XPRBgetsol(struct Xbvar * var);
int XB_CC XPRBsetobj(struct Xbprob * prob, struct Xbctr * ctr);
int XB_CC XPRBgetsense(struct Xbprob * prob);
int XB_CC XPRBaddqterm(struct Xbctr * ctr, struct Xbvar * var1, struct Xbvar * var2, double coeff);
int XB_CC XPRBseterrctrl(int flag);
int XB_CC XPRBsetmsglevel(struct Xbprob * prob, int level);
int XB_CC XPRBsetrealfmt(struct Xbprob * prob,const char *realfmt);
int XB_CC XPRBsetdecsign(char sign);
int XB_CC XPRBsetvartype(struct Xbvar * var, int type);
int XB_CC XPRBsetarrvarel(struct Xbvar ** av, int n, struct Xbvar * var);
int XB_CC XPRBapparrvarel(struct Xbvar ** av, struct Xbvar * var);
int XB_CC XPRBdelarrvar(struct Xbvar ** av);
int XB_CC XPRBdelctr(struct Xbctr * lct);
int XB_CC XPRBdelterm(struct Xbctr * lct, struct Xbvar * var);
int XB_CC XPRBsetterm(struct Xbctr * lct, struct Xbvar * var, double coeff);
int XB_CC XPRBsetqterm(struct Xbctr * lct, struct Xbvar * var1, struct Xbvar * var2,double coeff);
int XB_CC XPRBdelqterm(struct Xbctr * lct, struct Xbvar * var1, struct Xbvar * var2);
int XB_CC XPRBsetctrtype(struct Xbctr * lct, int qrtype);
int XB_CC XPRBsetrange(struct Xbctr * lct, double low, double up);
int XB_CC XPRBsetincvars(struct Xbctr * lct, int ivstat);
int XB_CC XPRBsetmodcut(struct Xbctr * lct, int mcstat);
int XB_CC XPRBsetdelayed(struct Xbctr * lct, int dstat);
int XB_CC XPRBsetindicator(struct Xbctr * lct, int dir, struct Xbvar * var);
int XB_CC XPRBdelsos(struct Xbsos * sos);
int XB_CC XPRBdelsosel(struct Xbsos * sos, struct Xbvar * var);
int XB_CC XPRBaddsosel(struct Xbsos * sos, struct Xbvar * var, double ref);
int XB_CC XPRBaddsosarrel(struct Xbsos * sos, struct Xbvar ** av, double *cof);
int XB_CC XPRBsetub(struct Xbvar * var, double c);
int XB_CC XPRBsetlb(struct Xbvar * var, double c);
int XB_CC XPRBfixvar(struct Xbvar * var, double c);
int XB_CC XPRBsetlim(struct Xbvar * var, double c);
int XB_CC XPRBsetdictionarysize(struct Xbprob * prob,int dico,int size);
int XB_CC XPRBsetvardir(struct Xbvar * var, int type, double cost);
int XB_CC XPRBsetsosdir(struct Xbsos * ls, int type, double val);
int XB_CC XPRBcleardir(struct Xbprob * prob);
int XB_CC XPRBaddidxel(struct Xbidxset * idx, const char *name);
int XB_CC XPRBprintprob(struct Xbprob * prob);
int XB_CC XPRBprintobj(struct Xbprob * prob);
int XB_CC XPRBexportprob(struct Xbprob * prob, int format, const char *filename);
int XB_CC XPRBwritedir(struct Xbprob * prob, const char *filename);
int XB_CC XPRBloadmat(struct Xbprob * prob);
int XB_CC XPRBprintvar(struct Xbvar * var);
int XB_CC XPRBprintarrvar(struct Xbvar ** av);
int XB_CC XPRBprintctr(struct Xbctr * lct);
int XB_CC XPRBprintsos(struct Xbsos * ls);
int XB_CC XPRBprintidxset(struct Xbidxset * idx);
int XB_CC XPRBprintsol(struct Xbsol * sol);
int XB_CC XPRBgetiis(struct Xbprob * prob, struct Xbvar ** *arrvar, int *numvar, struct Xbctr * **arrctr, int *numctr, int numiis);
int XB_CC XPRBgetmiiis(struct Xbprob * prob, struct Xbvar ** *arrvar, int *numvar, struct Xbctr * **arrctr, int *numctr,struct Xbsos * **arrsos, int *numsos, int numiis);
int XB_CC XPRBloadbasis(struct Xbbasis * basis);
void XB_CC XPRBdelbasis(struct Xbbasis * basis);
int XB_CC XPRBmipoptimize(struct Xbprob * prob, const char *alg);
int XB_CC XPRBsolve(struct Xbprob * prob, const char *alg);
int XB_CC XPRBminim(struct Xbprob * prob, const char *alg);
int XB_CC XPRBmaxim(struct Xbprob * prob, const char *alg);
int XB_CC XPRBloadmipsol(struct Xbprob * prob, double *sol, int ncol, int ifopt);
int XB_CC XPRBaddmipsol(struct Xbprob * prob, struct Xbsol * sol, const char *name);
int XB_CC XPRBsync(struct Xbprob * prob, int synctype);
int XB_CC XPRBbegincb(struct Xbprob * prob, struct xo_prob_struct* optprob);
int XB_CC XPRBendcb(struct Xbprob * prob);
int XB_CC XPRBsetcolorder(struct Xbprob * prob,int colorder);
int XB_CC XPRBfixmipentities(struct Xbprob * prob, int ifround);
int XB_CC XPRBwritesol(struct Xbprob * prob, const char *filename, const char *flags);
int XB_CC XPRBwritebinsol(struct Xbprob * prob, const char *filename, const char *flags);
int XB_CC XPRBwriteslxsol(struct Xbprob * prob, const char *filename, const char *flags);
int XB_CC XPRBwriteprtsol(struct Xbprob * prob, const char *filename, const char *flags);
int XB_CC XPRBreadbinsol(struct Xbprob * prob, const char *filename, const char *flags);
int XB_CC XPRBreadslxsol(struct Xbprob * prob, const char *filename, const char *flags);
int XB_CC XPRBsetvarlink(struct Xbvar * var,void *val);
int XB_CC XPRBdelcut(struct Xbcut * lct);
int XB_CC XPRBdelcutterm(struct Xbcut * lct, struct Xbvar * var);
int XB_CC XPRBaddcutterm(struct Xbcut * lct, struct Xbvar * var, double coeff);
int XB_CC XPRBsetcutterm(struct Xbcut * lct, struct Xbvar * var, double coeff);
int XB_CC XPRBaddcutarrterm(struct Xbcut * cut, struct Xbvar ** tv,double *tc);
int XB_CC XPRBaddcuts(struct Xbprob * prob, struct Xbcut * *cta, int num);
int XB_CC XPRBprintcut(struct Xbcut * lct);
int XB_CC XPRBsetcuttype(struct Xbcut * lct, int qrtype);
int XB_CC XPRBsetcutid(struct Xbcut * lct, int val);
int XB_CC XPRBsetcutmode(struct Xbprob * prob, int mode);
int XB_CC XPRBdelsol(struct Xbsol * sol);
int XB_CC XPRBdelsolvar(struct Xbsol * sol, struct Xbvar * var);
int XB_CC XPRBsetsolvar(struct Xbsol * sol, struct Xbvar * var, double coeff);
int XB_CC XPRBsetsolarrvar(struct Xbsol * sol, struct Xbvar ** tv, const double *tc);
int XB_CC XPRBgetbounds(struct Xbvar * var, double *lbd, double *ubd) ;
int XB_CC XPRBendarrvar(struct Xbvar ** av) ;
int XB_CC XPRBaddarrterm(struct Xbctr * lct, struct Xbvar ** av, double *cof);
int XB_CC XPRBgetrange(struct Xbctr * lct, double *low, double *up);
int XB_CC XPRBgetprobstat(struct Xbprob * prob);
int XB_CC XPRBgetidxel(struct Xbidxset * idx, const char *name);
int XB_CC XPRBgetidxsetsize(struct Xbidxset * idx);
int XB_CC XPRBgetcolnum(struct Xbvar * var);
int XB_CC XPRBgetrownum(struct Xbctr * lct);
int XB_CC XPRBgetarrvarsize(struct Xbvar ** av);
int XB_CC XPRBgetvartype(struct Xbvar * var);
int XB_CC XPRBgetctrtype(struct Xbctr * lct);
int XB_CC XPRBgetctrsize(struct Xbctr * lct);
int XB_CC XPRBgetsostype(struct Xbsos * sos);
int XB_CC XPRBgetmodcut(struct Xbctr * lct);
int XB_CC XPRBgetdelayed(struct Xbctr * lct);
int XB_CC XPRBgetincvars(struct Xbctr * lct);
int XB_CC XPRBgetindicator(struct Xbctr * lct);
int XB_CC XPRBgetlim(struct Xbvar * var, double *lim);
int XB_CC XPRBgetnumiis(struct Xbprob * prob);
int XB_CC XPRBgetlpstat(struct Xbprob * prob);
int XB_CC XPRBgetmipstat(struct Xbprob * prob);
int XB_CC XPRBgetcuttype(struct Xbcut * lct);
int XB_CC XPRBgetcutid(struct Xbcut * lct);
int XB_CC XPRBgetsolvar(struct Xbsol * sol, const struct Xbvar * var, double *val);
int XB_CC XPRBgetsolsize(struct Xbsol * sol);
const char * XB_CC XPRBgetversion(void);
const char * XB_CC XPRBgetprobname(struct Xbprob * prob);
const char * XB_CC XPRBgetidxelname(struct Xbidxset * idx, int i);
const char * XB_CC XPRBgetvarname(struct Xbvar * var);
const char * XB_CC XPRBgetctrname(struct Xbctr * lct);
const char * XB_CC XPRBgetarrvarname(struct Xbvar ** av);
const char * XB_CC XPRBgetsosname(struct Xbsos * sos);
const char * XB_CC XPRBgetidxsetname(struct Xbidxset * idx);
double XB_CC XPRBgetcoeff(struct Xbctr * lct, struct Xbvar * var);
double XB_CC XPRBgetqcoeff(struct Xbctr * lct, struct Xbvar * v1, struct Xbvar * v2);
double XB_CC XPRBgetrhs(struct Xbctr * lct);
double XB_CC XPRBgetctrrng(struct Xbctr * lct,int what);
double XB_CC XPRBgetvarrng(struct Xbvar * var,int what);
double XB_CC XPRBgetrcost(struct Xbvar * var);
double XB_CC XPRBgetslack(struct Xbctr * lct);
double XB_CC XPRBgetact(struct Xbctr * lct);
double XB_CC XPRBgetdual(struct Xbctr * lct);
double XB_CC XPRBgetcutrhs(struct Xbcut * lct);
struct Xbvar **  XB_CC XPRBnewarrvar(struct Xbprob * prob, int nbvar, int type, const char *name, double lob, double upb);
struct Xbvar **  XB_CC XPRBstartarrvar(struct Xbprob * prob, int nbvar, const char *name);
struct Xbvar *  XB_CC XPRBgetindvar(struct Xbctr * lct);
struct Xbctr *  XB_CC XPRBgetnextctr(struct Xbprob * prob, const struct Xbctr * lct);
struct Xbctr *  XB_CC XPRBnewsum(struct Xbprob * prob,const char *name, struct Xbvar ** av, int qrtype, double rhs);
struct Xbctr *  XB_CC XPRBnewsumc(struct Xbprob * prob,const char *name, struct Xbvar ** av, double c, int qrtype, double rhs);
struct Xbctr *  XB_CC XPRBnewarrsum(struct Xbprob * prob,const char *name, struct Xbvar ** av, double *cof, int qrtype, double rhs);
struct Xbctr *  XB_CC XPRBnewprec(struct Xbprob * prob,const char *name, struct Xbvar * v1, double dur,struct Xbvar * v2);
struct Xbcut *  XB_CC XPRBnewcut(struct Xbprob * prob, int qrtype, int mtype);
struct Xbcut *  XB_CC XPRBnewcutsum(struct Xbprob * prob, struct Xbvar ** tv, int qrtype, double rhs, int mtype);
struct Xbcut *  XB_CC XPRBnewcutsumc(struct Xbprob * prob, struct Xbvar ** tv, double c, int qrtype, double rhs, int mtype);
struct Xbcut *  XB_CC XPRBnewcutarrsum(struct Xbprob * prob, struct Xbvar ** tv, double *tc, int qrtype, double rhs, int mtype);
struct Xbcut *  XB_CC XPRBnewcutprec(struct Xbprob * prob, struct Xbvar * v1, double dur, struct Xbvar * v2, int mtype);
struct Xbsos *  XB_CC XPRBnewsos(struct Xbprob * prob, const char *name, int type);
struct Xbsos *  XB_CC XPRBnewsosrc(struct Xbprob * prob, const char *name, int type, struct Xbvar ** av, struct Xbctr * lct);
struct Xbsos *  XB_CC XPRBnewsosw(struct Xbprob * prob, const char *name, int type, struct Xbvar ** av, double *cof);
struct Xbidxset *  XB_CC XPRBnewidxset(struct Xbprob * prob, const char *name, int maxsize);
struct Xbbasis * XB_CC XPRBsavebasis(struct Xbprob * prob);
struct Xbsol *  XB_CC XPRBnewsol(struct Xbprob * prob);
void * XB_CC XPRBgetbyname(struct Xbprob * prob, const char *name, int type);
void * XB_CC XPRBgetvarlink(struct Xbvar * var);
const void * XB_CC XPRBgetnextterm(struct Xbctr * lct, const void *ref, struct Xbvar * *var, double *coeff);
const void * XB_CC XPRBgetnextqterm(struct Xbctr * lct, const void *ref, struct Xbvar * *v1, struct Xbvar * *v2, double *coeff);
const char * XB_CC XPRBnewname(const char *format, ...);
int XB_CC XPRBprintf(struct Xbprob * prob,const char *format, ...);
int XB_CC XPRBprint(struct Xbprob * prob,const char *msg);
int XB_CC XPRBreadlinecb(char *(*fgs)(char *,int,void *),void *f, int maxsize, const char *format,...);
int XB_CC XPRBreadarrlinecb(char *(*fgs)(char *,int,void *),void *f, int maxlen, const char *format, void *t, int size);
#ifdef _STDIO_H
int XB_CC XPRBreadline(FILE *f, int maxsize, const char *format,...);
int XB_CC XPRBreadarrline(FILE *f, int maxlen, const char *format, void *t, int size);
#endif
int XB_CC XPRBdefcbmsg(struct Xbprob * prob,void (XB_CC *userprint)(struct Xbprob * ,void *,const char *),void *vp);
xprb_deprecated("since 41.00")
int XB_CC XPRBdefcbdelvar(struct Xbprob * prob,void (XB_CC *userdelinter)(struct Xbprob * ,void *,struct Xbvar * ,void *),void *vp);
int XB_CC XPRBdefcberr(struct Xbprob * prob,void (XB_CC *usererror)(struct Xbprob * ,void *,int, int, const char *),void *vp);
void XB_CC XPRBfreemem(char *p);

#ifdef __cplusplus
}
#endif

#endif
