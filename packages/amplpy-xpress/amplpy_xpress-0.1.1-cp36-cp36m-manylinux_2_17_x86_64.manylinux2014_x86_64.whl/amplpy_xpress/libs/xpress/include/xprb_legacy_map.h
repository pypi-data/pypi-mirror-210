/* * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                 */
/* Copyright (C) 2018-2021 Fair Isaac Corporation  */
/*                            All rights reserved  */
/*                                                 */
/* * * * * * * * * * * * * * * * * * * * * * * * * */

XB_EXTERN void* (*xbsl_malloc)(size_t size);
XB_EXTERN void (*xbsl_free)(void *ptr);
XB_EXTERN void* (*xbsl_realloc)(void *ptr, size_t size);

#define xbslinit XPRBinit
#define xbslfinish XPRBfinish

#define xbgetversion XPRBgetversion
#define xbgettime XPRBgettime

#define xbseterrctrl XPRBseterrctrl
#define xbdefcberr_prob XPRBdefcberr

#define xbnewprob XPRBnewprob
#define xbgetsprob_prob XPRBgetXPRSprob

#define xbnewname XPRBnewname

#define xbdefcbmsg_prob XPRBdefcbmsg
#define xbsetmsglevel_prob XPRBsetmsglevel
#define xbsetrealfmt_prob XPRBsetrealfmt
#define xbsetdecsign XPRBsetdecsign
#define xbprintf_prob XPRBprintf

#define xbreadlinecb XPRBreadlinecb
#define xbreadarrlinecb XPRBreadarrlinecb
#define xbreadline XPRBreadline
#define xbreadarrline XPRBreadarrline

#define xbdelprob_prob XPRBdelprob
#define xbresetprob_prob XPRBresetprob
#define xbsetprobname_prob XPRBsetprobname

#define xbnewvar_prob XPRBnewvar
#define xbsetvartype XPRBsetvartype

#define xbnewarrvar_prob XPRBnewarrvar
#define xbstartarrvar_prob XPRBstartarrvar
#define xbsetarrvarel XPRBsetarrvarel
#define xbapparrvarel XPRBapparrvarel
#define xbendarrvar XPRBendarrvar
#define xbdelarrvar XPRBdelarrvar

#define xbnewctr_prob XPRBnewctr
#define xbgetnextctr_prob XPRBgetnextctr
#define xbdelctr XPRBdelctr
#define xbaddterm XPRBaddterm
#define xbdelterm XPRBdelterm
#define xbsetterm XPRBsetterm
#define xbgetcoeff XPRBgetcoeff
#define xbaddqterm XPRBaddqterm
#define xbdelqterm XPRBdelqterm
#define xbsetqterm XPRBsetqterm
#define xbgetqcoeff XPRBgetqcoeff
#define xbgetnextterm XPRBgetnextterm
#define xbgetnextqterm XPRBgetnextqterm
#define xbaddarrterm XPRBaddarrterm
#define xbnewsum_prob XPRBnewsum
#define xbnewsumc_prob XPRBnewsumc
#define xbnewarrsum_prob XPRBnewarrsum
#define xbnewprec_prob XPRBnewprec
#define xbsetctrtype XPRBsetctrtype
#define xbsetrange XPRBsetrange
#define xbsetincvars XPRBsetincvars
#define xbsetmodcut XPRBsetmodcut
#define xbsetdelayed XPRBsetdelayed
#define xbsetindicator XPRBsetindicator

#define xbnewsos_prob XPRBnewsos
#define xbdelsos XPRBdelsos
#define xbaddsosel XPRBaddsosel
#define xbdelsosel XPRBdelsosel
#define xbaddsosarrel XPRBaddsosarrel
#define xbnewsosrc_prob XPRBnewsosrc
#define xbnewsosw_prob XPRBnewsosw

#define xbsetsense_prob XPRBsetsense
#define xbgetsense_prob XPRBgetsense
#define xbsetobj_prob XPRBsetobj

#define xbsetub XPRBsetub
#define xbsetlb XPRBsetlb
#define xbfixvar XPRBfixvar
#define xbsetlim XPRBsetlim

#define xbgetbyname_prob XPRBgetbyname
#define xbsetdictsize_prob XPRBsetdictionarysize

#define xbsetvardir XPRBsetvardir
#define xbsetsosdir XPRBsetsosdir
#define xbcleardir_prob XPRBcleardir

#define xbnewidxset_prob XPRBnewidxset
#define xbaddidxel XPRBaddidxel
#define xbgetidxel XPRBgetidxel
#define xbgetidxelname XPRBgetidxelname
#define xbgetidxsetname XPRBgetidxsetname
#define xbgetidxsetsize XPRBgetidxsetsize

#define xbprintprob_prob XPRBprintprob
#define xbprintobj_prob XPRBprintobj
#define xbexportprob_prob XPRBexportprob
#define xbwritedir_prob XPRBwritedir
#define xbloadmat_prob XPRBloadmat

