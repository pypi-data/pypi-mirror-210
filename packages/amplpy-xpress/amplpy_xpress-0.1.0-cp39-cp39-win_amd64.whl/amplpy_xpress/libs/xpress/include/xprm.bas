Attribute VB_Name = "XPRM"

' Function and Constant declarations for use with
' Xpress Mosel Compiler and Runtime libraries
' (c) Copyright Fair Isaac Corporation 2002-2021. All rights reserved.

Option Explicit
Option Compare Text


' ----------------------------------------------------------------------------------
' Constants

Global Const XPRM_VERSION = "6.0.0"

#If Win64 Then
' this is the new 64-bit type
Global Const XPRM_NULL As LongPtr = 0
Global Const XPRM_PTR_VARTYPE = vbLongLong
#Else
Global Const XPRM_NULL As Long = 0
Global Const XPRM_PTR_VARTYPE = vbLong
#End If



' Possible types
Global Const XPRM_TYP_NOT = 0
Global Const XPRM_TYP_INT = 1
Global Const XPRM_TYP_REAL = 2
Global Const XPRM_TYP_STRING = 3
Global Const XPRM_TYP_BOOL = 4
Global Const XPRM_TYP_MPVAR = 5
Global Const XPRM_TYP_LINCTR = 6
Global Const XPRM_TYP_EXTN = &HFFF

' Possible structures
Global Const XPRM_STR_CONST = 0
Global Const XPRM_STR_REF = 4096
Global Const XPRM_STR_ARR = 8192
Global Const XPRM_STR_SET = 12288
Global Const XPRM_STR_LIST = 16384
Global Const XPRM_STR_PROC = 20480
Global Const XPRM_STR_UNION = 24576
Global Const XPRM_STR_MEM = 28672
Global Const XPRM_STR_UTYP = 32768
Global Const XPRM_STR_NTYP = 36864
Global Const XPRM_STR_REC = 40960
Global Const XPRM_STR_PROB = 45056
Global Const XPRM_STR_CSREF = 53248

' Possible set/array structure
Global Const XPRM_GRP_FIX = 0
Global Const XPRM_GRP_DYN = 131072
Global Const XPRM_GRP_RNG = 0
Global Const XPRM_GRP_GEN = 262144
Global Const XPRM_ARR_FIX = XPRM_GRP_FIX+XPRM_GRP_RNG
Global Const XPRM_ARR_DYFIX = XPRM_GRP_FIX+XPRM_GRP_GEN
Global Const XPRM_ARR_HMAP = XPRM_GRP_DYN+XPRM_GRP_GEN

' DSO parameters coding read/write
Global Const XPRM_CPAR_READ = 4096
Global Const XPRM_CPAR_WRITE = 8192

' DSO type properties encoding
Global Const XPRM_MTP_CREAT = 1
Global Const XPRM_MTP_DELET = 2
Global Const XPRM_MTP_TOSTR = 4
Global Const XPRM_MTP_FRSTR = 8
Global Const XPRM_MTP_PRTBL = 16
Global Const XPRM_MTP_RFCNT = 32
Global Const XPRM_MTP_COPY = 64
Global Const XPRM_MTP_APPND = 128
Global Const XPRM_MTP_ORSET = 256
Global Const XPRM_MTP_PROB = 512
Global Const XPRM_MTP_CMP = 1024
Global Const XPRM_MTP_SHARE = 2048
Global Const XPRM_MTP_TFBIN = 4096
Global Const XPRM_MTP_ORD = 8192
Global Const XPRM_MTP_CONST = 16384
Global Const XPRM_MTP_ANDX = 32768

' Mask
Global Const XPRM_MSK_TYP = &HFFF
Global Const XPRM_MSK_STR = &H1F000
Global Const XPRM_MSK_GRP = &H60000
Global Const XPRM_MSK_FIX = &H80000
Global Const XPRM_MSK_LOC = &HFFF00000

' Problem status
Global Const XPRM_PBSOL = 1   '  A solution is available
Global Const XPRM_PBOPT = 2   ' Optimal solution found
Global Const XPRM_PBUNF = 4   ' Optimisation unfinished
Global Const XPRM_PBINF = 6   ' Problem infeasible
Global Const XPRM_PBUNB = 8   ' Problem is unbounded
Global Const XPRM_PBOTH = 10  ' Optimisation failed (cutoff)
Global Const XPRM_PBRES = 14
Global Const XPRM_PBCHG = 16  ' modified since last matrix generation
Global Const XPRM_PBOBJ = 32  ' objective modified since last generation

' Returned values from "runmodel"
Global Const XPRM_RT_OK = 0
Global Const XPRM_RT_INSTR = 1     ' Invalid instruction
Global Const XPRM_RT_MATHERR = 3   ' Math error
Global Const XPRM_RT_UNKN_PF = 5   ' Call to an unknown procedure/function
Global Const XPRM_RT_UNKN_SYS = 9  ' Call to an unknown system function
Global Const XPRM_RT_PROB = 10     ' Error when opening/closing a problem
Global Const XPRM_RT_ERROR = 11    ' Runtime Error code
Global Const XPRM_RT_EXIT = 12     ' Termination via exit(code) [callproc only]
Global Const XPRM_RT_IOERR = 13    ' IO Error code
Global Const XPRM_RT_BREAK = 14    ' Stopped on a breakpoint (debugger only)
Global Const XPRM_RT_NIFCT = 15    ' Stopped in native function (debugger only)
Global Const XPRM_RT_NULL = 16     ' NULL reference
Global Const XPRM_RT_LICERR = 17   ' License error
Global Const XPRM_RT_STOP = 128    ' Stopped

' IO codes
Global Const XPRM_F_TEXT = 0
Global Const XPRM_F_BINARY = 1
Global Const XPRM_F_READ = 0
Global Const XPRM_F_INPUT = 0
Global Const XPRM_F_WRITE = 2
Global Const XPRM_F_OUTPUT = 2
Global Const XPRM_F_APPEND = 4
Global Const XPRM_F_ERROR = 8
Global Const XPRM_F_LINBUF = 16
Global Const XPRM_F_INIT = 32
Global Const XPRM_F_SILENT = 64

' Properties for getmodprop
Global Const XPRM_PROP_NAME = 0
Global Const XPRM_PROP_ID = 1
Global Const XPRM_PROP_VERSION = 2
Global Const XPRM_PROP_SYSCOM = 3
Global Const XPRM_PROP_USRCOM = 4
Global Const XPRM_PROP_SIZE = 5
Global Const XPRM_PROP_NBREF = 6
Global Const XPRM_PROP_DATE = 7
Global Const XPRM_PROP_PATH = 8
Global Const XPRM_PROP_IMCI = 9
Global Const XPRM_PROP_PRIORITY = 10
Global Const XPRM_PROP_SECSTAT = 11
Global Const XPRM_PROP_SKEYFP = 12
Global Const XPRM_PROP_NBTYPES = 13
Global Const XPRM_PROP_UNAME = 15

' Model security status decoding
Global Const XPRM_SECSTAT_CRYPTED = 1
Global Const XPRM_SECSTAT_SIGNED = 2
Global Const XPRM_SECSTAT_VERIFIED = 4
Global Const XPRM_SECSTAT_UNVERIFIED = 8

' Properties for gettypeprop
Global Const XPRM_TPROP_NAME = 0
Global Const XPRM_TPROP_FEAT = 1
Global Const XPRM_TPROP_EXP = 2
Global Const XPRM_TPROP_BID = 3
Global Const XPRM_TPROP_ITYPS = 4
Global Const XPRM_TPROP_NBELT = 5
Global Const XPRM_TPROP_SIGN = 6

' Control characters for CB init
Global Const XPRM_CBC_SKIP = 0
Global Const XPRM_CBC_OPENLST = 1
Global Const XPRM_CBC_CLOSELST = 2
Global Const XPRM_CBC_OPENNDX = 3
Global Const XPRM_CBC_CLOSENDX = 4

' character encodings
Global Const XNLS_ENC_SYS = -1
Global Const XNLS_ENC_WCHAR = -2
Global Const XNLS_ENC_FNAME = -3
Global Const XNLS_ENC_UTF16 = -4
Global Const XNLS_ENC_UTF32 = -5

Global Const XNLS_ENC_UTF8 = 0
Global Const XNLS_ENC_UTF16LE = 1
Global Const XNLS_ENC_UTF16BE = 2
Global Const XNLS_ENC_UTF32LE = 3
Global Const XNLS_ENC_UTF32BE = 4
Global Const XNLS_ENC_RAW = 5
Global Const XNLS_ENC_ASCII = 6
Global Const XNLS_ENC_88591 = 7
Global Const XNLS_ENC_885915 = 8
Global Const XNLS_ENC_CP1252 = 9

Private Const BUFFER_MAX As Long = 512

' ----------------------------------------------------------------------------------
' DLL stubs


' Utilities

' LPSAFEARRAY WINAPI vbXPRM_string_to_utf_bytes(LPCWSTR text);
' sp2ub - String Pointer to UTF-8 Bytes
#If Win64 Then
Private Declare PtrSafe Function sp2ub Lib "xprmvb" Alias "vbXPRM_wstring_to_utf_bytes" (ByVal bstrPtr As LongPtr) As Byte()
#Else
Private Declare Function sp2ub Lib "xprmvb" Alias "vbXPRM_wstring_to_utf_bytes" (ByVal bstrPtr As Long) As Byte()
#End If

