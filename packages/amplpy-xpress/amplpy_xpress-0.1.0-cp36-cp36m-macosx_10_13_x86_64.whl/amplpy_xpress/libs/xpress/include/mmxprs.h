/************************/
/*         Mosel        */
/*                      */
/* File  mmxprs.h       */
/************************/
/* (c) Copyright Fair Isaac Corporation 2001-2021. All rights reserved */

#ifndef _MMXPRS_H
#define _MMXPRS_H

struct Xprsctx;
struct Mpsol;
struct XoslPB;
struct Mmxprs_imci_xprs;
struct xo_prob_struct;

typedef struct Mmxprs_imci
        {
         void *unused;
         int (*syncstat)(struct Vimactx *,struct Xprsctx *);
         void (*loadcbks)(struct Vimactx *,struct Xprsctx *,int unload);
         void (*setverbose)(struct Vimactx *,struct Xprsctx *,int verb);
         void *(*getxprspb)(struct Vimactx *,struct Xprsctx *,void *pbref);
         int  (*getmpsol)(struct Vimactx *,struct Mpsol*,int ndx,struct Lpvar**,double *);
         mm_mpvar *(*getmapcol)(struct Vimactx *,void *xopb);
         void (*enterexternalcallback)(struct Vimactx*, struct XoslPB*, void *, void **);
         void (*leaveexternalcallback)(struct Vimactx*, struct XoslPB*, void *);

         const struct Mmxprs_imci_xprs* xprsapi;
         int (*getverbose)(struct Vimactx *,struct Xprsctx *);
        } *mmxprs_imci;


/* XPRS_CC calling convention from XPRS_H */
#ifndef XPRS_CC
#ifdef _WIN32
#define XPRS_CC __stdcall
#else
#define XPRS_CC
#endif
#endif

/**
 * Table of XPRS library functions exported throught the IMCI.
 **/
typedef const struct Mmxprs_imci_xprs {
  size_t size;   /* Size of this structure, in bytes. */

  int (XPRS_CC *XPRSgetintattrib)(struct xo_prob_struct* prob, int attrib, int* p_value);
  int (XPRS_CC *XPRSgetstrattrib)(struct xo_prob_struct* prob, int attrib, char* value);
  int (XPRS_CC *XPRSgetdblattrib)(struct xo_prob_struct* prob, int attrib, double* p_value);
  int (XPRS_CC *XPRSsetintcontrol)(struct xo_prob_struct* prob, int control, int value);
  int (XPRS_CC *XPRSsetdblcontrol)(struct xo_prob_struct* prob, int control, double value);
  int (XPRS_CC *XPRSsetstrcontrol)(struct xo_prob_struct* prob, int control, const char* value);
  int (XPRS_CC *XPRSgetintcontrol)(struct xo_prob_struct* prob, int control, int* p_value);
  int (XPRS_CC *XPRSgetdblcontrol)(struct xo_prob_struct* prob, int control, double* p_value);
  int (XPRS_CC *XPRSgetstrcontrol)(struct xo_prob_struct* prob, int control, char* value);
  int (XPRS_CC *XPRScreateprob)(struct xo_prob_struct** p_prob);
  int (XPRS_CC *XPRSdestroyprob)(struct xo_prob_struct* prob);
  int (XPRS_CC *XPRScopyprob)(struct xo_prob_struct* dest, struct xo_prob_struct* src, const char* name);
  int (XPRS_CC *XPRSwriteprob)(struct xo_prob_struct* prob, const char* filename, const char* flags);
  int (XPRS_CC *XPRSiisfirst)(struct xo_prob_struct* prob, int mode, int* p_status);
  int (XPRS_CC *XPRSiiswrite)(struct xo_prob_struct* prob, int iis, const char* filename, int filetype, const char* flags);
  int (XPRS_CC *XPRSaddcbmessage)(struct xo_prob_struct* prob, void (XPRS_CC *f_message)(struct xo_prob_struct* cbprob, void* cbdata, const char* msg, int msglen, int msgtype), void* p, int priority);
  int (XPRS_CC *XPRSremovecbmessage)(struct xo_prob_struct* prob, void (XPRS_CC *f_message)(struct xo_prob_struct* cbprob, void* cbdata, const char* msg, int msglen, int msgtype), void* p);
  int (XPRS_CC *XPRSaddcbpresolve)(struct xo_prob_struct* prob, void (XPRS_CC *f_presolve)(struct xo_prob_struct* cbprob, void* cbdata), void* p, int priority);
  int (XPRS_CC *XPRSremovecbpresolve)(struct xo_prob_struct* prob, void (XPRS_CC *f_presolve)(struct xo_prob_struct* cbprob, void* cbdata), void* p);
} *mmxprs_imci_xprs;

#endif
