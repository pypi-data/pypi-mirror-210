/************************/
/*         Mosel        */
/*                      */
/* File  bindrv.h       */
/************************/
/* (c) Copyright Fair Isaac Corporation 2011-2021 */

#ifndef _BINDRV_H
#define _BINDRV_H

#define BINDRV_VERSION "1.4.1"

			/* Token types */
#define BINDRV_TYP_INTP	0
#define BINDRV_TYP_INTM	(1<<5)
#define BINDRV_TYP_INT	(2<<5)
#define BINDRV_TYP_DATA	(3<<5)
#define BINDRV_TYP_REAL	(4<<5)
#define BINDRV_TYP_STR	(5<<5)
#define BINDRV_TYP_BOOL	(6<<5)
#define BINDRV_TYP_CTRL	(7<<5)
#define BINDRV_TYP_LONG	(8<<5) /* used only as a function return value */

			/* Control codes */
#define BINDRV_CTRL_SKIP     0
#define BINDRV_CTRL_LABEL    1
#define BINDRV_CTRL_OPENLST  2
#define BINDRV_CTRL_CLOSELST 3
#define BINDRV_CTRL_OPENNDX  4
#define BINDRV_CTRL_CLOSENDX 5
#define BINDRV_CTRL_NIL      6

#if defined(_WIN32) || defined(_WIN64)
#define BINDRV_LONG __int64
#else
#define BINDRV_LONG long long
#endif

typedef struct Bindrv *s_bindrvctx;

#ifdef __cplusplus
extern "C" {
#endif

s_bindrvctx bindrv_newreader(size_t (*doread)(void *,size_t,size_t,void*),void *rctx);
s_bindrvctx bindrv_newwriter(size_t (*dowrite)(const void *,size_t,size_t,void*),void *wctx);
void bindrv_setalloc(s_bindrvctx ctx,void* (*memalloc)(size_t,void*),void* mctx);
void bindrv_delete(s_bindrvctx todel);

/* Reader */
int bindrv_nexttoken(s_bindrvctx ctx);
int bindrv_getint(s_bindrvctx ctx,int *val);
int bindrv_getlong(s_bindrvctx ctx,BINDRV_LONG *val);
int bindrv_getreal(s_bindrvctx ctx,double *val);
int bindrv_getbool(s_bindrvctx ctx,char *val);
int bindrv_getstring(s_bindrvctx ctx,char **val);
int bindrv_getdata(s_bindrvctx ctx,void **val,size_t *size);
int bindrv_getctrl(s_bindrvctx ctx,int *val);

/* Writer */
int bindrv_putint(s_bindrvctx ctx,int val);
int bindrv_putlong(s_bindrvctx ctx,BINDRV_LONG val);
int bindrv_putreal(s_bindrvctx ctx,double val);
int bindrv_putbool(s_bindrvctx ctx,char val);
int bindrv_putstring(s_bindrvctx ctx,const char *val);
int bindrv_putdata(s_bindrvctx ctx,const void *val,size_t size);
int bindrv_putctrl(s_bindrvctx ctx,int val);

#ifdef __cplusplus
}
#endif

#endif
