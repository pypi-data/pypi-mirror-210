/************************************************************************
  BCL: Xpress Builder Component Library
  =====================================

  File xprb_cpp.h
  ```````````````
  -- C++ header file --

  (c) Copyright Fair Isaac Corporation 2000-2021. All rights reserved.
      rev. Mar. 2011
************************************************************************/

#ifndef _XPRB
#define BCL_CPP
#include "xprb.h"
#include "xprb_private.h"

#ifndef XPRB_NO_TOSTRING
#  include <string>
#endif

/* Compatilibity with BCL 3 */
#define XPRBlinExp XPRBexpr
#define XPRBquadExp XPRBexpr
#define XPRBlinRel XPRBrelation

namespace dashoptimization
{

#ifndef XPRB_NO_TOSTRING
  struct ToStringRAII {
    char *const data;
    ToStringRAII(struct Xbexpr *e) : data(XPRBexpr2str(e, 0)) {}
    ~ToStringRAII() {
      if ( data )
        XPRBfree2str(data);
    }
    std::string toString() const { return std::string(data ? data : ""); }
  };
#endif


class XPRB
{
 private:
  XPRB();
 public:
  static int init() { return XPRBinit(); }
  static int finish() { return XPRBfinish(); }
  static int free() { return XPRBfinish(); }
  static int setMsgLevel(int lev) { return XPRBsetmsglevel(NULL,lev); }
  static int setRealFmt(const char *fmt) { return XPRBsetrealfmt(NULL,fmt); }
  static int setColOrder(int num) { return XPRBsetcolorder(NULL,num); }
  static const char *getVersion() { return XPRBgetversion(); }
  static int getTime() { return XPRBgettime(); }
};

class XPRBvar
{
 private:
  struct Xbvar *varRef;
 public:
  XPRBvar() { varRef=NULL; }
  XPRBvar(struct Xbvar *v) { varRef=v; }

  struct Xbvar *getCRef() const { return varRef; }
  bool isValid() const { return (varRef!=NULL); }
  int print() { return XPRBprintvar(varRef); }

  int setType(int type)
   { return XPRBsetvartype(varRef, type); }
  int setUB(double val)
   { return XPRBsetub(varRef, val); }
  int setLB(double val)
   { return XPRBsetlb(varRef, val); }
  int setLim(double val)
   { return XPRBsetlim(varRef, val); }
  int fix(double val)
   { return XPRBfixvar(varRef, val); }
  int setDir(int type, double val)
   { return XPRBsetvardir(varRef, type, val); }
  int setDir(int type)
   { return XPRBsetvardir(varRef, type, 0); }
  const char *getName() const { return XPRBgetvarname(varRef); }
  int getColNum() const { return XPRBgetcolnum(varRef); }
  int getType() const { return XPRBgetvartype(varRef); }
  double getLB() const
   { double b=0.0; XPRBgetbounds(varRef, &b, NULL); return b; }
  double getUB() const
   { double b=0.0; XPRBgetbounds(varRef, NULL, &b); return b; }
  int getLim(double *val) const { return XPRBgetlim(varRef, val); }
  double getLim() const
   { double val; XPRBgetlim(varRef, &val); return val; }
  double getSol() const { return XPRBgetsol(varRef); }
  double getRCost() const { return XPRBgetrcost(varRef); }
  double getRNG(int rngtype) const { return XPRBgetvarrng(varRef,rngtype); }

#ifndef XPRB_NO_TOSTRING
  inline std::string toString() const;
#endif

  friend class XPRBctr;
};

class XPRBterm
{
 private:
  XPRBterm();
 public:
  struct Xbvar *varRef;
  double coeff;
  XPRBterm(double d, const XPRBvar& v) { varRef=v.getCRef(); coeff=d; }

  XPRBterm& neg() { coeff=-coeff; return *this; }
  static XPRBterm neg(const XPRBterm& l) { return XPRBterm(l).neg(); }

  XPRBterm operator - () const { return neg(*this); }

  XPRBterm &operator*= (double f) { coeff *= f; return *this; }
  XPRBterm &operator/= (double f) { coeff /= f; return *this; }

#ifndef XPRB_NO_TOSTRING
  inline std::string toString() const;
#endif

  friend class XPRBexpr;
};

class XPRBqterm
{
 private:
  XPRBqterm();
 public:
  struct Xbvar *varRef1;
  struct Xbvar *varRef2;
  double coeff;
  XPRBqterm(double d, struct Xbvar *ref1, struct Xbvar *ref2)
    : varRef1(ref1)
    , varRef2(ref2)
    , coeff(d)
    {
    }
  XPRBqterm(double d, const XPRBvar& v1, const XPRBvar& v2)
    : varRef1(v1.getCRef())
    , varRef2(v2.getCRef())
    , coeff(d)
    {
    }

  XPRBqterm& neg() { coeff=-coeff; return *this; }
  static XPRBqterm neg(const XPRBqterm& l) { return XPRBqterm(l).neg(); }

  XPRBqterm operator - () const { return neg(*this); }

  XPRBqterm &operator*= (double f) { coeff *= f; return *this; }
  XPRBqterm &operator/= (double f) { coeff /= f; return *this; }

