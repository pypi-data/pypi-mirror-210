/***************************************************************************\
 *                                                                         *
 * xslp.h                                                                  *
 *                                                                         *
 * Declarations necessary for using Xpress-XSLP from C                     *
 *                                                                         *
 * (c) 1984-2022 Fair Isaac Corporation                                    *
 * For FICO Xpress XSLP v41.01.01                                          *
 * All rights reserved                                                     *
 *                                                                         *
\***************************************************************************/

#ifndef XSLP_H
#define XSLP_H

#ifndef XPRS_H
#include "xprs.h"
#endif

/***************************************************************************\
 * calling conventions for Windows                                         *
\**************************************************************************/
#ifdef _WIN32
#define XSLP_CC __stdcall
#else
#define XSLP_CC
#endif


#ifndef XSLP_CC
#define XSLP_CC XPRS_CC
#endif

#ifndef XSLPalltype
#define XSLPalltype XPRSalltype
#endif

typedef struct tagXSLPproblem *XSLPprob;
typedef int (XPRS_CC *XSLPcbFunc)(XSLPprob,...);

/***************************************************************************\
  * Integer problem attributes                                             *
\**************************************************************************/
#define XSLP_VALIDATIONSTATUS               XPRS_NLPVALIDATIONSTATUS           //  Solution status as validated by the validation function
#define XSLP_SOLSTATUS                      XPRS_NLPSOLSTATUS                  //  Detailed type of the soluton found
#define XSLP_EXPLOREDELTAS                  XPRS_SLPEXPLOREDELTAS              //  Number of variables set as explore delta variables
#define XSLP_SEMICONTDELTAS                 XPRS_SLPSEMICONTDELTAS             //  Number of variables set as stepwise variables
#define XSLP_INTEGERDELTAS                  XPRS_SLPINTEGERDELTAS              //  Number of variables set as grid variables
#define XSLP_ORIGINALROWS                   XPRS_NLPORIGINALROWS               //  Number of model rows in the original problem as loaded by the uiser
#define XSLP_ORIGINALCOLS                   XPRS_NLPORIGINALCOLS               //  Number of model columns in the original problem as loaded by the user
#define XSLP_ITER                           XPRS_SLPITER                       //  SLP - NLP iteration count
#define XSLP_STATUS                         XPRS_SLPSTATUS                     //  Bitmap holding the problem convergence status
#define XSLP_UNCONVERGED                    XPRS_SLPUNCONVERGED                //  Number of unconverged values
#define XSLP_SBXCONVERGED                   XPRS_SLPSBXCONVERGED               //  Number of step-bounded variables converged only on extended criteria
#define XSLP_CVS                            12005                              //  Number of character variables
#define XSLP_UFS                            XPRS_NLPUFS                        //  Number of user functions
#define XSLP_IFS                            XPRS_NLPIFS                        //  Number of internal functions
#define XSLP_PENALTYDELTAROW                XPRS_SLPPENALTYDELTAROW            //  Index of equality row holding the penalties for delta vectors
#define XSLP_PENALTYDELTACOLUMN             XPRS_SLPPENALTYDELTACOLUMN         //  Index of column costing the penalty delta row
#define XSLP_PENALTYERRORROW                XPRS_SLPPENALTYERRORROW            //  Index of equality row holding the penalties for penalty error vectors
#define XSLP_PENALTYERRORCOLUMN             XPRS_SLPPENALTYERRORCOLUMN         //  Index of column costing the penalty error row
#define XSLP_EQUALSCOLUMN                   XPRS_NLPEQUALSCOLUMN               //  Index of the reserved '=' column
#define XSLP_VARIABLES                      XPRS_NLPVARIABLES                  //  Number of nonlinear variables
#define XSLP_IMPLICITVARIABLES              XPRS_NLPIMPLICITVARIABLES          //  Number of nonlinear variables appearing only in coefficients
#define XSLP_COEFFICIENTS                   XPRS_SLPCOEFFICIENTS               //  Number of nonlinear coefficients
#define XSLP_PENALTYDELTAS                  XPRS_SLPPENALTYDELTAS              //  Number of penalty delta vectors
#define XSLP_PENALTYERRORS                  XPRS_SLPPENALTYERRORS              //  Number of penalty error vectors
#define XSLP_PLUSPENALTYERRORS              XPRS_SLPPLUSPENALTYERRORS          //  Number of positive penalty error vectors
#define XSLP_MINUSPENALTYERRORS             XPRS_SLPMINUSPENALTYERRORS         //  Number of negative penalty error vectors
#define XSLP_UCCONSTRAINEDCOUNT             XPRS_SLPUCCONSTRAINEDCOUNT         //  Number of unconverged variables with coefficients in constraining rows
#define XSLP_MIPNODES                       XPRS_SLPMIPNODES                   //  Number of nodes explored in MISLP
#define XSLP_MIPITER                        XPRS_SLPMIPITER                    //  Total number of SLP iterations in MISLP
#define XSLP_VERSION                        12024                              //  Xpress-SLP major version number
#define XSLP_MINORVERSION                   12025                              //  Xpress-SLP minor version number
#define XSLP_NONLINEARCONSTRAINTS           XPRS_NONLINEARCONSTRAINTS          //  Number of nonlinear constraints in the problem
#define XSLP_TOLSETS                        XPRS_SLPTOLSETS                    //  Number of tolerance sets
#define XSLP_USERFUNCCALLS                  XPRS_NLPUSERFUNCCALLS              //  Number of calls made to user functions
#define XSLP_UFINSTANCES                    12034                              //  Number of user function instances
#define XSLP_ECFCOUNT                       XPRS_SLPECFCOUNT                   //  Number of infeasible constraints found at the point of linearization
#define XSLP_USEDERIVATIVES                 XPRS_NLPUSEDERIVATIVES             //  Indicates whether numeric or analytic derivatives were used to create the linear approximations and solve the problem 
#define XSLP_DELTAS                         XPRS_SLPDELTAS                     //  Number of delta vectors created during augmentation
#define XSLP_KEEPBESTITER                   XPRS_NLPKEEPBESTITER               //  If KEEPBEST is set and returned, the iteration where it was achieved
#define XSLP_NLPSTATUS                      XPRS_NLPSTATUS                     //  Status of the problem being solved
#define XSLP_ZEROESRESET                    XPRS_SLPZEROESRESET                //  Number of placeholder entries set to zero
#define XSLP_ZEROESTOTAL                    XPRS_SLPZEROESTOTAL                //  Number of potential zero placeholder entries
#define XSLP_ZEROESRETAINED                 XPRS_SLPZEROESRETAINED             //  Number of potentially zero placeholders left untouched
#define XSLP_PRESOLVEFIXEDSLPVAR            12051                              //  Number of SLP variables fixed by XSLPpresolve
#define XSLP_PRESOLVEFIXEDDR                12052                              //  Number of determining rows fixed by XSLPpresolve
#define XSLP_PRESOLVEFIXEDCOEF              12053                              //  Number of SLP coefficients fixed by XSLPpresolve
#define XSLP_PRESOLVEFIXEDZCOL              12054                              //  Number of variables fixed at zero by XSLPpresolve
#define XSLP_PRESOLVEFIXEDNZCOL             12055                              //  Number of variables fixed to a nonzero value by XSLPpresolve
#define XSLP_PRESOLVEDELETEDDELTA           12056                              //  Number of potential delta variables deleted by XSLPpresolve
#define XSLP_PRESOLVETIGHTENED              12057                              //  Number of bounds tightened by XSLPpresolve
#define XSLP_NONCONSTANTCOEFFS              XPRS_SLPNONCONSTANTCOEFFS          //  Number of coefficients in the augmented problem that might change between SLP iterations 
#define XSLP_SOLVERSELECTED                 XPRS_LOCALSOLVERSELECTED           //  The library that was selected for local solves
#define XSLP_MODELROWS                      XPRS_NLPMODELROWS                  //  Number of model rows currently in the problem (loaded by the user)
#define XSLP_MODELCOLS                      XPRS_NLPMODELCOLS                  //  Number of model columns currently in the problem (columns loaded by the user)
#define XSLP_JOBID                          XPRS_NLPJOBID                      //  The identifier for the current job (e.g. used in multistart)
#define XSLP_MSSTATUS                       12085                              //  The status of the multi-start search
#define XSLP_PRESOLVESTATE                  12087                              //  If the problem currently in a presolved - transformed form
#define XSLP_MIPSOLS                        XPRS_SLPMIPSOLS                    //  The number of MIP solutions found so far
#define XSLP_STOPSTATUS                     XPRS_NLPSTOPSTATUS                 //  Number of eliminations in XSLPpresolve
#define XSLP_PRESOLVEELIMINATIONS           XPRS_NLPPRESOLVEELIMINATIONS       //  Status of the optimization process
#define XSLP_TOTALEVALUATIONERRORS          XPRS_NLPTOTALEVALUATIONERRORS       //  The total number of evaluation errors during the solve



/***************************************************************************\
  * Double control variables                                               *
\**************************************************************************/
#define XSLP_DAMP                           XPRS_SLPDAMP                       //  Damping factor for updating values of variables
#define XSLP_DAMPEXPAND                     XPRS_SLPDAMPEXPAND                 //  Multiplier to increase damping factor during dynamic damping
#define XSLP_DAMPSHRINK                     XPRS_SLPDAMPSHRINK                 //  Multiplier to decrease damping factor during dynamic damping
#define XSLP_DELTA_A                        XPRS_SLPDELTA_A                    //  Absolute perturbation of values for calculating numerical derivatives
#define XSLP_DELTA_R                        XPRS_SLPDELTA_R                    //  Relative perturbation of values for calculating numerical derivatives
#define XSLP_DELTA_Z                        XPRS_SLPDELTA_Z                    //  Zero tolerance used when calculating numerical derivatives
#define XSLP_DELTACOST                      XPRS_SLPDELTACOST                  //  Initial penalty cost multiplier for penalty delta vectors
#define XSLP_DELTAMAXCOST                   XPRS_SLPDELTAMAXCOST               //  Maximum penalty cost multiplier for penalty delta vectors
#define XSLP_DJTOL                          XPRS_SLPDJTOL                      //  Tolerance on DJ value for determining if a variable is at its step bound
#define XSLP_ERRORCOST                      XPRS_SLPERRORCOST                  //  Initial penalty cost multiplier for penalty error vectors
#define XSLP_ERRORMAXCOST                   XPRS_SLPERRORMAXCOST               //  Maximum penalty cost multiplier for penalty error vectors
#define XSLP_ERRORTOL_A                     XPRS_SLPERRORTOL_A                 //  Absolute tolerance for error vectors
#define XSLP_EXPAND                         XPRS_SLPEXPAND                     //  Multiplier to increase a step bound
#define XSLP_INFINITY                       XPRS_NLPINFINITY                   //  Value returned by a divide-by-zero in a formula
#define XSLP_MAXWEIGHT                      XPRS_SLPMAXWEIGHT                  //  Maximum penalty weight for delta or error vectors
#define XSLP_MINWEIGHT                      XPRS_SLPMINWEIGHT                  //  Minimum penalty weight for delta or error vectors
#define XSLP_SHRINK                         XPRS_SLPSHRINK                     //  Multiplier to reduce a step bound
#define XSLP_ZERO                           XPRS_NLPZERO                       //  Absolute zero tolerance
#define XSLP_CTOL                           XPRS_SLPCTOL                       //  Closure convergence tolerance
#define XSLP_ATOL_A                         XPRS_SLPATOL_A                     //  Absolute delta convergence tolerance
#define XSLP_ATOL_R                         XPRS_SLPATOL_R                     //  Relative delta convergence tolerance
#define XSLP_MTOL_A                         XPRS_SLPMTOL_A                     //  Absolute effective matrix element convergence tolerance
#define XSLP_MTOL_R                         XPRS_SLPMTOL_R                     //  Relative effective matrix element convergence tolerance
#define XSLP_ITOL_A                         XPRS_SLPITOL_A                     //  Absolute impact convergence tolerance
#define XSLP_ITOL_R                         XPRS_SLPITOL_R                     //  Relative impact convergence tolerance
#define XSLP_STOL_A                         XPRS_SLPSTOL_A                     //  Absolute slack convergence tolerance
#define XSLP_STOL_R                         XPRS_SLPSTOL_R                     //  Relative slack convergence tolerance
#define XSLP_MVTOL                          XPRS_SLPMVTOL                      //  Marginal value tolerance for determining if a constraint is slack
#define XSLP_XTOL_A                         XPRS_SLPXTOL_A                     //  Absolute static objective function (1) tolerance
#define XSLP_XTOL_R                         XPRS_SLPXTOL_R                     //  Relative static objective function (1) tolerance
#define XSLP_DEFAULTSTEPBOUND               XPRS_SLPDEFAULTSTEPBOUND           //  Minimum IV for the step bound of an SLP variable if none is explicitly given
#define XSLP_DAMPMAX                        XPRS_SLPDAMPMAX                    //  Maximum value for the damping factor of a variable during dynamic damping
#define XSLP_DAMPMIN                        XPRS_SLPDAMPMIN                    //  Minimum value for the damping factor of a variable during dynamic damping
#define XSLP_DELTACOSTFACTOR                XPRS_SLPDELTACOSTFACTOR            //  Factor for increasing cost multiplier on total penalty delta vectors
#define XSLP_ERRORCOSTFACTOR                XPRS_SLPERRORCOSTFACTOR            //  Factor for increasing cost multiplier on total penalty error vectors
#define XSLP_ERRORTOL_P                     XPRS_SLPERRORTOL_P                 //  Absolute tolerance for printing error vectors
#define XSLP_CASCADETOL_PA                  XPRS_SLPCASCADETOL_PA              //  Absolute cascading print tolerance
#define XSLP_CASCADETOL_PR                  XPRS_SLPCASCADETOL_PR              //  Relative cascading print tolerance
#define XSLP_DEFAULTIV                      XPRS_NLPDEFAULTIV                  //  Default initial value for an SLP variable if none is explicitly given
#define XSLP_OBJSENSE                       12146                              //  Objective function sense
#define XSLP_OPTTIME                        XPRS_NLPOPTTIME                    //  Time spent in optimization
#define XSLP_OTOL_A                         XPRS_SLPOTOL_A                     //  Absolute static objective (2) convergence tolerance
#define XSLP_OTOL_R                         XPRS_SLPOTOL_R                     //  Relative static objective (2) convergence tolerance
#define XSLP_DELTA_X                        XPRS_SLPDELTA_X                    //  Minimum absolute value of delta coefficients to be retained
#define XSLP_ERRORCOSTS                     XPRS_SLPERRORCOSTS                 //  Total penalty costs in the solution
#define XSLP_GRANULARITY                    XPRS_SLPGRANULARITY                //  Base for calculating penalty costs
#define XSLP_MIPCUTOFF_A                    XPRS_SLPMIPCUTOFF_A                //  Absolute objective function cutoff for MIP termination
#define XSLP_MIPCUTOFF_R                    XPRS_SLPMIPCUTOFF_R                //  Absolute objective function cutoff for MIP termination
#define XSLP_MIPOTOL_A                      XPRS_SLPMIPOTOL_A                  //  Absolute objective function tolerance for MIP termination
#define XSLP_MIPOTOL_R                      XPRS_SLPMIPOTOL_R                  //  Relative objective function tolerance for MIP termination
#define XSLP_MEMORYFACTOR                   12164                              //  Factor for expanding size of dynamic arrays in memory
#define XSLP_VALIDATIONTOL_A                XPRS_NLPVALIDATIONTOL_A            //  Absolute tolerance for the XSLPvalidate procedure
#define XSLP_VALIDATIONTOL_R                XPRS_NLPVALIDATIONTOL_R            //  Relative tolerance for the XSLPvalidate procedure
#define XSLP_VALIDATIONINDEX_A              XPRS_NLPVALIDATIONINDEX_A          //  Absolute validation index
#define XSLP_VALIDATIONINDEX_R              XPRS_NLPVALIDATIONINDEX_R          //  Relative validation index
#define XSLP_ESCALATION                     XPRS_SLPESCALATION                 //  Factor for increasing cost multiplier on individual penalty error vectors
#define XSLP_OBJTOPENALTYCOST               XPRS_SLPOBJTOPENALTYCOST           //  Factor to estimate initial penalty costs from objective function
#define XSLP_SHRINKBIAS                     XPRS_SLPSHRINKBIAS                 //  Shrink side step bound update overwrite for improving iterations
#define XSLP_FEASTOLTARGET                  XPRS_SLPFEASTOLTARGET              //  Ideal target of feasibility level of the linearizations
#define XSLP_OPTIMALITYTOLTARGET            XPRS_SLPOPTIMALITYTOLTARGET        //  Ideal target of optimality level of the linearizations
#define XSLP_DELTA_INFINITY                 XPRS_SLPDELTA_INFINITY             //  Maximum value for partial derivatives
#define XSLP_PRIMALINTEGRALREF              XPRS_NLPPRIMALINTEGRALREF          //  Reference (estimated global) objective when calculating the primal integral
#define XSLP_PRIMALINTEGRALALPHA            XPRS_NLPPRIMALINTEGRALALPHA        //  The exponential weight function's alpha in the primal integral
#define XSLP_VTOL_A                         XPRS_SLPVTOL_A                     //  Absolute static objective (3) convergence tolerance
#define XSLP_VTOL_R                         XPRS_SLPVTOL_R                     //  Relative static objective (3) convergence tolerance
#define XSLP_OBJVAL                         XPRS_NLPOBJVAL                     //  Objective function value excluding any penalty costs
#define XSLP_ETOL_A                         XPRS_SLPETOL_A                     //  Absolute tolerance on penalty vectors
#define XSLP_ETOL_R                         XPRS_SLPETOL_R                     //  Relative tolerance on penalty vectors
#define XSLP_EVTOL_A                        XPRS_SLPEVTOL_A                    //  Absolute tolerance on total penalty costs
#define XSLP_EVTOL_R                        XPRS_SLPEVTOL_R                    //  Relative tolerance on total penalty costs
#define XSLP_DELTA_ZERO                     XPRS_SLPDELTA_ZERO                 //  Absolute zero tolerance for derivatives. Smaller values not pushed by DELTA_Z
#define XSLP_MINSBFACTOR                    XPRS_SLPMINSBFACTOR                //  The min step bound size no longer decreased is max(ATOL_A, CTOL*IV)*MINSBFACTOR
#define XSLP_CLAMPVALIDATIONTOL_A           XPRS_SLPCLAMPVALIDATIONTOL_A       //  Absolute validation violation before clamping is applied
#define XSLP_CLAMPVALIDATIONTOL_R           XPRS_SLPCLAMPVALIDATIONTOL_R       //  Relative validation violation before clamping is applied
#define XSLP_CLAMPSHRINK                    XPRS_SLPCLAMPSHRINK                //  Step bound shrinking ratio applied to step bounds during clamping
#define XSLP_ECFTOL_A                       XPRS_SLPECFTOL_A                   //  Absolute tolerance on testing feasibility at the point of linearization
#define XSLP_ECFTOL_R                       XPRS_SLPECFTOL_R                   //  Relative tolerance on testing feasibility at the point of linearization
#define XSLP_WTOL_A                         XPRS_SLPWTOL_A                     //  Absolute extended convergence continuation tolerance
#define XSLP_WTOL_R                         XPRS_SLPWTOL_R                     //  Relative extended convergence continuation tolerance
#define XSLP_PRESOLVEZERO                   XPRS_NLPPRESOLVEZERO               //  Minimum absolute value for a variable which is identified as nonzero during NLP presolve 
#define XSLP_MATRIXTOL                      XPRS_SLPMATRIXTOL                  //  Override value for the smallest element that can be loaded into the linearization
#define XSLP_DRFIXRANGE                     XPRS_SLPDRFIXRANGE                 //  Relaxation relative radius around previous value for CASCADE_DRCOL_PVRANGE
#define XSLP_DRCOLTOL                       XPRS_SLPDRCOLTOL                   //  Minimum value of the main column multiplied with the variable being determined 
#define XSLP_MERITLAMBDA                    XPRS_NLPMERITLAMBDA                //  Ratio, by which the objective can dominate feasibility in the objective
#define XSLP_MIPERRORTOL_A                  XPRS_SLPMIPERRORTOL_A              //  Absolute penalty error cost tolerance for MIP cut-off
#define XSLP_MIPERRORTOL_R                  XPRS_SLPMIPERRORTOL_R              //  Relative penalty error cost tolerance for MIP cut-off
#define XSLP_CDTOL_A                        XPRS_SLPCDTOL_A                    //  Absolute tolerance for deducing constant derivatives
#define XSLP_CDTOL_R                        XPRS_SLPCDTOL_R                    //  Relative tolerance for deducing constant derivatives
#define XSLP_ENFORCEMAXCOST                 XPRS_SLPENFORCEMAXCOST             //  Maximum penalty cost in the objective before enforcing most violating rows
#define XSLP_ENFORCECOSTSHRINK              XPRS_SLPENFORCECOSTSHRINK          //  Factor by which to decrease the current penalty multiplier when enforcing rows 
#define XSLP_MSMAXBOUNDRANGE                XPRS_MSMAXBOUNDRANGE               //  The maximum perturbation to any initial value non ranged variables
#define XSLP_VALIDATIONTOL_K                XPRS_NLPVALIDATIONTOL_K            //  Relative tolerance for the XSLPvalidatekkt procedure
#define XSLP_PRESOLVE_ELIMTOL               XPRS_NLPPRESOLVE_ELIMTOL           //  Presolve nonlinear elimination tolerance
#define XSLP_DRCOLDJTOL                     XPRS_SLPDRCOLDJTOL                 //  Reduced cost tolerance on the delta variable for the drcol handler
#define XSLP_VALIDATIONTARGET_R             XPRS_NLPVALIDATIONTARGET_R         //  Relative validation index target
#define XSLP_VALIDATIONTARGET_K             XPRS_NLPVALIDATIONTARGET_K         //  Relative KKT validatiob index target
#define XSLP_VALIDATIONFACTOR               XPRS_NLPVALIDATIONFACTOR           //  Minimum improvement in validation targets
#define XSLP_BARSTALLINGTOL                 XPRS_SLPBARSTALLINGTOL             //  Range for the objective change for the barrier stalling limit checks
#define XSLP_OBJTHRESHOLD                   XPRS_SLPOBJTHRESHOLD               //  Assumed maximum value of the objecive function
#define XSLP_BOUNDTHRESHOLD                 XPRS_SLPBOUNDTHRESHOLD             //  The maxumum size of a bound that can be introduced by presolve



