/************************/
/*         Mosel        */
/*                      */
/* File  mosel_dso.h    */
/************************/
/* (c) Copyright Fair Isaac Corporation 2001-2022. All rights reserved. */

struct Vimactx;
union Alltypes;

#ifdef MM_NICOMPAT
 #if MM_NICOMPAT < 3000000 || MM_NICOMPAT > MM_VERSNUM
  #error "Compatibility version not supported"
 #elif MM_NICOMPAT < 3002000
  #define MM_NIVERS	5005
 #elif MM_NICOMPAT < 3003000
  #define MM_NIVERS	5007
 #elif MM_NICOMPAT < 3004002
  #define MM_NIVERS	5008
 #elif MM_NICOMPAT < 3005003
  #define MM_NIVERS	5009
 #elif MM_NICOMPAT < 3007000
  #define MM_NIVERS	5010
 #elif MM_NICOMPAT < 3009000
  #define MM_NIVERS	5011
 #elif MM_NICOMPAT < 3013000
  #define MM_NIVERS	5012
 #elif MM_NICOMPAT < 4003000
  #define MM_NIVERS	5013
 #elif MM_NICOMPAT < 4005000
  #define MM_NIVERS	5014
 #elif MM_NICOMPAT < 4007000
  #define MM_NIVERS	5015
 #elif MM_NICOMPAT < 4009000
  #define MM_NIVERS	5016
 #elif MM_NICOMPAT < 5001000
  #define MM_NIVERS	5017
 #elif MM_NICOMPAT < 5003000
  #define MM_NIVERS	5018
 #elif MM_NICOMPAT < 5005000
  #define MM_NIVERS	5019
 #elif MM_NICOMPAT < 5007000
  #define MM_NIVERS	5020
 #elif MM_NICOMPAT < 5098000
  #define MM_NIVERS	5021
 #elif MM_NICOMPAT < 6001000
  #define MM_NIVERS	5022
 #endif
#endif

						/* Interface version */
#ifndef MM_NIVERS
#define MM_NIVERS	5023
#endif
						/* Make module version */
#define MM_MKVER(M,m,r) ((r)+(m)*1000+(M)*1000000)
						/* Make module priority */
#define MM_MKPRIORITY(p) ((void*)((size_t)(p)))
							/* Services codes */
#define MM_SRV_PARAM	0		/* Encode a parameter */
				/* int findparm(char *,int *,int,void*,void*) */
#define MM_SRV_RESET	1		/* Reset a DSo for a run */
				/* void *reset(ctx, void *,int) */
#define MM_SRV_CHKVER	2		/* Check version numbers */
				/* int chkvers(int) */
#define MM_SRV_UNLOAD	3		/* Before unloading the DSO */
				/* void unload(void) */
#define MM_SRV_PARLST	4		/* Enumerate the parameter names */
		/* void *nextpar(void *,const char **,const char **,int *) */
#define MM_SRV_IMCI	5	/* Inter-Module Communication Interface */
				/* void * */
#define MM_SRV_DEPLST	6		/* Module dependency list */
				/* const char ** */
#define MM_SRV_STATIC	7		/* Static module (cannot be unloaded) */
				/* STATIC_PROC or STATIC_INST */
#define MM_SRV_IODRVS	8		/* table of IO drivers */
				/* mm_iodrvtab * */
#define MM_SRV_ONEXIT	9		/* End of execution of the model */
				/* void onexit(mm_context,void *,int) */
#define MM_SRV_CHKRES	10		/* Check restrictions */
				/* int chkres(int) */
#define MM_SRV_PRIORITY	11		/* Set module priority level (int) */
				/* MM_MKPRIORITY(level) */
#define MM_SRV_UPDVERS	12		/* update version number (compilation)*/
				/* void updvers(int,int,int*) */
#define MM_SRV_IMPLST	13		/* implied dependency list */
				/* const char ** */
#define MM_SRV_ANNOT	14		/* Annotation definitions */
				/* const char ** */
#define MM_SRV_DSOSTRE	15		/* remote service/data stream */
				/* mm_rfct_open* */
#define MM_SRV_REQTYPS	16		/* list of required types */
				/* const char ** */
#define MM_SRV_PROVIDER	17		/* Identity of provider */
				/* const char * */
#define MM_SRV_NSGRP	18		/* Namespace groups (name,group) */
				/* const char ** */
#define MM_SRV_MEMUSE	19		/* memory used by dso/type */
				/* size_t memuse(ctx,void *,void*,code) */
