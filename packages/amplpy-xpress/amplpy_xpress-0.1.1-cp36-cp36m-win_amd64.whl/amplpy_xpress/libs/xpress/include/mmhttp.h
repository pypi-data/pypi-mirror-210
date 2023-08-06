/************************/
/*         Mosel        */
/*                      */
/* File  mmhttp.h       */
/************************/
/* (c) Copyright Fair Isaac Corporation 2014. All rights reserved */

#ifndef _MMHTTP_H
#define _MMHTTP_H

#define HTTP_GET      1
#define HTTP_POST     2
#define HTTP_PUT      4
#define HTTP_DELETE   8
#define HTTP_HEAD   128
#define HTTP_PATCH  256

#define HTTP_MODE_DEFAULT -1
#define HTTP_MODE_SYNC     0
#define HTTP_MODE_ASYNC    1

#define HTTP_URLALLOW_ADD  0
#define HTTP_URLALLOW_DEL  1

struct Hctx;
typedef struct Mmhttp_imci
	{
	 int (*httpsend)(struct Vimactx *ctx,struct Hctx *hctx,int *status,int qtype,const char *query,const char *querydatafile,const char *resultfile,const char *extrahdr);
	 int (*httpsend_async)(struct Vimactx *ctx,struct Hctx *hctx,int mode,int *status,int qtype,const char *query,const char *querydatafile,const char *resultfile,const char *extrahdr);
	 int (*urlallowctrl)(struct Vimactx *ctx,struct Hctx *hctx,int what,void *uactx,int (*urlalrt)(mm_context,void*,const char *));
	} *mmhttp_imci;
#endif
