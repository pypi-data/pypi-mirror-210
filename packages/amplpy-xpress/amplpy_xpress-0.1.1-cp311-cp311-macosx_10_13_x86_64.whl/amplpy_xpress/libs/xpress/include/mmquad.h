/************************/
/*         Mosel        */
/*                      */
/* File  mmquad.h       */
/************************/
/* (c) Copyright Fair Isaac Corporation 2002-2020. All rights reserved */

#ifndef _MMQUAD_H
#define _MMQUAD_H

typedef struct Qexp *mmquad_qexp;

typedef struct Mmquad_imci
	{
	 int (*getqexpstat)(struct Vimactx *ctx, void *libctx, mmquad_qexp q,
	 	int *nblin, int *nbqd, int *changed,struct Lpvar ***lsvar);
	 void (*clearqexpstat)(struct Vimactx *ctx, void *libctx);
	 void *(*getqexpnextterm)(struct Vimactx *ctx, void *libctx,
	 		mmquad_qexp q, void *prev, struct Lpvar **v1,
			struct Lpvar **v2, double *coeff);
	 double (*getqexpsol)(struct Vimactx *ctx,void *libctx,mmquad_qexp q);
	 int (*getqexpstat_hmv)(struct Vimactx *ctx,void *libctx,mmquad_qexp q,
	 	int *nblin, int *nbqd, int *changed,mm_hashmap hmv);
	 int (*gsetmodflag)(struct Vimactx *ctx,void *libctx,mmquad_qexp q,int how);
	} *mmquad_imci;
#endif