#define MM_SRV_ARRIND	20		/* array index for an iterator */
				/* int arrind(ctx,void*,void*,cde,arr,int*,op)*/

typedef int (*mm_srv_findparm)(const char *,int *,int,struct Vimactx*,void*);
typedef void *(*mm_srv_reset)(struct Vimactx*,void*,int);
typedef size_t (*mm_srv_memuse)(struct Vimactx*,void*,void*,int);
struct Array;
typedef int (*mm_srv_arrind)(struct Vimactx*,void*,void*,int,struct Array*,int*,int);
					
					/* Values for SRV_STATIC */
#define MM_STATIC_PROC	((void*)2)
#define MM_STATIC_INST	((void*)1)

#define MM_FCT_GETPAR	0		/* Read a library parameter */
				/* {int,text,real} getpar(int) */
#define MM_FCT_SETPAR	1		/* Set a library parameter */
				/* void setpar(int,{int,text,real}) */

                                        /* updvers event types */
#define MM_UPDV_INIT    0       /* module just loaded for compilation */
#define MM_UPDV_FUNC    1       /* procedure/function number */
#define MM_UPDV_TYPE    2       /* type code */
#define MM_UPDV_GPAR    3       /* 'getparam' on parameter number */
#define MM_UPDV_SPAR    4       /* 'setparam' on parameter number */
#define MM_UPDV_ENDP    5       /* end of parsing */

					/* 'findparm': values of 'why' */
#define MM_FNDP_MCREAD	0	/* compilation: getparam */
#define MM_FNDP_MCWRITE	1	/* compilation: setparam */
#define MM_FNDP_RTWRITE	2	/* setparam via 'run' arguments */
#define MM_FNDP_NIREAD	3	/* 'getparam' from another module */
#define MM_FNDP_RTREAD	4	/* 'getparam' from RT library */

					/* Type properties */
#define MM_DTYP_PNCTX	1	/* 'tostring' does not use ctx */
#define MM_DTYP_RFCNT	2	/* create/delete supports reference count */
#define MM_DTYP_APPND	4	/* 'copy' supports 'append' (+=) */
#define MM_DTYP_ORSET	8	/* 'copy' supports 'reset' only */
#define MM_DTYP_PROB	16	/* type represents a problem */
#define MM_DTYP_SHARE	32	/* an object of this type can be shared */
#define MM_DTYP_TFBIN	64	/* 'to/fromstring' support binary format */
#define MM_DTYP_ORD	128	/* 'cmp' supports lt,gt,leq,geq,cmp */
#define MM_DTYP_CONST	256	/* 'create' supports creation of constants&'copy' hash */
#define MM_DTYP_ANDX	512	/* array indexer type (service 'ARRIND' defined) */
#define MM_DTYP_NAMED	1024	/* 'create' supports NAMED */

				/* Decoding of last parameter of 'create' fct */
#define MM_CREATE_NEW	0
#define MM_CREATE_SHR	(1<<12)
#define MM_CREATE_CST	(2<<12)
#define MM_CREATE_NAMED	(3<<12)
#define MM_CREATE(o)	((o)&0x1F000)

				/* Decoding of last parameter of 'copy' fct */
#define MM_CPY_COPY	0
#define MM_CPY_RESET	(1<<12)
#define MM_CPY_APPEND	(2<<12)
#define MM_CPY_HASH	(3<<12)
#define MM_CPY(o)	((o)&0x1F000)

				/* Decoding of last parameter of 'compare' fct*/
#define MM_COMPARE_EQ	0
#define MM_COMPARE_NEQ	(1<<12)
#define MM_COMPARE_LTH	(2<<12)
#define MM_COMPARE_LEQ	(3<<12)
#define MM_COMPARE_GEQ	(4<<12)
#define MM_COMPARE_GTH	(5<<12)
#define MM_COMPARE_CMP	(6<<12)
#define MM_COMPARE(o)	((o)&0x1F000)
#define MM_COMPARE_ERROR	-13
				/* Operation code for 'arrind' service */
#define MM_OPNDX_EXISTS	0
#define MM_OPNDX_DEL	1
#define MM_OPNDX_GET	2
#define MM_OPNDX_SET	3
				/* Flag for from/tostring */
#define MM_TFSTR_BIN	(1<<12)

				/* Control codes for IO drivers */