  friend class XPRBexpr;

#ifndef XPRB_NO_TOSTRING
  inline std::string toString() const;
#endif
};

class XPRBexpr
{
 protected:
  struct Xbexpr *expr;
 public:
  XPRBexpr(double d=0) { expr=XPRBnewexpr(d,NULL,NULL); }
  XPRBexpr(int i) { expr=XPRBnewexpr(i,NULL,NULL); }
  XPRBexpr(double d, const XPRBvar& v) { expr=XPRBnewexpr(d, v.getCRef(),NULL); }
  XPRBexpr(double d, const XPRBvar& v1,const XPRBvar& v2) { expr=XPRBnewexpr(d, v1.getCRef(),v2.getCRef()); }
  XPRBexpr(const XPRBvar& v) { expr=XPRBnewexpr(1, v.getCRef(),NULL); }
  XPRBexpr(struct Xbexpr *l) {expr=l;}
  XPRBexpr(const XPRBterm& t) { expr=XPRBnewexpr(t.coeff, t.varRef,NULL); }
  XPRBexpr(const XPRBterm& t1,const XPRBterm& t2) { expr=XPRBnewexpr(t1.coeff*t2.coeff, t1.varRef,t2.varRef); }
  XPRBexpr(const XPRBqterm& q) : expr(XPRBnewexpr(q.coeff, q.varRef1, q.varRef2)) {}
  XPRBexpr(const XPRBexpr& l) { XPRBdupexpr(&expr,l.expr);}
  ~XPRBexpr() { XPRBdelexpr(expr); }

  void reset() { XPRBclearexpr(expr); }
  double getSol() const { return XPRBevalexpr(expr); }
  XPRBexpr& neg() { XPRBchsexpr(expr); return *this; }
  static XPRBexpr neg(const XPRBexpr& l) { return XPRBexpr(l).neg(); }
  XPRBexpr& add(const XPRBvar& v)
   { XPRBaddexpr_term(expr,v.getCRef(),NULL,1); return *this; }
  XPRBexpr& add(const XPRBterm& t)
   { XPRBaddexpr_term(expr,t.varRef,NULL,t.coeff); return *this; }
  XPRBexpr& add(const XPRBqterm& q)
   { XPRBaddexpr_term(expr,q.varRef1,q.varRef2,q.coeff); return *this; }
  XPRBexpr& add(const XPRBexpr& l)
   { XPRBaddexpr(expr,l.expr); return *this; }
  XPRBexpr& sub(const XPRBvar& v)
   { XPRBaddexpr_term(expr,v.getCRef(),NULL,-1); return *this; }
  XPRBexpr& sub(const XPRBterm& t)
   { XPRBaddexpr_term(expr,t.varRef,NULL,-t.coeff); return *this; }
  XPRBexpr& sub(const XPRBqterm& q)
   { XPRBaddexpr_term(expr,q.varRef1,q.varRef2,-q.coeff); return *this; }
  XPRBexpr& sub(const XPRBexpr& l)
   { XPRBaddexpr(expr,neg(l).expr); return *this; }
  XPRBexpr& setTerm(const XPRBvar& var, double val)
   { XPRBsetexpr_term(expr, var.getCRef(), NULL, val); return *this; }
  XPRBexpr& setTerm(double val, const XPRBvar& var)
   { XPRBsetexpr_term(expr, var.getCRef(), NULL, val); return *this; }
  XPRBexpr& setTerm(double val)
   { XPRBsetexpr_term(expr, NULL, NULL, val); return *this; }
  XPRBexpr& setTerm(const XPRBvar& var1, const XPRBvar& var2, double val)
   { XPRBsetexpr_term(expr, var1.getCRef(), var2.getCRef(), val); return *this; }
  XPRBexpr& setTerm(double val, const XPRBvar& var1, const XPRBvar& var2)
   { XPRBsetexpr_term(expr, var1.getCRef(), var2.getCRef(), val); return *this; }
  XPRBexpr& addTerm(const XPRBvar& var, double val)
   { XPRBaddexpr_term(expr, var.getCRef(), NULL, val); return *this; }
  XPRBexpr& addTerm(double val, const XPRBvar& var)
   { XPRBaddexpr_term(expr, var.getCRef(), NULL, val); return *this; }
  XPRBexpr& addTerm(const XPRBvar& var)
   { XPRBaddexpr_term(expr, var.getCRef(), NULL, 1); return *this; }
  XPRBexpr& addTerm(double val)
   { XPRBaddexpr_term(expr, NULL, NULL, val); return *this; }
  XPRBexpr& addTerm(const XPRBvar& var1, const XPRBvar& var2, double val)
   { XPRBaddexpr_term(expr, var1.getCRef(), var2.getCRef(), val); return *this; }
  XPRBexpr& addTerm(double val, const XPRBvar& var1, const XPRBvar& var2)
   { XPRBaddexpr_term(expr, var1.getCRef(), var2.getCRef(), val); return *this; }
  XPRBexpr& delTerm(const XPRBvar& var)
   { XPRBsetexpr_term(expr, var.getCRef(), NULL,0); return *this; }
  XPRBexpr& delTerm(const XPRBvar& var1, const XPRBvar& var2)
   { XPRBsetexpr_term(expr, var1.getCRef(), var2.getCRef(), 0); return *this; }
  XPRBexpr& mul(double d) { XPRBmulcexpr(expr,d); return *this; }
  XPRBexpr& mul(const XPRBexpr& l)
   {
    if(XPRBmulexpr(expr,l.expr))
    throw("Non-quadratic expression");
    else return *this;
   }