' LPSAFEARRAY WINAPI vbXPRM_utf_to_wstring_bytes(LPCSTR utf);
' up2sb - UTF-8 Pointer to String as Bytes
#If Win64 Then
Private Declare PtrSafe Function up2sb Lib "xprmvb" Alias "vbXPRM_utf_to_wstring_bytes" (ByVal utfPtr As LongPtr) As Byte()
#Else
Private Declare Function up2sb Lib "xprmvb" Alias "vbXPRM_utf_to_wstring_bytes" (ByVal utfPtr As Long) As Byte()
#End If

' UTF-8 encoding functions

' int XNLS_RTC XNLSinit(void);
#If Win64 Then
Private Declare PtrSafe Function XNLSinit Lib "xprnls" () As Long
#Else
Private Declare Function XNLSinit Lib "xprnls" Alias "_XNLSinit@0" () As Long
#End If

' void XNLS_RTC XNLSfinish(void);
#If Win64 Then
Private Declare PtrSafe Sub XNLSfinish Lib "xprnls" ()
#Else
Private Declare Sub XNLSfinish Lib "xprnls" Alias "_XNLSfinish@0" ()
#End If

'int XNLS_RTC XNLSgetencid(const char *enc);
#If Win64 Then
Private Declare PtrSafe Function c_XNLSgetencid Lib "xprnls" Alias "XNLSgetencid" (ByVal encname As LongPtr) As Long
#Else
Private Declare Function c_XNLSgetencid Lib "xprnls" Alias "_XNLSgetencid@4" (ByVal encname As Long) As Long
#End If

'const char * XNLS_RTC XNLSgetencname(int eid);
#If Win64 Then
Private Declare PtrSafe Function c_XNLSgetencname Lib "xprnls" Alias "XNLSgetencname" (ByVal encnid As Long) As LongPtr
#Else
Private Declare Function c_XNLSgetencname Lib "xprnls" Alias "_XNLSgetencname@4" (ByVal encnid As Long) As Long
#End If


' Model functions

'int MM_RTC XPRMcompmod(const char *options,const char *srcfile,const char *destfile,const char *userc);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMcompmod Lib "xprm_mc" Alias "XPRMcompmod" (ByVal options As LongPtr, ByVal srcfile As LongPtr, ByVal dstfile As LongPtr, ByVal userc As LongPtr) As Long
#Else
Private Declare Function c_XPRMcompmod Lib "xprm_mc" Alias "_XPRMcompmod@16" (ByVal options As Long, ByVal srcfile As Long, ByVal dstfile As Long, ByVal userc As Long) As Long
#End If


' const char * MM_RTC XPRMgetlibpath(void);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetlibpath Lib "xprm_rt" Alias "XPRMgetlibpath" () As LongPtr
#Else
Private Declare Function c_XPRMgetlibpath Lib "xprm_rt" Alias "_XPRMgetlibpath@0" () As Long
#End If


' int MM_RTC XPRMcompmodsec(const char *options,const char *srcfile,const char *destfile,const char *userc,const char *passfile,const char *privkey,const char *kfile);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMcompmodsec Lib "xprm_mc" Alias "XPRMcompmodsec" (ByVal options As LongPtr, ByVal srcfile As LongPtr, ByVal dstfile As LongPtr, ByVal userc As LongPtr, ByVal passfile As LongPtr, ByVal privkey As LongPtr, ByVal kfile As LongPtr) As Long
#Else
Private Declare Function c_XPRMcompmodsec Lib "xprm_mc" Alias "_XPRMcompmodsec@28" (ByVal options As Long, ByVal srcfile As Long, ByVal dstfile As Long, ByVal userc As Long, ByVal passfile As Long, ByVal privkey As Long, ByVal kfile As Long) As Long
#End If

' int MM_RTC XPRMexecmod(const char *options,const char *srcfile,const char *parlist, int *returned, mm_model *rtmod);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMexecmod Lib "xprm_mc" Alias "XPRMexecmod" (ByVal options As LongPtr, ByVal srcfile As LongPtr, ByVal parlist As LongPtr, ByRef returned As Long, ByRef rtmod As LongPtr) As Long
#Else
Private Declare Function c_XPRMexecmod Lib "xprm_mc" Alias "_XPRMexecmod@20" (ByVal options As Long, ByVal srcfile As Long, ByVal parlist As Long, ByRef returned As Long, ByRef rtmod As Long) As Long
#End If

' mm_model MM_RTC XPRMfindmod(const char *name,int number);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMfindmod Lib "xprm_rt" Alias "XPRMfindmod" (ByVal name As LongPtr, ByVal number As Long) As LongPtr
#Else
Private Declare Function c_XPRMfindmod Lib "xprm_rt" Alias "_XPRMfindmod@8" (ByVal name As Long, ByVal number As Long) As Long
#End If

' int WINAPI vbXPRMgetmodprop(XPRMmodel model,int what,VARIANT *result)
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetmodprop Lib "xprmvb" Alias "vbXPRMgetmodprop" (ByVal model As LongPtr, ByVal what As Long, ByRef result As Variant) As Long
#Else
Private Declare Function c_XPRMgetmodprop Lib "xprmvb" Alias "vbXPRMgetmodprop" (ByVal model As Long, ByVal what As Long, ByRef result As Variant) As Long
#End If

' void MM_RTC XPRMsetmonitor(mm_model model,int (MM_RTC *monitor)(void *mctx,int evt, void *data,size_t datasize),void *monctx);
' funcPtr parameter is AddressOf Function(ByVal context As Long/LongPtr, ByVal event As Long, Byval data As Long/LongPtr, ByVal dataSize As Long/LongPtr) As Long
#If Win64 Then
Public Declare PtrSafe Sub XPRMsetmonitor Lib "xprm_rt" (ByVal model As LongPtr, ByVal funcPtr As LongPtr, ByVal context As LongPtr)
#Else
Public Declare Sub XPRMsetmonitor Lib "xprm_rt" Alias "_XPRMsetmonitor@12" (ByVal model As Long, ByVal funcPtr As Long, ByVal context As Long)
#End If

' int MM_RTC XPRMrunmod(mm_model model,int *returned, const char *parlist);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMrunmod Lib "xprm_rt" Alias "XPRMrunmod" (ByVal model As LongPtr, ByRef returned As Long, ByVal parlist As LongPtr) As Long
#Else
Private Declare Function c_XPRMrunmod Lib "xprm_rt" Alias "_XPRMrunmod@12" (ByVal model As Long, ByRef returned As Long, ByVal parlist As Long) As Long
#End If

' mm_model MM_RTC XPRMloadmod(const char *bname,const char *intname);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMloadmod Lib "xprm_rt" Alias "XPRMloadmod" (ByVal bname As LongPtr, ByVal intname As LongPtr) As LongPtr
#Else
Private Declare Function c_XPRMloadmod Lib "xprm_rt" Alias "_XPRMloadmod@8" (ByVal bname As Long, ByVal intname As Long) As Long
#End If

' mm_model MM_RTC XPRMloadmodsec(const char *bname,const char *intname,const char *flags,const char *passfile,const char *privkey,const char *keys);
#If Win64 Then
Declare PtrSafe Function c_XPRMloadmodsec Lib "xprm_rt" Alias "XPRMloadmodsec" (ByVal bname As LongPtr, ByVal intname As LongPtr, ByVal flags As LongPtr, ByVal passfile As LongPtr, ByVal privkey As LongPtr, ByVal keys As LongPtr) As LongPtr
#Else
Declare Function c_XPRMloadmodsec Lib "xprm_rt" Alias "_XPRMloadmodsec@24" (ByVal bname As Long, ByVal intname As Long, ByVal flags As Long, ByVal passfile As Long, ByVal privkey As Long, ByVal keys As Long) As Long
#End If



'int MM_RTC XPRMfindident(mm_model model,const char *text,mm_alltypes *value);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMfindident Lib "xprmvb" Alias "vbXPRMfindident" (ByVal model As LongPtr, ByVal text As LongPtr, ByRef value As Variant) As Long
#Else
Private Declare Function c_XPRMfindident Lib "xprmvb" Alias "vbXPRMfindident" (ByVal model As Long, ByVal text As Long, ByRef value As Variant) As Long
#End If

'const char * MM_RTC XPRMgetnextident(mm_model model, void **ref);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextident Lib "xprm_rt" Alias "XPRMgetnextident" (ByVal model As LongPtr, ByRef ref As LongPtr) As LongPtr
#Else
Private Declare Function c_XPRMgetnextident Lib "xprm_rt" Alias "_XPRMgetnextident@8" (ByVal model As Long, ByRef ref As Long) As Long
#End If

'const char * MM_RTC XPRMgetnextanident(mm_model model, void **ref);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextanident Lib "xprm_rt" Alias "XPRMgetnextanident" (ByVal model As LongPtr, ByRef ref As LongPtr) As LongPtr
#Else
Private Declare Function c_XPRMgetnextanident Lib "xprm_rt" Alias "_XPRMgetnextanident@8" (ByVal model As Long, ByRef ref As Long) As Long
#End If

'int MM_RTC XPRMgetannotations(mm_model model, const char *ident, const char *prefix, const char **ann, int maxann);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetannotations Lib "xprm_rt" Alias "XPRMgetannotations" (ByVal model As LongPtr, ByVal ident As LongPtr, ByVal prefix As LongPtr, ByRef annStrings As LongPtr, ByVal maxann As Long) As Long
#Else
Private Declare Function c_XPRMgetannotations Lib "xprm_rt" Alias "_XPRMgetannotations@20" (ByVal model As Long, ByVal ident As Long, ByVal prefix As Long, ByRef annStrings As Long, ByVal maxann As Long) As Long
#End If

'const char * MM_RTC XPRMgetnextparam(mm_model model, void **ref);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextparam Lib "xprm_rt" Alias "XPRMgetnextparam" (ByVal model As LongPtr, ByRef ref As LongPtr) As LongPtr
#Else
Private Declare Function c_XPRMgetnextparam Lib "xprm_rt" Alias "_XPRMgetnextparam@8" (ByVal model As Long, ByRef ref As Long) As Long
#End If