/***************************************************************************\
  * Character string control variables                                     *
\**************************************************************************/
#define XSLP_CVNAME                         12451                              //  MPS file: name of the character variable set to use
#define XSLP_DELTAFORMAT                    XPRS_SLPDELTAFORMAT                //  Formatting string for creation of names for SLP delta vectors
#define XSLP_IVNAME                         XPRS_NLPIVNAME                     //  MPS file: name of the initial value set to use
#define XSLP_MINUSDELTAFORMAT               XPRS_SLPMINUSDELTAFORMAT           //  Formatting string for creation of names for SLP negative penalty delta vectors 
#define XSLP_MINUSERRORFORMAT               XPRS_SLPMINUSERRORFORMAT           //  Formatting string for creation of names for SLP negative penalty error vectors 
#define XSLP_PLUSDELTAFORMAT                XPRS_SLPPLUSDELTAFORMAT            //  Formatting string for creation of names for SLP positive penalty delta vectors 
#define XSLP_PLUSERRORFORMAT                XPRS_SLPPLUSERRORFORMAT            //  Formatting string for creation of names for SLP positive penalty error vectors 
#define XSLP_SBNAME                         XPRS_SLPSBNAME                     //  MPS file: name of the step bound set to use
#define XSLP_TOLNAME                        XPRS_SLPTOLNAME                    //  MPS file: name of the tolerance set to use
#define XSLP_UPDATEFORMAT                   XPRS_SLPUPDATEFORMAT               //  Formatting string for creation of names for SLP update rows
#define XSLP_PENALTYROWFORMAT               XPRS_SLPPENALTYROWFORMAT           //  Formatting string for creation of the names of the SLP penalty rows
#define XSLP_PENALTYCOLFORMAT               XPRS_SLPPENALTYCOLFORMAT           //  Formatting string for creation of the names of the SLP penalty transfer vectors
#define XSLP_SBLOROWFORMAT                  XPRS_SLPSBLOROWFORMAT              //  Formatting string for creation of names for SLP lower step bound rows
#define XSLP_SBUPROWFORMAT                  XPRS_SLPSBUPROWFORMAT              //  Formatting string for creation of names for SLP upper step bound rows
#define XSLP_TRACEMASK                      XPRS_SLPTRACEMASK                  //  Mask for rows and columns to be traced for changes through the SLP iterations
#define XSLP_ITERFALLBACKOPS                XPRS_SLPITERFALLBACKOPS            //  List of arguments to try as fallback for numerically challenging iterations



/***************************************************************************\
  * Character string attributes                                            *
\**************************************************************************/
#define XSLP_UNIQUEPREFIX                   12501                              //  Unique prefix for generated names
#define XSLP_VERSIONDATE                    12502                              //  Date of creation of Xpress-SLP



/***************************************************************************\
  * Pointer attributes                                                     *
\**************************************************************************/
#define XSLP_XPRSPROBLEM                    12601                              //  The underlying Optimizer problem pointer
#define XSLP_XSLPPROBLEM                    12602                              //  The Xpress-SLP problem pointer
#define XSLP_GLOBALFUNCOBJECT               12607                              //  The user-defined global function object
#define XSLP_USERFUNCOBJECT                 12608                              //  The user function object for the current function
#define XSLP_INSTANCEFUNCOBJECT             12609                              //  The instance function object for the current instance
#define XSLP_MIPPROBLEM                     12611                              //  The underlying Optimizer MIP problem
#define XSLP_SOLUTIONPOOL                   12613                              //  Access to the XSLP solution pool (see XSLP_ANALYZE)



/***************************************************************************\
  * Double attributes                                                      *
\**************************************************************************/
#define XSLP_CURRENTDELTACOST               XPRS_SLPCURRENTDELTACOST           //  Current value of penalty cost multiplier for penalty delta vectors
#define XSLP_CURRENTERRORCOST               XPRS_SLPCURRENTERRORCOST           //  Current value of penalty cost multiplier for penalty error vectors
#define XSLP_PENALTYERRORTOTAL              XPRS_SLPPENALTYERRORTOTAL          //  Total activity of penalty error vectors
#define XSLP_PENALTYERRORVALUE              XPRS_SLPPENALTYERRORVALUE          //  Total penalty cost attributed to penalty error vectors
#define XSLP_PENALTYDELTATOTAL              XPRS_SLPPENALTYDELTATOTAL          //  Total activity of penalty delta vectors
#define XSLP_PENALTYDELTAVALUE              XPRS_SLPPENALTYDELTAVALUE          //  Total penalty cost attributed to penalty delta vectors
#define XSLP_VSOLINDEX                      12708                              //  Vertex solution index
#define XSLP_VALIDATIONINDEX_K              XPRS_NLPVALIDATIONINDEX_K          //  The level of dual side KKT violation of the solution, set by validatekkt
#define XSLP_VALIDATIONINDEX_I              12721                              //  Integrality validation
#define XSLP_VALIDATIONNETOBJ               XPRS_NLPVALIDATIONNETOBJ           //  Net objective as calculated by validation
#define XSLP_PRIMALINTEGRAL                 XPRS_NLPPRIMALINTEGRAL             //  Observed primal integral presented to the user, depending on what we solved



/***************************************************************************\
  * Knitro parameter mapping (to be used in XSLP parameter functions)      *
\**************************************************************************/
#define XKTR_PARAM_NEWPOINT                      XPRS_KNITRO_PARAM_NEWPOINT       //  Extra action to take after every iteration in a solve of a continuous problem
#define XKTR_PARAM_HONORBNDS                    XPRS_KNITRO_PARAM_HONORBNDS       //  If enforce satisfaction of simple variable bounds throughout the optimization
#define XKTR_PARAM_ALGORITHM                    XPRS_KNITRO_PARAM_ALGORITHM       //  Algorithm selection
#define XKTR_PARAM_BAR_MURULE                  XPRS_KNITRO_PARAM_BAR_MURULE       //  Which strategy to use for modifying the barrier parameter
#define XKTR_PARAM_BAR_FEASIBLE              XPRS_KNITRO_PARAM_BAR_FEASIBLE       //  If special emphasis on getting and staying feasible in the IP algorithms
#define XKTR_PARAM_GRADOPT                        XPRS_KNITRO_PARAM_GRADOPT       //  How to compute the gradients of the objective and constraint functions
#define XKTR_PARAM_HESSOPT                        XPRS_KNITRO_PARAM_HESSOPT       //  How to compute the (approximate) Hessian of the Lagrangian
#define XKTR_PARAM_BAR_INITPT                  XPRS_KNITRO_PARAM_BAR_INITPT       //  If an initial point strategy is used with barrier algorithms
#define XKTR_PARAM_MAXCGIT                        XPRS_KNITRO_PARAM_MAXCGIT       //  Maximum number of inner CG iterations per minor iteration
#define XKTR_PARAM_MAXIT                            XPRS_KNITRO_PARAM_MAXIT       //  Maximum number of iterations before termination
#define XKTR_PARAM_OUTLEV                          XPRS_KNITRO_PARAM_OUTLEV       //  Level of output produced by KNITRO
#define XKTR_PARAM_SCALE                            XPRS_KNITRO_PARAM_SCALE       //  If the problem should be scaled
#define XKTR_PARAM_SOC                                XPRS_KNITRO_PARAM_SOC       //  Whether or not to try second order corrections
#define XKTR_PARAM_DELTA                            XPRS_KNITRO_PARAM_DELTA       //  Initial trust region radius factor to determine the initial trust region size
#define XKTR_PARAM_BAR_FEASMODETOL           XPRS_KNITRO_PARAM_BAR_FEASMODETOL       //  Tolerance determining whether to force subsequent iterates to remain feasible
#define XKTR_PARAM_FEASTOL                        XPRS_KNITRO_PARAM_FEASTOL       //  Final relative stopping tolerance for the feasibility error
#define XKTR_PARAM_FEASTOLABS                  XPRS_KNITRO_PARAM_FEASTOLABS       //  Final absolute stopping tolerance for the feasibility error
#define XKTR_PARAM_BAR_INITMU                  XPRS_KNITRO_PARAM_BAR_INITMU       //  Initial value for the barrier parameter
#define XKTR_PARAM_OBJRANGE                      XPRS_KNITRO_PARAM_OBJRANGE       //  Limits of the objective function for purposes of determining unboundedness
#define XKTR_PARAM_OPTTOL                          XPRS_KNITRO_PARAM_OPTTOL       //  Relative stopping tolerance for the KKT (optimality) error
#define XKTR_PARAM_OPTTOLABS                    XPRS_KNITRO_PARAM_OPTTOLABS       //  Absolute stopping tolerance for the KKT (optimality) error
#define XKTR_PARAM_PIVOT                            XPRS_KNITRO_PARAM_PIVOT       //  Initial pivot threshold used in factorization routines
#define XKTR_PARAM_XTOL                              XPRS_KNITRO_PARAM_XTOL       //  Relative change tolerance
#define XKTR_PARAM_DEBUG                            XPRS_KNITRO_PARAM_DEBUG       //  Controls the level of debugging output
#define XKTR_PARAM_MULTISTART                  XPRS_KNITRO_PARAM_MULTISTART       //  If to solve from multiple start points to find a better local minimum
#define XKTR_PARAM_MSMAXSOLVES                XPRS_KNITRO_PARAM_MSMAXSOLVES       //  Number of start points to try in multi-start
#define XKTR_PARAM_MSMAXBNDRANGE             XPRS_KNITRO_PARAM_MSMAXBNDRANGE       //  Maximum range that unbounded variables can take when determining start points
#define XKTR_PARAM_LMSIZE                          XPRS_KNITRO_PARAM_LMSIZE       //  Number of limited memory pairs stored if using the limited-memory BFGS option
#define XKTR_PARAM_BAR_MAXCROSSIT            XPRS_KNITRO_PARAM_BAR_MAXCROSSIT       //  The maximum number of crossover iterations before termination
#define XKTR_PARAM_BLASOPTION                  XPRS_KNITRO_PARAM_BLASOPTION       //  Specifies the BLAS/LAPACK function library to use
#define XKTR_PARAM_BAR_MAXREFACTOR           XPRS_KNITRO_PARAM_BAR_MAXREFACTOR       //  Max number of refactorizations of the KKT per iteration before reverting to CG 
#define XKTR_PARAM_BAR_MAXBACKTRACK          XPRS_KNITRO_PARAM_BAR_MAXBACKTRACK       //  Max number of backtracks in linesearch before reverting to a CG step
#define XKTR_PARAM_BAR_PENRULE                XPRS_KNITRO_PARAM_BAR_PENRULE       //  Penalty parameter strategy for determining if to accept a trial iterate
#define XKTR_PARAM_BAR_PENCONS                XPRS_KNITRO_PARAM_BAR_PENCONS       //  If a penalty approach is applied to the constraints
#define XKTR_PARAM_MSNUMTOSAVE                XPRS_KNITRO_PARAM_MSNUMTOSAVE       //  Number of distinct feasible points to save to KNITRO_mspoints.log
#define XKTR_PARAM_MSSAVETOL                    XPRS_KNITRO_PARAM_MSSAVETOL       //  Specifies the tolerance for deciding if two feasible points are distinct
#define XKTR_PARAM_MSTERMINATE                XPRS_KNITRO_PARAM_MSTERMINATE       //  Condition for terminating multi-start
#define XKTR_PARAM_MSSTARTPTRANGE            XPRS_KNITRO_PARAM_MSSTARTPTRANGE       //  Maximum range that each variable can take when determining new start points
#define XKTR_PARAM_INFEASTOL                    XPRS_KNITRO_PARAM_INFEASTOL       //  Relative tolerance used for declaring infeasibility of a model
#define XKTR_PARAM_LINSOLVER                    XPRS_KNITRO_PARAM_LINSOLVER       //  Which linear solver to use to solve linear systems
#define XKTR_PARAM_BAR_DIRECTINTERVAL        XPRS_KNITRO_PARAM_BAR_DIRECTINTERVAL       //  Controls the maximum number of consecutive conjugate gradient (CG) steps
#define XKTR_PARAM_PRESOLVE                      XPRS_KNITRO_PARAM_PRESOLVE       //  If to use the KNITRO presolver
#define XKTR_PARAM_PRESOLVE_TOL              XPRS_KNITRO_PARAM_PRESOLVE_TOL       //  Tolerance used by the KNITRO presolver
#define XKTR_PARAM_BAR_SWITCHRULE            XPRS_KNITRO_PARAM_BAR_SWITCHRULE       //  If the barrier can switch from an optimality phase to a pure feasibility phase 
#define XKTR_PARAM_MA_TERMINATE              XPRS_KNITRO_PARAM_MA_TERMINATE       //  Termination condition for the multi-algorithm
#define XKTR_PARAM_MSSEED                          XPRS_KNITRO_PARAM_MSSEED       //  Seed value used to generate random initial points in multi-start
#define XKTR_PARAM_BAR_RELAXCONS             XPRS_KNITRO_PARAM_BAR_RELAXCONS       //  Indicates whether a relaxation approach is applied to the constraints.
#define XKTR_PARAM_MIP_METHOD                  XPRS_KNITRO_PARAM_MIP_METHOD       //  Which MIP method to use
#define XKTR_PARAM_MIP_BRANCHRULE            XPRS_KNITRO_PARAM_MIP_BRANCHRULE       //  Branching rule to use
#define XKTR_PARAM_MIP_SELECTRULE            XPRS_KNITRO_PARAM_MIP_SELECTRULE       //  Node selection rule
#define XKTR_PARAM_MIP_INTGAPABS             XPRS_KNITRO_PARAM_MIP_INTGAPABS       //  The absolute integrality gap stop tolerance for MIP
#define XKTR_PARAM_MIP_INTGAPREL             XPRS_KNITRO_PARAM_MIP_INTGAPREL       //  The relative integrality gap stop tolerance for MIP
#define XKTR_PARAM_MIP_OUTLEVEL              XPRS_KNITRO_PARAM_MIP_OUTLEVEL       //  How much MIP information to print
#define XKTR_PARAM_MIP_OUTINTERVAL           XPRS_KNITRO_PARAM_MIP_OUTINTERVAL       //  Node printing interval for mip_outlevel
#define XKTR_PARAM_MIP_DEBUG                    XPRS_KNITRO_PARAM_MIP_DEBUG       //  Debugging level for MIP solution
#define XKTR_PARAM_MIP_IMPLICATNS            XPRS_KNITRO_PARAM_MIP_IMPLICATNS       //  If to add constraints to the MIP derived from logical implications
#define XKTR_PARAM_MIP_GUB_BRANCH            XPRS_KNITRO_PARAM_MIP_GUB_BRANCH       //  If allow branching on generalized upper bounds
#define XKTR_PARAM_MIP_KNAPSACK              XPRS_KNITRO_PARAM_MIP_KNAPSACK       //  Rules for adding MIP knapsack cuts
#define XKTR_PARAM_MIP_ROUNDING              XPRS_KNITRO_PARAM_MIP_ROUNDING       //  MIP rounding rule to apply
#define XKTR_PARAM_MIP_ROOTALG                XPRS_KNITRO_PARAM_MIP_ROOTALG       //  Algorithm to use for the root node solve in MIP
#define XKTR_PARAM_MIP_LPALG                    XPRS_KNITRO_PARAM_MIP_LPALG       //  Algorithm to use for solving LPs in the MIP search
#define XKTR_PARAM_MIP_MAXNODES              XPRS_KNITRO_PARAM_MIP_MAXNODES       //  Specifies the maximum number of nodes explored
#define XKTR_PARAM_MIP_HEURISTIC             XPRS_KNITRO_PARAM_MIP_HEURISTIC       //  Which MIP heuristic to apply for an initial integer feasible point
#define XKTR_PARAM_MIP_HEUR_MAXIT            XPRS_KNITRO_PARAM_MIP_HEUR_MAXIT       //  Maximum number of iterations to allow for MIP heuristic
#define XKTR_PARAM_MIP_PSEUDOINIT            XPRS_KNITRO_PARAM_MIP_PSEUDOINIT       //  Method to initialize pseudo-costs for variables not yet branched on
#define XKTR_PARAM_MIP_STRONG_MAXIT          XPRS_KNITRO_PARAM_MIP_STRONG_MAXIT       //  Maximum number of iterations to allow for strong branching solves
#define XKTR_PARAM_MIP_STRONG_CANDLIM        XPRS_KNITRO_PARAM_MIP_STRONG_CANDLIM       //  Maximum number of candidates to explore in strong branching
#define XKTR_PARAM_MIP_STRONG_LEVEL          XPRS_KNITRO_PARAM_MIP_STRONG_LEVEL       //  Maximum number of tree levels on which to perform strong branching
#define XKTR_PARAM_PAR_NUMTHREADS            XPRS_KNITRO_PARAM_PAR_NUMTHREADS       //  Number of threads to use for parallel computing features