#define xbprintvar XPRBprintvar
#define xbprintarrvar XPRBprintarrvar
#define xbprintctr XPRBprintctr
#define xbprintsos XPRBprintsos
#define xbprintidxset XPRBprintidxset

#define xbgetprobname_prob XPRBgetprobname
#define xbgetvarname XPRBgetvarname
#define xbgetctrname XPRBgetctrname
#define xbgetarrvarname XPRBgetarrvarname
#define xbgetsosname XPRBgetsosname
#define xbgetcolnum XPRBgetcolnum
#define xbgetrownum XPRBgetrownum
#define xbgetarrvarsize XPRBgetarrvarsize
#define xbgetvartype XPRBgetvartype
#define xbgetctrtype XPRBgetctrtype
#define xbgetctrsize XPRBgetctrsize
#define xbgetsostype XPRBgetsostype
#define xbgetrhs XPRBgetrhs
#define xbgetmodcut XPRBgetmodcut
#define xbgetdelayed XPRBgetdelayed
#define xbgetincvars XPRBgetincvars
#define xbgetindicator XPRBgetindicator
#define xbgetindvar XPRBgetindvar
#define xbgetbounds XPRBgetbounds
#define xbgetlim       XPRBgetlim
#define xbgetctrrng  XPRBgetctrrng
#define xbgetvarrng  XPRBgetvarrng
#define xbgetnumiis_prob XPRBgetnumiis
#define xbgetiis_prob XPRBgetiis
#define xbgetmiis_prob XPRBgetmiis
#define xbgetrange  XPRBgetrange
#define xbsavebasis_prob XPRBsavebasis
#define xbloadbasis XPRBloadbasis
#define xbdelbasis XPRBdelbasis

#define xblpoptimize_prob XPRBlpoptimize
#define xbmipoptimize_prob XPRBmipoptimize
#define xbsolve_prob XPRBsolve
#define xbminim_prob XPRBminim
#define xbmaxim_prob XPRBmaxim
#define xbloadmipsol_prob XPRBloadmipsol
#define xbaddmipsol_prob XPRBaddmipsol
#define xbgetprobstat_prob XPRBgetprobstat
#define xbgetlpstat_prob XPRBgetlpstat
#define xbgetmipstat_prob XPRBgetmipstat
#define xbsync_prob XPRBsync
#define xbbegincb_prob XPRBbegincb
#define xbendcb_prob XPRBendcb
#define xbgetobjval_prob XPRBgetobjval
#define xbgetsol XPRBgetsol
#define xbgetrcost XPRBgetrcost
#define xbgetslack XPRBgetslack
#define xbgetact XPRBgetact
#define xbgetdual XPRBgetdual
#define xbsetcolorder_prob XPRBsetcolorder
#define xbfixglobals_prob XPRBfixmipentities
#define XPRBfixglobals XPRBfixmipentities
#define xbwritesol_prob XPRBwritesol
#define xbwritebinsol_prob XPRBwritebinsol
#define xbwriteslxsol_prob XPRBwriteslxsol
#define xbwriteprtsol_prob XPRBwriteprtsol
#define xbreadbinsol_prob XPRBreadbinsol
#define xbreadslxsol_prob XPRBreadslxsol

#define xbgetvarlink XPRBgetvarlink
#define xbsetvarlink XPRBsetvarlink
#define xbdefcbdelvar_prob XPRBdefcbdelvar

#define xbnewcut_prob XPRBnewcut
#define xbdelcut XPRBdelcut
#define xbaddcutterm XPRBaddcutterm
#define xbdelcutterm XPRBdelcutterm
#define xbsetcutterm XPRBsetcutterm
#define xbaddcutarrterm XPRBaddcutarrterm
#define xbaddcuts_prob XPRBaddcuts
#define xbnewcutsum_prob XPRBnewcutsum
#define xbnewcutsumc_prob XPRBnewcutsumc
#define xbnewcutarrsum_prob XPRBnewcutarrsum
#define xbnewcutprec_prob XPRBnewcutprec
#define xbprintcut XPRBprintcut
#define xbsetcuttype XPRBsetcuttype
#define xbsetcutid XPRBsetcutid
#define xbgetcuttype XPRBgetcuttype
#define xbgetcutrhs XPRBgetcutrhs
#define xbgetcutid XPRBgetcutid
#define xbsetcutmode_prob XPRBsetcutmode

#define xbnewsol_prob XPRBnewsol
#define xbdelsol XPRBdelsol
#define xbsetsolvar XPRBsetsolvar
#define xbsetsolarrvar XPRBsetsolarrvar
#define xbdelsolvar XPRBdelsolvar
#define xbgetsolvar XPRBgetsolvar
#define xbgetsolsize XPRBgetsolsize
#define xbprintsol XPRBprintsol

#define XPRBmalloc