' void * MM_RTC XPRMgetnextdep(mm_model model, void *ref, const char **name, int *version, int *dso_pkg);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextdep Lib "xprm_rt" Alias "XPRMgetnextdep" (ByVal model As LongPtr, ByVal ref As LongPtr, ByRef name As LongPtr, ByRef version As Long, ByRef dso_pkg As Long) As LongPtr
#Else
Private Declare Function c_XPRMgetnextdep Lib "xprm_rt" Alias "_XPRMgetnextdep@20" (ByVal model As Long, ByVal ref As Long, ByRef name As Long, ByRef version As Long, ByRef dso_pkg As Long) As Long
#End If


' void * MM_RTC XPRMgetnextreq(mm_model model, void *ref,const char **name, int *type,void **data);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextreq Lib "xprm_rt" Alias "XPRMgetnextreq" (ByVal model As LongPtr, ByVal ref As LongPtr, ByRef name As LongPtr, ByRef typecode As Long, ByRef data As LongPtr) As LongPtr
#Else
Private Declare Function c_XPRMgetnextreq Lib "xprm_rt" Alias "_XPRMgetnextreq@20" (ByVal model As Long, ByVal ref As Long, ByRef name As Long, ByRef typecode As Long, ByRef data As Long) As Long
#End If

' int MM_RTC XPRMgetprocinfo(mm_proc proc,const char **partyp,int *nbpar,int *type);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetprocinfo Lib "xprm_rt" Alias "XPRMgetprocinfo" (ByVal proc As LongPtr, ByRef partyp As LongPtr, ByRef nbpar As Long, ByRef ftype As Long) As Long
#Else
Private Declare Function c_XPRMgetprocinfo Lib "xprm_rt" Alias "_XPRMgetprocinfo@16" (ByVal proc As Long, ByRef partyp As Long, ByRef nbpar As Long, ByRef ftype As Long) As Long
#End If

' void* MM_RTC XPRMgetnextfield(mm_model model, void *ref,int code,const char **name, int *type,int *number);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextfield Lib "xprm_rt" Alias "XPRMgetnextfield" (ByVal model As LongPtr, ByVal ref As LongPtr, ByVal code As Long, ByRef name As LongPtr, ByRef typecode As Long, ByRef number As Long) As LongPtr
#Else
Private Declare Function c_XPRMgetnextfield Lib "xprm_rt" Alias "_XPRMgetnextfield@24" (ByVal model As Long, ByVal ref As Long, ByVal code As Long, ByRef name As Long, ByRef typecode As Long, ByRef number As Long) As Long
#End If


' int MM_RTC XPRMcb_sendstring(mm_cbinit cb,const char *text,int len,int flush);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMcb_sendstring Lib "xprm_rt" Alias "XPRMcb_sendstring" (ByVal cb As LongPtr, ByVal s As LongPtr, ByVal length As Long, ByVal bFlush As Long) As Long
#Else
Private Declare Function c_XPRMcb_sendstring Lib "xprm_rt" Alias "_XPRMcb_sendstring@12" (ByVal cb As Long, ByVal s As Long, ByVal length As Long, ByVal bFlush As Long) As Long
#End If

' void MM_RTC XPRMsetlocaledir(const char *path);
#If Win64 Then
Private Declare PtrSafe Sub c_XPRMsetlocaledir Lib "xprm_rt" Alias "XPRMsetlocaledir" (ByVal path As LongPtr)
#Else
Private Declare Sub c_XPRMsetlocaledir Lib "xprm_rt" Alias "_XPRMsetlocaledir@4" (ByVal path As Long)
#End If

' const char * MM_RTC XPRMgetlocaledir(void);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetlocaledir Lib "xprm_rt" Alias "XPRMgetlocaledir" () As LongPtr
#Else
Private Declare Function c_XPRMgetlocaledir Lib "xprm_rt" Alias "_XPRMgetlocaledir@0" () As Long
#End If

' void MM_RTC XPRMsetdefworkdir(const char *path);
#If Win64 Then
Private Declare PtrSafe Sub c_XPRMsetdefworkdir Lib "xprm_rt" Alias "XPRMsetdefworkdir" (ByVal path As LongPtr)
#Else
Private Declare Sub c_XPRMsetdefworkdir Lib "xprm_rt" Alias "_XPRMsetdefworkdir@4" (ByVal path As Long)
#End If

' const char * MM_RTC XPRMgetdefworkdir(void);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetdefworkdir Lib "xprm_rt" Alias "XPRMgetdefworkdir" () As LongPtr
#Else
Private Declare Function c_XPRMgetdefworkdir Lib "xprm_rt" Alias "_XPRMgetdefworkdir@0" () As Long
#End If

' int MM_RTC XPRMsetdefstream(mm_model model,int wmd,const char *name);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMsetdefstream Lib "xprm_rt" Alias "XPRMsetdefstream" (ByVal model As LongPtr, ByVal wmd As Long, ByVal name As LongPtr) As Long
#Else
Private Declare Function c_XPRMsetdefstream Lib "xprm_rt" Alias "_XPRMsetdefstream@12" (ByVal model As Long, ByVal wmd As Long, ByVal name As Long) As Long
#End If

' typedef long (WINAPI *cbfunc)(XPRMmodel model, void *ref, const char* buf, unsigned long size);
' long WINAPI vbXPRMcallcbio(XPRMmodel model, cbfunc cb, BSTR text, unsigned long size)
#If Win64 Then
Private Declare PtrSafe Function c_vbXPRMcallcbio Lib "xprmvb" Alias "vbXPRMcallcbio" (ByVal model As LongPtr, ByVal vbaptr As LongPtr, ByVal sptr As LongPtr, ByVal size As Long) As Long
#Else
Private Declare Function c_vbXPRMcallcbio Lib "xprmvb" Alias "vbXPRMcallcbio" (ByVal model As Long, ByVal vbaptr As Long, ByVal sptr As Long, ByVal size As Long) As Long
#End If


' const char * MM_RTC XPRMgetversion(void);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetversion Lib "xprm_rt" Alias "XPRMgetversion" () As LongPtr
#Else
Private Declare Function c_XPRMgetversion Lib "xprm_rt" Alias "_XPRMgetversion@0" () As Long
#End If

' int MM_RTC XPRMgetlicerrmsg(char *msg,int len);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetlicerrmsg Lib "xprm_rt" Alias "XPRMgetlicerrmsg" (ByVal msg As LongPtr, ByVal length As Long) As Long
#Else
Private Declare Function c_XPRMgetlicerrmsg Lib "xprm_rt" Alias "_XPRMgetlicerrmsg@8" (ByVal msg As Long, ByVal length As Long) As Long
#End If


' int MM_RTC XPRMlicense(int *oemnum, char *oemmsg);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMlicense Lib "xprm_rt" Alias "XPRMlicense" (ByRef oemnum As Long, ByVal oemmsg As LongPtr) As Long
#Else
Private Declare Function c_XPRMlicense Lib "xprm_rt" Alias "_XPRMlicense@8" (ByRef oemnum As Long, ByVal oemmsg As Long) As Long
#End If

' const char * MM_RTC XPRMgetlicinfo(void);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetlicinfo Lib "xprm_rt" Alias "XPRMgetlicinfo" () As LongPtr
#Else
Private Declare Function c_XPRMgetlicinfo Lib "xprm_rt" Alias "_XPRMgetlicinfo@0" () As Long
#End If

' int MM_RTC XPRMexportprob(mm_model model, const char *options,const char *fname, mm_linctr obj);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMexportprob Lib "xprm_rt" Alias "XPRMexportprob" (ByVal model As LongPtr, ByVal options As LongPtr, ByVal fname As LongPtr, ByVal obj As LongPtr) As Long
#Else
Private Declare Function c_XPRMexportprob Lib "xprm_rt" Alias "_XPRMexportprob@16" (ByVal model As Long, ByVal options As Long, ByVal fname As Long, ByVal obj As Long) As Long
#End If


' int MM_RTC XPRMpathcheck(const char *str,char *path,int rlen,int acc);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMpathcheck Lib "xprm_rt" Alias "XPRMpathcheck" (ByVal str As LongPtr, ByVal path As LongPtr, ByVal maxlen As Long, ByVal acc As Long) As Long
#Else
Private Declare Function c_XPRMpathcheck Lib "xprm_rt" Alias "_XPRMpathcheck@16" (ByVal str As Long, ByVal path As Long, ByVal maxlen As Long, ByVal acc As Long) As Long
#End If


' int MM_RTC XPRMfindtypecode(mm_model model, const char *typenme);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMfindtypecode Lib "xprm_rt" Alias "XPRMfindtypecode" (ByVal model As LongPtr, ByVal typenme As LongPtr) As Long
#Else
Private Declare Function c_XPRMfindtypecode Lib "xprm_rt" Alias "_XPRMfindtypecode@8" (ByVal model As Long, ByVal typenme As Long) As Long
#End If

' int MM_RTC XPRMdsotyptostr(mm_model model,int code, void *value, char *str, int size);
#If Win64 Then
Private Declare PtrSafe Function c_XPRMdsotyptostr Lib "xprm_rt" Alias "XPRMdsotyptostr" (ByVal model As LongPtr, ByVal code As Long, ByVal value As LongPtr, ByRef str As LongPtr, ByVal size As Long) As Long
#Else
Private Declare Function c_XPRMdsotyptostr Lib "xprm_rt" Alias "_XPRMdsotyptostr@20" (ByVal model As Long, ByVal code As Long, ByVal value As Long, ByRef str As Long, ByVal size As Long) As Long
#End If

