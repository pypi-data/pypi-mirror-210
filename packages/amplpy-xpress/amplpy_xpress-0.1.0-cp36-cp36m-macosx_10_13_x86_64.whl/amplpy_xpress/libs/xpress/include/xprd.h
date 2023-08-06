/************************/
/*         Mosel        */
/*                      */
/* File  xprd.h         */
/************************/
/* (c) Copyright Fair Isaac Corporation 2011-2014. All rights reserved */

#ifndef _XPRD_H
#define _XPRD_H

#define XPRD_VERSION "1.8.0"

#if defined(_WIN32) || defined(_WIN64)
#ifndef XPRD_RTC
 #define XPRD_RTC(t) t __stdcall
#endif
#define XPRD_CC __stdcall
#else
#define XPRD_RTC(t) t
#define XPRD_CC
#endif

					/* Returned values from "runmodel" */
#define XPRD_RT_OK	0
#define XPRD_RT_INSTR	1	/* Invalid instruction */
#define XPRD_RT_MATHERR	3	/* Math error */
#define XPRD_RT_UNKN_PF	5	/* Call to an unknown procedure/function */
#define XPRD_RT_UNKN_SYS	9	/* Call to an unknown system function */
#define XPRD_RT_PROB	10	/* Error when opening/closing a problem */
#define XPRD_RT_ERROR	11	/* Runtime Error code */
#define XPRD_RT_EXIT	12	/* Termination via exit(code) [callproc only] */
#define XPRD_RT_IOERR	13	/* IO Error code */
#define XPRD_RT_BREAK	14	/* Stopped on a breakpoint (debugger only) */
#define XPRD_RT_NIFCT	15	/* Stopped in native function (debugger only) */
#define XPRD_RT_NULL	16	/* NULL reference */
#define XPRD_RT_LICERR	17	/* License error */
#define XPRD_RT_STOP	128	/* Stopped */
#define XPRD_RT_DETACHED -4
#define XPRD_RT_FDCLOSED -3
#define XPRD_RT_NOTINIT	 -2
#define XPRD_RT_RUNNING	 -1

					/* Constants for the IO module */
#define XPRD_F_TEXT	0
#define XPRD_F_BINARY	1
#define XPRD_F_READ	0
#define XPRD_F_INPUT	0
#define XPRD_F_WRITE	2
#define XPRD_F_OUTPUT	2
#define XPRD_F_APPEND	4
#define XPRD_F_ERROR	8
#define XPRD_F_LINBUF	16
#define XPRD_F_INIT	32
#define XPRD_F_SILENT	64
#define XPRD_F_ONCE	128
#define XPRD_F_BSZ(s)	(((s)&127)<<24)

#define XPRD_SYS_NAME	1
#define XPRD_SYS_REL  	2
#define XPRD_SYS_VER	4
#define XPRD_SYS_PROC	8
#define XPRD_SYS_ARCH	16
#define XPRD_SYS_NODE	32
#define XPRD_SYS_RAM	64
#define XPRD_SYS_ALL	0xFFFF

#define XPRD_EVENT_END	1

#define XPRD_FMGR_ERR ((void*)(-1))

typedef struct XDctx *XPRDcontext;
typedef struct XDfstr *XPRDfile;
typedef struct XDmos *XPRDmosel;
typedef struct XDmod *XPRDmodel;

typedef int (XPRD_CC *XPRDfct_data)(void *,char *,int);
typedef int (XPRD_CC *XPRDfct_skip)(void *,int);
typedef int (XPRD_CC *XPRDfct_close)(void *);
typedef void* (XPRD_CC *XPRDfct_open)(void *,char *,int,XPRDfct_data*,XPRDfct_close*,XPRDfct_skip*,char *,int);