#define XSLP_OBJTOL_A XSLP_XTOL_A
#define XSLP_OBJTOL_R XSLP_XTOL_R



/***************************************************************************\
  * Token types                                                            *
\**************************************************************************/
#define XSLP_EOF                      XPRS_TOK_EOF                    //  End of formula
#define XSLP_CON                      XPRS_TOK_CON                    //  Constant, (double) value
#define XSLP_COL                      XPRS_TOK_COL                    //  Column, index of matrix column
#define XSLP_FUN                      XPRS_TOK_FUN                    //  User function, index of function
#define XSLP_IFUN                     XPRS_TOK_IFUN                   //  Internal function, index of function
#define XSLP_LB                       XPRS_TOK_LB                     //  Left bracket
#define XSLP_RB                       XPRS_TOK_RB                     //  Right bracket
#define XSLP_DEL                      XPRS_TOK_DEL                    //  Delimiter, XPRS_DEL_COMMA (1) = comma (','); XPRS_DEL_COLON (2) = colon (':')
#define XSLP_OP                       XPRS_TOK_OP                     //  Operator, XSLP_UMINUS (1) = unary minus ('-'), XSLP_EXPONENT (2) = exponent ('**' or '^'); XSLP_MULTIPLY (3) = multiplication ('*'); XSLP_DIVIDE (4) = division ('/'); XSLP_PLUS (5) = addition ('+'); XSLP_MINUS (6) = subtraction ('-')

/***************************************************************************\
  * Token operand types                                                     *
\**************************************************************************/
#define XSLP_UMINUS                   XPRS_OP_UMINUS                  //  Operand, unary minus (-)
#define XSLP_EXPONENT                 XPRS_OP_EXPONENT                //  Operand, exponent (**) or (^)
#define XSLP_MULTIPLY                 XPRS_OP_MULTIPLY                //  Operand, multiplication (*)
#define XSLP_DIVIDE                   XPRS_OP_DIVIDE                  //  Operand, division (/)
#define XSLP_PLUS                     XPRS_OP_PLUS                    //  Operand, addition (+)
#define XSLP_MINUS                    XPRS_OP_MINUS                   //  Operand, subtraction (-)

#define XSLP_COMMA                    XPRS_DEL_COMMA                  //  Delimiter comma (1)
#define XSLP_COLON                    XPRS_DEL_COLON                  //  Delimiter colon (2)



/***************************************************************************\
  * Internal functions                                                     *
\**************************************************************************/
#define XSLP_MATH_LOG                         XPRS_IFUN_LOG                   //  Log to the base 10 maths function.
#define XSLP_MATH_LOG10                       XPRS_IFUN_LOG10                 //  Log to the base 10 maths function.
#define XSLP_MATH_LN                          XPRS_IFUN_LN                    //  Natural log maths function.
#define XSLP_MATH_EXP                         XPRS_IFUN_EXP                   //  Exponential maths function.
#define XSLP_MATH_ABS                         XPRS_IFUN_ABS                   //  Absolute value maths function.
#define XSLP_MATH_SQRT                        XPRS_IFUN_SQRT                  //  Square root maths function.
#define XSLP_MATH_SIN                         XPRS_IFUN_SIN                   //  Sine maths function (radians).
#define XSLP_MATH_COS                         XPRS_IFUN_COS                   //  Cosine maths function (radians).
#define XSLP_MATH_TAN                         XPRS_IFUN_TAN                   //  Tangent maths function (radians).
#define XSLP_MATH_ARCSIN                      XPRS_IFUN_ARCSIN                //  Arc-sine maths function (returns radians).
#define XSLP_MATH_ARCCOS                      XPRS_IFUN_ARCCOS                //  Arc-cosine maths function (returns radians).
#define XSLP_MATH_ARCTAN                      XPRS_IFUN_ARCTAN                //  Arc-tangent maths function (returns radians).
#define XSLP_MMX_MIN                         XPRS_IFUN_MIN                   //  Minimum function - variable argument
#define XSLP_MMX_MAX                         XPRS_IFUN_MAX                   //  Maximum function - variable argument
#define XSLP_MATH_PWL                         XPRS_IFUN_PWL                   //  Piecewise linear function - variable argument
#define XSLP_MATH_SIGN                        XPRS_IFUN_SIGN                  //  The sign function
#define XSLP_MATH_ERF                         XPRS_IFUN_ERF                   //  The error function
#define XSLP_MATH_ERFC                        XPRS_IFUN_ERFC                  //  The complementary error function



/***************************************************************************\
  * Problem status settings                                                *
\**************************************************************************/
#define XSLP_MADECONSTRUCT               0x01                            //  The problem is augmented
#define XSLP_MADECASCADE                 0x02                            //  Cascaded solution
#define XSLP_NODELTAZ                    0x08                            //  DeltaZ is off
#define XSLP_GLOBALINIT                  0x80                            //  Global has been initialized
#define XSLP_GLOBALOPT                   0x100                           //  Solving an MI-SLP
#define XSLP_ENDGLOBALOPT                0x200                           //  Global solve finished
#define XSLP_BOUND_PRESOLVED             0x1000                          //  Problem is bound propagated (the legacy notation of presolved)
#define XSLP_FUNCTIONERROR               0x2000                          //  There was a function evaluation error
#define XSLP_ERRORCOSTSET                0x20000                         //  Error costs have been updated
#define XSLP_NODE0                       0x80000                         //  Root node
#define XSLP_ENFORCEDROWS                0x1000000                       //  Some rows have been enforced during the solution
#define XSLP_ENFORCESBOUNDS              0x2000000                       //  Step bounds were enforced early (before XSLP_SBSTART)
#define XSLP_STEPBOUNDS                  0x4000000                       //  Step bounds have been activated



/***************************************************************************\
  * XSLP_STATUS settings                                                   *
\**************************************************************************/
#define XSLP_STATUS_CONVERGEDOBJUCC             XPRS_SLPSTATUS_CONVERGEDOBJUCC       //  Converged on objective with no unconverged values in active constraints
#define XSLP_STATUS_CONVERGEDOBJSBX             XPRS_SLPSTATUS_CONVERGEDOBJSBX       //  Converged on objective with some variables converged on extended criteria only 
#define XSLP_STATUS_LPINFEASIBLE                XPRS_SLPSTATUS_LPINFEASIBLE       //  LP solution is infeasible
#define XSLP_STATUS_LPUNFINISHED                XPRS_SLPSTATUS_LPUNFINISHED       //  LP solution is unfinished (not optimal or infeasible).
#define XSLP_STATUS_MAXSLPITERATIONS            XPRS_SLPSTATUS_MAXSLPITERATIONS       //  SLP terminated on maximum SLP iterations
#define XSLP_STATUS_INTEGERINFEASIBLE           XPRS_SLPSTATUS_INTEGERINFEASIBLE       //  SLP is integer infeasible.
#define XSLP_STATUS_RESIDUALPENALTIES           XPRS_SLPSTATUS_RESIDUALPENALTIES       //  SLP converged with residual penalty errors.
#define XSLP_STATUS_CONVERGEDOBJOBJ             XPRS_SLPSTATUS_CONVERGEDOBJOBJ       //  Converged on objective
#define XSLP_STATUS_MAXTIME                     XPRS_SLPSTATUS_MAXTIME          //  SLP terminated on max time
#define XSLP_STATUS_USER                        XPRS_SLPSTATUS_USER             //  SLP terminated by user
#define XSLP_STATUS_VARSLINKEDINACTIVE          XPRS_SLPSTATUS_VARSLINKEDINACTIVE       //  Some variables are linked to active constraints
#define XSLP_STATUS_NOVARSINACTIVE              XPRS_SLPSTATUS_NOVARSINACTIVE       //  No unconverged values in active constraints
#define XSLP_STATUS_OTOL                        XPRS_SLPSTATUS_OTOL             //  OTOL is satisfied - range of objective change small, active step bounds
#define XSLP_STATUS_VTOL                        XPRS_SLPSTATUS_VTOL             //  VTOL is satisfied - range of objective change is small
#define XSLP_STATUS_XTOL                        XPRS_SLPSTATUS_XTOL             //  XTOL is satisfied - range of objective change small, no unconverged in active
#define XSLP_STATUS_WTOL                        XPRS_SLPSTATUS_WTOL             //  WTOL is satisfied - convergence continuation
#define XSLP_STATUS_ERROTOL                     XPRS_SLPSTATUS_ERROTOL          //  ERRORTOL satisfied - penalties not increased further
#define XSLP_STATUS_EVTOL                       XPRS_SLPSTATUS_EVTOL            //  EVTOL satisfied - penalties not increased further
#define XSLP_STATUS_POLISHED                    XPRS_SLPSTATUS_POLISHED         //  There were iterations where the solution had to be polished
#define XSLP_STATUS_POLISH_FAILURE              XPRS_SLPSTATUS_POLISH_FAILURE       //  There were iterations where the solution polishing failed
#define XSLP_STATUS_ENFORCED                    XPRS_SLPSTATUS_ENFORCED         //  There were iterations where rows were enforced
#define XSLP_STATUS_CONSECUTIVE_INFEAS          XPRS_SLPSTATUS_CONSECUTIVE_INFEAS       //  Terminated due to INFEASLIMIT
#define XSLP_STATUS_KEEPBEST                    XPRS_SLPSTATUS_KEEPBEST         //  The solution with the best merit function value has been saved
#define XSLP_STATUS_CLAMPING                    XPRS_SLPSTATUS_CLAMPING         //  Clamping of variables converged only in extended criteria has been carried out 
#define XSLP_STATUS_ADAPTIVEITERS               XPRS_SLPSTATUS_ADAPTIVEITERS       //  The adaptive iteration strategy has been activated
#define XSLP_STATUS_OBJQNONCONVEX               XPRS_SLPSTATUS_OBJQNONCONVEX       //  The quadratic part of the objective is nonconvex
#define XSLP_NLPSTATUS_UNSTARTED                XPRS_NLPSTATUS_UNSTARTED        //  The optimization has not yet commenced
#define XSLP_NLPSTATUS_SOLUTION                 XPRS_NLPSTATUS_SOLUTION         //  A solution is available
#define XSLP_NLPSTATUS_LOCALLY_OPTIMAL          XPRS_NLPSTATUS_LOCALLY_OPTIMAL       //  Legacy define for 'NLPSTATUS_SOLUTION'
#define XSLP_NLPSTATUS_OPTIMAL                  XPRS_NLPSTATUS_OPTIMAL          //  Globally optimal solution has been found
#define XSLP_NLPSTATUS_NOSOLUTION               XPRS_NLPSTATUS_NOSOLUTION       //  No solution found to the problem
#define XSLP_NLPSTATUS_LOCALLY_INFEASIBLE       XPRS_NLPSTATUS_LOCALLY_INFEASIBLE       //  The problem is locally infeasible or unbounded
#define XSLP_NLPSTATUS_INFEASIBLE               XPRS_NLPSTATUS_INFEASIBLE       //  The problem is infeasible
#define XSLP_NLPSTATUS_UNBOUNDED                XPRS_NLPSTATUS_UNBOUNDED        //  The problem is unbounded
#define XSLP_NLPSTATUS_UNFINISHED               XPRS_NLPSTATUS_UNFINISHED       //  The problem has yet been solved to completion
#define XSLP_NLPSTATUS_UNSOLVED                 XPRS_NLPSTATUS_UNSOLVED         //  The problem could not be solved due to numerical issues
#define XSLP_SOLSTATUS_NONE                     XPRS_NLPSOLSTATUS_NONE          //  Solution is not available
#define XSLP_SOLSTATUS_SOLUTION_NODUALS         XPRS_NLPSOLSTATUS_SOLUTION_NODUALS       //  A solution without dual inforation
#define XSLP_SOLSTATUS_LOCALLYOPTIMAL_WITHDUALS XPRS_NLPSOLSTATUS_LOCALLYOPTIMAL_WITHDUALS       //  A locally optimal solution with dual information
#define XSLP_SOLSTATUS_GLOBALLYOPTIMAL_NODUALS  XPRS_NLPSOLSTATUS_GLOBALLYOPTIMAL_NODUALS       //  A globally optimal solution without dual information
#define XSLP_SOLSTATUS_GLOBALLYOPTIMAL_WITHDUALSXPRS_NLPSOLSTATUS_GLOBALLYOPTIMAL_WITHDUALS       //  A globally optimal solution with dual information
#define XSLP_SOLSTATUS_SOLUTION                 XPRS_NLPSOLSTATUS_SOLUTION_NODUALS       //  A solution without dual inforation
#define XSLP_SOLSTATUS_LOCALLYOPTIMAL           XPRS_NLPSOLSTATUS_LOCALLYOPTIMAL_WITHDUALS       //  A locally optimal solution with dual information 
#define XSLP_SOLSTATUS_GLOBALSOLUTION           XPRS_NLPSOLSTATUS_GLOBALLYOPTIMAL_NODUALS       //  A globally optimal solution without dual information 
#define XSLP_SOLSTATUS_OPTIMAL                  XPRS_NLPSOLSTATUS_GLOBALLYOPTIMAL_WITHDUALS       //  A globally optimal solution with dual information 
#define XSLP_STOP_NONE                          XPRS_STOP_NONE                  //  Value of STOPSTATUS: no interruption
#define XSLP_STOP_TIMELIMIT                     XPRS_STOP_TIMELIMIT             //  Value of STOPSTATUS: time limit hit
#define XSLP_STOP_CTRLC                         XPRS_STOP_CTRLC                 //  Value of STOPSTATUS: control C hit
#define XSLP_STOP_NODELIMIT                     XPRS_STOP_NODELIMIT             //  Value of STOPSTATUS: node limit hit
#define XSLP_STOP_ITERLIMIT                     XPRS_STOP_ITERLIMIT             //  Value of STOPSTATUS: iteration limit hit
#define XSLP_STOP_MIPGAP                        XPRS_STOP_MIPGAP                //  Value of STOPSTATUS: MIP gap is sufficiently small
#define XSLP_STOP_SOLLIMIT                      XPRS_STOP_SOLLIMIT              //  Value of STOPSTATUS: solution limit hit
#define XSLP_STOP_USER                          XPRS_STOP_USER                  //  Value of STOPSTATUS: user interrupt
#define XSLP_STOP_NUMERICALERROR                XPRS_STOP_NUMERICALERROR        //  Value of STOPSTATUS: numerical error
#define XSLP_GRIDENUMERATE                      XPRS_SLPGRIDENUMERATE           //  Value of GRIDHEURSELECT: enumerative search
#define XSLP_GRIDCYCLIC                         XPRS_SLPGRIDCYCLIC              //  Value of GRIDHEURSELECT: cyclic coordinate search
#define XSLP_GRIDANNEALING                      XPRS_SLPGRIDANNEALING           //  Value of GRIDHEURSELECT: simulated annealing