' void WINAPI vbXPRMgetelsetval(XPRMset mmset, int ndx, VARIANT* value)
#If Win64 Then
Private Declare PtrSafe Sub c_XPRMgetelsetval Lib "xprmvb" Alias "vbXPRMgetelsetval" (ByVal mmset As LongPtr, ByVal ndx As Long, ByRef value As Variant)
#Else
Private Declare Sub c_XPRMgetelsetval Lib "xprmvb" Alias "vbXPRMgetelsetval" (ByVal mmset As Long, ByVal ndx As Long, ByRef value As Variant)
#End If

' int WINAPI vbXPRMgetarrval(XPRMarray mmarray, LPSAFEARRAY FAR *indices, VARIANT* adr)
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetarrval Lib "xprmvb" Alias "vbXPRMgetarrval" (ByVal mmarray As LongPtr, ByRef indices() As Long, ByRef adr As Variant) As Long
#Else
Private Declare Function c_XPRMgetarrval Lib "xprmvb" Alias "vbXPRMgetarrval" (ByVal mmarray As Long, ByRef indices() As Long, ByRef adr As Variant) As Long
#End If

' int WINAPI vbXPRMgetmodversion(XPRMmodel model, int what, VARIANT* result)
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetmodversion Lib "xprmvb" Alias "vbXPRMgetmodversion" (ByVal model As LongPtr, ByVal what As Long, ByRef result As Variant) As Long
#Else
Private Declare Function c_XPRMgetmodversion Lib "xprmvb" Alias "vbXPRMgetmodversion" (ByVal model As Long, ByVal what As Long, ByRef result As Variant) As Long
#End If


' void* WINAPI vbXPRMgetprevlistelt(XPRMlist list, void* ref, int* type, VARIANT* value)
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetprevlistelt Lib "xprmvb" Alias "vbXPRMgetprevlistelt" (ByVal list As LongPtr, ByVal ref As LongPtr, ByRef typeref As Long, ByRef value As Variant) As LongPtr
#Else
Private Declare Function c_XPRMgetprevlistelt Lib "xprmvb" Alias "vbXPRMgetprevlistelt" (ByVal list As Long, ByVal ref As Long, ByRef typeref As Long, ByRef value As Variant) As Long
#End If

' void* WINAPI vbXPRMgetnextlistelt(XPRMlist list, void* ref, int* type, VARIANT* value)
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgetnextlistelt Lib "xprmvb" Alias "vbXPRMgetnextlistelt" (ByVal list As LongPtr, ByVal ref As LongPtr, ByRef typeref As Long, ByRef value As Variant) As LongPtr
#Else
Private Declare Function c_XPRMgetnextlistelt Lib "xprmvb" Alias "vbXPRMgetnextlistelt" (ByVal list As Long, ByVal ref As Long, ByRef typeref As Long, ByRef value As Variant) As Long
#End If


' void __stdcall vbXPRMgetfieldval(XPRMmodel model, int recordType, void* ptrToRecord, int fieldNum, int fieldType, VARIANT* pResult)
' The VB version of XPRMgetfieldval takes an extra parameter (compared to the C version) telling it the type of the data in the field
#If Win64 Then
Private Declare PtrSafe Sub c_XPRMgetfieldval Lib "xprmvb" Alias "vbXPRMgetfieldval" (ByVal model As LongPtr, ByVal recordtype As Long, ByVal recordptr As LongPtr, ByVal fieldnum As Long, ByVal fieldtype As Long, ByRef value As Variant)
#Else
Private Declare Sub c_XPRMgetfieldval Lib "xprmvb" Alias "vbXPRMgetfieldval" (ByVal model As Long, ByVal recordtype As Long, ByVal recordptr As Long, ByVal fieldnum As Long, ByVal fieldtype As Long, ByRef value As Variant)
#End If


' int WINAPI vbXPRMgettypeprop(XPRMmodel model, int ntyp, int what, VARIANT* value)
#If Win64 Then
Private Declare PtrSafe Function c_XPRMgettypeprop Lib "xprmvb" Alias "vbXPRMgettypeprop" (ByVal model As LongPtr, ByVal ntyp As Long, ByVal what As Long, ByRef value As Variant) As Long
#Else
Private Declare Function c_XPRMgettypeprop Lib "xprmvb" Alias "vbXPRMgettypeprop" (ByVal model As Long, ByVal ntyp As Long, ByVal what As Long, ByRef value As Variant) As Long
#End If

#If Win64 Then
#Else
#End If

#If Win64 Then

Declare PtrSafe Function XPRMgetnextmod Lib "xprm_rt" (ByVal model As LongPtr) As LongPtr
Declare PtrSafe Sub XPRMresetmod Lib "xprm_rt" (ByVal model As LongPtr)
Declare PtrSafe Function XPRMisrunmod Lib "xprm_rt" (ByVal model As LongPtr) As Long
Declare PtrSafe Sub XPRMstoprunmod Lib "xprm_rt" (ByVal model As LongPtr)
Declare PtrSafe Sub XPRMtermrunmod Lib "xprm_rt" (ByVal model As LongPtr)
Declare PtrSafe Function XPRMunloadmod Lib "xprm_rt" (ByVal model As LongPtr) As Long


Declare PtrSafe Sub XPRMfreelibpath Lib "xprm_rt" ()

' Dictionary access
Declare PtrSafe Function XPRMgetnextpbcomp Lib "xprm_rt" (ByVal model As LongPtr, ByVal ref As LongPtr, ByVal code As Long, ByRef typecode As Long) As LongPtr
Declare PtrSafe Function XPRMselectprob Lib "xprm_rt" (ByVal model As LongPtr, ByVal code As Long, ByVal pb As LongPtr) As Long

' Procedures/functions
Declare PtrSafe Function XPRMgetnextproc Lib "xprmvb" Alias "vbXPRMgetnextproc" (ByVal proc As LongPtr) As LongPtr

' Set access
Declare PtrSafe Function XPRMgetsetsize Lib "xprmvb" Alias "vbXPRMgetsetsize" (ByVal mmset As LongPtr) As Long
Declare PtrSafe Function XPRMgetsettype Lib "xprmvb" Alias "vbXPRMgetsettype" (ByVal mmset As LongPtr) As Long
Declare PtrSafe Function XPRMgetfirstsetndx Lib "xprmvb" Alias "vbXPRMgetfirstsetndx" (ByVal mmset As LongPtr) As Long
Declare PtrSafe Function XPRMgetlastsetndx Lib "xprmvb" Alias "vbXPRMgetlastsetndx" (ByVal mmset As LongPtr) As Long
Declare PtrSafe Function XPRMgetelsetndx Lib "xprmvb" Alias "vbXPRMgetelsetndx" (ByVal model As LongPtr, ByVal mmset As LongPtr, ByRef value As Variant) As Long

' List access
Declare PtrSafe Function XPRMgetlistsize Lib "xprmvb" Alias "vbXPRMgetlistsize" (ByVal list As LongPtr) As Long
Declare PtrSafe Function XPRMgetlisttype Lib "xprmvb" Alias "vbXPRMgetlisttype" (ByVal list As LongPtr) As Long

' Array access
Declare PtrSafe Sub XPRMgetarrsets Lib "xprmvb" Alias "vbXPRMgetarrsets" (ByVal mm_array As LongPtr, ByRef sets() As LongPtr)
Declare PtrSafe Function XPRMgetarrdim Lib "xprmvb" Alias "vbXPRMgetarrdim" (ByVal mmarray As LongPtr) As Long
Declare PtrSafe Function XPRMgetarrtype Lib "xprmvb" Alias "vbXPRMgetarrtype" (ByVal mmarray As LongPtr) As Long
Declare PtrSafe Function XPRMgetarrsize Lib "xprmvb" Alias "vbXPRMgetarrsize" (ByVal mmarray As LongPtr) As Long
Declare PtrSafe Function XPRMgetfirstarrentry Lib "xprmvb" Alias "vbXPRMgetfirstarrentry" (ByVal mmarray As LongPtr, ByRef indices() As Long) As Long
Declare PtrSafe Function XPRMgetfirstarrtruentry Lib "xprmvb" Alias "vbXPRMgetfirstarrtruentry" (ByVal mmarray As LongPtr, ByRef indices() As Long) As Long
Declare PtrSafe Function XPRMgetlastarrentry Lib "xprmvb" Alias "vbXPRMgetlastarrentry" (ByVal mmarray As LongPtr, ByRef indices() As Long) As Long
Declare PtrSafe Function XPRMgetnextarrentry Lib "xprmvb" Alias "vbXPRMgetnextarrentry" (ByVal mmarray As LongPtr, ByRef indices() As Long) As Long
Declare PtrSafe Function XPRMgetnextarrtruentry Lib "xprmvb" Alias "vbXPRMgetnextarrtruentry" (ByVal mmarray As LongPtr, ByRef indices() As Long) As Long
Declare PtrSafe Function XPRMchkarrind Lib "xprmvb" Alias "vbXPRMchkarrind" (ByVal mmarray As LongPtr, ByRef indices() As Long) As Long
Declare PtrSafe Function XPRMcmpindices Lib "xprmvb" Alias "vbXPRMcmpindices" (ByVal nbdim As Long, ByRef ind1() As Long, ByRef ind2() As Long) As Long

' Union
Declare PtrSafe Function XPRMgetnextuncomptype Lib "xprm_rt" (ByVal model As LongPtr, ByVal ref As LongPtr, ByVal code As Long, ByRef typ As Long) As LongPtr
Declare PtrSafe Function XPRMgetuntype Lib "xprm_rt" (ByVal un As LongPtr) As Long
Declare PtrSafe Function XPRMgetuntypeid Lib "xprm_rt" (ByVal un As LongPtr) As Long
Private Declare PtrSafe Function c_XPRMgetunvalue Lib "xprmvb" Alias "vbXPRMgetunvalue" (ByVal model As LongPtr, ByVal un As LongPtr, ByRef val As Variant) As Long