/************************** Prototypes ****************************/
#ifdef __cplusplus
extern "C" {
#endif
						/* Dispatcher management */
XPRD_RTC(void) XPRDsetmsglev(int lev);
XPRD_RTC(void) XPRDsetmsgcb(void *ctx,long (*cbmsg)(void*,void *,char *,unsigned long));
XPRD_RTC(int) XPRDstart();
XPRD_RTC(void) XPRDshutdown();
						/* Context management */
XPRD_RTC(XPRDcontext) XPRDinit();
XPRD_RTC(void) XPRDfinish(XPRDcontext ctx);
XPRD_RTC(int) XPRDqueueempty(XPRDcontext ctx);
XPRD_RTC(int) XPRDgetevent(XPRDcontext ctx,XPRDmodel *sender,int *cls, double *value);
XPRD_RTC(void) XPRDdropevent(XPRDcontext ctx);
XPRD_RTC(int) XPRDwaitevent(XPRDcontext ctx,int timeout);
XPRD_RTC(void) XPRDabortwait(XPRDcontext ctx);
XPRD_RTC(int) XPRDsetkeepalive(XPRDcontext ctx,int maxfail,int inter);
XPRD_RTC(void) XPRDgetkeepalive(XPRDcontext ctx,int *maxfail,int *inter);
XPRD_RTC(int) XPRDsetsshcmd(XPRDcontext ctx,const char *sshcmd);
XPRD_RTC(const char *) XPRDgetsshcmd(XPRDcontext ctx);
						/* Mosel instance management */
XPRD_RTC(XPRDcontext) XPRDgetxprd(XPRDmosel mosel);
XPRD_RTC(XPRDmosel) XPRDconnect(XPRDcontext ctx,const char *cnstr,XPRDfct_open fmgr,void *fctx,char *errmsg,int msglen);
XPRD_RTC(int) XPRDdisconnect(XPRDmosel mosel);
XPRD_RTC(int) XPRDconnected(XPRDmosel mosel);
XPRD_RTC(char *) XPRDsysinfo(XPRDmosel mosel,int what, char *buf,size_t buflen);
XPRD_RTC(const char *) XPRDbanner(XPRDmosel mosel);
XPRD_RTC(int) XPRDinstid(XPRDmosel mosel);
XPRD_RTC(int) XPRDcompmod(XPRDmosel mosel,const char *options,const char *srcfile,const char *destfile,const char *userc);
XPRD_RTC(int) XPRDcompmodsec(XPRDmosel mos,const char *opt,const char *src,const char *dst,const char *userc,const char *passfile,const char *privkey,const char *kfile);
XPRD_RTC(int) XPRDsetdefstream(XPRDmosel mosel,XPRDmodel model,int wmd,const char *name);
XPRD_RTC(int) XPRDsetcontrol(XPRDmosel mosel,XPRDmodel model,const char *name,const char *val);
						/* Model management */
XPRD_RTC(XPRDmosel) XPRDgetmosel(XPRDmodel model);
XPRD_RTC(XPRDmodel) XPRDloadmod(XPRDmosel mosel,const char *bname);
XPRD_RTC(XPRDmodel) XPRDloadmodsec(XPRDmosel mos,const char *fname,const char *flags,const char *passfile,const char *privkey,const char *keys);
XPRD_RTC(int) XPRDunloadmod(XPRDmodel model);
XPRD_RTC(int) XPRDrunmod(XPRDmodel model,const char *parlist);
XPRD_RTC(int) XPRDgetexitcode(XPRDmodel model);
XPRD_RTC(int) XPRDgetstatus(XPRDmodel model);
XPRD_RTC(int) XPRDgetnumber(XPRDmodel mod);
XPRD_RTC(void*) XPRDgetdata(XPRDmodel mod);
XPRD_RTC(void) XPRDsetdata(XPRDmodel mod,void* data);
XPRD_RTC(int) XPRDgetrmtid(XPRDmodel mod);
XPRD_RTC(void) XPRDstoprunmod(XPRDmodel model);
XPRD_RTC(void) XPRDresetmod(XPRDmodel model);
XPRD_RTC(int) XPRDsendevent(XPRDmodel model,int cls,double value);
						/* File access */
XPRD_RTC(XPRDfile) XPRDfopen(XPRDmosel mosel,const char *fname,int mode,char *errmsg,int msglen);
XPRD_RTC(long) XPRDfread(XPRDfile f,void *buf, long size);
XPRD_RTC(int) XPRDfskip(XPRDfile f,int size);
XPRD_RTC(long) XPRDfwrite(XPRDfile f,const void *buf, long size);
XPRD_RTC(int) XPRDfflush(XPRDfile f);
XPRD_RTC(int) XPRDfclose(XPRDfile f);
						/* Miscellaneous */
XPRD_RTC(void) XPRDsetfsrvopt(XPRDcontext ctx,unsigned short port,int nbiter,int delay);
XPRD_RTC(void) XPRDgetfsrvopt(XPRDcontext ctx,unsigned short *port,int *nbiter,int *delay);
XPRD_RTC(int) XPRDfindxsrvs(XPRDcontext ctx,int grp,int maxip,unsigned int *addrs);

#ifdef __cplusplus
}
#endif

#endif