/***************************************************************************\
  * Tolerance                                                              *
\**************************************************************************/
#define XSLP_TOLSET_TC                   XPRS_SLPTOLSET_TC               //  Closure tolerance
#define XSLP_TOLSET_TA                   XPRS_SLPTOLSET_TA               //  Absolute delta tolerance
#define XSLP_TOLSET_RA                   XPRS_SLPTOLSET_RA               //  Relative delta tolerance
#define XSLP_TOLSET_TM                   XPRS_SLPTOLSET_TM               //  Absolute matrix tolerance
#define XSLP_TOLSET_RM                   XPRS_SLPTOLSET_RM               //  Relative matrix tolerance
#define XSLP_TOLSET_TI                   XPRS_SLPTOLSET_TI               //  Absolute impact tolerance
#define XSLP_TOLSET_RI                   XPRS_SLPTOLSET_RI               //  Relative impact tolerance
#define XSLP_TOLSET_TS                   XPRS_SLPTOLSET_TS               //  Absolute slack impact tolerance
#define XSLP_TOLSET_RS                   XPRS_SLPTOLSET_RS               //  Relative slack impact tolerance
#define XSLP_TOLSETBIT_TC                XPRS_SLPTOLSETBIT_TC            //  Closure tolerance
#define XSLP_TOLSETBIT_TA                XPRS_SLPTOLSETBIT_TA            //  Absolute delta tolerance
#define XSLP_TOLSETBIT_RA                XPRS_SLPTOLSETBIT_RA            //  Relative delta tolerance
#define XSLP_TOLSETBIT_TM                XPRS_SLPTOLSETBIT_TM            //  Absolute matrix tolerance
#define XSLP_TOLSETBIT_RM                XPRS_SLPTOLSETBIT_RM            //  Relative matrix tolerance
#define XSLP_TOLSETBIT_TI                XPRS_SLPTOLSETBIT_TI            //  Absolute impact tolerance
#define XSLP_TOLSETBIT_RI                XPRS_SLPTOLSETBIT_RI            //  Relative impact tolerance
#define XSLP_TOLSETBIT_TS                XPRS_SLPTOLSETBIT_TS            //  Absolute slack impact tolerance
#define XSLP_TOLSETBIT_RS                XPRS_SLPTOLSETBIT_RS            //  Relative slack impact tolerance



/***************************************************************************\
  * Convergence specials                                                   *
\**************************************************************************/
#define XSLP_CONVERGEBIT_CTOL               XPRS_SLPCONVERGEBIT_CTOL        //  Closure tolerance                     (1)
#define XSLP_CONVERGEBIT_ATOL               XPRS_SLPCONVERGEBIT_ATOL        //  Delta tolerance                       (2)
#define XSLP_CONVERGEBIT_MTOL               XPRS_SLPCONVERGEBIT_MTOL        //  Matrix tolerance                      (3)
#define XSLP_CONVERGEBIT_ITOL               XPRS_SLPCONVERGEBIT_ITOL        //  Impact tolerance                      (4)
#define XSLP_CONVERGEBIT_STOL               XPRS_SLPCONVERGEBIT_STOL        //  Slack impact tolerance                (5)
#define XSLP_CONVERGEBIT_USER               XPRS_SLPCONVERGEBIT_USER        //  User convergence test                 (6)
#define XSLP_CONVERGEBIT_VTOL               XPRS_SLPCONVERGEBIT_VTOL        //  Objective range check                 (7)
#define XSLP_CONVERGEBIT_XTOL               XPRS_SLPCONVERGEBIT_XTOL        //  Objective range + constraint activity (8)
#define XSLP_CONVERGEBIT_OTOL               XPRS_SLPCONVERGEBIT_OTOL        //  Objective range + active step bounds  (9)
#define XSLP_CONVERGEBIT_WTOL               XPRS_SLPCONVERGEBIT_WTOL        //  Convergence continuation             (10)
#define XSLP_CONVERGEBIT_EXTENDEDSCALING    XPRS_SLPCONVERGEBIT_EXTENDEDSCALING       //  Take scaling of individual variables / rows into account
#define XSLP_CONVERGEBIT_VALIDATION         XPRS_SLPCONVERGEBIT_VALIDATION       //  Continue while validation improves towards the target
#define XSLP_CONVERGEBIT_VALIDATION_K       XPRS_SLPCONVERGEBIT_VALIDATION_K       //  Continue while KKT validation improves towards the target
#define XSLP_CONVERGEBIT_NOQUADCHECK        XPRS_SLPCONVERGEBIT_NOQUADCHECK       //  Allow convex quadratic problem to convergence on extended criteria



/***************************************************************************\
  * Variable status                                                        *
\**************************************************************************/
#define XSLP_HASNOCOEFS                  XPRS_SLPHASNOCOEFS              //  The variable has no coefficients
#define XSLP_HASDELTA                    XPRS_SLPHASDELTA                //  The column has a delta vector
#define XSLP_HASIV                       XPRS_SLPHASIV                   //  The column has an initial value
#define XSLP_HASCALCIV                   XPRS_SLPHASCALCIV               //  The column has an initial calculated value
#define XSLP_ISDELTA                     XPRS_SLPISDELTA                 //  The variable is a delta variable
#define XSLP_ISPLUSPENALTYDELTA          XPRS_SLPISPLUSPENALTYDELTA       //  The variable is a positive penalty delta
#define XSLP_ISMINUSPENALTYDELTA         XPRS_SLPISMINUSPENALTYDELTA       //  The variable is a negative penalty delta
#define XSLP_ISPENALTYDELTA              XPRS_SLPISPENALTYDELTA          //  The variable is a penalty delta variable
#define XSLP_ISPLUSERRORVECTOR           XPRS_SLPISPLUSERRORVECTOR       //  The variable is a positive error vector
#define XSLP_ISMINUSERRORVECTOR          XPRS_SLPISMINUSERRORVECTOR       //  The variable is a negative error vector
#define XSLP_ISERRORVECTOR               XPRS_SLPISERRORVECTOR           //  The variable is an error vector
#define XSLP_ISMISCVECTOR                XPRS_SLPISMISCVECTOR            //  The variable is a miscellaneous vector
#define XSLP_ISEQUALSCOLUMN              XPRS_SLPISEQUALSCOLUMN          //  The variable is the equals column
#define XSLP_PRESOLVEPROTECT             XPRS_NLPPRESOLVEPROTECT         //  Do not eliminate / remove the column in presolve (hidden usage)
#define XSLP_HASCONVERGED                XPRS_SLPHASCONVERGED            //  The variable has converged to a solution
#define XSLP_ACTIVESTEPBOUND             XPRS_SLPACTIVESTEPBOUND         //  The variable has active stepbounds
#define XSLP_ACTIVESBROW                 XPRS_SLPACTIVESBROW             //  The variable has an active step bound row
#define XSLP_NOTSLPVAR                   0x100000                        //  The variable is not an SLP variable
#define XSLP_ISSTRUCTURALCOLUMN          XPRS_SLPISSTRUCTURALCOLUMN       //  The variable is one of the structural columns
#define XSLP_ISINCOEFS                   XPRS_SLPISINCOEFS               //  The variable appears in non-linear coefficients. Valid after construct.
#define XSLP_ISINGLOBAL                  XPRS_SLPISINGLOBAL              //  The variable is involved in the global items
#define XSLP_HASZEROBOUND                XPRS_SLPHASZEROBOUND            //  The variable has a zero lower bound
#define XSLP_FIXEDVAR                    XPRS_SLPFIXEDVAR                //  The variable is a fixed value variable.
#define XSLP_BOUNDSSET                   XPRS_SLPBOUNDSSET               //  The variable is part of a bounds set
#define XSLP_USEFULDELTA                 XPRS_SLPUSEFULDELTA             //  Check/mark as a useful delta column
#define XSLP_NOUSEFULDELTA               XPRS_SLPNOUSEFULDELTA           //  Check/mark as a non-useful delta column
#define XSLP_ISINTEGER                   XPRS_SLPISINTEGER               //  The variable is an integer variable
#define XSLP_CASCADECONTRACTION          XPRS_SLPCASCADECONTRACTION       //



/***************************************************************************\
  * Row status                                                              *
\**************************************************************************/
#define XSLP_ISUPDATEROW                 XPRS_SLPISUPDATEROW             //  The row is an update row
#define XSLP_ISPENALTYROW                XPRS_SLPISPENALTYROW            //  The row is a penalty row
#define XSLP_ISMISCROW                   XPRS_SLPISMISCROW               //  The row is a miscellaneous row
#define XSLP_ISSBROW                     XPRS_SLPISSBROW                 //  The row is a step bound row
#define XSLP_HASPLUSERROR                XPRS_SLPHASPLUSERROR            //  The row has a positive error vector
#define XSLP_HASMINUSERROR               XPRS_SLPHASMINUSERROR           //  The row has a negative error vector
#define XSLP_HASERROR                    XPRS_SLPHASERROR                //  The row has an error vector
#define XSLP_ISDETERMININGROW            XPRS_SLPISDETERMININGROW        //  The row is a determining row
#define XSLP_NOERRORVECTORS              XPRS_SLPNOERRORVECTORS          //  The row has no error vectors
#define XSLP_HASNONZEROCOEF              XPRS_SLPHASNONZEROCOEF          //  The row has non-zero coefficients
#define XSLP_REDUNDANTROW                XPRS_SLPREDUNDANTROW            //  The row is redundant
#define XSLP_UNCONVERGEDROW              XPRS_SLPUNCONVERGEDROW          //  The row is unconverged
#define XSLP_ACTIVEPENALTY               XPRS_SLPACTIVEPENALTY           //  The row has active penalty vectors
#define XSLP_HASSLPELEMENT               XPRS_SLPHASSLPELEMENT           //  The row has SLP elements
#define XSLP_TRANSFERROW                 XPRS_SLPTRANSFERROW             //  The row is an objective transfer row



/***************************************************************************\
  * Augmentation settings                                                  *
\**************************************************************************/
#define XSLP_MINIMUMAUGMENTATION         XPRS_SLPMINIMUMAUGMENTATION       //  (   1 ) Perform minimal augmentation only
#define XSLP_EVENHANDEDAUGMENTATION      XPRS_SLPEVENHANDEDAUGMENTATION       //  (   2 ) Perform even-handed augmentation
#define XSLP_EQUALITYERRORVECTORS        XPRS_SLPEQUALITYERRORVECTORS       //  (   4 ) Penalty error vectors on all non-linear equality constraints
#define XSLP_ALLERRORVECTORS             XPRS_SLPALLERRORVECTORS         //  (   8 ) Penalty error vectors on all non-linear inequality constraints
#define XSLP_PENALTYDELTAVECTORS         XPRS_SLPPENALTYDELTAVECTORS       //  (  16 ) Penalty vectors to exceed step bounds
#define XSLP_AMEANWEIGHT                 XPRS_SLPAMEANWEIGHT             //  (  32 ) Use arithmetic means to estimate penalty weights
#define XSLP_SBFROMVALUES                XPRS_SLPSBFROMVALUES            //  (  64 ) Estimate step bounds from values of row coefficients
#define XSLP_SBFROMABSVALUES             XPRS_SLPSBFROMABSVALUES         //  ( 128 ) Estimate step bounds from absolute values of row coefficients
#define XSLP_STEPBOUNDROWS               XPRS_SLPSTEPBOUNDROWS           //  ( 256 ) Row-based step bounds
#define XSLP_ALLROWERRORVECTORS          XPRS_SLPALLROWERRORVECTORS       //  ( 512 ) Penalty error vectors on all constraints
#define XSLP_NOUPDATEIFONLYIV            XPRS_SLPNOUPDATEIFONLYIV        //  (1024 ) Having an IV itself will not cause the augmentation to include the corresponding delta variable 
#define XSLP_NOFORMULADOMAINIV           XPRS_SLPNOFORMULADOMAINIV       //  (2048 ) Skip formula domain propagating into initial values for default IV values
#define XSLP_SKIPIVLPHEURISTICS          XPRS_SLPSKIPIVLPHEURISTICS       //  (4096 ) Avoid running an LP around fixed initial values trying to get feasible 



/***************************************************************************\
  * Algorithm settings                                                      *
\**************************************************************************/
#define XSLP_NOSTEPBOUNDS                XPRS_SLPNOSTEPBOUNDS            //  (    1 ) Do not apply step bounds
#define XSLP_STEPBOUNDSASREQUIRED        XPRS_SLPSTEPBOUNDSASREQUIRED       //  (    2 ) Apply step bounds to SLP delta vectors only when required
#define XSLP_ESTIMATESTEPBOUNDS          XPRS_SLPESTIMATESTEPBOUNDS       //  (    4 ) Estimate step bounds from early SLP iterations
#define XSLP_DYNAMICDAMPING              XPRS_SLPDYNAMICDAMPING          //  (    8 ) Use dynamic damping
#define XSLP_HOLDVALUES                  XPRS_SLPHOLDVALUES              //  (   16 ) Do not update values which are converged within strict tolerance
#define XSLP_RETAINPREVIOUSVALUE         XPRS_SLPRETAINPREVIOUSVALUE       //  (   32 ) Retain previous value when cascading if determining row is zero
#define XSLP_RESETDELTAZ                 XPRS_SLPRESETDELTAZ             //  (   64 ) Reset XSLP_DELTA_Z to zero when converged and continue SLP
#define XSLP_QUICKCONVERGENCECHECK       XPRS_SLPQUICKCONVERGENCECHECK       //  (  128 ) Quick convergence check
#define XSLP_ESCALATEPENALTIES           XPRS_SLPESCALATEPENALTIES       //  (  256 ) Escalate penalties
#define XSLP_SWITCHTOPRIMAL              XPRS_SLPSWITCHTOPRIMAL          //  (  512 ) Use the primal simplex algorithm when all error vectors become inactive 
#define XSLP_NONZEROBOUND                XPRS_SLPNONZEROBOUND            //  ( 1024 ) Not currently used
#define XSLP_MAXCOSTOPTION               XPRS_SLPMAXCOSTOPTION           //  ( 2048 ) Continue optimizing after penalty cost reaches maximum
#define XSLP_RESIDUALERRORS              XPRS_SLPRESIDUALERRORS          //  ( 4096 ) Accept a solution which has converged even if there are still significant active penalty error vectors 
#define XSLP_NOLPPOLISHING               XPRS_SLPNOLPPOLISHING           //  ( 8192 ) Skip the clean up call if the LP postsolve returns a slightly feasible, but claimed optimal solution 
#define XSLP_CASCADEDBOUNDS              XPRS_SLPCASCADEDBOUNDS          //  (16384 ) Step bounds are updated to accommodate cascaded values (otherwise cascaded values are pushed to respect step bounds 
#define XSLP_CLAMPEXTENDEDACTIVESB       XPRS_SLPCLAMPEXTENDEDACTIVESB       //  (32768 ) Clamp variables converged on extended criteria only with active step bounds
#define XSLP_CLAMPEXTENDEDALL            XPRS_SLPCLAMPEXTENDEDALL        //  (65536 ) Clamp all variables converged on extended criteria only