' TODO: Add 32-bit versions

' Solution
Declare PtrSafe Function XPRMgetvarnum Lib "xprmvb" Alias "vbXPRMgetvarnum" (ByVal model As LongPtr, ByVal var As LongPtr) As Long
Declare PtrSafe Function XPRMgetctrnum Lib "xprmvb" Alias "vbXPRMgetctrnum" (ByVal model As LongPtr, ByVal ctr As LongPtr) As Long
Declare PtrSafe Function XPRMgetprobstat Lib "xprmvb" Alias "vbXPRMgetprobstat" (ByVal model As LongPtr) As Long
Declare PtrSafe Function XPRMgetobjval Lib "xprmvb" Alias "vbXPRMgetobjval" (ByVal model As LongPtr) As Double
Declare PtrSafe Function XPRMgetvsol Lib "xprmvb" Alias "vbXPRMgetvsol" (ByVal model As LongPtr, ByVal var As LongPtr) As Double
Declare PtrSafe Function XPRMgetcsol Lib "xprmvb" Alias "vbXPRMgetcsol" (ByVal model As LongPtr, ByVal ctr As LongPtr) As Double
Declare PtrSafe Function XPRMgetrcost Lib "xprmvb" Alias "vbXPRMgetrcost" (ByVal model As LongPtr, ByVal var As LongPtr) As Double
Declare PtrSafe Function XPRMgetdual Lib "xprmvb" Alias "vbXPRMgetdual" (ByVal model As LongPtr, ByVal crt As LongPtr) As Double
Declare PtrSafe Function XPRMgetslack Lib "xprmvb" Alias "vbXPRMgetslack" (ByVal model As LongPtr, ByVal ctr As LongPtr) As Double
Declare PtrSafe Function XPRMgetact Lib "xprmvb" Alias "vbXPRMgetact" (ByVal model As LongPtr, ByVal ctr As LongPtr) As Double

' Miscellaneous
Declare PtrSafe Function XPRMinit Lib "xprm_rt" () As Long
Declare PtrSafe Function XPRMfinish Lib "xprm_rt" () As Long
Declare PtrSafe Function XPRMgetversions Lib "xprm_rt" (ByVal whichone As Long) As Long

Declare PtrSafe Sub XPRMskipalldep Lib "xprmvb" Alias "vbXPRMskipalldep" (ByVal model As LongPtr, ByVal ref As LongPtr)



' Begin/end licensing
Declare PtrSafe Function XPRMbeginlicensing Lib "xprm_rt" (ByRef bIsLicensed As Long) As Long
Declare PtrSafe Function XPRMendlicensing Lib "xprm_rt" () As Long

' the functions below are now obsolete but are included for backwards compatibility
' type interrogating
Declare PtrSafe Function XPRM_TYP Lib "xprmvb" Alias "vbXPRM_TYP" (ByVal t As Long) As Long
Declare PtrSafe Function XPRM_STR Lib "xprmvb" Alias "vbXPRM_STR" (ByVal t As Long) As Long
Declare PtrSafe Function XPRM_GRP Lib "xprmvb" Alias "vbXPRM_GRP" (ByVal t As Long) As Long

' Callback-initialization IO driver
Declare PtrSafe Function XPRMcb_sendint Lib "xprm_rt" (ByVal cb As LongPtr, ByVal i As Long, ByVal bFlush As Long) As Long
Declare PtrSafe Function XPRMcb_sendreal Lib "xprm_rt" (ByVal cb As LongPtr, ByVal d As Double, ByVal bFlush As Long) As Long
Declare PtrSafe Function XPRMcb_sendctrl Lib "xprm_rt" (ByVal cb As LongPtr, ByVal c As Byte, ByVal bFlush As Long) As Long


' Time functions
Declare PtrSafe Function XPRMdate2jdn Lib "xprmvb" Alias "vbXPRMdate2jdn" (ByVal y As Long, ByVal m As Long, ByVal d As Long) As Long
Declare PtrSafe Sub XPRMjdn2date Lib "xprmvb" Alias "vbXPRMjdn2date" (ByVal jd As Long, ByRef y As Long, ByRef m As Long, ByRef d As Long)
Declare PtrSafe Sub XPRMtime Lib "xprmvb" Alias "vbXPRMtime" (ByRef jdn As Long, ByRef t As Long, ByRef utc As Long)



#Else

' Utilities

' Model functions
Declare Function XPRMgetnextmod Lib "xprm_rt" Alias "_XPRMgetnextmod@4" (ByVal model As Long) As Long
Declare Sub XPRMresetmod Lib "xprm_rt" Alias "_XPRMresetmod@4" (ByVal model As Long)
Declare Function XPRMisrunmod Lib "xprm_rt" Alias "_XPRMisrunmod@4" (ByVal model As Long) As Long
Declare Sub XPRMstoprunmod Lib "xprm_rt" Alias "_XPRMstoprunmod@4" (ByVal model As Long)
Declare Sub XPRMtermrunmod Lib "xprm_rt" Alias "_XPRMtermrunmod@4" (ByVal model As Long)
Declare Function XPRMunloadmod Lib "xprm_rt" Alias "_XPRMunloadmod@4" (ByVal model As Long) As Long

Declare Sub XPRMfreelibpath Lib "xprm_rt" Alias "_XPRMfreelibpath@0" ()


' Dictionary access
Declare Function XPRMgetnextpbcomp Lib "xprm_rt" Alias "_XPRMgetnextbpcomp@16" (ByVal model As Long, ByVal ref As Long, ByVal code As Long, ByRef typecode As Long) As Long
Declare Function XPRMselectprob Lib "xprm_rt" Alias "_XPRMselectprob@12" (ByVal model As Long, ByVal code As Long, ByVal pb As Long) As Long

' Procedures/functions
Declare Function XPRMgetnextproc Lib "xprmvb" Alias "vbXPRMgetnextproc" (ByVal proc As Long) As Long

' Set access
Declare Function XPRMgetsetsize Lib "xprmvb" Alias "vbXPRMgetsetsize" (ByVal mmset As Long) As Long
Declare Function XPRMgetsettype Lib "xprmvb" Alias "vbXPRMgetsettype" (ByVal mmset As Long) As Long
Declare Function XPRMgetfirstsetndx Lib "xprmvb" Alias "vbXPRMgetfirstsetndx" (ByVal mmset As Long) As Long
Declare Function XPRMgetlastsetndx Lib "xprmvb" Alias "vbXPRMgetlastsetndx" (ByVal mmset As Long) As Long
Declare Function XPRMgetelsetndx Lib "xprmvb" Alias "vbXPRMgetelsetndx" (ByVal model As Long, ByVal mmset As Long, ByRef value As Variant) As Long

' List access
Declare Function XPRMgetlistsize Lib "xprmvb" Alias "vbXPRMgetlistsize" (ByVal list As Long) As Long
Declare Function XPRMgetlisttype Lib "xprmvb" Alias "vbXPRMgetlisttype" (ByVal list As Long) As Long


' Array access
Declare Sub XPRMgetarrsets Lib "xprmvb" Alias "vbXPRMgetarrsets" (ByVal mm_array As Long, ByRef sets() As Long)
Declare Function XPRMgetarrdim Lib "xprmvb" Alias "vbXPRMgetarrdim" (ByVal mmarray As Long) As Long
Declare Function XPRMgetarrtype Lib "xprmvb" Alias "vbXPRMgetarrtype" (ByVal mmarray As Long) As Long
Declare Function XPRMgetarrsize Lib "xprmvb" Alias "vbXPRMgetarrsize" (ByVal mmarray As Long) As Long
Declare Function XPRMgetfirstarrentry Lib "xprmvb" Alias "vbXPRMgetfirstarrentry" (ByVal mmarray As Long, ByRef indices() As Long) As Long
Declare Function XPRMgetfirstarrtruentry Lib "xprmvb" Alias "vbXPRMgetfirstarrtruentry" (ByVal mmarray As Long, ByRef indices() As Long) As Long
Declare Function XPRMgetlastarrentry Lib "xprmvb" Alias "vbXPRMgetlastarrentry" (ByVal mmarray As Long, ByRef indices() As Long) As Long
Declare Function XPRMgetnextarrentry Lib "xprmvb" Alias "vbXPRMgetnextarrentry" (ByVal mmarray As Long, ByRef indices() As Long) As Long
Declare Function XPRMgetnextarrtruentry Lib "xprmvb" Alias "vbXPRMgetnextarrtruentry" (ByVal mmarray As Long, ByRef indices() As Long) As Long
Declare Function XPRMchkarrind Lib "xprmvb" Alias "vbXPRMchkarrind" (ByVal mmarray As Long, ByRef indices() As Long) As Long
Declare Function XPRMcmpindices Lib "xprmvb" Alias "vbXPRMcmpindices" (ByVal nbdim As Long, ByRef ind1() As Long, ByRef ind2() As Long) As Long


