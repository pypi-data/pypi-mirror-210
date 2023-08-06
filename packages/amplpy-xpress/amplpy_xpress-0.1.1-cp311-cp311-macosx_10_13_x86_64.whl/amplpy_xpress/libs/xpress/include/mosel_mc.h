/************************/
/*         Mosel        */
/*                      */
/* File  mosel_mc.h     */
/************************/
/* (c) Copyright Fair Isaac Corporation 2001-2019. All rights reserved */

#ifndef _MOSEL_MC_H
#define _MOSEL_MC_H
#include "mosel_rt.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _MOSEL_NI_H
int mmcompmod(struct Vimactx *ctx, const char *options,const char *srcfile,const char *destfile,const char *userc,const char *passfile,const char *privkey,const char *kfile);
#else
int MM_RTC XPRMcompmod(const char *options,const char *srcfile,const char *destfile,const char *userc);
int MM_RTC XPRMcompmodsec(const char *options,const char *srcfile,const char *destfile,const char *userc,const char *passfile,const char *privkey,const char *kfile);
int MM_RTC XPRMexecmod(const char *options,const char *srcfile,const char *parlist, int *returned, mm_model *rtmod);
#endif

#ifdef __cplusplus
}
#endif
#endif
