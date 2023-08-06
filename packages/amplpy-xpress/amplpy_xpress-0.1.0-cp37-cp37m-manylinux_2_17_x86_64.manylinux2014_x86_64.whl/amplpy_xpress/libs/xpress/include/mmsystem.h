/************************/
/*         Mosel        */
/*                      */
/* File  mmsystem.h     */
/************************/
/* (c) Copyright Fair Isaac Corporation 2001-2021. All rights reserved */

#ifndef _MMSYSTEM_H
#define _MMSYSTEM_H

struct Sysctx;

typedef struct Mmsystem_imci
	{
	 int (*setenv)(struct Vimactx *ctx,struct Sysctx *sysctx,const char *name,const char *value);
	 const char *(*getenv)(struct Vimactx *ctx,struct Sysctx *sysctx,const char *name);
	 int (*system)(struct Vimactx *ctx,struct Sysctx *sysctx,const char *cmd);
	 int (*gettxtsize)(struct Vimactx *ctx,struct Sysctx *sysctx,void *txt);
	 char *(*gettxtbuf)(struct Vimactx *ctx,struct Sysctx *sysctx,void *txt);
	 char *(*txtresize)(struct Vimactx *ctx,struct Sysctx *sysctx,void *txt,int size);
#ifdef _WIN32
	 wchar_t *(*envproc)(struct Vimactx *ctx,struct Sysctx *sysctx,wchar_t *todel);
#else
	 void (*envfork_deprec)(struct Vimactx *ctx,struct Sysctx *sysctx);
	 char **(*envfork)(struct Vimactx *ctx,struct Sysctx *sysctx,char **todel);
#endif
	 int (*gettime)(struct Vimactx *ctx,struct Sysctx *sysctx,void *t,int *h,int *m,int *s,int *ms);
	 int (*settime)(struct Vimactx *ctx,struct Sysctx *sysctx,void *t,int h,int m,int s,int ms);
	 int (*getdate)(struct Vimactx *ctx,struct Sysctx *sysctx,void *t,int *y,int *m,int *d);
	 int (*setdate)(struct Vimactx *ctx,struct Sysctx *sysctx,void *t,int y,int m,int d);
	 int (*getdatetime)(struct Vimactx *ctx,struct Sysctx *sysctx,void *t,int *y,int *m,int *d,int *h,int *mi,int *s,int *ms);
	 int (*setdatetime)(struct Vimactx *ctx,struct Sysctx *sysctx,void *t,int y,int m,int d,int h,int mi,int s,int ms);
	 const char *(*getcsttxtbuf)(struct Vimactx *ctx,struct Sysctx *sysctx,void *txt);
	 int (*systeml)(struct Vimactx *ctx,struct Sysctx *sysctx,const char *argv[]);
	} *mmsystem_imci;
#endif