  static XPRBexpr add(const XPRBexpr& l1,const XPRBvar& v)
   { return XPRBexpr(l1).add(v); }
  static XPRBexpr add(const XPRBexpr& l1,const XPRBterm& t)
   { return XPRBexpr(l1).add(t); }
  static XPRBexpr add(const XPRBexpr& l1,const XPRBqterm& q)
   { return XPRBexpr(l1).add(q); }
  static XPRBexpr add(const XPRBexpr& l1,const XPRBexpr& l2)
   { return XPRBexpr(l1).add(l2); }
  static XPRBexpr mul(const XPRBexpr& l,double d) { return XPRBexpr(l).mul(d);}
  static XPRBexpr mul(double d,const XPRBexpr& l) { return mul(l,d);}
  static XPRBexpr mul(const XPRBexpr& l1,const XPRBexpr& l2)
   { return XPRBexpr(l1).mul(l2); }

  XPRBexpr& assign(const XPRBexpr& l)
   { XPRBassignexpr(expr,l.expr); return *this;}
  int print() const { return XPRBprintexpr(NULL,expr,0,0); }

  XPRBexpr operator - () const { return neg(*this); }
  XPRBexpr& operator += (const XPRBvar& v) { return add(v); }
  XPRBexpr& operator += (const XPRBterm& t) { return add(t); }
  XPRBexpr& operator += (const XPRBqterm& q) { return add(q); }
  XPRBexpr& operator += (const XPRBexpr& l) { return add(l); }
  XPRBexpr& operator -= (const XPRBvar& v)
   { XPRBaddexpr_term(expr,v.getCRef(),NULL,-1); return *this; }
  XPRBexpr& operator -= (const XPRBterm& t)
   { XPRBaddexpr_term(expr,t.varRef,NULL,-t.coeff); return *this; }
  XPRBexpr& operator -= (const XPRBqterm& q)
   { XPRBaddexpr_term(expr,q.varRef1,q.varRef2,-q.coeff); return *this; }
  XPRBexpr& operator -= (const XPRBexpr& l) { return add(neg(l)); }
  XPRBexpr& operator = (const XPRBexpr& l) { return assign(l); }

#ifndef XPRB_NO_TOSTRING
  inline std::string toString() const;
#endif