#define MM_IOCTRL_FCTS	-2
#define MM_IOCTRL_DSO	-1
#define MM_IOCTRL_NAME	0
#define MM_IOCTRL_OPEN	1
#define MM_IOCTRL_CLOSE	2
#define MM_IOCTRL_READ	3
#define MM_IOCTRL_WRITE	4
#define MM_IOCTRL_IFROM	5
#define MM_IOCTRL_ITO	6
#define MM_IOCTRL_INFO	7
#define MM_IOCTRL_SIZE	8
#define MM_IOCTRL_RM	9
#define MM_IOCTRL_MV	10
#define MM_IOCTRL_DUP	11
#define MM_IOCTRL_SKIP	12

			/* Type decoding for records in IO drivers */
#define MM_INIT_SHT_FLD		12
#define MM_INIT_SHT_SKIP	(MM_INIT_SHT_FLD+10)
#define MM_INIT_FLD(o)		(((o)>>MM_INIT_SHT_FLD)&1023)
#define MM_INIT_SKIP(o)		((o)>>MM_INIT_SHT_SKIP)
#define MM_INIT_MSK_SKIP	(1023u<<MM_INIT_SHT_SKIP)

			/* Flags for findident */
#define MM_FID_NOLOC	1
#define MM_FID_BTREF	2

typedef struct Dsoconst
	{
	 char *name;
	 int type;
	 union
	 {
	  char *s;
	  int i;
	  double *d;
	 } val;
	} mm_dsoconst;

			/* Function type flags */
/* #define MM_FTYP_PTR MM_GRP_GEN*/  /* Function returns a pointer */
#define MM_FTYP_NOATTR (1<<29)	/* Function is not an attribute */

typedef struct Dsovimfct
	{
	 char *name;
	 int code;
	 int type;
	 int nbpar;
	 char *typpar;
	 int (*vimfct)(struct Vimactx *,void *);
	} mm_dsofct;

typedef struct Dsotype
	{
	 char *name;
	 int code;
	 int props;
	 void *(*create)(struct Vimactx *,void *,void *,int);
	 void (*fdelete)(struct Vimactx *,void *,void *,int);
	 int (*tostring)(struct Vimactx *,void *,void *,char *,int,int);
	 int (*fromstring)(struct Vimactx *,void *,void *,const char *,int,const char **);
	 int (*copy)(struct Vimactx *,void *,void *,void *,int);
	 int (*compare)(struct Vimactx *,void *,void *,void *,int);
	} mm_dsotyp;

typedef struct
	{
	 int code;
	 void *fct;
	} mm_dsoserv;

typedef struct Dsointer
	{
	 unsigned int nbconst;
	 mm_dsoconst *tabconst;
	 unsigned int nbvmfct;
	 mm_dsofct *tabvmfct;
	 unsigned int nbtypes;
	 mm_dsotyp *tabtypes;
	 unsigned int nbserv;
	 mm_dsoserv *tabserv;
	} mm_dsointer;

typedef struct
	{
	 int code;
	 void *fct;
	} mm_iofcttab;

typedef struct
	{
	 const char *name;
	 mm_iofcttab *fcttab;
	} mm_iodrvtab;

				/* Functions for IO drivers */
typedef void *(*mm_iodrv_open)(struct Vimactx *,int *mode,const char *filename,unsigned int *enc,int *bufsize);
typedef int (*mm_iodrv_close)(struct Vimactx *,void *fd,int mode);
typedef long (*mm_iodrv_sync)(struct Vimactx *,void *fd,void *buffer,unsigned long size);
typedef int (*mm_iodrv_skip)(struct Vimactx *,void *fd,int size);
typedef int (*mm_iodrv_initfrom)(struct Vimactx *,void *fd,int nbrec,const char **labels,int *types,union Alltypes **adrs,int *nbread);
typedef int (*mm_iodrv_initto)(struct Vimactx *,void *fd,int nbrec,const char **labels,int *types,union Alltypes **adrs);
typedef size_t (*mm_iodrv_size)(struct Vimactx *,const char *);
typedef int (*mm_iodrv_rm)(struct Vimactx *,const char *);
typedef int (*mm_iodrv_mv)(struct Vimactx *,const char *,const char *);

typedef int (*mm_rfct_data)(void *,char *,int);
typedef int (*mm_rfct_close)(void *);
typedef void* (*mm_rfct_open)(struct Model*,int,char *,char *,mm_rfct_data*,mm_rfct_close*,char *,int);

typedef struct Iodrvlst* mm_iodrv;
typedef struct Mosel_ni* mm_nifct;
