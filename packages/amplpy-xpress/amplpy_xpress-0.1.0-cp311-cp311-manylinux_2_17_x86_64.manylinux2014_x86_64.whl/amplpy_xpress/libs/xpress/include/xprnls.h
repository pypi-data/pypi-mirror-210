/************************/
/*        xprnls        */
/*                      */
/* File  xprnls.h       */
/************************/
/* (c) Copyright Fair Isaac Corporation 2015. All rights reserved */

#ifndef _XNLS_H
#define _XNLS_H

#define XNLS_VERSION "1.2.1"

#if defined(_WIN32) || defined(_WIN64)
#define XNLS_RTC __stdcall
#else
#define XNLS_RTC
#endif

/* Options for 'openconv' */
#define XNLS_OPT_READ	0	/* = MM_F_READ */
#define XNLS_OPT_STRICT	1	/* = XNLS_UTF_FLAG_STRICT */
#define XNLS_OPT_WRITE	2	/* = MM_F_WRITE */
#define XNLS_OPT_NOBOM	4
#define XNLS_OPT_BOM	8
#define XNLS_OPT_BSZ(s)	(((s)&127)<<24)

/* Predefined encoding IDs */
#define XNLS_ENC_SYS	-1
#define XNLS_ENC_WCHAR	-2
#define XNLS_ENC_FNAME	-3
#define XNLS_ENC_UTF16	-4
#define XNLS_ENC_UTF32	-5

#define XNLS_ENC_UTF8	 0
#define XNLS_ENC_UTF16LE 1
#define XNLS_ENC_UTF16BE 2
#define XNLS_ENC_UTF32LE 3
#define XNLS_ENC_UTF32BE 4
#define XNLS_ENC_RAW     5
#define XNLS_ENC_ASCII   6
#define XNLS_ENC_88591   7
#define XNLS_ENC_885915  8
#define XNLS_ENC_CP1252  9

/* Message catalog limits */
#define XNLS_MAXMSGS 2048
#define XNLS_MAXLEN  0xFFFF

/* Option flags for 'convbuf' routines */
#define XNLS_UTF_FLAG_STRICT  1
#define XNLS_UTF_FLAG_PARTIAL 2

/* Return codes of 'convbuf' routines */
#define XNLS_CONV_OK      0
#define XNLS_CONV_PARTIAL 1
#define XNLS_CONV_DSTOUT  2
#define XNLS_CONV_FAIL    3

/* Main function name */
#if defined(_WIN32) || defined(_WIN64)
#define XNLS_MAIN wmain
typedef wchar_t *XNLSargv;
#else
#define XNLS_MAIN main
typedef char *XNLSargv;
#endif

struct XnlsStream;
typedef struct XnlsStream *XNLSstream;
struct XnlsDomain;
typedef struct XnlsDomain *XNLSdomain;
typedef long (*xnls_sync)(void *,void *,void *,unsigned long);

/************************** Prototypes ****************************/
#ifdef __cplusplus
extern "C" {
#endif

#ifndef XNLS_INTERNAL

/**** General ****/
int XNLS_RTC XNLSinit(void);
void XNLS_RTC XNLSfinish(void);
int XNLS_RTC XNLSgetencid(const char *enc);
const char * XNLS_RTC XNLSgetencname(int eid);
const char * XNLS_RTC XNLSsetlang(const char *lang);
char** XNLSconvargv(int *argc, XNLSargv sargv[]);
void XNLSfreeargv(char **argv);
const char * XNLS_RTC XNLSprogpath(const char *path);

/**** Buffer conversion ****/
const char* XNLS_RTC XNLSconvstrfrom(int eid,const char *src,int srclen,int *dstlen);
const char* XNLS_RTC XNLSconvstrto(int eid,const char *src,int srclen,int *dstlen);
int XNLS_RTC XNLSconvbuffrom(int eid,
		char **srcstart, char *srcend, 
		char **dststart, char *dstend, int flags);
int XNLS_RTC XNLSconvbufto(int eid,
		char **srcstart, char *srcend, 
		char **dststart, char *dstend, int flags);
int XNLS_RTC XNLSutf8tocode(const char **src,const char *srcend);
int XNLS_RTC XNLScodetoutf8(unsigned int ch,char *dst);

#if defined(_WIN32) || defined(_WIN64)
const wchar_t * XNLS_RTC XNLSmakefname(const char *fname,int srclen,int *dstlen);
#else
#define XNLSmakefname(p,sl,dl) XNLSconvstrto(XNLS_ENC_FNAME,p,sl,dl)
#endif
/**** Stream conversion ****/
struct XnlsStream *XNLSopenconv(int eid,int flags,xnls_sync sync,void *fd);
long XNLSconvwrite(void *vctx,struct XnlsStream *xctx,const void *sbuf,unsigned long size);
long XNLSconvread(void *vctx,struct XnlsStream *xctx,void *buffer,unsigned long size);
int XNLSbackconvread(struct XnlsStream *xctx,long offset);
int XNLSgetenc(struct XnlsStream *xctx,int *status);
int XNLSsetenc(struct XnlsStream *xctx,int eid);
void *XNLSgetfd(struct XnlsStream *xctx);
size_t XNLSgetoffset(struct XnlsStream *xctx);
int XNLScloseconv(void *vctx,struct XnlsStream *xctx);

/**** Message catalog management ****/
struct XnlsDomain * XNLS_RTC XNLSopenmsgdom(const char *name,const char *localedir);
struct XnlsDomain * XNLS_RTC XNLSfindmsgdom(const char *name);
const char * XNLS_RTC XNLSgettext(struct XnlsDomain *dom,const char *msgid);
void XNLS_RTC XNLSclosemsgdom(struct XnlsDomain *dom);
const char * XNLS_RTC XNLSsetlocaledir(struct XnlsDomain *dom,const char *localedir);
int XNLScmpprtfmt(const char *s1, const char *s2);

#endif

#ifdef __cplusplus
}
#endif
#endif