  friend class XPRBcut;
  friend class XPRBctr;
  friend class XPRBprob;
  friend class XPRBsos;
};

inline XPRBexpr operator + (const XPRBexpr& l1, const XPRBexpr& l2)
 { return XPRBexpr::add(l1,l2); }
inline XPRBexpr operator - (const XPRBexpr& l1, const XPRBexpr& l2)
 { return XPRBexpr::add(l1,XPRBexpr::neg(l2)); }
inline XPRBexpr operator * (const XPRBexpr& l, double d)
 { return XPRBexpr::mul(l,d); }
inline XPRBexpr operator * (double d, const XPRBexpr& l)
 { return XPRBexpr::mul(l,d); }
inline XPRBexpr operator + (const XPRBvar& v1, const XPRBvar& v2)
 { return XPRBexpr::add(v1,v2); }
inline XPRBexpr operator + (double t1, const XPRBvar& t2)
 { return XPRBexpr::add(t1,t2); }
inline XPRBexpr operator + (const XPRBvar& t1, double t2)
 { return XPRBexpr::add(t1,t2); }
inline XPRBexpr operator - (double t1, const XPRBvar& t2)
 { return XPRBexpr(t1).addTerm(t2,-1); }
inline XPRBexpr operator - (const XPRBvar& t1, double t2)
 { return XPRBexpr(-t2).add(t1); }
inline XPRBexpr operator - (const XPRBvar& v1, const XPRBvar& v2)
 { return XPRBexpr::add(v1,XPRBexpr::neg(v2)); }

inline XPRBexpr operator + (const XPRBvar& v1, const XPRBterm& t)
 { return XPRBexpr(v1).add(t); }
inline XPRBexpr operator - (const XPRBvar& v1, const XPRBterm& t)
 { return XPRBexpr(v1).sub(t); }
inline XPRBexpr operator + (const XPRBterm& t,const XPRBvar& v1)
 { return XPRBexpr(v1).add(t); }
inline XPRBexpr operator - (const XPRBterm& t,const XPRBvar& v1)
 { return XPRBexpr(t).sub(v1); }
inline XPRBterm operator * (double d, const XPRBvar& v)
 { return XPRBterm(d,v); }
inline XPRBterm operator * (const XPRBvar& v, double d)
 { return XPRBterm(d,v); }
inline XPRBterm operator - (const XPRBvar& v)
 { return XPRBterm(-1,v); }
inline XPRBexpr operator + (const XPRBterm& t1, const XPRBterm& t2)
 { return XPRBexpr(t1).add(t2); }
inline XPRBexpr operator - (const XPRBterm& t1, const XPRBterm& t2)
{ return XPRBexpr(t1).sub(t2); }

inline XPRBexpr operator + (double const &d, XPRBqterm const &q)
 { return XPRBexpr(d).add(q); }
inline XPRBexpr operator + (XPRBqterm const &q, double const &d)
 { return XPRBexpr(q).add(d); }
inline XPRBexpr operator + (XPRBvar const &v, XPRBqterm const &q)
 { return XPRBexpr(v).add(q); }
inline XPRBexpr operator + (XPRBqterm const &q, XPRBvar const &v)
 { return XPRBexpr(q).add(v); }
inline XPRBexpr operator + (XPRBterm const &t, XPRBqterm const &q)
 { return XPRBexpr(t).add(q); }
inline XPRBexpr operator + (XPRBqterm const &q1, XPRBqterm const &q2)
 { return XPRBexpr(q1).add(q2); }
inline XPRBexpr operator + (XPRBqterm const &q, XPRBterm const &t)
 { return XPRBexpr(q).add(t); }
inline XPRBexpr operator + (XPRBexpr const &e, XPRBqterm const &q)
 { return XPRBexpr(e).add(q); }
inline XPRBexpr operator + (XPRBqterm const &q, XPRBexpr const &e)
 { return XPRBexpr(q).add(e); }
inline XPRBexpr operator - (double const &d, XPRBqterm const &q)
 { return XPRBexpr(d).sub(q); }
inline XPRBexpr operator - (XPRBqterm const &q, double const &d)
 { return XPRBexpr(q).sub(d); }
inline XPRBexpr operator - (XPRBvar const &v, XPRBqterm const &q)
 { return XPRBexpr(v).sub(q); }
inline XPRBexpr operator - (XPRBqterm const &q, XPRBvar const &v)
 { return XPRBexpr(q).sub(v); }
inline XPRBexpr operator - (XPRBterm const &t, XPRBqterm const &q)
 { return XPRBexpr(t).sub(q); }
inline XPRBexpr operator - (XPRBqterm const &q, XPRBterm const &t)
 { return XPRBexpr(q).sub(t); }
inline XPRBexpr operator - (XPRBexpr const &e, XPRBqterm const &q)
 { return XPRBexpr(e).sub(q); }
inline XPRBexpr operator - (XPRBqterm const &q, XPRBexpr const &e)
 { return XPRBexpr(q).sub(e); }
inline XPRBexpr operator - (XPRBqterm const &q1, XPRBqterm const &q2)
 { return XPRBexpr(q1).sub(q2); }
inline XPRBqterm operator * (double const &d, XPRBqterm const &q)
 { return XPRBqterm(d * q.coeff, q.varRef1, q.varRef2); }
inline XPRBqterm operator * (XPRBqterm const &q, double const &d)
 { return XPRBqterm(d * q.coeff, q.varRef1, q.varRef2); }
inline XPRBterm operator / (XPRBvar const &v, double const &d)
 { return XPRBterm(1.0/d, v); }
inline XPRBqterm operator / (XPRBqterm const &q, double const &d)
 { return XPRBqterm(q.coeff / d, q.varRef1, q.varRef2); }
inline XPRBterm operator / (XPRBterm const &t, double const &d)
 { return XPRBterm(t.coeff / d, t.varRef); }
inline XPRBexpr operator / (XPRBexpr const &e, double const &d)
{ return e * (1.0 / d); }

#ifdef XPRB_LEGACY_OPERATORS
inline XPRBexpr operator * (const XPRBvar& v1, const XPRBvar& v2)
 { return XPRBexpr(1,v1,v2); }
#else
inline XPRBqterm operator * (const XPRBvar& v1, const XPRBvar& v2)
 { return XPRBqterm(1,v1,v2); }
inline XPRBqterm operator * (const XPRBterm& t, const XPRBvar& v)
 { return XPRBqterm(t.coeff,t.varRef,v.getCRef()); }
inline XPRBqterm operator * (const XPRBvar& v, const XPRBterm& t)
 { return XPRBqterm(t.coeff,t.varRef,v.getCRef()); }
#endif

inline XPRBexpr operator * (const XPRBexpr& l, const XPRBvar& v)
 { return XPRBexpr(l).mul(XPRBexpr(v)); }
inline XPRBexpr operator * (const XPRBvar& v, const XPRBexpr& l)
 { return XPRBexpr(l).mul(XPRBexpr(v)); }

inline XPRBexpr operator * (const XPRBexpr& q1, const XPRBexpr& q2)
 { return XPRBexpr(q1).mul(q2); }

inline XPRBexpr sqr(const XPRBexpr& l) { return XPRBexpr(l).mul(l); }
inline XPRBqterm sqr(const XPRBterm& t) { return XPRBqterm(t.coeff*t.coeff,t.varRef,t.varRef); }
inline XPRBexpr sqr(const XPRBqterm& q) { return XPRBexpr(q).mul(q); }
inline XPRBqterm sqr(const XPRBvar& v) { return XPRBqterm(1,v,v); }
inline double sqr(double r) { return r*r; }
inline int sqr(int i) { return i*i; }

class XPRBrelation: public XPRBexpr
{
 private:
  int qrtype;
 public:
  XPRBrelation(const XPRBexpr& l,int t=XB_N):XPRBexpr(l) {qrtype=t;}
  XPRBrelation(const XPRBvar& v):XPRBexpr(v) {qrtype=XB_N;}
  friend class XPRBctr;
  friend class XPRBcut;
  int getType() const { return qrtype; }
  int print() { return XPRBprintexpr(NULL,expr,qrtype,0); }
};

inline XPRBrelation operator <= (const XPRBexpr& l1, const XPRBexpr& l2)
 { return XPRBrelation(l1-l2,XB_L); }
inline XPRBrelation operator >= (const XPRBexpr& l1, const XPRBexpr& l2)
 { return XPRBrelation(l1-l2,XB_G); }
inline XPRBrelation operator == (const XPRBexpr& l1, const XPRBexpr& l2)
 { return XPRBrelation(l1-l2,XB_E); }

class XPRBctr
{
 protected:
  struct Xbctr *ctrRef;
 public:
  XPRBctr() { ctrRef=NULL; }
  XPRBctr(struct Xbctr *c) { ctrRef=c; }
  XPRBctr(struct Xbctr *c, const XPRBrelation& ctr)
  { ctrRef=c; assign(ctr); }
  struct Xbctr *getCRef() const { return ctrRef; }
  bool isValid() const { return (ctrRef!=NULL); }