' Solution
Declare Function XPRMgetvarnum Lib "xprmvb" Alias "vbXPRMgetvarnum" (ByVal model As Long, ByVal var As Long) As Long
Declare Function XPRMgetctrnum Lib "xprmvb" Alias "vbXPRMgetctrnum" (ByVal model As Long, ByVal ctr As Long) As Long
Declare Function XPRMgetprobstat Lib "xprmvb" Alias "vbXPRMgetprobstat" (ByVal model As Long) As Long
Declare Function XPRMgetobjval Lib "xprmvb" Alias "vbXPRMgetobjval" (ByVal model As Long) As Double
Declare Function XPRMgetvsol Lib "xprmvb" Alias "vbXPRMgetvsol" (ByVal model As Long, ByVal var As Long) As Double
Declare Function XPRMgetcsol Lib "xprmvb" Alias "vbXPRMgetcsol" (ByVal model As Long, ByVal ctr As Long) As Double
Declare Function XPRMgetrcost Lib "xprmvb" Alias "vbXPRMgetrcost" (ByVal model As Long, ByVal var As Long) As Double
Declare Function XPRMgetdual Lib "xprmvb" Alias "vbXPRMgetdual" (ByVal model As Long, ByVal crt As Long) As Double
Declare Function XPRMgetslack Lib "xprmvb" Alias "vbXPRMgetslack" (ByVal model As Long, ByVal ctr As Long) As Double
Declare Function XPRMgetact Lib "xprmvb" Alias "vbXPRMgetact" (ByVal model As Long, ByVal ctr As Long) As Double

' Union
Declare Function XPRMgetnextuncomptype Lib "xprm_rt" (ByVal model As Long, ByVal ref As Long, ByVal code As Long, ByRef typ As Long) As Long
Declare Function XPRMgetuntype Lib "xprm_rt" (ByVal un As Long) As Long
Declare Function XPRMgetuntypeid Lib "xprm_rt" (ByVal un As Long) As Long
Private Declare Function c_XPRMgetunvalue Lib "xprmvb" Alias "vbXPRMgetunvalue" (ByVal model As Long, ByVal un As Long, ByRef val As Variant) As Long

' Miscellaneous
Declare Function XPRMinit Lib "xprm_rt" Alias "_XPRMinit@0" () As Long
Declare Function XPRMfinish Lib "xprm_rt" Alias "_XPRMfinish@0" () As Long
Declare Function XPRMgetversions Lib "xprm_rt" Alias "_XPRMgetversions@4" (ByVal whichone As Long) As Long

Declare Sub XPRMskipalldep Lib "xprmvb" Alias "vbXPRMskipalldep" (ByVal model As Long, ByVal ref As Long)



' Begin/end licensing
Declare Function XPRMbeginlicensing Lib "xprm_rt" Alias "_XPRMbeginlicensing@4" (ByRef bIsLicensed As Long) As Long
Declare Function XPRMendlicensing Lib "xprm_rt" Alias "_XPRMendlicensing@0" () As Long

' the functions below are now obsolete but are included for backwards compatibility
' type interrogating
Declare Function XPRM_TYP Lib "xprmvb" Alias "vbXPRM_TYP" (ByVal t As Long) As Long
Declare Function XPRM_STR Lib "xprmvb" Alias "vbXPRM_STR" (ByVal t As Long) As Long
Declare Function XPRM_GRP Lib "xprmvb" Alias "vbXPRM_GRP" (ByVal t As Long) As Long

' Callback-initialization IO driver
Declare Function XPRMcb_sendint Lib "xprm_rt" Alias "_XPRMcb_sendint@12" (ByVal cb As Long, ByVal i As Long, ByVal bFlush As Long) As Long
Declare Function XPRMcb_sendreal Lib "xprm_rt" Alias "_XPRMcb_sendreal@12" (ByVal cb As Long, ByVal d As Double, ByVal bFlush As Long) As Long
Declare Function XPRMcb_sendctrl Lib "xprm_rt" Alias "_XPRMcb_sendctrl@9" (ByVal cb As Long, ByVal d As Byte, ByVal bFlush As Long) As Long


' Time functions
Declare Function XPRMdate2jdn Lib "xprmvb" Alias "vbXPRMdate2jdn" (ByVal y As Long, ByVal m As Long, ByVal d As Long) As Long
Declare Sub XPRMjdn2date Lib "xprmvb" Alias "vbXPRMjdn2date" (ByVal jd As Long, ByRef y As Long, ByRef m As Long, ByRef d As Long)
Declare Sub XPRMtime Lib "xprmvb" Alias "vbXPRMtime" (ByRef jdn As Long, ByRef t As Long, ByRef utc As Long)


#End If


' b2p - Bytes to Pointer
#If Win64 Then
Private Function b2p(ByRef bytes() As Byte) As LongPtr
    b2p = XPRM_NULL
    On Error Resume Next
    b2p = VarPtr(bytes(LBound(bytes)))
End Function
#Else
Private Function b2p(ByRef bytes() As Byte) As Long
    b2p = XPRM_NULL
    On Error Resume Next
    b2p = VarPtr(bytes(LBound(bytes)))
End Function
#End If

' ub2s - UTF-8 Bytes to String
Private Function ub2s(ByRef utfBytes() As Byte) As String
    Dim utf16() As Byte
    utf16 = up2sb(b2p(utfBytes))
    ub2s = utf16
End Function

' s2ub - String to UTF-8 Bytes
Private Function s2ub(ByRef text As String) As Byte()
    s2ub = sp2ub(StrPtr(text))
End Function

' up2s - UTF-8 Pointer To String
Private Function up2s(ByVal utfPtr As Variant) As String
    Dim sb() As Byte
    sb = up2sb(utfPtr)
    up2s = sb
End Function

' Takes a pointer (as a Long/LongPtr) to UTF-8 encoded NULL-terminated text, decodes to String
Public Function XPRMreadcstring(ByVal utfPtr As Variant) As String
    If XNLSinit Then Exit Function
    XPRMreadcstring = up2s(utfPtr)
    XNLSfinish
End Function

'int XNLS_RTC XNLSgetencid(const char *enc);
Public Function XNLSgetencid(ByVal encname As String) As Long
    If XNLSinit Then Exit Function
    Dim utf_encname() As Byte
    utf_encname = s2ub(encname)
    XNLSgetencid = c_XNLSgetencid(b2p(utf_encname))
    XNLSfinish
End Function

'const char * XNLS_RTC XNLSgetencname(int eid);
Public Function XNLSgetencname(Optional ByVal encid As Long = XNLS_ENC_SYS) As String
    If XNLSinit Then Exit Function
    XNLSgetencname = up2s(c_XNLSgetencname(encid))
    XNLSfinish
End Function


' Alias for XPRMfinish
Public Function XPRMfree() As Long
    XPRMfree = XPRMfinish()
End Function

' const char * MM_RTC XPRMgetlibpath(void);
Public Function XPRMgetlibpath() As String
    If XNLSinit Then Exit Function
    XPRMgetlibpath = up2s(c_XPRMgetlibpath())
    XNLSfinish
End Function

' Alias for XPRMgetlibpath
Public Function XPRMgetdllpath() As String
    XPRMgetdllpath = XPRMgetlibpath
End Function


'int MM_RTC XPRMcompmod(const char *options,const char *srcfile,const char *destfile,const char *userc);
Public Function XPRMcompmod(ByVal options As String, ByVal srcfile As String, ByVal dstfile As String, ByVal userc As String) As Long
    Dim utf_options() As Byte, utf_srcfile() As Byte, utf_dstfile() As Byte, utf_userc() As Byte
    utf_options = s2ub(options)
    utf_srcfile = s2ub(srcfile)
    utf_dstfile = s2ub(dstfile)
    utf_userc = s2ub(userc)

    XPRMcompmod = c_XPRMcompmod(b2p(utf_options), b2p(utf_srcfile), b2p(utf_dstfile), b2p(utf_userc))
End Function

' int MM_RTC XPRMcompmodsec(const char *options,const char *srcfile,const char *destfile,const char *userc,const char *passfile,const char *privkey,const char *kfile);
Public Function XPRMcompmodsec(ByVal options As String, ByVal srcfile As String, ByVal dstfile As String, ByVal userc As String, ByVal passfile As String, ByVal privkey As String, ByVal kfile As String) As Long
    Dim utf_options() As Byte, utf_srcfile() As Byte, utf_dstfile() As Byte, utf_userc() As Byte, utf_passfile() As Byte, utf_privkey() As Byte, utf_kfile() As Byte
    utf_options = s2ub(options)
    utf_srcfile = s2ub(srcfile)
    utf_dstfile = s2ub(dstfile)
    utf_userc = s2ub(userc)
    utf_passfile = s2ub(passfile)
    utf_privkey = s2ub(privkey)
    utf_kfile = s2ub(kfile)

    XPRMcompmodsec = c_XPRMcompmodsec(b2p(utf_options), b2p(utf_srcfile), b2p(utf_dstfile), b2p(utf_userc), b2p(utf_passfile), b2p(utf_privkey), b2p(utf_kfile))
End Function


' int MM_RTC XPRMexecmod(const char *options,const char *srcfile,const char *parlist, int *returned, mm_model *rtmod);
Public Function XPRMexecmod(ByVal options As String, ByVal srcfile As String, ByVal parlist As String, ByRef returned As Long, ByRef rtmod As Variant) As Long
    Dim utf_options() As Byte, utf_srcfile() As Byte, utf_parlist() As Byte
    utf_options = s2ub(options)
    utf_srcfile = s2ub(srcfile)
    utf_parlist = s2ub(parlist)
    
    XPRMexecmod = c_XPRMexecmod(b2p(utf_options), b2p(utf_srcfile), b2p(utf_parlist), returned, rtmod)
End Function

' mm_model MM_RTC XPRMfindmod(const char *name,int number);
Public Function XPRMfindmod(ByVal name As String, ByVal number As Long) As Variant
    Dim utf_name() As Byte
    utf_name = s2ub(name)
    XPRMfindmod = c_XPRMfindmod(b2p(utf_name), number)
End Function