/***************************************************************************\
  * MIP-Algorithm settings                                                  *
\**************************************************************************/
#define XSLP_MIPINITIALSLP               XPRS_SLPMIPINITIALSLP           //  (    1 ) Solve the initial SLP to convergence
#define XSLP_MIPINITIALRELAXSLP          XPRS_SLPMIPINITIALRELAXSLP       //  (    4 ) Relax step-bounds according to XSLP_MIPRELAXSTEPBOUNDS after initial node 
#define XSLP_MIPINITIALFIXSLP            XPRS_SLPMIPINITIALFIXSLP        //  (    8 ) Fix step-bounds according to XLSP_MIPFIXSTEPBOUNDS after initial node 
#define XSLP_MIPNODERELAXSLP             XPRS_SLPMIPNODERELAXSLP         //  (   16 ) Relax step-bounds according to XSLP_MIPRELAXSTEPBOUNDS at each node
#define XSLP_MIPNODEFIXSLP               XPRS_SLPMIPNODEFIXSLP           //  (   32 ) Fix step-bounds according to XSLP_MIPFIXSTEPBOUNDS at each node
#define XSLP_MIPNODELIMITSLP             XPRS_SLPMIPNODELIMITSLP         //  (   64 ) Limit iterations at each node to XSLP_MIPITERLIMIT
#define XSLP_MIPFINALRELAXSLP            XPRS_SLPMIPFINALRELAXSLP        //  (  128 ) Relax step-bounds according to XSLP_MIPRELAXSTEPBOUNDS after MIP solution is found 
#define XSLP_MIPFINALFIXSLP              XPRS_SLPMIPFINALFIXSLP          //  (  256 ) Fix step-bounds according to XSLP_MIPFIXSTEPBOUNDS after MIP solution is found 
#define XSLP_MIPWITHINSLP                XPRS_SLPMIPWITHINSLP            //  (  512 ) Use MIP at each SLP iteration instead of SLP at each node
#define XSLP_SLPTHENMIP                  XPRS_SLPSLPTHENMIP              //  ( 1024 ) Use MIP on converged SLP solution and then SLP on the resulting MIP solution 
#define XSLP_ROOTMIPDRIVEN               XPRS_SLPROOTMIPDRIVEN           //  ( 4096 ) Only re-solve as an SLP problem for the incumbent solutions



/***************************************************************************\
  * Formula and coefficient                                                *
\**************************************************************************/



/***************************************************************************\
  * Function types                                                         *
\**************************************************************************/
#define XSLP_USERFUNCTION1               1                               //  A user function in a user dll taking a single argument
#define XSLP_MOSELFUNCTION1              2                               //  A Mosel user function taking a single argument
#define XSLP_USERFUNCTIONA               3                               //  A user function in a user dll taking multiple arguments
#define XSLP_INTERNAL_EXETYPE            0                               //  Define the UF executable type as being as internal, function pointer will be updated by user code
#define XSLP_DLL_EXETYPE                 1                               //  Define the UF executable type as being a dll
#define XSLP_MOSEL_EXETYPE               5                               //  Define the UF executable type as being a compiled Mosel function



/***************************************************************************\
  * Calculation status                                                     *
\**************************************************************************/



/***************************************************************************\
  * Info tokens                                                            *
\**************************************************************************/
#define XSLPINFO_CALLERFLAG               1       //  Position in 'arginfo' for: caller flag
#define XSLPINFO_NINPUT                   2       //  Position in 'arginfo' for: number of inout arguments to the function
#define XSLPINFO_NOUTPUT                  3       //  Position in 'arginfo' for: number of expected output arguments
#define XSLPINFO_NDELTA                   4       //  Position in 'arginfo' for: number of expected deltas returned
#define XSLPINFO_NINSTRING                5       //  Position in 'arginfo' for: number of strings for input
#define XSLPINFO_NOUTSTRING               6       //  Position in 'arginfo' for: number of string for output
#define XSLPINFO_FUNCNUM                  7       //  Position in 'arginfo' for: functions number
#define XSLPINFO_INSTANCE                 8       //  Position in 'arginfo' for: function instance number



