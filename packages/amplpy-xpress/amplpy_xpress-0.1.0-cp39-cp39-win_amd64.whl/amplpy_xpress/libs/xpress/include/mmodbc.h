/************************/
/*         Mosel        */
/*                      */
/* File  mmodbc.h       */
/************************/
/* (c) Copyright Fair Isaac Corporation 2017. All rights reserved */

#ifndef _MMODBC_H
#define _MMODBC_H

struct Odbcctx;

#ifndef SQL_NULL_DATA
#define SQL_NULL_DATA (-1)
#endif

typedef struct
	{
	 int eid;	/* Encoding of the connection */
	 int colsize;	/* Maximum size of text columns (bytes) */
	 int rowcnt;	/* Row number, 0->before first fetch */
	 int nbcol;	/* Number of columns */
	 int *coltyp;	/* Column types (Mosel) [nbcol] */
	 short *sqltyp;	/* Column types (ODBC) [nbcol] */
#ifdef _WIN64
	 __int64 *indic;
#else			/* Indicator (SQL_NULL_DATA or column length) [nbcol] */
	 long *indic;
#endif
	 void **cols;	/* Column data [nbcol] */
	 const char **names;	/* Column names [nbcol] */
	} mm_sqldata;

typedef const char *(*mm_dsnfilter)(struct Vimactx *,void *,const char *);
typedef int (*mm_sqlcb)(struct Vimactx *,void *,mm_sqldata*);

typedef struct Mmodbc_imci
	{
	 int (*setfilter)(struct Vimactx *,struct Odbcctx *,mm_dsnfilter,void*);
	 int (*sqlexecute)(struct Vimactx *,struct Odbcctx *,const char *query,mm_sqlcb,void*);
	} *mmodbc_imci;
#endif
