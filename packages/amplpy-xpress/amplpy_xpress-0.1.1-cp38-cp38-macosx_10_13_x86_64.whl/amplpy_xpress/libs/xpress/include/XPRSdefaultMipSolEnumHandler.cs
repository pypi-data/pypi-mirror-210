using System;
using Optimizer;

/**
 * This is the default implementation of MipSolEnumHandlerCallback, included in <tt>xprsdn.dll</tt>
 * as XPRSdefaultMipSolEnumHandler.  The source code is also included,
 * in the file <tt>xpressmp/includes/XPRSdefaultMipSolEnumHandler.cs</tt>.
 *
 * The XPRSdefaultMipSolEnumHandler.MipSolEnumEvent function implements most of the functionality you will want to
 * use with the MIP solution enumerator, but you can provide alternate implementations, possibly
 * based on XPRSdefaultMipSolEnumHandler, if you require additional functionality.
 **/

namespace UserCode {
  public class XPRSdefaultMipSolEnumHandler {

    public static MipSolEnumHandlerCallback GetDefaultHandlerCallback() {
      return new MipSolEnumHandlerCallback(MipSolEnumEvent);
    }

    public static int MipSolEnumEvent(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, object vContext, ref int  nMaxSols, double[] x_Zb, int nCols, double dMipObject, ref double dModifiedObject, ref bool bRejectSoln, ref bool bUpdateMipAbsCutOffOnCurrentSet) {
      int iSolutionIdStatus;
      int nDeleted = 0;
      bool bStorageIsFullOnEntry = false;
      int nMaxSolsToCull_MIPOBJECT = -1;
      int nMaxSolsToCull_DIVERSITY = -1;

      if (nMaxSols>0 && mse.Solutions >= nMaxSols) {
        /*
        Keeping the new solution will put the number of solutions above the max limit.
        Either choose to ignore the new solution and/or delete some solutions already
        stored.
        */
        int nMaxSolsToCull = 1;

        bStorageIsFullOnEntry = true;

        nMaxSolsToCull_MIPOBJECT = mse.CallbackCullSols_MipObject;
        nMaxSolsToCull_DIVERSITY = mse.CallbackCullSols_Diversity;


        nMaxSolsToCull = Math.Max(nMaxSolsToCull, nMaxSolsToCull_MIPOBJECT);
        nMaxSolsToCull = Math.Max(nMaxSolsToCull, nMaxSolsToCull_DIVERSITY);

        /* Allocate an array for storing the existing solutions we may be culling */
        int[] cull_sol_id_list = new int[nMaxSolsToCull];

        /* Try culling some existing solutions and maybe choose to ignore the new solution as well */
        if (nMaxSolsToCull_MIPOBJECT>=0) {
          int nSolsToCull = mse.GetCullChoice((int)XPRSattribute.Mse_Metric_MipObject, cull_sol_id_list, nMaxSolsToCull_MIPOBJECT, dMipObject, out bRejectSoln);
          for (int i=1;i<=nSolsToCull;i++) {
            msp.DelSol(cull_sol_id_list[i-1],out iSolutionIdStatus);
            nDeleted++;
          }
        }
        if (nMaxSolsToCull_DIVERSITY>=0) {
          int nSolsToCull = mse.GetCullChoice((int)XPRSattribute.Mse_Metric_Diversity, cull_sol_id_list, nMaxSolsToCull_DIVERSITY, 0.0, x_Zb, nCols, out bRejectSoln);
          for (int i=1;i<=nSolsToCull;i++) {
            msp.DelSol(cull_sol_id_list[i-1],out iSolutionIdStatus);
            nDeleted++;
          }
        }

        if (!bRejectSoln && nDeleted==0) {
          /*
          None of the policies above were able to handle the current situation.
          We need to either ignore the new solution or delete an existing
          solution to make way for the new solution. Use the mip objective to
          decide the worst solution.
          */
          nMaxSolsToCull_MIPOBJECT = 1;
          int nSolsToCull = mse.GetCullChoice((int)XPRSattribute.Mse_Metric_MipObject, cull_sol_id_list, nMaxSolsToCull_MIPOBJECT, dMipObject, out bRejectSoln);
          if (bRejectSoln || nSolsToCull==0) {
            /* We still haven't rejected any solutions */
            nMaxSolsToCull_MIPOBJECT = 0;
          }
          else {
            /* The new solution is better than the worst stored solution */
            msp.DelSol(cull_sol_id_list[0], out iSolutionIdStatus);
            nDeleted++;
          }
        }
      }

      /* solution rejected */
      if (bStorageIsFullOnEntry) {
        if ((nDeleted==1) ^ bRejectSoln) {
          /* We haven't reduced the number of solutions in storage and the storage is full */
          if (nMaxSolsToCull_MIPOBJECT >= 0) {
            /*
            The storage is full and we are using the mip objective as a metric for
            managing the stored solutions. Update the mip cut-off to reflect the
            worst solution we have stored (or that we will have stored once the new
            solution is loaded when we return from here).
            */
            bUpdateMipAbsCutOffOnCurrentSet = true;
          }
        }
      }

      return 0;
    }
  }
}