  void assign(const XPRBrelation& ctr)
  { XPRBsetctr(ctrRef, ctr.expr, ctr.qrtype); }
  void reset() { ctrRef=NULL; }
  int print() { return XPRBprintctr(ctrRef); }

  int setType(int type)
   { return XPRBsetctrtype(ctrRef, type); }
  int setRange(double low, double up)
   { return XPRBsetrange(ctrRef, low, up); }
  int setModCut(bool m) { return XPRBsetmodcut(ctrRef, m?1:0); }
  bool isModCut() { return (XPRBgetmodcut(ctrRef)!=0); }
  int setIncludeVars(bool m) { return XPRBsetincvars(ctrRef, m ? 1 : 0); }
  bool isIncludeVars() { return (XPRBgetincvars(ctrRef) != 0); }
  int setDelayed(bool d) { return XPRBsetdelayed(ctrRef, d?1:0); }
  bool isDelayed() { return (XPRBgetdelayed(ctrRef)!=0); }
  int setIndicator(int dir, const XPRBvar& var)
   { return XPRBsetindicator(ctrRef, dir, var.getCRef()); }
  int setIndicator(const XPRBvar& var, int dir)
   { return XPRBsetindicator(ctrRef, dir, var.getCRef()); }
  int setIndicator(int dir)
   { return XPRBsetindicator(ctrRef, dir, NULL); }
  bool isIndicator() { return (XPRBgetindicator(ctrRef)!=0); }
  int getIndicator() { return XPRBgetindicator(ctrRef); }
  XPRBvar getIndVar() { return XPRBvar((struct Xbvar *)XPRBgetindvar(ctrRef)); }
  const char *getName() const { return XPRBgetctrname(ctrRef); }
  int getRange(double *lw, double *up) const
   { return XPRBgetrange(ctrRef, lw, up); }
  double getRangeL() const
   {
    double lw;
    XPRBgetrange(ctrRef, &lw, NULL);
    return lw;
   }
  double getRangeU() const
   {
    double up;
    XPRBgetrange(ctrRef, NULL, &up);
    return up;
   }
  double getRHS() const { return XPRBgetrhs(ctrRef); }
  int getRowNum() const { return XPRBgetrownum(ctrRef); }
  int getType() const { return XPRBgetctrtype(ctrRef); }
  double getSlack() const { return XPRBgetslack(ctrRef); }
  double getAct() const { return XPRBgetact(ctrRef); }
  double getDual() const { return XPRBgetdual(ctrRef); }
  double getRNG(int rngtype) const { return XPRBgetctrrng(ctrRef,rngtype); }
  double getCoefficient(const XPRBvar& var)
   { return XPRBgetcoeff(ctrRef, var.getCRef()); }
  double getCoefficient(const XPRBvar& var1, const XPRBvar& var2)
   { return XPRBgetqcoeff(ctrRef, var1.getCRef(), var2.getCRef()); }
  int setTerm(const XPRBvar& var, double val)
   { return XPRBsetterm(ctrRef, var.getCRef(), val); }
  int setTerm(double val, const XPRBvar& var)
   { return XPRBsetterm(ctrRef, var.getCRef(), val); }
  int setTerm(const XPRBvar& var)
   { return XPRBsetterm(ctrRef, var.getCRef(), 1); }
  int setTerm(double val)
   { return XPRBsetterm(ctrRef, NULL, val); }
  int setTerm(double val, const XPRBvar& var1, const XPRBvar& var2)
   { return XPRBsetqterm(ctrRef, var1.getCRef(), var2.getCRef(), val); }
  int setTerm(const XPRBvar& var1, const XPRBvar& var2, double val)
   { return XPRBsetqterm(ctrRef, var1.getCRef(), var2.getCRef(), val); }
  int addTerm(const XPRBvar& var, double val)
   { return XPRBaddterm(ctrRef, var.getCRef(), val); }
  int addTerm(double val, const XPRBvar& var)
   { return XPRBaddterm(ctrRef, var.getCRef(), val); }
  int addTerm(const XPRBvar& var)
   { return XPRBaddterm(ctrRef, var.getCRef(), 1); }
  int addTerm(double val)
   { return XPRBaddterm(ctrRef, NULL, val); }
  int addTerm(double val, const XPRBvar& var1, const XPRBvar& var2)
   { return XPRBaddqterm(ctrRef, var1.getCRef(), var2.getCRef(), val); }
  int addTerm(const XPRBvar& var1, const XPRBvar& var2, double val)
   { return XPRBaddqterm(ctrRef, var1.getCRef(), var2.getCRef(), val); }
  int addTerm(const XPRBvar& var1, const XPRBvar& var2)
   { return XPRBaddqterm(ctrRef, var1.getCRef(), var2.getCRef(), 1); }
  int delTerm(const XPRBvar& var)
   { return XPRBdelterm(ctrRef, var.getCRef()); }
  int delTerm(const XPRBvar& var1, const XPRBvar& var2)
   { return XPRBdelqterm(ctrRef, var1.getCRef(), var2.getCRef()); }
  int getSize() { return XPRBgetctrsize(ctrRef); }
  int add(const XPRBexpr& l)
   { return XPRBappctr(ctrRef, l.expr); }