' int MM_RTC XPRMrunmod(mm_model model,int *returned, const char *parlist);
Public Function XPRMrunmod(ByVal model As Variant, ByRef returned As Long, ByVal parlist As String) As Long
    Dim utf_parlist() As Byte
    utf_parlist = s2ub(parlist)
    XPRMrunmod = c_XPRMrunmod(model, returned, b2p(utf_parlist))
End Function


' mm_model MM_RTC XPRMloadmod(const char *bname,const char *intname);
Public Function XPRMloadmod(ByVal bname As String, ByVal intname As String) As Variant
    Dim utf_bname() As Byte, utf_intname() As Byte
    utf_bname = s2ub(bname)
    utf_intname = s2ub(intname)
    XPRMloadmod = c_XPRMloadmod(b2p(utf_bname), b2p(utf_intname))
End Function

' mm_model MM_RTC XPRMloadmodsec(const char *bname,const char *intname,const char *flags,const char *passfile,const char *privkey,const char *keys);
Public Function XPRMloadmodsec(ByVal bname As String, ByVal intname As String, ByVal flags As String, ByVal passfile As String, ByVal privkey As String, ByVal keys As String) As Variant
    Dim utf_bname() As Byte, utf_intname() As Byte, utf_flags() As Byte, utf_passfile() As Byte, utf_privkey() As Byte, utf_keys() As Byte
    utf_bname = s2ub(bname)
    utf_intname = s2ub(intname)
    utf_flags = s2ub(flags)
    utf_passfile = s2ub(passfile)
    utf_privkey = s2ub(privkey)
    utf_keys = s2ub(keys)
    XPRMloadmodsec = c_XPRMloadmodsec(b2p(utf_bname), b2p(utf_intname), b2p(utf_flags), b2p(utf_passfile), b2p(utf_privkey), b2p(utf_keys))
End Function


'int MM_RTC XPRMfindident(mm_model model,const char *text,mm_alltypes *value);
Public Function XPRMfindident(ByVal model As Variant, ByVal text As String, ByRef value As Variant) As Long
    Dim utf_text() As Byte, v As Variant
    utf_text = s2ub(text)
    XPRMfindident = c_XPRMfindident(model, b2p(utf_text), v)
    value = v
End Function


'const char * MM_RTC XPRMgetnextident(mm_model model, void **ref);
Public Function XPRMgetnextident(ByVal model As Variant, ByRef ref As Variant) As String
    XPRMgetnextident = vbNullString
    If model Then
        Dim sb() As Byte
        sb = up2sb(c_XPRMgetnextident(model, ref))
        XPRMgetnextident = sb
    End If
End Function

'const char * MM_RTC XPRMgetnextanident(mm_model model, void **ref);
Public Function XPRMgetnextanident(ByVal model As Variant, ByRef ref As Variant) As String
    XPRMgetnextanident = vbNullString
    If model Then
        Dim sb() As Byte
        sb = up2sb(c_XPRMgetnextanident(model, ref))
        XPRMgetnextanident = sb
    End If
End Function


' int MM_RTC XPRMgetannotations(mm_model model, const char *ident, const char *prefix, const char **ann, int maxann);
' For historical reasons, this function treats an empty string value for ident as if it were a vbNullString
Public Function XPRMgetannotations(ByVal model As Variant, ByVal ident As String, ByVal prefix As String, ByRef annotations() As String, ByVal maxann As Long) As Long
    Dim i, nStrings As Long, nStringsFetched As Long, ann As String
#If Win64 Then
    Dim annptrs() As LongPtr
#Else
    Dim annptrs() As Long
#End If
    ReDim annptrs(1 To maxann + 1)
    If ident = "" Then ident = vbNullString
    Dim utf_ident() As Byte, utf_prefix() As Byte
    utf_ident = s2ub(ident)
    utf_prefix = s2ub(prefix)
    
    nStrings = c_XPRMgetannotations(model, b2p(utf_ident), b2p(utf_prefix), annptrs(LBound(annptrs)), maxann)
    nStringsFetched = IIf(nStrings > maxann, maxann, nStrings)
    
    If nStringsFetched > 0 Then
        For i = 1 To nStringsFetched
            ann = up2s(annptrs(i))
            annotations(LBound(annotations) + i - 1) = ann
        Next
    End If
    XPRMgetannotations = nStrings
End Function

'int vbXPRMgetunvalue(XPRMmodel model, XPRMunion mUnion, VARIANT* value)
Public Function XPRMgetunvalue(ByVal model As LongPtr, ByVal un As LongPtr, ByRef value As Variant) As Long
    Dim v As Variant
    XPRMgetunvalue = c_XPRMgetunvalue(model, un, v)
    value = v
End Function

'const char * MM_RTC XPRMgetnextparam(mm_model model, void **ref);
Public Function XPRMgetnextparam(ByVal model As Variant, ByRef ref As Variant) As String
    XPRMgetnextparam = vbNullString
    If model Then
        Dim sb() As Byte
        sb = up2sb(c_XPRMgetnextparam(model, ref))
        XPRMgetnextparam = sb
    End If
End Function

' void * MM_RTC XPRMgetnextdep(mm_model model, void *ref, const char **name, int *version, int *dso_pkg);
Public Function XPRMgetnextdep(ByVal model As Variant, ByVal ref As Variant, ByRef name As String, ByRef version As Long, ByRef dso_pkg As Long) As Variant
    Dim utfName As Variant
    XPRMgetnextdep = c_XPRMgetnextdep(model, ref, utfName, version, dso_pkg)
    name = up2s(utfName)
End Function

' void * MM_RTC XPRMgetnextreq(mm_model model, void *ref,const char **name, int *type,void **data);
Public Function XPRMgetnextreq(ByVal model As Variant, ByVal ref As Variant, ByRef name As String, ByRef typecode As Long, ByRef data As Variant) As Variant
    Dim utfName As Variant
    XPRMgetnextreq = c_XPRMgetnextreq(model, ref, utfName, typecode, data)
    name = up2s(utfName)
End Function


' int MM_RTC XPRMgetprocinfo(mm_proc proc,const char **partyp,int *nbpar,int *type);
Public Function XPRMgetprocinfo(ByVal proc As Variant, ByRef partyp As String, ByRef nbpar As Long, ByRef ftype As Long) As Long
    If proc Then
        Dim utf_partyp As Variant
        XPRMgetprocinfo = c_XPRMgetprocinfo(proc, utf_partyp, nbpar, ftype)
        partyp = up2s(utf_partyp)
    End If
End Function


' void* MM_RTC XPRMgetnextfield(mm_model model, void *ref,int code,const char **name, int *type,int *number);
Public Function XPRMgetnextfield(ByVal model As Variant, ByVal ref As Variant, ByVal code As Long, ByRef name As String, ByRef typecode As Long, ByRef number As Long) As Variant
    Dim utf_name As Variant
    XPRMgetnextfield = c_XPRMgetnextfield(model, ref, code, utf_name, typecode, number)
    name = up2s(utf_name)
End Function

' int MM_RTC XPRMcb_sendstring(mm_cbinit cb,const char *text,int len,int flush);
Public Function XPRMcb_sendstring(ByVal cb As Variant, ByVal s As String, ByVal bFlush As Long) As Long
    Dim utf_s() As Byte, lenUtf_s As Long
    utf_s = s2ub(s)
    If StrPtr(s) Then
        lenUtf_s = UBound(utf_s) - LBound(utf_s) + 1
    End If
    XPRMcb_sendstring = c_XPRMcb_sendstring(cb, b2p(utf_s), lenUtf_s, bFlush)
End Function

' typedef long (WINAPI *cbfunc)(XPRMmodel model, void *ref, const char* buf, unsigned long size);
#If Win64 Then
Private Function onCBtext(ByVal model As LongPtr, ByVal vbaptr As LongPtr, ByVal utf As LongPtr, ByVal size As Long) As Long
    onCBtext = onCBtext_v(model, vbaptr, utf, size)
End Function
#Else
Private Function onCBtext(ByVal model As Long, ByVal vbaptr As Long, ByVal utf As Long, ByVal size As Long) As Long
    onCBtext = onCBtext_v(model, vbaptr, utf, size)
End Function
#End If
Private Function onCBtext_v(ByVal model As Variant, ByVal vbaptr As Variant, ByVal utf As Variant, ByVal size As Long) As Long
    Dim s As String
    s = up2s(utf)
    onCBtext_v = c_vbXPRMcallcbio(model, vbaptr, StrPtr(s), Len(s))
End Function

' Creates IO driver filename from function pointer
' This is only valid when used for output, and files in text mode
' address is AddressOf Function (ByVal model As Long/LongPtr, ByVal info As Long/LongPtr, ByVal text As String, ByVal size As Long) As Long
Public Function XPRM_IO_CB(ByVal address As Variant) As String
    XPRM_IO_CB = "cb:0x" & Hex(AddressOf onCBtext) & "/" & Hex(address)
End Function


' void MM_RTC XPRMsetlocaledir(const char *path);
Public Sub XPRMsetlocaledir(ByVal path As String)
    Dim utf_path() As Byte
    utf_path = s2ub(path)
    Call c_XPRMsetlocaledir(b2p(utf_path))
End Sub

' const char * MM_RTC XPRMgetlocaledir(void);
Public Function XPRMgetlocaledir() As String
    XPRMgetlocaledir = up2s(c_XPRMgetlocaledir())
End Function

' void MM_RTC XPRMsetdefworkdir(const char *path);
Public Sub XPRMsetdefworkdir(ByVal path As String)
    Dim utf_path() As Byte
    utf_path = s2ub(path)
    Call c_XPRMsetdefworkdir(b2p(utf_path))
End Sub

' const char * MM_RTC XPRMgetdefworkdir(void);
Public Function XPRMgetdefworkdir() As String
    XPRMgetdefworkdir = up2s(c_XPRMgetdefworkdir())