/***************************************************************************\
  * Misc settings                                                          *
\**************************************************************************/
#define XSLP_RECALC                              XPRS_NLPRECALC       //  Setting of FUNCEVAL: re-evaluate user functions at each iteration
#define XSLP_TOLCALC                             XPRS_NLPTOLCALC       //  Setting of FUNCEVAL: re evaluate UFs if independent variables change outside tolerance 
#define XSLP_ALLCALCS                            XPRS_NLPALLCALCS       //  Setting of FUNCEVAL: overwrite user function specific re-evaluation settings
#define XSLP_2DERIVATIVE                         XPRS_NLP2DERIVATIVE       //  Setting of FUNCEVAL: use tangential derivatives
#define XSLP_1DERIVATIVE                         XPRS_NLP1DERIVATIVE       //  Setting of FUNCEVAL: use forward derivatives
#define XSLP_ALLDERIVATIVES                      XPRS_NLPALLDERIVATIVES       //  Setting of FUNCEVAL: overwrite user function specific derivative settings
#define XSLP_CDECL                                     0x100       //  Setting of UFEXETYPE: CDECL call (Windows only)
#define XSLP_STDCALL                                   0x000       //  Setting of UFEXETYPE: standard call
#define XSLP_INSTANCEFUNCTION                    XPRS_NLPINSTANCEFUNCTION       //  Setting of UFEXETYPE: instantiate function
#define XSLP_NETCALL                                   0x400       //
#define XSLP_DEDUCECONSTDERIVS                         0x800       //  Setting of UFEXETYPE: assume derivatives which do not change outside tolerance are constant 
#define XSLP_SOMECONSTDERIVS                          0x1000       //  Setting of UFEXETYPE: interrogate function for constant derivatives
#define XSLP_PROVIDESDERIVATIVES                      0x1000       //  User function setting, the function provides its own derivatives
#define XSLP_MULTIPURPOSE                             0x2000       //  Setting of UFEXETYPE: multi-valued function with dependency matrix
#define XSLP_MULTIVALUED                           0x1000000       //  Setting of UFEXETYPE: function is multivalued
#define XSLP_NODERIVATIVES                        0x10000000       //  Setting of UFEXETYPE: function is non differentiable
#define XSLP_PRESOLVEOPS_GENERAL                 XPRS_NLPPRESOLVEOPS_GENERAL       //  PRESOLVEOPS: general (simple reductions) presolve
#define XSLP_PRESOLVEFIXZERO                     XPRS_NLPPRESOLVEFIXZERO       //  PRESOLVEOPS: explicitly fix columns identified as fixed to zero
#define XSLP_PRESOLVEFIXALL                      XPRS_NLPPRESOLVEFIXALL       //  PRESOLVEOPS: explicitly fix all columns identified as fixed
#define XSLP_PRESOLVESETBOUNDS                   XPRS_NLPPRESOLVESETBOUNDS       //  PRESOLVEOPS: SLP bound tightening
#define XSLP_PRESOLVEINTBOUNDS                   XPRS_NLPPRESOLVEINTBOUNDS       //  PRESOLVEOPS: MISLP bound tightening
#define XSLP_PRESOLVEDOMAIN                      XPRS_NLPPRESOLVEDOMAIN       //  PRESOLVEOPS: Perform reduction based on function domains (e.g. log, sqrt)
#define XSLP_NOPRESOLVECOEFFICIENTS              XPRS_SLPNOPRESOLVECOEFFICIENTS       //  PRESOLVEOPS: do not presolve coefficients
#define XSLP_NOPRESOLVEDELTAS                    XPRS_SLPNOPRESOLVEDELTAS       //  PRESOLVEOPS: do not remove delta variables
#define XSLP_PRESOLVEOPS_NO_DUAL_SIDE            XPRS_NLPPRESOLVEOPS_NO_DUAL_SIDE       //  PRESOLVEOPS: avoid reductions that can't be dual postsolved
#define XSLP_PRESOLVEOPS_ELIMINATIONS            XPRS_NLPPRESOLVEOPS_ELIMINATIONS       //  PRESOLVEOPS: apply nlp eliminations, i.e. look for defined variables
#define XSLP_PRESOLVEOPS_NOLINEAR                XPRS_NLPPRESOLVEOPS_NOLINEAR       //  PRESOVELOPS: do not apply linear reductions in the nlp level
#define XSLP_PRESOLVEOPS_NOSIMPLIFIER            XPRS_NLPPRESOLVEOPS_NOSIMPLIFIER       //  PRESOVELOPS: do not apply the formula simplifier
#define XSLP_PRESOLVEOPS_KEEPNAMES                    0x4000       //  PRESOLVEOPS: names should be kept in the presolved problem
#define XSLP_PRESOLVELEVEL_LOCALIZED                       1       //  Individual rows only presolve, no nonlinear transformations
#define XSLP_PRESOLVELEVEL_BASIC                 XPRS_NLPPRESOLVELEVEL_BASIC       //  Individual rows and bounds only presolve, no nonlinear transformations
#define XSLP_PRESOLVELEVEL_LINEAR                XPRS_NLPPRESOLVELEVEL_LINEAR       //  Presolve allowing changing problem dimension, no nonlinear transformations
#define XSLP_PRESOLVELEVEL_FULL                  XPRS_NLPPRESOLVELEVEL_FULL       //  Full presolve
#define XSLP_FUNCINFOSIZE                                 12       //  Number of integers the FunctionInfo structure consists of
#define XSLP_GETUFNAME                                    31       //  XSLPuserfuncinfo: Retrieve the external name of the user function
#define XSLP_GETUFPARAM1                                  32       //  XSLPuserfuncinfo: Retrieve the first string parameter
#define XSLP_GETUFPARAM2                                  33       //  XSLPuserfuncinfo: Retrieve the second string parameter
#define XSLP_GETUFPARAM3                                  34       //  XSLPuserfuncinfo: Retrieve the third string parameter
#define XSLP_GETUFARGTYPE                                 35       //  XSLPuserfuncinfo: Retrieve the argument types
#define XSLP_GETUFEXETYPE                                 36       //  XSLPuserfuncinfo: Retrieve the linkage type
#define XSLP_SETUFNAME                                    41       //  XSLPuserfuncinfo: Set the external name of the user function
#define XSLP_SETUFPARAM1                                  42       //  XSLPuserfuncinfo: Set the first string parameter
#define XSLP_SETUFPARAM2                                  43       //  XSLPuserfuncinfo: Set the second string parameter
#define XSLP_SETUFPARAM3                                  44       //  XSLPuserfuncinfo: Set the third string parameter
#define XSLP_SETUFARGTYPE                                 45       //  XSLPuserfuncinfo: Set the argument types
#define XSLP_SETUFEXETYPE                                 46       //  XSLPuserfuncinfo: Set the linkage type
#define XSLP_GETROWNUMPENALTYERRORS                      201       //  Setting of XSLProwinfo: get the number of times the penalty error vector has been active 
#define XSLP_GETROWMAXPENALTYERROR                       202       //  Setting of XSLProwinfo: get the maximum size of the penalty error vector activity 
#define XSLP_GETROWTOTALPENALTYERROR                     203       //  Setting of XSLProwinfo: get the total of the penalty error vector activities
#define XSLP_GETROWAVERAGEPENALTYERROR                   204       //  Setting of XSLProwinfo: get the average size of the penalty error vector activity 
#define XSLP_GETROWCURRENTPENALTYERROR                   205       //  Setting of XSLProwinfo: get the size of the penalty error vector activity in the current iteration
#define XSLP_GETROWCURRENTPENALTYFACTOR                  206       //  Setting of XSLProwinfo: get the size of the penalty error factor for the current iteration 
#define XSLP_SETROWPENALTYFACTOR                         207       //  Setting of XSLProwinfo: set the size of the penalty error factor for the next iteration 
#define XSLP_GETROWPENALTYCOLUMN1                        208       //  Setting of XSLProwinfo: get the index of the penalty column for the row (+)
#define XSLP_GETROWPENALTYCOLUMN2                        209       //  Setting of XSLProwinfo: get the index of the second penalty column for an equality row (-) 
#define XSLP_CASCADE_ALL                         XPRS_SLPCASCADE_ALL       //  Setting of CASCADE: cascade all variables with determining rows
#define XSLP_CASCADE_COEF_VAR                    XPRS_SLPCASCADE_COEF_VAR       //  Setting of CASCADE: cascade SLP variables which appear in coefficients, and would change by more than XPRS_FEASTOL 
#define XSLP_CASCADE_ALL_COEF_VAR                XPRS_SLPCASCADE_ALL_COEF_VAR       //  Setting of CASCADE: cascade all SLP variables which appear in coefficients
#define XSLP_CASCADE_STRUCT_VAR                  XPRS_SLPCASCADE_STRUCT_VAR       //  Setting of CASCADE: cascade SLP variables which are structural and which would change by more than XPRS_FEASTOL 
#define XSLP_CASCADE_ALL_STRUCT_VAR              XPRS_SLPCASCADE_ALL_STRUCT_VAR       //  Setting of CASCADE: cascade all SLP variables which are structural
#define XSLP_CASCADE_SECONDARY_GROUPS            XPRS_SLPCASCADE_SECONDARY_GROUPS       //  Setting of CASCADE: create secondary grouping for instantiated UF rows
#define XSLP_CASCADE_DRCOL_PREVOUSVALUE          XPRS_SLPCASCADE_DRCOL_PREVOUSVALUE       //  Setting of CASCADE: DRCOLTOL fixes at previous value, not current
#define XSLP_CASCADE_DRCOL_PVRANGE               XPRS_SLPCASCADE_DRCOL_PVRANGE       //  Setting of CASCADE: DRCOLTOL fixes defines a range around the previous value
#define XSLP_CASCADE_AUTOAPPLY                   XPRS_SLPCASCADE_AUTOAPPLY       //  Setting of CASCADE: Automatically determine when to apply cascading
#define XSLP_SOLVER_AUTO                         XPRS_LOCALSOLVER_AUTO       //  Setting of LOCALSOLVER: autoselect / not selected yet
#define XSLP_SOLVER_XSLP                         XPRS_LOCALSOLVER_XSLP       //  Setting of LOCALSOLVER: use XSLP
#define XSLP_SOLVER_KNITRO                       XPRS_LOCALSOLVER_KNITRO       //  Setting of LOCALSOLVER: use KNITRO
#define XSLP_SOLVER_OPTIMIZER                    XPRS_LOCALSOLVER_OPTIMIZER       //  Setting of LOCALSOLVER: use the optimizer
#define XSLP_MSSET_INITIALVALUES                 XPRS_MSSET_INITIALVALUES       //  Option for the multi-start: load different initial points
#define XSLP_MSSET_SOLVERS                       XPRS_MSSET_SOLVERS       //  Option for the multi-start: load all solvers to try
#define XSLP_MSSET_SLP_BASIC                     XPRS_MSSET_SLP_BASIC       //  Option for the multi-start: try the fundamental SLP controls
#define XSLP_MSSET_SLP_EXTENDED                  XPRS_MSSET_SLP_EXTENDED       //  Option for the multi-start: try an extensive set of SLP controls
#define XSLP_MSSET_KNITRO_BASIC                  XPRS_MSSET_KNITRO_BASIC       //  Option for the multi-start: try the fundamental Knitro controls
#define XSLP_MSSET_KNITRO_EXTENDED               XPRS_MSSET_KNITRO_EXTENDED       //  Option for the multi-start: try an extensive set of Knitro controls
#define XSLP_MSSET_INITIALFILTERED               XPRS_MSSET_INITIALFILTERED       //  Option for the multi-start: load different initial points filtered by merit
#define XSLP_CLASS_GENERAL                                 0       //  Problem classification: general
#define XSLP_CLASS_LP                                      1       //  Problem classification: linear
#define XSLP_CLASS_CONVEX_Q                                2       //  Problem classification: convex quadratic, including convex QCQP
#define XSLP_CLASS_NON_CONVEX_Q                            3       //  Problem classification: non-convex quadratic
#define XSLP_CLASS_SOCP                                    4       //  Problem classification: second order cone in the standard form
#define XSLP_CLASS_SIMPLE_BLENDING                         5       //  Problem classification: simple blending constraints
#define XSLP_CLASS_GENERAL_PROCESS_STRUCTURE               6       //  Problem classification: general with process structural process information
#define XSLP_CLASS_TRIGONOMETRICAL                         7       //  Problem classification: dominantly trigonometrical
#define XSLP_CLASS_FRACTIONAL_EXPONENTIAL                  8       //  Problem classification: exponentials with a fractional power
#define XSLP_CLASS_POTENTIAL_GENCON_COMPATIBLE             9       //  Problem classification: potentially a general constraints compatible problem
#define XSLP_CLASS_GENCON_COMPATIBLE                      10       //  Problem classification: a general constraints compatible problem
#define XSLP_KKT_CALCULATION_RECALCULATE_RDJ     XPRS_KKT_CALCULATION_RECALCULATE_RDJ       //  KKT calculations: recalculate the rdj using the current duals
#define XSLP_KKT_CALCULATION_MINIMZE_KKT_ERROR   XPRS_KKT_CALCULATION_MINIMZE_KKT_ERROR       //  KKT calculations: fix solution and minimize dual side violations
#define XSLP_KKT_CALCULATION_MEASURE_BOTH        XPRS_KKT_CALCULATION_MEASURE_BOTH       //  KKT calculations: both calculate and minimize error
#define XSLP_KKT_CALCULATION_ACTIVITY_BASED      XPRS_KKT_CALCULATION_ACTIVITY_BASED       //  KKT calculations: use constraint activity to define active constraints
#define XSLP_KKT_CALCULATION_RESPECT_BASIS       XPRS_KKT_CALCULATION_RESPECT_BASIS       //  KKT calculations: use the basis status if any to define active constraints
#define XSLP_KKT_CALCULATION_ACTIVITY_BOTH       XPRS_KKT_CALCULATION_ACTIVITY_BOTH       //  KKT calculations: use the basis status & activity to define active constraints 
#define XSLP_KKT_JUST_CALCULATE                  XPRS_KKT_JUST_CALCULATE       //  KKT calculations: only do the calculations but do not modify the dual solution 
#define XSLP_KKT_UPDATE_MULTIPLIERS              XPRS_KKT_UPDATE_MULTIPLIERS       //  KKT calculations: update the dual side solution
#define XSLP_BARSTARTOPS_STALLING_OBJECTIVE                1       //  Barrier stalling checks: check progress in the objective
#define XSLP_BARSTARTOPS_STALLING_NUMERICAL                2       //  Barrier stalling checks: check for numerical failures in the barrier
#define XSLP_BARSTARTOPS_ALLOWINTERIORSOLUTION             4       //  Barrier start option: if a non-crossed over solution is allowable
#define XSLP_BARSTARTOPS_POSTSOLVEFEASIBLITY               8       //  Barrier start option: check postsolved feasiblity of barrier iterations
#define XSLP_PARMTYP_INT                                 001       //  Integer parameter
#define XSLP_PARMTYP_DBL                                 002       //  Double parameter
#define XSLP_PARMTYP_STR                                 004       //  String parameter
#define XSLP_PARMTYP_READ                                010       //  Parameter is readable
#define XSLP_PARMTYP_WRITE                               020       //  Parameter is writeable
#define XSLP_UFARGTYPE_OMITTED                             0       //  Argument is omitted
#define XSLP_UFARGTYPE_NULL                                1       //  Argument is NULL
#define XSLP_UFARGTYPE_INTEGER                             2       //  Argument type is integer
#define XSLP_UFARGTYPE_DOUBLE                              3       //  Argument type is double
#define XSLP_UFARGTYPE_VARIANT                             4       //  Argument type is variant
#define XSLP_UFARGTYPE_CHAR                                6       //  Argument type is string
#define XSLP_ZEROCRITERION_NBSLPVAR                        1       //  Setting of ZEROCRITERION: remove placeholders in nonbasic SLP variables
#define XSLP_ZEROCRITERION_NBDELTA                         2       //  Setting of ZEROCRITERION: remove placeholders in nonbasic delta variables
#define XSLP_ZEROCRITERION_SLPVARNBUPDATEROW               4       //  Setting of ZEROCRITERION: remove placeholders in a basic SLP variable if its update row is nonbasic 
#define XSLP_ZEROCRITERION_DELTANBUPSATEROW                8       //  Setting of ZEROCRITERION: remove placeholders in a basic delta variable if its update row is nonbasic and the corresponding SLP variable is nonbasic 
#define XSLP_ZEROCRITERION_DELTANBDRROW                   16       //  Setting of ZEROCRITERION: remove placeholders in a basic delta variable if the determining row for the corresponding SLP variable is nonbasic 
#define XSLP_ZEROCRITERION_PRINT                          32       //  Setting of ZEROCRITERION: print information about zero placeholders
#define XSLP_TRACEMASK_GENERALFIT                XPRS_SLPTRACEMASK_GENERALFIT       //  Setting of TRACEMASKOPS: the variable name is used a mask, not an exact fit
#define XSLP_TRACEMASK_ROWS                      XPRS_SLPTRACEMASK_ROWS       //  Setting of TRACEMASKOPS: use mask to trace rows
#define XSLP_TRACEMASK_COLS                      XPRS_SLPTRACEMASK_COLS       //  Setting of TRACEMASKOPS: use mask to trace columns
#define XSLP_TRACEMASK_CASCADE                   XPRS_SLPTRACEMASK_CASCADE       //  Setting of TRACEMASKOPS: use mask to trace cascaded columns
#define XSLP_TRACEMASK_TYPE                      XPRS_SLPTRACEMASK_TYPE       //  Setting of TRACEMASKOPS: show row - column category
#define XSLP_TRACEMASK_SLACK                     XPRS_SLPTRACEMASK_SLACK       //  Setting of TRACEMASKOPS: trace slack values
#define XSLP_TRACEMASK_DUAL                      XPRS_SLPTRACEMASK_DUAL       //  Setting of TRACEMASKOPS: trace dual values
#define XSLP_TRACEMASK_WEIGHT                    XPRS_SLPTRACEMASK_WEIGHT       //  Setting of TRACEMASKOPS: trace row penalty multipliers
#define XSLP_TRACEMASK_SOLUTION                  XPRS_SLPTRACEMASK_SOLUTION       //  Setting of TRACEMASKOPS: trace variable values
#define XSLP_TRACEMASK_REDUCEDCOST               XPRS_SLPTRACEMASK_REDUCEDCOST       //  Setting of TRACEMASKOPS: trace reduced costs
#define XSLP_TRACEMASK_SLPVALUE                  XPRS_SLPTRACEMASK_SLPVALUE       //  Setting of TRACEMASKOPS: trace slp value (value used in linearization-cascaded)
#define XSLP_TRACEMASK_STEPBOUND                 XPRS_SLPTRACEMASK_STEPBOUND       //  Setting of TRACEMASKOPS: trace step bounds
#define XSLP_TRACEMASK_CONVERGE                  XPRS_SLPTRACEMASK_CONVERGE       //  Setting of TRACEMASKOPS: trace convergence status
#define XSLP_TRACEMASK_LINESEARCH                XPRS_SLPTRACEMASK_LINESEARCH       //  Setting of TRACEMASKOPS: use mask to trace line search
#define XSLP_FILTER_KEEPBEST                     XPRS_SLPFILTER_KEEPBEST       //  Setting of FILTER: retrain solution best according to the merit function
#define XSLP_FILTER_CASCADE                      XPRS_SLPFILTER_CASCADE       //  Setting of FILTER: check cascaded solutions for improvements in merit function 
#define XSLP_FILTER_ZEROLINESEARCH               XPRS_SLPFILTER_ZEROLINESEARCH       //  Setting of FILTER: force minimum step sizes in line search
#define XSLP_FILTER_ZEROLINESEARCHTR             XPRS_SLPFILTER_ZEROLINESEARCHTR       //  Setting of FILTER: accept the trust region step is the line search fails
#define XSLP_ANALYZE_RECORDLINEARIZATION         XPRS_SLPANALYZE_RECORDLINEARIZATION       //  Setting of ANALYZE: add solutions of the linearizations to the solution pool
#define XSLP_ANALYZE_RECORDCASCADE               XPRS_SLPANALYZE_RECORDCASCADE       //  Setting of ANALYZE: add cascaded solutions to the solution pool
#define XSLP_ANALYZE_RECORDLINESEARCH            XPRS_SLPANALYZE_RECORDLINESEARCH       //  Setting of ANALYZE: add line search solutions to the solution pool
#define XSLP_ANALYZE_EXTENDEDFINALSUMMARY        XPRS_SLPANALYZE_EXTENDEDFINALSUMMARY       //  Setting of ANALYZE: included an extended iteration summary
#define XSLP_ANALYZE_INFEASIBLE_ITERATION        XPRS_SLPANALYZE_INFEASIBLE_ITERATION       //  Setting of ANALYZE: run infeasibility analysis on infeasible iterations
#define XSLP_ANALYZE_AUTOSAVEPOOL                XPRS_SLPANALYZE_AUTOSAVEPOOL       //  Setting of ANALYZE: automatically save the solution pool to file
#define XSLP_ANALYZE_SAVELINEARIZATIONS          XPRS_SLPANALYZE_SAVELINEARIZATIONS       //  Setting of ANALYZE: automatically save the linearizations
#define XSLP_ANALYZE_SAVEITERBASIS               XPRS_SLPANALYZE_SAVEITERBASIS       //  Setting of ANALYZE: automatically save the initial basis of the linearizations 
#define XSLP_ANALYZE_SAVEFILE                    XPRS_SLPANALYZE_SAVEFILE       //  Setting of ANALYZE: create a save file at the beginning of an iteration
#define XSLP_REFORMULATE_SLP2QP                  XPRS_NLPREFORMULATE_SLP2QP       //  Setting of REFORMULATE: solve convex QP objectives using the XPRS library
#define XSLP_REFORMULATE_QP2SLP                  XPRS_NLPREFORMULATE_QP2SLP       //  Setting of REFORMULATE: convert non-convex QP objectives to SLP constructs
#define XSLP_REFORMULATE_SLP2QCQP                XPRS_NLPREFORMULATE_SLP2QCQP       //  Setting of REFORMULATE: solve convex QCQP constraints using the XPRS library
#define XSLP_REFORMULATE_QCQP2SLP                XPRS_NLPREFORMULATE_QCQP2SLP       //  Setting of REFORMULATE: convert non-convex QCQP constraints to SLP constructs
#define XSLP_REFORMULATE_SOCP2SLP                XPRS_NLPREFORMULATE_SOCP2SLP       //  Setting of REFORMULATE: convert SOCP constraints to XPRS - SLP hybrid
#define XSLP_REFORMULATE_QPSOLVE                 XPRS_NLPREFORMULATE_QPSOLVE       //  Setting of REFORMULATE: covexity may be checked by trying to solve the problem 
#define XSLP_REFORMULATE_PWL                     XPRS_NLPREFORMULATE_PWL       //  Setting of REFORMULATE: convert PWLs to the optimizer
#define XSLP_REFORMULATE_ABS                     XPRS_NLPREFORMULATE_ABS       //  Setting of REFORMULATE: convert ABS functions to the optimizer if compatible
#define XSLP_REFORMULATE_MINMAX                  XPRS_NLPREFORMULATE_MINMAX       //  Setting of REFORMULATE: convert MINMAX functions to the optimizer if compatible
#define XSLP_REFORMULATE_ALLABS                  XPRS_NLPREFORMULATE_ALLABS       //  Setting of REFORMULATE: convert ABS functions to the optimizer: always
#define XSLP_REFORMULATE_ALLMINMAX               XPRS_NLPREFORMULATE_ALLMINMAX       //  Setting of REFORMULATE: convert MINMAX functions to the optimizer: always
#define XSLP_SIGN_ARGLIST_vv                             044       //  Function signature: taking two subsequent variants
#define XSLP_SIGN_ARGLIST_ArAi                           023       //  Function signature: taking array of double, array of int
#define XSLP_SIGN_RET_r                                    1       //  Function signature: returning a single real
#define XSLP_SIGN_RET_Ai_r                                 2       //  Function signature: returning an array of reals indexed by integers
#define XSLP_DELTA_CONT                          XPRS_SLPDELTA_CONT       //  Setting for CHGDELTATYPE: the variable is continuous
#define XSLP_DELTA_SEMICONT                      XPRS_SLPDELTA_SEMICONT       //  Setting for CHGDELTATYPE: the variable's delta has a minimum perturnation size 
#define XSLP_DELTA_INTEGER                       XPRS_SLPDELTA_INTEGER       //  Setting for CHGDELTATYPE: the variable takes values along a grid
#define XSLP_DELTA_EXPLORE                       XPRS_SLPDELTA_EXPLORE       //  Setting for CHGDELTATYPE: the variable's perturbation size needs exploration
#define XSLP_ROWINFO_SLACK                       XPRS_SLPROWINFO_SLACK       //  Setting of GETROWINFO: slack value
#define XSLP_ROWINFO_DUAL                        XPRS_SLPROWINFO_DUAL       //  Setting of GETROWINFO: dual multiplier
#define XSLP_ROWINFO_NUMPENALTYERRORS            XPRS_SLPROWINFO_NUMPENALTYERRORS       //  Setting of GETROWINFO: get the number of times the penalty error vector has been active 
#define XSLP_ROWINFO_MAXPENALTYERROR             XPRS_SLPROWINFO_MAXPENALTYERROR       //  Setting of GETROWINFO: get the maximum size of the penalty error vector activity 
#define XSLP_ROWINFO_TOTALPENALTYERROR           XPRS_SLPROWINFO_TOTALPENALTYERROR       //  Setting of GETROWINFO: get the total of the penalty error vector activities
#define XSLP_ROWINFO_CURRENTPENALTYERROR         XPRS_SLPROWINFO_CURRENTPENALTYERROR       //  Setting of GETROWINFO: get the size of the penalty error vector activity in the current iteration
#define XSLP_ROWINFO_CURRENTPENALTYFACTOR        XPRS_SLPROWINFO_CURRENTPENALTYFACTOR       //  Setting of GETROWINFO: get the size of the penalty error factor for the current iteration 
#define XSLP_ROWINFO_PENALTYCOLUMNPLUS           XPRS_SLPROWINFO_PENALTYCOLUMNPLUS       //  Setting of GETROWINFO: get the index of the penalty column for the row (+)
#define XSLP_ROWINFO_PENALTYCOLUMNPLUSVALUE      XPRS_SLPROWINFO_PENALTYCOLUMNPLUSVALUE       //  Setting of GETROWINFO: get the value of the penalty column for the row (+)
#define XSLP_ROWINFO_PENALTYCOLUMNPLUSDJ         XPRS_SLPROWINFO_PENALTYCOLUMNPLUSDJ       //  Setting of GETROWINFO: get the rdj of the penalty column for the row (+)
#define XSLP_ROWINFO_PENALTYCOLUMNMINUS          XPRS_SLPROWINFO_PENALTYCOLUMNMINUS       //  Setting of GETROWINFO: get the index of the second penalty column for an equality row (-) 
#define XSLP_ROWINFO_PENALTYCOLUMNMINUSVALUE     XPRS_SLPROWINFO_PENALTYCOLUMNMINUSVALUE       //  Setting of GETROWINFO: get the value of the second penalty column for an equality row (-) 
#define XSLP_ROWINFO_PENALTYCOLUMNMINUSDJ        XPRS_SLPROWINFO_PENALTYCOLUMNMINUSDJ       //  Setting of GETROWINFO: get the rdj of the second penalty column for an equality row (-) 
#define XSLP_COLINFO_VALUE                       XPRS_SLPCOLINFO_VALUE       //  Setting of GETCOLINFO: solution value
#define XSLP_COLINFO_RDJ                         XPRS_SLPCOLINFO_RDJ       //  Setting of GETCOLINFO: reduced cost
#define XSLP_COLINFO_DELTAINDEX                  XPRS_SLPCOLINFO_DELTAINDEX       //  Setting of GETCOLINFO: delta variable index
#define XSLP_COLINFO_DELTA                       XPRS_SLPCOLINFO_DELTA       //  Setting of GETCOLINFO: delta value
#define XSLP_COLINFO_DELTADJ                     XPRS_SLPCOLINFO_DELTADJ       //  Setting of GETCOLINFO: delta's reduced cost
#define XSLP_COLINFO_UPDATEROW                   XPRS_SLPCOLINFO_UPDATEROW       //  Setting of GETCOLINFO: update row index (step bound row)
#define XSLP_COLINFO_SB                          XPRS_SLPCOLINFO_SB       //  Setting of GETCOLINFO: step bound on the variable
#define XSLP_COLINFO_SBDUAL                      XPRS_SLPCOLINFO_SBDUAL       //  Setting of GETCOLINFO: dual multiplier of the step bound row for the variable 
#define XSLP_COLINFO_LPVALUE                     XPRS_SLPCOLINFO_LPVALUE       //  Setting of GETCOLINFO: non-adjusted solution as returned from the LP solve
#define XSLP_USERFUNCTION_MAP                    XPRS_USERFUNCTION_MAP       //  Option of ADDUSERFUNCTION: function takes double, returns double
#define XSLP_USERFUNCTION_VECMAP                 XPRS_USERFUNCTION_VECMAP       //  Option of ADDUSERFUNCTION: function takes double array, returns double
#define XSLP_USERFUNCTION_MULTIMAP               XPRS_USERFUNCTION_MULTIMAP       //  Option of ADDUSERFUNCTION: function takes double array, returns double array
#define XSLP_USERFUNCTION_MAPDELTA               XPRS_USERFUNCTION_MAPDELTA       //  Option of ADDUSERFUNCTION: function takes double, returns double and delta
#define XSLP_USERFUNCTION_VECMAPDELTA            XPRS_USERFUNCTION_VECMAPDELTA       //  Option of ADDUSERFUNCTION: function takes double array, returns double and deltas 
#define XSLP_USERFUNCTION_MULTIMAPDELTA          XPRS_USERFUNCTION_MULTIMAPDELTA       //  Option of ADDUSERFUNCTION: function takes double array, returns double array and deltas
#define XSLP_USERFUNCNAMES                       XPRS_NLPUSERFUNCNAMES       //  user function names
#define XSLP_INTERNALFUNCNAMES                   XPRS_NLPINTERNALFUNCNAMES       //  internal function names
#define XSLP_USERFUNCNAMESNOCASE                 XPRS_NLPUSERFUNCNAMESNOCASE       //  case insensitive lookup of user functions
#define XSLP_INTERNALFUNCNAMESNOCASE             XPRS_NLPINTERNALFUNCNAMESNOCASE       //  case insensitive lookup of internal functions
#define XSLP_FORMULACOEFFCOULMNINDEX             XPRS_NLPFORMULACOEFFCOULMNINDEX       //  column index of formulas, when worked with as coefficients
#define XSLP_OBJECTIVEROWINDEX                   XPRS_NLPOBJECTIVEROWINDEX       //  row index of the objective, when worked with as a row
#define XSLP_OMIT_CONTROLS                                 1       //  Omit conrols: omit controls
#define XSLP_OMIT_CALLBACKS                                2       //  Omit conrols: omit callbacks
#define XSLP_OMIT_PRESOLVECOPY                             4       //  Omit conrols: omit the presolved copy
#define XSLP_OMIT_MSNAMES                                  8       //  Omit conrols: omit multistart names
#define XSLP_OMIT_SETUPASORIGINAL                         16       //  Omit conrols: set up the presolved problem as original