  const void *nextTerm(const void *ref, XPRBvar &v, double *coeff) { return XPRBgetnextterm(ctrRef, ref, &v.varRef, coeff); }
  const void *nextTerm(const void *ref, XPRBvar &v1, XPRBvar &v2, double *coeff) { return XPRBgetnextqterm(ctrRef, ref, &v1.varRef, &v2.varRef, coeff); }

  XPRBctr &operator = ( const XPRBrelation& ctr)
    { assign(ctr); return *this; }
  XPRBctr &operator += ( const XPRBexpr& l)
    { add(l); return *this; }
  XPRBctr &operator -= ( const XPRBexpr& l)
    { add(XPRBexpr::neg(l)); return *this; }

  friend class XPRBprob;
};

class XPRBcut
{
 private:
  struct Xbcut *cutRef;
 public:
  XPRBcut() { cutRef=NULL; }
  XPRBcut(struct Xbcut *c) { cutRef=c; }
  XPRBcut(struct Xbcut *c, const XPRBrelation& cut)
  { cutRef=c; assign(cut); }
  struct Xbcut *getCRef() const { return cutRef; }
  bool isValid() const { return (cutRef!=NULL); }

  int assign(const XPRBrelation& cut)
  { return XPRBsetcut(cutRef, cut.expr, cut.qrtype); }
  void reset() { cutRef=NULL; }
  int print() { return XPRBprintcut(cutRef); }

  double getRHS() const { return XPRBgetcutrhs(cutRef); }
  int setType(int type)
   { return XPRBsetcuttype(cutRef, type); }
  int getType() const { return XPRBgetcuttype(cutRef); }
  int setID(int type)
   { return XPRBsetcutid(cutRef, type); }
  int getID() const { return XPRBgetcutid(cutRef); }
  int setTerm(const XPRBvar& var, double val)
   { return XPRBsetcutterm(cutRef, var.getCRef(), val); }
  int setTerm(double val, const XPRBvar& var)
   { return XPRBsetcutterm(cutRef, var.getCRef(), val); }
  int setTerm(const XPRBvar& var)
   { return XPRBsetcutterm(cutRef, var.getCRef(), 1); }
  int setTerm(double val)
   { return XPRBsetcutterm(cutRef, NULL, val); }
  int addTerm(const XPRBvar& var, double val)
   { return XPRBaddcutterm(cutRef, var.getCRef(), val); }
  int addTerm(double val, const XPRBvar& var)
   { return XPRBaddcutterm(cutRef, var.getCRef(), val); }
  int addTerm(const XPRBvar& var)
   { return XPRBaddcutterm(cutRef, var.getCRef(), 1); }
  int addTerm(double val)
   { return XPRBaddcutterm(cutRef, NULL, val); }
  int delTerm(const XPRBvar& var)
   { return XPRBdelcutterm(cutRef, var.getCRef()); }
  int add(const XPRBexpr& l)
   { return XPRBappcut(cutRef, l.expr); }

  XPRBcut &operator = ( const XPRBrelation& cut)
    { assign(cut); return *this;}
  XPRBcut &operator += ( const XPRBexpr& l)
    { add(l); return *this; }
  XPRBcut &operator -= ( const XPRBexpr& l)
    { add(XPRBexpr::neg(l)); return *this; }
};

class XPRBsos
{
 private:
  struct Xbsos *sosRef;
 public:
  XPRBsos() { sosRef=NULL; }
  XPRBsos(struct Xbsos *s) { sosRef=s; }
  XPRBsos(struct Xbsos *s, const XPRBexpr& l)
  { sosRef=s; assign(l); }

  int assign(const XPRBexpr& l)
   { return XPRBsetsos(sosRef, l.expr); }
  struct Xbsos *getCRef() const { return sosRef; }
  bool isValid() const { return (sosRef!=NULL); }
  void reset() { sosRef=NULL; }
  int print() { return XPRBprintsos(sosRef); }

  const char *getName() const { return XPRBgetsosname(sosRef); }
  int getType() const { return XPRBgetsostype(sosRef); }
  int setDir(int type, double val)
   { return XPRBsetsosdir(sosRef, type, val); }
  int setDir(int type)
   { return XPRBsetsosdir(sosRef, type, 0); }
  int addElement(XPRBvar& var, double val)
   { return XPRBaddsosel(sosRef, var.getCRef(), val); }
  int addElement(double val, XPRBvar& var)
   { return XPRBaddsosel(sosRef, var.getCRef(), val); }
  int delElement(XPRBvar& var)
   { return XPRBdelsosel(sosRef, var.getCRef()); }
  int add(const XPRBexpr& l)
   { return XPRBappsos(sosRef, l.expr); }

  XPRBsos &operator = ( const XPRBexpr& l) { assign(l); return *this; }
  XPRBsos &operator += ( const XPRBexpr& l) { add(l); return *this; }
};

class XPRBindexSet
{
 private:
  struct Xbidxset *idxRef;
 public:
  XPRBindexSet() {idxRef=NULL; }
  XPRBindexSet(struct Xbidxset *i) { idxRef=i; }
  struct Xbidxset *getCRef() const { return idxRef; }
  bool isValid() const { return (idxRef!=NULL); }
  void reset() { idxRef=NULL; }
  int print() const { return XPRBprintidxset(idxRef); }

  const char *getName() const { return XPRBgetidxsetname(idxRef); }
  int getSize() const { return XPRBgetidxsetsize(idxRef); }