End Function

' int MM_RTC XPRMsetdefstream(mm_model model,int wmd,const char *name);
Public Function XPRMsetdefstream(ByVal model As Variant, ByVal wmd As Long, ByVal name As String) As Long
    Dim utf_name() As Byte
    utf_name = s2ub(name)
    XPRMsetdefstream = c_XPRMsetdefstream(model, wmd, b2p(utf_name))
End Function


' const char * MM_RTC XPRMgetversion(void);
Public Function XPRMgetversion() As String
    XPRMgetversion = up2s(c_XPRMgetversion())
End Function

' int MM_RTC XPRMgetlicerrmsg(char *msg,int len);
Public Function XPRMgetlicerrmsg(ByRef msg As String) As Long
    If XNLSinit Then Exit Function
    Dim utf_msg() As Byte
    ReDim utf_msg(0 To BUFFER_MAX - 1)
    XPRMgetlicerrmsg = c_XPRMgetlicerrmsg(b2p(utf_msg), BUFFER_MAX)
    msg = ub2s(utf_msg)
    XNLSfinish
End Function

' int MM_RTC XPRMlicense(int *oemnum, char *oemmsg);
Public Function XPRMlicense(ByRef oemnum As Long, ByRef oemmsg As String) As Long
    If XNLSinit Then Exit Function
    Dim utf_oemmsg() As Byte, lb As Long, ub As Long, needReDim As Boolean
    utf_oemmsg = s2ub(RTrim(oemmsg))
    ' ensure big enough
    needReDim = False
    If b2p(utf_oemmsg) = XPRM_NULL Then
        needReDim = True
    Else
        lb = LBound(utf_oemmsg)
        ub = UBound(utf_oemmsg)
        needReDim = ub - lb + 1 < BUFFER_MAX
    End If
    
    If needReDim Then
        ReDim Preserve utf_oemmsg(lb To (lb + BUFFER_MAX - 1))
    End If
    XPRMlicense = c_XPRMlicense(oemnum, b2p(utf_oemmsg))
    oemmsg = ub2s(utf_oemmsg)
    XNLSfinish
End Function


' const char * MM_RTC XPRMgetlicinfo(void);
Public Function XPRMgetlicinfo() As String
    If XNLSinit Then Exit Function
    XPRMgetlicinfo = up2s(c_XPRMgetlicinfo)
    XNLSfinish
End Function

' int MM_RTC XPRMexportprob(mm_model model, const char *options,const char *fname, mm_linctr obj);
Public Function XPRMexportprob(ByVal model As Variant, ByVal options As String, ByVal fname As String, ByVal obj As Variant) As Long
    If model Then
        Dim utf_options() As Byte, utf_fname() As Byte
        utf_options = s2ub(options)
        utf_fname = s2ub(fname)
        XPRMexportprob = c_XPRMexportprob(model, b2p(utf_options), b2p(utf_fname), obj)
    Else
        XPRMexportprob = XPRM_RT_ERROR
    End If
End Function


' int MM_RTC XPRMpathcheck(const char *str,char *path,int rlen,int acc);
Public Function XPRMpathcheck(ByVal path As String, ByRef fullpath As String, ByVal maxlen As Long, ByVal acc As Long) As Long
    Dim utf_path() As Byte, utf_fullpath() As Byte
    utf_path = s2ub(path)
    ReDim utf_fullpath(0 To maxlen - 1)
    XPRMpathcheck = c_XPRMpathcheck(b2p(utf_path), b2p(utf_fullpath), maxlen, acc)
    fullpath = ub2s(utf_path)
End Function



' int MM_RTC XPRMfindtypecode(mm_model model, const char *typenme);
Public Function XPRMfindtypecode(ByVal model As Variant, ByVal typename As String) As Long
    Dim utf_typename() As Byte
    utf_typename = s2ub(typename)
    XPRMfindtypecode = c_XPRMfindtypecode(model, b2p(utf_typename))
End Function


' int MM_RTC XPRMdsotyptostr(mm_model model,int code, void *value, char *str, int size);
Public Function XPRMdsotyptostr(ByVal model As Variant, ByVal code As Long, ByVal value As Variant, ByRef str As String) As Long
    If model Then
        Dim utf_str() As Byte
        ReDim utf_str(0 To BUFFER_MAX - 1)
        XPRMdsotyptostr = c_XPRMdsotyptostr(model, code, value, b2p(utf_str), BUFFER_MAX)
        str = ub2s(utf_str)
    Else
        XPRMdsotyptostr = 0
    End If
End Function



' int WINAPI vbXPRMgetmodprop(XPRMmodel model,int what,VARIANT *result)
Public Function XPRMgetmodprop(ByVal model As Variant, ByVal what As Long, ByRef result As Variant) As Long
    Dim v As Variant
    XPRMgetmodprop = c_XPRMgetmodprop(model, what, v)
    result = v
End Function


' void WINAPI vbXPRMgetelsetval(XPRMset mmset, int ndx, VARIANT* value)
Public Sub XPRMgetelsetval(ByVal mmset As Variant, ByVal ndx As Long, ByRef value As Variant)
    Dim v As Variant
    Call c_XPRMgetelsetval(mmset, ndx, v)
    value = v
End Sub


' int WINAPI vbXPRMgetarrval(XPRMarray mmarray, LPSAFEARRAY FAR *indices, VARIANT* adr)
Public Function XPRMgetarrval(ByVal mmarray As Variant, ByRef indices() As Long, ByRef adr As Variant) As Long
    Dim v As Variant
    XPRMgetarrval = c_XPRMgetarrval(mmarray, indices, v)
    adr = v
End Function



' int WINAPI vbXPRMgetmodversion(XPRMmodel model, int what, VARIANT* result)
Public Function XPRMgetmodversion(ByVal model As Variant, ByVal what As Long, ByRef result As Variant) As Long
    Dim v As Variant
    XPRMgetmodversion = c_XPRMgetmodversion(model, what, v)
    result = v
End Function

' void* WINAPI vbXPRMgetprevlistelt(XPRMlist list, void* ref, int* type, VARIANT* value)
Public Function XPRMgetprevlistelt(ByVal list As Variant, ByVal ref As Variant, ByRef typeref As Long, ByRef value As Variant) As Variant
    Dim v As Variant
    XPRMgetprevlistelt = c_XPRMgetprevlistelt(list, ref, typeref, v)
    value = v
End Function

' void* WINAPI vbXPRMgetnextlistelt(XPRMlist list, void* ref, int* type, VARIANT* value)
Public Function XPRMgetnextlistelt(ByVal list As Variant, ByVal ref As Variant, ByRef typeref As Long, ByRef value As Variant) As Variant
    Dim v As Variant
    XPRMgetnextlistelt = c_XPRMgetnextlistelt(list, ref, typeref, v)
    value = v
End Function

' void __stdcall vbXPRMgetfieldval(XPRMmodel model, int recordType, void* ptrToRecord, int fieldNum, int fieldType, VARIANT* pResult)
' The VB version of XPRMgetfieldval takes an extra parameter (compared to the C version) telling it the type of the data in the field
Public Sub XPRMgetfieldval(ByVal model As Variant, ByVal recordtype As Long, ByVal recordptr As Variant, ByVal fieldnum As Long, ByVal fieldtype As Long, ByRef value As Variant)
    Dim v As Variant
    Call c_XPRMgetfieldval(model, recordtype, recordptr, fieldnum, fieldtype, v)
    value = v
End Sub

' int WINAPI vbXPRMgettypeprop(XPRMmodel model, int ntyp, int what, VARIANT* value)
Public Function XPRMgettypeprop(ByVal model As Variant, ByVal ntyp As Long, ByVal what As Long, ByRef value As Variant) As Long
    Dim v As Variant
    XPRMgettypeprop = c_XPRMgettypeprop(model, ntyp, what, v)
    value = v
End Function


' This function is intended to make it easier to wite code independent of 32bit-vs-64-bit and VBA6-vs-VBA7 concerns.
' The parameter "sets" should be an array of appropriate size, with element type being one of Variant, Long, LongPtr
' or LongLong. The actual XPRM API call will be made with a temporary array of Longs or LongPtrs (depending on VBA
' version) and the data will then be copied back if the call is successful.
Public Sub XPRMgetarrsetstovariant(ByVal mmarray As Variant, ByRef sets As Variant)
#If Win64 Then
    Dim tempsets() As LongPtr
#Else
    Dim tempsets() As Long
#End If
    XPRMarrayhelper_init tempsets, sets
    XPRMgetarrsets mmarray, tempsets
    XPRMarrayhelper_copy tempsets, sets
End Sub

Private Sub XPRMarrayhelper_redim(ByRef newarray As Variant, ByVal lb As Long, ByVal ub As Long)
#If Win64 Then
    ' VBA editor autocorrects "LongPtr" to "Long" here, so use explicit LongLong instead
    ReDim newarray(lb To ub) As LongLong
#Else
    ReDim newarray(lb To ub) As Long
#End If
End Sub

Private Sub XPRMarrayhelper_init(ByRef newarray As Variant, ByRef oldarray As Variant, Optional ByVal copyold = False)
    XPRMarrayhelper_redim newarray, LBound(oldarray), UBound(oldarray)
    If copyold Then XPRMarrayhelper_copy oldarray, newarray
End Sub

Private Sub XPRMarrayhelper_copy(ByRef fromarray As Variant, ByRef toarray As Variant)
    If VarType(fromarray) = VarType(toarray) Then
        toarray = fromarray
        Exit Sub
    End If
        
    Dim i As Long
    For i = LBound(toarray) To UBound(toarray)
        toarray(i) = fromarray(i)
    Next i
End Sub