/***************************************************************************\
  * Integer control variables                                              *
\**************************************************************************/
#define XSLP_ALGORITHM                      XPRS_SLPALGORITHM                  //  Bit map describing the SLP algorithm(s) to be used
#define XSLP_AUGMENTATION                   XPRS_SLPAUGMENTATION               //  Bit map describing the SLP augmentation method(s) to be used
#define XSLP_BARLIMIT                       XPRS_SLPBARLIMIT                   //  Number of initial SLP iterations using the barrier method
#define XSLP_CASCADE                        XPRS_SLPCASCADE                    //  Bit map describing the cascading to be used
#define XSLP_CASCADENLIMIT                  XPRS_SLPCASCADENLIMIT              //  Maximum number of iterations for cascading with non-linear determining rows
#define XSLP_CONTROL                        12307                              //  Bit map describing which SLP functions also activate the corresponding Optimizer Library function 
#define XSLP_DAMPSTART                      XPRS_SLPDAMPSTART                  //  SLP iteration at which damping is activated
#define XSLP_CUTSTRATEGY                    XPRS_SLPCUTSTRATEGY                //  Cutstrategy overwrite for generating cuts from linearizations
#define XSLP_DELTAZLIMIT                    XPRS_SLPDELTAZLIMIT                //  Number of SLP iterations during which to apply XSLP_DELTA_Z
#define XSLP_FUNCEVAL                       XPRS_NLPFUNCEVAL                   //  Bit map for determining the method of evaluating user functions and their derivatives 
#define XSLP_INFEASLIMIT                    XPRS_SLPINFEASLIMIT                //  The maximum number of consecutive infeasible SLP iterations which can occur before Xpress-SLP terminates 
#define XSLP_ITERLIMIT                      XPRS_SLPITERLIMIT                  //  The maximum number of SLP iterations
#define XSLP_LOG                            XPRS_NLPLOG                        //  Level of printing during SLP iterations
#define XSLP_SAMECOUNT                      XPRS_SLPSAMECOUNT                  //  Number of steps reaching the step bound in the same direction before step bounds are increased 
#define XSLP_SAMEDAMP                       XPRS_SLPSAMEDAMP                   //  Number of steps in same direction before damping factor is increased
#define XSLP_SBSTART                        XPRS_SLPSBSTART                    //  SLP iteration after which step bounds are first applied
#define XSLP_XCOUNT                         XPRS_SLPXCOUNT                     //  Number of SLP iterations over which to measure static objective (1) convergence 
#define XSLP_XLIMIT                         XPRS_SLPXLIMIT                     //  Number of SLP iterations up to which static objective (1) convergence testing starts 
#define XSLP_EXTRAUFS                       12324                              //  Expansion number for user functions
#define XSLP_KEEPEQUALSCOLUMN               XPRS_NLPKEEPEQUALSCOLUMN           //  If the MPS reader should keep coefficients on the = column there
#define XSLP_DELAYUPDATEROWS                XPRS_SLPDELAYUPDATEROWS            //  Number of SLP iterations before update rows are fully activated
#define XSLP_AUTOSAVE                       XPRS_SLPAUTOSAVE                   //  Frequency with which to save information about the solution process
#define XSLP_ANALYZE                        XPRS_SLPANALYZE                    //  Extra analytics options not directly affecting the optimization
#define XSLP_OCOUNT                         XPRS_SLPOCOUNT                     //  Number of SLP iterations over which to measure objective function variation for static objective (2) convergence criterion 
#define XSLP_EVALUATE                       XPRS_NLPEVALUATE                   //  Evaluation strategy for user functions
#define XSLP_MIPALGORITHM                   XPRS_SLPMIPALGORITHM               //  Bitmap describing the MISLP algorithms to be used
#define XSLP_MIPRELAXSTEPBOUNDS             XPRS_SLPMIPRELAXSTEPBOUNDS         //  Bitmap describing the step-bound relaxation strategy during MISLP
#define XSLP_MIPFIXSTEPBOUNDS               XPRS_SLPMIPFIXSTEPBOUNDS           //  Bitmap describing the step-bound fixing strategy during MISLP
#define XSLP_MIPITERLIMIT                   XPRS_SLPMIPITERLIMIT               //  Maximum number of SLP iterations at each node
#define XSLP_MIPCUTOFFLIMIT                 XPRS_SLPMIPCUTOFFLIMIT             //  Number of SLP iterations to check when considering a node for cutting off
#define XSLP_MIPOCOUNT                      XPRS_SLPMIPOCOUNT                  //  Number of SLP iterations at each node over which to measure objective function variation 
#define XSLP_MIPDEFAULTALGORITHM            XPRS_SLPMIPDEFAULTALGORITHM        //  Default algorithm to be used during the tree search in MISLP
#define XSLP_PRESOLVE                       XPRS_NLPPRESOLVE                   //  Indicates if NLP presolve is on
#define XSLP_SLPLOG                         12346                              //  Frequency with which SLP log is printed
#define XSLP_MIPLOG                         XPRS_SLPMIPLOG                     //  Frequency with which MIP log is printed
#define XSLP_DELTAOFFSET                    XPRS_SLPDELTAOFFSET                //  Position of first char of SLP variable name used to create name of delta vector 
#define XSLP_UPDATEOFFSET                   XPRS_SLPUPDATEOFFSET               //  Position of first char of SLP variable name used to create name of SLP update row 
#define XSLP_ERROROFFSET                    XPRS_SLPERROROFFSET                //  Position of first char of constraint name used to create name of penalty error vectors 
#define XSLP_SBROWOFFSET                    XPRS_SLPSBROWOFFSET                //  Position of first char of SLP variable name used to create name of SLP lower and upper step bound rows 
#define XSLP_SOLVER                         XPRS_LOCALSOLVER                   //  Selects the library to use for local solves: -1 auto, 0 XSLP, 1 Knitro
#define XSLP_STOPOUTOFRANGE                 XPRS_NLPSTOPOUTOFRANGE             //  Stop optimization and return error code if internal function argument is out of range 
#define XSLP_DISABLEAPICHECKS               12355                              //  If the API should check for consistency and calling context
#define XSLP_VCOUNT                         XPRS_SLPVCOUNT                     //  Number of SLP iterations over which to measure static objective (3) convergence
#define XSLP_VLIMIT                         XPRS_SLPVLIMIT                     //  Number of SLP iterations after which static objective (3) convergence testing starts 
#define XSLP_THREADSAFEUSERFUNC             XPRS_NLPTHREADSAFEUSERFUNC         //  If concurrent calls to user functions are allowed
#define XSLP_JACOBIAN                       XPRS_NLPJACOBIAN                   //  Determines how the Jacobian is calculated
#define XSLP_HESSIAN                        XPRS_NLPHESSIAN                    //  Determines how the Hessian is calculated
#define XSLP_MULTISTART                     XPRS_MULTISTART                    //  If the multi-start algorithm should be executed
#define XSLP_MULTISTART_THREADS             XPRS_MULTISTART_THREADS            //  Number of threads to be used in a multistart run
#define XSLP_MULTISTART_MAXSOLVES           XPRS_MULTISTART_MAXSOLVES          //  Maximum number of solves to execute in the multi-start search
#define XSLP_MULTISTART_MAXTIME             XPRS_MULTISTART_MAXTIME            //  Maximum total time to be spent in the multi-start search (+:only after feasible)
#define XSLP_MAXTIME                        XPRS_NLPMAXTIME                    //  The maximum time in seconds that the optimization will run before it terminates 
#define XSLP_SCALE                          12367                              //  When to re-scale the SLP problem
#define XSLP_SCALECOUNT                     12368                              //  Iteration limit used in determining when to re-scale the SLP matrix
#define XSLP_ECFCHECK                       XPRS_SLPECFCHECK                   //  Check feasibility at the point of linearization for extended convergence criteria 
#define XSLP_MIPCUTOFFCOUNT                 XPRS_SLPMIPCUTOFFCOUNT             //  Number of SLP iterations to check when considering a node for cutting off
#define XSLP_DERIVATIVES                    XPRS_NLPDERIVATIVES                //  Method of calculating derivatives
#define XSLP_WCOUNT                         XPRS_SLPWCOUNT                     //  Number of SLP iterations over which to measure the objective for the extended convergence continuation criterion 
#define XSLP_PRESOLVEPASSLIMIT              12375                              //  Maximum number of passes through the problem to improve SLP bounds
#define XSLP_UNFINISHEDLIMIT                XPRS_SLPUNFINISHEDLIMIT            //  Number of times within one SLP iteration that an unfinished LP optimization will be continued 
#define XSLP_CONVERGENCEOPS                 XPRS_SLPCONVERGENCEOPS             //  Bitmap control determining the convergence tests applied
#define XSLP_ZEROCRITERION                  XPRS_SLPZEROCRITERION              //  Bitmap determining the behavior of the placeholder deletion procedure
#define XSLP_ZEROCRITERIONSTART             XPRS_SLPZEROCRITERIONSTART         //  SLP iteration at which criteria for deletion of placeholder entries are first activated 
#define XSLP_ZEROCRITERIONCOUNT             XPRS_SLPZEROCRITERIONCOUNT         //  Number of consecutive times a placeholder entry is zero before being considered for deletion 
#define XSLP_LSPATTERNLIMIT                 XPRS_SLPLSPATTERNLIMIT             //  Number of exploratory steps to be carried out in the line search
#define XSLP_LSITERLIMIT                    XPRS_SLPLSITERLIMIT                //  Maximum number of iterations in the line search
#define XSLP_LSSTART                        XPRS_SLPLSSTART                    //  Iteration from which line search is applied (if other LS options are on)
#define XSLP_PENALTYINFOSTART               XPRS_SLPPENALTYINFOSTART           //  Iteration from which to record row penalty information
#define XSLP_DECOMPOSE                      12386                              //  Bitmap controlling the action of function XSLPdecompose
#define XSLP_FILTER                         XPRS_SLPFILTER                     //  Bitmap controlling how solution updates should be filtered
#define XSLP_TRACEMASKOPS                   XPRS_SLPTRACEMASKOPS               //  What information to trace using the TRACEMASK control
#define XSLP_LSZEROLIMIT                    XPRS_SLPLSZEROLIMIT                //  Maximum number of consecutive zero step sizes accepted by the line search
#define XSLP_DECOMPOSEPASSLIMIT             12390                              //  Maximum number of repeats of presolve+decompose
#define XSLP_REFORMULATE                    XPRS_NLPREFORMULATE                //  If problem classes should be recognised and transformed for efficient solve
#define XSLP_PRESOLVEOPS                    XPRS_NLPPRESOLVEOPS                //  Bitmap indicating the SLP presolve actions to be taken (default: boundreduce)
#define XSLP_AUTOTUNE                       12394                              //  If XSLP is to analyze the problem and attempt to tune the settings
#define XSLP_MULTISTART_LOG                 XPRS_MULTISTART_LOG                //  Level of logging during the multistart
#define XSLP_MULTISTART_SEED                XPRS_MULTISTART_SEED               //  The random number seed used to while generating initial point in the multistart
#define XSLP_MULTISTART_POOLSIZE            XPRS_MULTISTART_POOLSIZE           //  The maximum number of jobs that are allowed to be pooled up in deterministic ms
#define XSLP_POSTSOLVE                      XPRS_NLPPOSTSOLVE                  //  Indicates if NLP postsolve is automatically carried out
#define XSLP_DETERMINISTIC                  XPRS_NLPDETERMINISTIC              //  Indicates if the parallel feature of SLP is expected to be deterministic
#define XSLP_HEURSTRATEGY                   XPRS_SLPHEURSTRATEGY               //  Level of heuristics MISLP should be performing
#define XSLP_ECHOXPRSMESSAGES               12401                              //  If SLP should itself re-echo the optimizer messages
#define XSLP_PRESOLVELEVEL                  XPRS_NLPPRESOLVELEVEL              //  Presolving level (how much the individual features may change the problem)
#define XSLP_PROBING                        XPRS_NLPPROBING                    //  Probing level, i.e., variables for probing. -1:auto, 0:none, 1:binary, 2:unbounded integer or binary, 3:integer, 4:unbounded or binary, 5:all
#define XSLP_CALCTHREADS                    XPRS_NLPCALCTHREADS                //  Number of threads to use in calculations
#define XSLP_THREADS                        XPRS_NLPTHREADS                    //  General number of threads to be used
#define XSLP_BARCROSSOVERSTART              XPRS_SLPBARCROSSOVERSTART          //  Maximum number of barrier iterations without crossover
#define XSLP_BARSTALLINGLIMIT               XPRS_SLPBARSTALLINGLIMIT           //  Maximum number of barrier stalling failiures before switching to dual
#define XSLP_BARSTALLINGOBJLIMIT            XPRS_SLPBARSTALLINGOBJLIMIT        //  Number of pure barrier runs with no progress before crossover is activated
#define XSLP_BARSTARTOPS                    XPRS_SLPBARSTARTOPS                //  Fine tuning how the initial barrier solves are carried out
#define XSLP_GRIDHEURSELECT                 XPRS_SLPGRIDHEURSELECT             //  The selection of grid heuristics to run
#define XSLP_FINDIV                         XPRS_NLPFINDIV                     //  Whether to employ a Bound-Reduction based heuristic to find an initial point
#define XSLP_LINQUADBR                      XPRS_NLPLINQUADBR                  //  Whether Bound Reduction should be applied to linear/quadratic expressions too
#define XSLP_GLOBALSOLVE                    XPRS_GLOBALSOLVE                   //  Whether to solve the problem to global optimality