  int addElement(const char *text)
   { return XPRBaddidxel(idxRef, text);}
  int getIndex(const char *text) const
   { return XPRBgetidxel(idxRef, text); }
  const char *getIndexName(int i) const
   { return XPRBgetidxelname(idxRef, i); }

  int operator += ( const char *text)
  { return addElement(text); }
  int operator[] (const char *text) const
  { return getIndex(text); }
  const char * operator[] (int i) const
  { return getIndexName(i); }
};

class XPRBbasis
{
 private:
  struct Xbbasis *basRef;
 public:
  XPRBbasis() { basRef=NULL; }
  XPRBbasis(struct Xbbasis *b) { basRef=b; }
  XPRBbasis(const XPRBbasis& b)
   { //if(basRef!=NULL) XPRBdelbasis(basRef); //Windows-problem?
     basRef=b.basRef; }
  struct Xbbasis *getCRef() const { return basRef; }
  bool isValid() const { return (basRef!=NULL); }
  void reset() { if(basRef!=NULL) XPRBdelbasis(basRef);
                 basRef=NULL; }
};

class XPRBsol
{
private:
  struct Xbsol *solRef;
  public:
  XPRBsol() { solRef = NULL; }
  XPRBsol(struct Xbsol *s) { solRef = s; }
  struct Xbsol *getCRef() const { return solRef; }
  bool isValid() const { return (solRef != NULL); }
  int print() { return XPRBprintsol(solRef); }
  int delVar(const XPRBvar& var) { return XPRBdelsolvar(solRef, var.getCRef()); }
  int setVar(const XPRBvar& var, double val) { return XPRBsetsolvar(solRef, var.getCRef(), val); }
  int getVar(const XPRBvar& var, double *val) { return XPRBgetsolvar(solRef, var.getCRef(), val); }
  int getSize() { return XPRBgetsolsize(solRef); }
  void reset() { if( solRef ) { XPRBdelsol( solRef ); solRef = NULL; } }
};

class XPRBprob
{
 private:
  struct Xbprob *prob_ref;
  void operator = (const struct Xbprob&);
  XPRBprob& operator=(const XPRBprob&);
  XPRBprob(const XPRBprob&);
 public:
  XPRBprob(const char *name=NULL) { prob_ref=XPRBnewprob(name); }
  ~XPRBprob() { XPRBdelprob(prob_ref); }
  struct Xbprob *getCRef() const { return prob_ref; }
  bool isValid() const { return (prob_ref!=NULL); }
  int reset() { return XPRBresetprob(prob_ref); }
  int print() { return XPRBprintprob(prob_ref); }
  int printObj() { return XPRBprintobj(prob_ref); }
  int setDictionarySize(int dict,int size)
   { return XPRBsetdictionarysize(prob_ref,dict,size); }
  int setMsgLevel(int lev) { return XPRBsetmsglevel(prob_ref,lev); }
  int setRealFmt(const char *fmt) { return XPRBsetrealfmt(prob_ref,fmt); }
  int setColOrder(int num) { return XPRBsetcolorder(prob_ref,num); }
  struct xo_prob_struct * getXPRSprob() { return XPRBgetXPRSprob(prob_ref); }

  XPRBvar newVar(const char *name=NULL,int type=XB_PL, double lob=0, double upb=XB_INFINITY)
   { return XPRBvar(XPRBnewvar(prob_ref,type,name,lob,upb)); }

  XPRBctr newCtr(const char *name,const XPRBrelation& ac)
   { return XPRBctr(XPRBnewctr(prob_ref,name,XB_N),ac); }
  XPRBctr newCtr(const char *name=NULL)
   { return XPRBctr(XPRBnewctr(prob_ref,name,XB_N)); }
  XPRBctr newCtr(const XPRBrelation& ac)
   { return XPRBctr(XPRBnewctr(prob_ref,NULL,XB_N),ac); }
  void delCtr(XPRBctr& ctr) { XPRBdelctr(ctr.getCRef()); ctr.reset(); }
  bool nextCtr(XPRBctr& ctr) { return (ctr.ctrRef = XPRBgetnextctr(prob_ref, ctr.ctrRef)) != 0; }

  int setObj(double val) { return XPRBsetobjexpr(prob_ref, XPRBexpr(val).expr); }
  int setObj(XPRBctr ctr) { return XPRBsetobj(prob_ref, ctr.getCRef()); }
  int setObj(const XPRBexpr& q)
   { return XPRBsetobjexpr(prob_ref, q.expr); }

  XPRBsos newSos(int type)
   { return XPRBsos(XPRBnewsos(prob_ref,NULL,type)); }
  XPRBsos newSos(const char *name=NULL, int type=XB_S1)
   { return XPRBsos(XPRBnewsos(prob_ref,name,type)); }
  XPRBsos newSos(int type, const XPRBexpr& le)
   { return XPRBsos(XPRBnewsos(prob_ref,NULL,type), le); }
  XPRBsos newSos(const char *name, int type, const XPRBexpr& le)
   { return XPRBsos(XPRBnewsos(prob_ref,name,type), le); }
  void delSos(XPRBsos& sos) { XPRBdelsos(sos.getCRef()); sos.reset(); }

  XPRBindexSet newIndexSet(const char *name=NULL,int maxsize=0)
   { return XPRBindexSet(XPRBnewidxset(prob_ref,name,maxsize)); }

  XPRBbasis saveBasis() { return XPRBbasis(XPRBsavebasis(prob_ref)); }
  int loadBasis(const XPRBbasis& b) { return XPRBloadbasis(b.getCRef()); }