/****************************************************************************\
 * function declarations                                                    *
\****************************************************************************/
#ifdef __cplusplus
extern "C" {
#endif

int XSLP_CC XSLPinit( void ); 
int XSLP_CC XSLPcreateprob( XSLPprob * Prob, XPRSprob * XprsProb); 
int XSLP_CC XSLPreadprob( XSLPprob Prob, const char * probname, const char * flags); 
int XSLP_CC XSLPmaxim( XSLPprob Prob, const char * Flags); 
int XSLP_CC XSLPminim( XSLPprob Prob, const char * Flags); 
int XSLP_CC XSLPremaxim( XSLPprob Prob, const char * Flags); 
int XSLP_CC XSLPreminim( XSLPprob Prob, const char * Flags); 
int XSLP_CC XSLPcalcslacks( XSLPprob Prob, const double * dsol, double * slacks); 
int XSLP_CC XSLPcascade( XSLPprob Prob); 
int XSLP_CC XSLPcascadeorder( XSLPprob Prob); 
int XSLP_CC XSLPchgrowstatus( XSLPprob Prob, int RowIndex, int * Status); 
int XSLP_CC XSLPchgrowwt( XSLPprob Prob, int RowIndex, const double * Value); 
int XSLP_CC XSLPchgvar( XSLPprob Prob, int ColIndex, const int * DetRow, const double * InitStepBound, const double * StepBound, const double * Penalty, const double * Damp, const double * InitValue, const double * Value, const int * TolSet, const int * History, const int * Converged, const int * VarType); 
int XSLP_CC XSLPchgdeltatype( XSLPprob Prob, int nVar, const int * Vars, const int * DeltaTypes, const double * Values); 
int XSLP_CC XSLPchgcascadenlimit( XSLPprob Prob, int iCol, int CascadeNLimit); 
int XSLP_CC XSLPconstruct( XSLPprob Prob); 
int XSLP_CC XSLPcopycallbacks( XSLPprob Prob, const XSLPprob OldProb); 
int XSLP_CC XSLPcopycontrols( XSLPprob NewProb, const XSLPprob OldProb); 
int XSLP_CC XSLPcopyprob( XSLPprob NewProb, const XSLPprob OldProb, const char * probname); 
int XSLP_CC XSLPvalidate( XSLPprob Prob); 
int XSLP_CC XSLPresetprob( XSLPprob Prob); 
int XSLP_CC XSLPdumpattributes( XSLPprob Prob); 
int XSLP_CC XSLPdumpcontrols( XSLPprob Prob); 
int XSLP_CC XSLPrestore( XSLPprob Prob, const char * ProbName); 
int XSLP_CC XSLPnlpoptimize( XSLPprob Prob, const char * Flags); 
int XSLP_CC XSLPopt( XSLPprob Prob, const char * Flags); 
int XSLP_CC XSLPreinitialize( XSLPprob Prob); 
int XSLP_CC XSLPsave( XSLPprob Prob); 
int XSLP_CC XSLPsaveas( XSLPprob Prob, const char * File); 
int XSLP_CC XSLPscaling( XSLPprob Prob); 
int XSLP_CC XSLPsetcurrentiv( XSLPprob Prob); 
int XSLP_CC XSLPprintmemory( XSLPprob Prob); 
int XSLP_CC XSLPprintevalinfo( XSLPprob Prob); 
int XSLP_CC XSLPpostsolve( XSLPprob Prob); 
int XSLP_CC XSLPpresolve( XSLPprob Prob); 
int XSLP_CC XSLPunconstruct( XSLPprob Prob); 
int XSLP_CC XSLPupdatelinearization( XSLPprob Prob); 
int XSLP_CC XSLPsetdefaults( XSLPprob Prob); 
int XSLP_CC XSLPgetdblattrib( XSLPprob Prob, int param, double * value); 
int XSLP_CC XSLPgetdblcontrol( XSLPprob Prob, int Param, double * dValue); 
int XSLP_CC XSLPgetintattrib( XSLPprob Prob, int Param, int * iValue); 
int XSLP_CC XSLPgetintcontrol( XSLPprob Prob, int Param, int * iValue); 
int XSLP_CC XSLPsetfunctionerror( XSLPprob Prob); 
int XSLP_CC XSLPsetdefaultcontrol( XSLPprob Prob, int Param); 
int XSLP_CC XSLPwriteslxsol( XSLPprob Prob, const char * sFileName, const char * sFlags); 
int XSLP_CC XSLPwriteamplsol( XSLPprob Prob, const char * sFileName, const char * sFlags); 
int XSLP_CC XSLPreadamplsol( XSLPprob Prob, const char * sFileName, const char * sFlags); 
int XSLP_CC XSLPfixpenalties( XSLPprob Prob, int * RetrunStatus); 
int XSLP_CC XSLPsetparam( XSLPprob Prob, const char * Name, const char * Value); 
int XSLP_CC XSLPgetparam( XSLPprob Prob, const char * Name, int buffersize, char * Value); 
int XSLP_CC XSLPsetstrcontrol( XSLPprob Prob, int Param, const char * cValue); 
int XSLP_CC XSLPsetintcontrol( XSLPprob Prob, int Param, int iValue); 
int XSLP_CC XSLPsetlogfile( XSLPprob Prob, const char * filename, int option); 
int XSLP_CC XSLPinterrupt( XSLPprob Prob, int Reason); 
int XSLP_CC XSLPboundtighten( XSLPprob Prob, int * nTightened); 
int XSLP_CC XSLPgetrowstatus( XSLPprob Prob, int RowIndex, int * Status); 
int XSLP_CC XSLPgetrowwt( XSLPprob Prob, int RowIndex, double * Value); 
int XSLP_CC XSLPgetcascadenlimit( XSLPprob Prob, int iCol, int * CascadeNLimit); 
int XSLP_CC XSLPvalidaterow( XSLPprob Prob, int Row); 
int XSLP_CC XSLPvalidateprob( XSLPprob Prob, int * nErrors, int * nWarnings); 
int XSLP_CC XSLPwriteprob( XSLPprob Prob, const char * filename, const char * flags); 
int XSLP_CC XSLPgetindex( XSLPprob Prob, int Type, const char * Name, int * SeqNo); 
int XSLP_CC XSLPgetvar( XSLPprob Prob, int ColIndex, int * DetRow, double * InitStepBound, double * StepBound, double * Penalty, double * Damp, double * InitValue, double * Value, int * TolSet, int * History, int * Converged, int * VarType, int * Delta, int * PenaltyDelta, int * UpdateRow, double * OldValue); 
int XSLP_CC XSLPvalidatekkt( XSLPprob Prob, int iCalculationMode, int iRespectBasisStatus, int iUpdateMultipliers, double dKKTViolationTarget); 
int XSLP_CC XSLPdestroyprob( XSLPprob Prob); 
int XSLP_CC XSLPgetcolinfo( XSLPprob Prob, int Type, int ColIndex, XPRSalltype * Value); 
int XSLP_CC XSLPgetrowinfo( XSLPprob Prob, int Type, int RowIndex, XPRSalltype * Value); 
int XSLP_CC XSLPgetslpsol( XSLPprob Prob, double * dx, double * dslack, double * dual, double * dj); 
int XSLP_CC XSLPsetdblcontrol( XSLPprob Prob, int Param, double dValue); 
int XSLP_CC XSLPmsclear( XSLPprob Prob); 
int XSLP_CC XSLPgetstringattrib( XSLPprob Prob, int Param, char * cValue, int bufferLength, int * controlSize); 
int XSLP_CC XSLPgetstringcontrol( XSLPprob Prob, int Param, char * cValue, int bufferLength, int * controlSize); 
int XSLP_CC XSLPgetlasterror( XSLPprob Prob, int * Code, char * Buffer); 
int XSLP_CC XSLPitemname( XSLPprob Prob, int Type, double Value, char * Buffer); 
int XSLP_CC XSLPevaluateformula( XSLPprob Prob, int Parsed, const int * Type, const double * Value, double * dValue); 
int XSLP_CC XSLPvalidatevector( XSLPprob Prob, const double * Vector, double * SumInf, double * SumScaledInf, double * Objective); 
int XSLP_CC XSLPmsaddjob( XSLPprob Prob, const char * sDescription, int nIVs, const int * ivCols, const double * ivValues, int nIntControls, const int * IntControlIndices, const int * IntControlValues, int nDblControls, const int * DblControlIndices, const double * DblControlValues, void * pJobObject); 
int XSLP_CC XSLPmsaddpreset( XSLPprob Prob, const char * sDescription, int Preset, int Count, void * pJobObject); 
int XSLP_CC XSLPmsaddcustompreset( XSLPprob Prob, const char * sDescription, int Preset, int Count, int nIVs, const int * ivCols, const double * ivValues, int nIntControls, const int * IntControlIndices, const int * IntControlValues, int nDblControls, const int * DblControlIndices, const double * DblControlValues, void * pJobObject); 
int XSLP_CC XSLPfree( void ); 
int XSLP_CC XSLPgetbanner( char * Banner); 
int XSLP_CC XSLPadduserfunction( XSLPprob Prob, const char * FunctionName, int FunctionType, int nInput, int nOutput, int Options, XPRSfunctionptr FunctionPointer, void * UserContext, int * FunctionTokenId); 
int XSLP_CC XSLPdeluserfunction( XSLPprob Prob, int FunctionTokenId); 
int XSLP_CC XSLPimportlibfunc( XSLPprob Prob, const char * LibName, const char * FunctionName, XPRSfunctionptraddr FuncPointer, int * Status); 
int XSLP_CC XSLPgetccoef( XSLPprob Prob, int RowIndex, int ColIndex, double * Factor, char * Formula, int fLen); 
int XSLP_CC XSLPgetformulastring( XSLPprob Prob, int RowIndex, char * Formula, int fLen); 
int XSLP_CC XSLPdelcoefs( XSLPprob Prob, int nSLPCoef, const int * RowIndex, const int * ColIndex); 
int XSLP_CC XSLPloadcoefs( XSLPprob Prob, int nSLPCoef, const int * RowIndex, const int * ColIndex, const double * Factor, const int * FormulaStart, int Parsed, const int * Type, const double * Value); 
int XSLP_CC XSLPevaluatecoef( XSLPprob Prob, int RowIndex, int ColIndex, double * dValue); 
int XSLP_CC XSLPgetcoefs( XSLPprob Prob, int * nCoef, int * RowIndices, int * ColIndices); 
int XSLP_CC XSLPgetcoefformula( XSLPprob Prob, int RowIndex, int ColIndex, double * Factor, int Parsed, int BufferSize, int * TokenCount, int * Type, double * Value); 
int XSLP_CC XSLPaddcoefs( XSLPprob Prob, int nSLPCoef, const int * RowIndex, const int * ColIndex, const double * Factor, const int * FormulaStart, int Parsed, const int * Type, const double * Value); 
int XSLP_CC XSLPchgccoef( XSLPprob Prob, int RowIndex, int ColIndex, const double * Factor, const char * Formula); 
int XSLP_CC XSLPchgcoef( XSLPprob Prob, int RowIndex, int ColIndex, const double * Factor, int Parsed, const int * Type, const double * Value); 
int XSLP_CC XSLPaddformulas( XSLPprob Prob, int nSLPCoef, const int * RowIndex, const int * FormulaStart, int Parsed, const int * Type, const double * Value); 
int XSLP_CC XSLPchgformulastring( XSLPprob Prob, int RowIndex, const char * Formula); 
int XSLP_CC XSLPchgformula( XSLPprob Prob, int RowIndex, int Parsed, const int * Type, const double * Value); 
int XSLP_CC XSLPloadformulas( XSLPprob Prob, int nSLPCoef, const int * RowIndex, const int * FormulaStart, int Parsed, const int * Type, const double * Value); 
int XSLP_CC XSLPgetformularows( XSLPprob Prob, int * nCoef, int * RowIndices); 
int XSLP_CC XSLPgetformula( XSLPprob Prob, int RowIndex, int Parsed, int BufferSize, int * TokenCount, int * Type, double * Value); 
int XSLP_CC XSLPdelformulas( XSLPprob Prob, int nSLPCoef, const int * ColIndex); 
int XSLP_CC XSLPsetinitval( XSLPprob Prob, int nVars, const int * varIndices, const double * initialValues); 
int XSLP_CC XSLPsetdetrow( XSLPprob Prob, int nVars, const int * vvarIndicesar, const int * rowIndices); 
int XSLP_CC XSLPgetdf( XSLPprob Prob, int ColIndex, int RowIndex, double * DFValue); 
int XSLP_CC XSLPloaddfs( XSLPprob Prob, int nDF, const int * ColIndex, const int * RowIndex, const double * DFValue); 
int XSLP_CC XSLPloadvars( XSLPprob Prob, int nSLPVar, const int * ColIndex, const int * VarType, const int * DetRow, const int * SeqNum, const int * TolIndex, const double * InitValue, const double * StepBound); 
int XSLP_CC XSLPdelvars( XSLPprob Prob, int nCol, const int * ColIndex); 
int XSLP_CC XSLPchgtolset( XSLPprob Prob, int nSLPTol, const int * Status, const double * Tols); 
int XSLP_CC XSLPchgdf( XSLPprob Prob, int ColIndex, int RowIndex, const double * DFValue); 
int XSLP_CC XSLPadddfs( XSLPprob Prob, int nDF, const int * ColIndex, const int * RowIndex, const double * DFValue); 
int XSLP_CC XSLPaddtolsets( XSLPprob Prob, int nSLPTol, const double * SLPTol); 
int XSLP_CC XSLPloadtolsets( XSLPprob Prob, int nSLPTol, const double * SLPTol); 
int XSLP_CC XSLPgettolset( XSLPprob Prob, int nSLPTol, int * Status, double * Tols); 
int XSLP_CC XSLPdeltolsets( XSLPprob Prob, int nTolSet, int * TolSetIndex); 
int XSLP_CC XSLPaddvars( XSLPprob Prob, int nSLPVar, const int * ColIndex, const int * VarType, const int * DetRow, const int * SeqNum, const int * TolIndex, const double * InitValue, const double * StepBound); 
int XSLP_CC XSLPsetcbcascadeend( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbcascadestart( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbcascadevar( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int), void * Object); 
int XSLP_CC XSLPsetcbcascadevarfail( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int), void * Object); 
int XSLP_CC XSLPsetcbconstruct( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbdestroy( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbintsol( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbiterend( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbiterstart( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbitervar( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int), void * Object); 
int XSLP_CC XSLPsetcbmessage( XSLPprob Prob, void (XSLP_CC *UserFunc)(XSLPprob,void*,const char*,int,int), void * Object); 
int XSLP_CC XSLPsetcboptnode( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int*), void * Object); 
int XSLP_CC XSLPsetcbprenode( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int*), void * Object); 
int XSLP_CC XSLPsetcbslpend( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbslpnode( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int*), void * Object); 
int XSLP_CC XSLPsetcbslpstart( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPsetcbdrcol( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*, int, int, double,double *, double,double), void * Object); 
int XSLP_CC XSLPsetcbmsjobstart( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,void*,const char*,int*), void * Object); 
int XSLP_CC XSLPsetcbmsjobend( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,void*,const char*,int*), void * Object); 
int XSLP_CC XSLPsetcbmswinner( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,void*,const char*), void * Object); 
int XSLP_CC XSLPsetcbcoefevalerror( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int,int), void * Object); 
int XSLP_CC XSLPsetcbpreupdatelinearization( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*,int*), void * Object); 
int XSLP_CC XSLPsetcbpresolved( XSLPprob Prob, int (XSLP_CC *UserFunc)(XSLPprob,void*), void * Object); 
int XSLP_CC XSLPgetptrattrib(XSLPprob Prob, int param, void** value);
int XPRS_CC XPRSnlpnlpoptimize(XPRSprob prob, const char* flags);
int XPRS_CC XPRSaddcbnlpintsol(XPRSprob prob, int (XPRS_CC *f_slpintsol)(XPRSprob cbprob, void* cbdata), void* p, int priority);
int XPRS_CC XPRSremovecbnlpintsol(XPRSprob prob, int (XPRS_CC *f_slpintsol)(XPRSprob cbprob, void* cbdata), void* p);

#ifdef __cplusplus
}
#endif


/****************************************************************************\
 * Compatibility for slp namespace                                          *
\****************************************************************************/
#define XPRSnlpgetcoefformula        XPRSslpgetcoefformula
#define XPRSnlpgetcoefs              XPRSslpgetcoefs
#define XPRSnlploadcoefs             XPRSslploadcoefs
#define XPRSnlpdelcoefs              XPRSslpdelcoefs
#define XPRSnlpgetccoef              XPRSslpgetccoef
#define XPRSnlpsetdetrow             XPRSslpsetdetrow
#define XPRSnlpaddcoefs              XPRSslpaddcoefs
#define XPRSnlpchgccoef              XPRSslpchgccoef
#define XPRSnlpchgcoef               XPRSslpchgcoef
#define XPRSnlpgetcolinfo            XPRSslpgetcolinfo
#define XPRSnlpgetrowinfo            XPRSslpgetrowinfo
#define XPRSnlpgetvar                XPRSslpgetvar
#define XPRSnlpcascade               XPRSslpcascade
#define XPRSnlpcascadeorder          XPRSslpcascadeorder
#define XPRSnlpchgdf                 XPRSslpchgdf
#define XPRSnlpchgrowstatus          XPRSslpchgrowstatus
#define XPRSnlpchgrowwt              XPRSslpchgrowwt
#define XPRSnlpchgtolset             XPRSslpchgtolset
#define XPRSnlpchgdeltatype          XPRSslpchgdeltatype
#define XPRSnlpchgcascadenlimit      XPRSslpchgcascadenlimit
#define XPRSnlpconstruct             XPRSslpconstruct
#define XPRSnlpreminim               XPRSslpreminim
#define XPRSnlpremaxim               XPRSslpremaxim
#define XPRSnlpadddfs                XPRSslpadddfs
#define XPRSnlpaddtolsets            XPRSslpaddtolsets
#define XPRSnlpchgvar                XPRSslpchgvar
#define XPRSnlpgetrowstatus          XPRSslpgetrowstatus
#define XPRSnlpgetrowwt              XPRSslpgetrowwt
#define XPRSnlpdeltolsets            XPRSslpdeltolsets
#define XPRSnlpgetdf                 XPRSslpgetdf
#define XPRSnlpgettolset             XPRSslpgettolset
#define XPRSnlploadtolsets           XPRSslploadtolsets
#define XPRSnlploaddfs               XPRSslploaddfs
#define XPRSnlpevaluatecoef          XPRSslpevaluatecoef
#define XPRSnlpreinitialize          XPRSslpreinitialize
#define XPRSnlpunconstruct           XPRSslpunconstruct
#define XPRSnlpupdatelinearization   XPRSslpupdatelinearization
#define XPRSnlpfixpenalties          XPRSslpfixpenalties
#define XPRSnlpgetcascadenlimit      XPRSslpgetcascadenlimit
#define XPRSnlpgetdf                 XPRSslpgetdf
#define XPRSnlploaddfs               XPRSslploaddfs
#define XPRSnlploadvars              XPRSslploadvars
#define XPRSnlpdelvars               XPRSslpdelvars
#define XPRSnlpchgtolset             XPRSslpchgtolset
#define XPRSnlpchgdf                 XPRSslpchgdf
#define XPRSnlpadddfs                XPRSslpadddfs
#define XPRSnlpaddtolsets            XPRSslpaddtolsets
#define XPRSnlploadtolsets           XPRSslploadtolsets
#define XPRSnlpgettolset             XPRSslpgettolset
#define XPRSnlpdeltolsets            XPRSslpdeltolsets
#define XPRSnlpaddvars               XPRSslpaddvars
#define XPRSaddcbnlpiterend          XPRSaddcbslpiterend
#define XPRSaddcbnlpiterstart        XPRSaddcbslpiterstart
#define XPRSaddcbnlpitervar          XPRSaddcbslpitervar
#define XPRSaddcbnlpcascadestart     XPRSaddcbslpcascadestart
#define XPRSaddcbnlpcascadeend       XPRSaddcbslpcascadeend
#define XPRSaddcbnlpcascadevar       XPRSaddcbslpcascadevar
#define XPRSaddcbnlpconstruct        XPRSaddcbslpconstruct
#define XPRSaddcbnlppreupdatelinearization XPRSaddcbslppreupdatelinearization
#define XPRSremovecbnlpiterend       XPRSremovecbslpiterend
#define XPRSremovecbnlpiterstart     XPRSremovecbslpiterstart
#define XPRSremovecbnlpitervar       XPRSremovecbslpitervar
#define XPRSremovecbnlpcascadestart  XPRSremovecbslpcascadestart
#define XPRSremovecbnlpcascadeend    XPRSremovecbslpcascadeend
#define XPRSremovecbnlpcascadevar    XPRSremovecbslpcascadevar
#define XPRSremovecbnlpconstruct     XPRSremovecbslpconstruct
#define XPRSremovecbnlppreupdatelinearization XPRSremovecbslppreupdatelinearization
#define XPRSaddcbnlpmsjobstart       XPRSaddcbmsjobstart
#define XPRSaddcbnlpmsjobend         XPRSaddcbmsjobend
#define XPRSaddcbnlpmswinner         XPRSaddcbmswinner
#define XPRSremovecbnlpmsjobstart    XPRSremovecbmsjobstart
#define XPRSremovecbnlpmsjobend      XPRSremovecbmsjobend
#define XPRSremovecbnlpmswinner      XPRSremovecbmswinner

/****************************************************************************\
 * Compatibility for nlp namespace now native XPRS                          *
\****************************************************************************/
#define XPRSnlpmsaddjob              XPRSmsaddjob
#define XPRSnlpmsaddpreset           XPRSmsaddpreset
#define XPRSnlpmsaddcustompreset     XPRSmsaddcustompreset
#define XPRSnlpmsclear               XPRSmsclear

#endif