  XPRBsol newSol() { return XPRBsol(XPRBnewsol(prob_ref)); }

  void clearDir() { XPRBcleardir(prob_ref); }
  int setSense(int dir) { return XPRBsetsense(prob_ref,dir); }
  int getSense() const { return XPRBgetsense(prob_ref); }
  const char *getName() { return XPRBgetprobname(prob_ref); }
  int exportProb(int format=XB_LP, const char *filename=NULL)
  { return XPRBexportprob(prob_ref, format, filename); }
  int writeDir(const char *filename=NULL)
  { return XPRBwritedir(prob_ref, filename); }
  int loadMat() { return XPRBloadmat(prob_ref); }

  int lpOptimize(const char *alg="") { return XPRBlpoptimize(prob_ref, alg); }
  int lpOptimise(const char *alg="") { return XPRBlpoptimize(prob_ref, alg); }
  int mipOptimize(const char *alg="") { return XPRBmipoptimize(prob_ref, alg); }
  int mipOptimise(const char *alg="") { return XPRBmipoptimize(prob_ref, alg); }
  int solve(const char *alg="") { return XPRBsolve(prob_ref, alg); }
  int minim(const char *alg="") { return XPRBminim(prob_ref, alg); }
  int maxim(const char *alg="") { return XPRBmaxim(prob_ref, alg); }
  int loadMIPSol(double *sol, int ncol, bool ifopt)
   { return XPRBloadmipsol(prob_ref, sol, ncol, ifopt?1:0); }
  int loadMIPSol(double *sol, int ncol)
   { return XPRBloadmipsol(prob_ref, sol, ncol, 0); }
  int addMIPSol(XPRBsol& sol, const char *name = 0) { return XPRBaddmipsol(prob_ref, sol.getCRef(), name); }
  int fixMIPEntities(int ifround = 1) { return XPRBfixmipentities(prob_ref, ifround); }
  int setName(const char *name) { return XPRBsetprobname(prob_ref, name); }
  int getProbStat() { return XPRBgetprobstat(prob_ref); }
  int getLPStat() { return XPRBgetlpstat(prob_ref); }
  int getMIPStat() { return XPRBgetmipstat(prob_ref); }
  int sync(int synctype) { return XPRBsync(prob_ref, synctype); }
  int beginCB(struct xo_prob_struct *optprob)
  { return XPRBbegincb(prob_ref, optprob); }
  int endCB() { return XPRBendcb(prob_ref); }
  double getObjVal() { return XPRBgetobjval(prob_ref); }
  int getNumIIS() { return XPRBgetnumiis(prob_ref); }

  XPRBvar getVarByName(const char *name)
  { return XPRBvar((struct Xbvar *)XPRBgetbyname(prob_ref, name, XB_VAR)); }
  XPRBctr getCtrByName(const char *name)
  { return XPRBctr((struct Xbctr *)XPRBgetbyname(prob_ref, name, XB_CTR)); }
  XPRBsos getSosByName(const char *name)
  { return XPRBsos((struct Xbsos *)XPRBgetbyname(prob_ref, name, XB_SOS)); }
  XPRBindexSet getIndexSetByName(const char *name)
  { return XPRBindexSet((struct Xbidxset *)XPRBgetbyname(prob_ref, name,
  XB_IDX)); }

  XPRBcut newCut(int id=0)
   { return XPRBcut(XPRBnewcut(prob_ref,XB_E,id)); }
  XPRBcut newCut(const XPRBrelation& ac, int id=0)
   { return XPRBcut(XPRBnewcut(prob_ref,ac.getType(),id),ac); }
  void delCut(XPRBcut& cut) { XPRBdelcut(cut.getCRef()); cut.reset(); }
  int setCutMode(int mode) { return XPRBsetcutmode(prob_ref, mode); }
  int addCuts(XPRBcut *cuts, int num)
  { struct Xbcut **ccuts=new struct Xbcut*[num];
    int rts;
    for(int i=0;i<num;i++) ccuts[i]=cuts[i].getCRef();
    rts=XPRBaddcuts(prob_ref, ccuts, num);
    delete []ccuts;
    return rts;}

  int writeSol(const char *filename = NULL, const char *flags = "") { return XPRBwritesol(prob_ref, filename, flags); }
  int writePrtSol(const char *filename = NULL, const char *flags = "") { return XPRBwriteprtsol(prob_ref, filename, flags); }
  int writeBinSol(const char *filename = NULL, const char *flags = "") { return XPRBwritebinsol(prob_ref, filename, flags); }
  int writeSlxSol(const char *filename = NULL, const char *flags = "") { return XPRBwriteslxsol(prob_ref, filename, flags); }
  int readBinSol(const char *filename = NULL, const char *flags = "") { return XPRBreadbinsol(prob_ref, filename, flags); }
  int readSlxSol(const char *filename = NULL, const char *flags = "") { return XPRBreadslxsol(prob_ref, filename, flags); }

};

#ifndef XPRB_NO_TOSTRING
inline std::string XPRBvar::toString() const {
  return XPRBexpr(*this).toString();
}
inline std::string XPRBterm::toString() const {
  return XPRBexpr(*this).toString();
}
inline std::string XPRBqterm::toString() const {
  return XPRBexpr(*this).toString();
}
inline std::string XPRBexpr::toString() const {
  if ( !expr ) return "";
  return ToStringRAII(expr).toString();
}
#endif

} // end namespace dashoptimization
#endif
