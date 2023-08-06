// ********************************************************************
// * Xpress-Kalis                                                     *
// * Copyright (C) 2001-2008 by Artelys                               *
// *                                                                  *
// * All Rights Reserved                                              *
// *                                                                  *
// * Description : A Mosel module for Artelys Kalis                   *
// * Parts of this module were written by Yves Colombani              *
// ********************************************************************

#ifdef ALLOW_XPRESS_KALIS_EXTENSIONS

#define INDEX_EXTENSIONS 5000

static int nbextensionsfound = 0;
static int loadedExtensions = 0;
typedef int          ( * pGetNumberOfXpressKalisExtensions)();
typedef XPRMdsofct * ( * pGetXpressKalisModuleDefinition)();
typedef void         ( * pDoCleaning)(void *);
typedef void         ( * pSetNiFCT)(XPRMnifct , u_iorp *,u_iorp *, XPRMdsointer **);

pGetNumberOfXpressKalisExtensions getNumberOfXpressKalisExtensions;
pGetXpressKalisModuleDefinition   getXpressKalisModuleDefinition;
pDoCleaning                       doCleaning;
pSetNiFCT                         setNiFCT;


static int loadXpressKalisExtensions(XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf,int exts)
{

   /* The actual call to the function contained in the dll */
   XPRMdsofct * extension = getXpressKalisModuleDefinition();

   int ext= 0;

   for (ext=0;ext<exts;ext++) {
       if (loadedExtensions < MAXEXTENSIONS) {
          //nifct->dispmsg(NULL,"loading extension : %s code = %i type = %i params = %i [%s]\n",extension[ext].name,extension[ext].code,extension[ext].type,extension[ext].nbpar,extension[ext].typpar);
          // loadedExtensions ++;
          extension[ext].code = INDEX_EXTENSIONS + loadedExtensions ++;// renumbering extension code ...

          tabfct[NB_FUNC+(loadedExtensions-1)] = extension[ext];
//		  cptr += snprintf(cptr,4096,"Loading extension : %20s ... [%i]",tabfct[NB_FUNC+(loadedExtensions-1)].name,tabfct[NB_FUNC+(loadedExtensions-1)].code);
//		  cptr += snprintf(cptr,4096,"ok\n");
          //mm->dispmsg(NULL,"Loading extension : %20s ... [%i]",tabfct[NB_FUNC+(loadedExtensions-1)].name,tabfct[NB_FUNC+(loadedExtensions-1)].code);
          //mm->dispmsg(NULL," ok\n");
       }
   }


   /* The return val from the dll */
   return 0;
}

// ################################################ WIN32 ##################################################"""

#ifdef WIN32	// EXTENSIONS FOR WIN32

#include "windows.h"

static HINSTANCE hGetProcIDDLL;
NAMESPACE_STL::vector<HINSTANCE> dllHandles;
NAMESPACE_STL::vector<pDoCleaning> dllCleaningFunctions;

static int cleanXpressKalisExtensions(void *libctx,bool closedll)
{


    try {
        //	printf("Cleaning dll extensions [%i]\n",dllHandles.size());
        int dllIndex = 0;
        for (dllIndex = 0; dllIndex < dllHandles.size(); dllIndex++) {
            HINSTANCE cinstance = dllHandles[dllIndex];
            pDoCleaning doCleaning = dllCleaningFunctions[dllIndex];
            if (closedll) {
                //printf("Closing dll extension %i\n",dllIndex);
                doCleaning(libctx);
                FreeLibrary(cinstance);
            } else {

                //mm->printf (NULL,"Cleaning extension %i\n", dllIndex);
                doCleaning(libctx);
            }
            //printf("Done Closing dll extension %i\n",dllIndex);
        }
        //dllHandles.clear();
        //dllCleaningFunctions.clear();

        nbextensionsfound = 0;
        loadedExtensions = 0;
        return 0;
    } catch (...) {
        printf("Unknown exception has occured in cleanXpressKalisExtensions!\n");
        return 0;
    }
}



static int loadExtensionDLL(char * fullPath,XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf)
{


   hGetProcIDDLL = LoadLibrary(fullPath);

   if (hGetProcIDDLL == NULL) {
       //mm->dispmsg(NULL," failed\n",fullPath);
       return 0;
   }
   //mm->dispmsg(NULL," ok\n",fullPath);



   FARPROC lpfnGetProcessID = GetProcAddress(HMODULE(hGetProcIDDLL), "getNumberOfXpressKalisExtensions\0");
   if (lpfnGetProcessID == NULL) {

       FreeLibrary(hGetProcIDDLL);
       return 0;
   }
   getNumberOfXpressKalisExtensions = pGetNumberOfXpressKalisExtensions(lpfnGetProcessID);

   int exts =  getNumberOfXpressKalisExtensions();
  // mm->dispmsg(NULL,"%i extensions'\n",exts);


   lpfnGetProcessID = GetProcAddress(HMODULE(hGetProcIDDLL), "getXpressKalisModuleDefinition\0");
   if (lpfnGetProcessID == NULL) {

       FreeLibrary(hGetProcIDDLL);
       return 0;
   }
   getXpressKalisModuleDefinition = pGetXpressKalisModuleDefinition(lpfnGetProcessID);


   lpfnGetProcessID = GetProcAddress(HMODULE(hGetProcIDDLL), "resetXpressKalisModule\0");
   if (lpfnGetProcessID == NULL) {

       FreeLibrary(hGetProcIDDLL);
       return 0;
   }
   doCleaning = pDoCleaning(lpfnGetProcessID);


   lpfnGetProcessID = GetProcAddress(HMODULE(hGetProcIDDLL), "setNiFCT\0");
   if (lpfnGetProcessID == NULL) {

       FreeLibrary(hGetProcIDDLL);
       return 0;
   }
   setNiFCT = pSetNiFCT(lpfnGetProcessID);

   //   cptr += snprintf(cptr,4096,"%i extensions found\n",exts);

   dllHandles.push_back(hGetProcIDDLL);
   dllCleaningFunctions.push_back(doCleaning);
   // First set Interface function pointer
   setNiFCT( nifct, interver,libver, interf);

   // Load the extensions
   loadXpressKalisExtensions(nifct,interver,libver,interf,exts);




   return exts;
}

static int loadExtensionsDLLS(XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf)
{
    char * pPath;
    char fullPath[2048];
    char simplePath[2048];
    DWORD dwError=0;



    char dsoPath[4096];
    int ret = XPRMgetdsopath(dsoPath, 4096);
    //	printf("DSO PATHS  = %s\n",dsoPath);

    pPath = strtok (dsoPath,";");
    while (pPath != NULL)
    {
        //mm->printf (NULL,"Looking in %s\n",pPath);
        //		cptr += snprintf(cptr,4096,"Looking in %s\n",pPath);


           snprintf(simplePath,2048,"%s//*.dll\0",pPath);

        // Find the first file in the directory.

           WIN32_FIND_DATA ffd;
           HANDLE hFind = FindFirstFile(simplePath, &ffd);

           if (INVALID_HANDLE_VALUE == hFind)
           {
              dwError = GetLastError();
              //printf("FindFirstFile failed (%u)\n", dwError);
             // return 1;
           }
           else
           {

            //  cptr += snprintf(cptr,4096,"Trying to load %s : ", ffd.cFileName);
              if (!strstr(ffd.cFileName,"Kalis.dll")) {
                  //mm->printf (NULL,"Trying to load %s\n", ffd.cFileName);
                  snprintf(fullPath,2048,"%s//%s\0",pPath,ffd.cFileName);
                  int nbext = 0;
                  if (! (nbext = loadExtensionDLL(fullPath,nifct,interver,libver,interf))) {
                    // mm->printf (NULL,"%s is not an Xpress-Kalis extension module !\n",fullPath);
                //	 cptr += snprintf(cptr,4096,"%s is not an Xpress-Kalis extension module !\n",fullPath);
                  }
              }

              // List all the other files in the directory.

              while (FindNextFile(hFind, &ffd) != 0)
              {

                  if (!strstr(ffd.cFileName,"Kalis.dll")) {
                     // mm->printf (NULL,"Trying to load %s\n", ffd.cFileName);

                     //cptr += snprintf(cptr,4096,"Trying to load %s : ", ffd.cFileName);
                     snprintf(fullPath,2048,"%s//%s\0",pPath,ffd.cFileName);
                     int nbext = 0;
                     if (! (nbext = loadExtensionDLL(fullPath,nifct,interver,libver,interf))) {
                    //   cptr += snprintf(cptr,4096,"Not an Xpress-Kalis extension module !\n",fullPath);
                    //	 mm->printf (NULL,"Not an Xpress-Kalis extension module !\n",fullPath);
                     }
                  }
              }

              dwError = GetLastError();
              if (dwError != ERROR_NO_MORE_FILES)
              {
                 //return 1;
              }
           }


           FindClose(hFind);

        pPath = strtok (NULL, ";");
    }

   return 0;

}


#endif	// WIN32

// ################################################ LINUX ##################################################"""

#ifdef LINUX

#include <dlfcn.h>      /* defines dlopen(), etc.       */
#include <stddef.h>
#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>		/* for directory listing */

#include <cstdlib>		/* defines getenv */

static void* hGetProcIDDLL;
NAMESPACE_STL::vector<void*> dllHandles;
NAMESPACE_STL::vector<pDoCleaning> dllCleaningFunctions;

static int cleanXpressKalisExtensions(void *libctx,bool closedll)
{
    try {
        //	printf("Cleaning dll extensions [%i]\n",dllHandles.size());
        int dllIndex = 0;
        for (dllIndex = 0; dllIndex < dllHandles.size(); dllIndex++) {
            void* cinstance = dllHandles[dllIndex];
            pDoCleaning doCleaning = dllCleaningFunctions[dllIndex];
            /* The actual call to the function contained in the dll */
            //printf("Cleaning dll extension %i\n",dllIndex);

            if (closedll) {
                //printf("Closing dll extension %i\n",dllIndex);
                dlclose(cinstance);
            } else {
                doCleaning(libctx);
            }
            //printf("Done Closing dll extension %i\n",dllIndex);
        }
        //dllHandles.clear();
        //dllCleaningFunctions.clear();

        nbextensionsfound = 0;
        loadedExtensions = 0;
        return 0;
    } catch (...) {
        printf("Unknown exception has occured in cleanXpressKalisExtensions!\n");
        return 0;
    }
}


static int loadExtensionDLL(char * fullPath,XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf)
{

    //printf("Trying to Loading %s in memory\n",fullPath);
    hGetProcIDDLL = dlopen(fullPath, RTLD_NOLOAD);
    if (hGetProcIDDLL != NULL) {
//		printf("library %s has already been loaded in memory!\n",fullPath);
        return 0;
    }
    //printf("Loading %s in memory\n",fullPath);
    hGetProcIDDLL = dlopen(fullPath, RTLD_LAZY);
    if (hGetProcIDDLL == NULL) {
        return 0;
    }

    const char* error_msg;

    getNumberOfXpressKalisExtensions = (pGetNumberOfXpressKalisExtensions) dlsym(hGetProcIDDLL, "getNumberOfXpressKalisExtensions\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

   int exts =  getNumberOfXpressKalisExtensions();
   // mm->dispmsg(NULL,"%i extensions'\n",exts);


    getXpressKalisModuleDefinition = (pGetXpressKalisModuleDefinition) dlsym(hGetProcIDDLL, "getXpressKalisModuleDefinition\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

    doCleaning = (pDoCleaning) dlsym(hGetProcIDDLL, "resetXpressKalisModule\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

    setNiFCT = (pSetNiFCT) dlsym(hGetProcIDDLL, "setNiFCT\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

   //mm->printf (NULL,"%i extensions found\n",exts);
   //cptr += snprintf(cptr,4096,"%i extensions found\n",exts);
   dllHandles.push_back(hGetProcIDDLL);
   dllCleaningFunctions.push_back(doCleaning);
   // First set Interface function pointer
   setNiFCT( nifct, interver,libver, interf);

   // Load the extensions
   loadXpressKalisExtensions(nifct,interver,libver,interf,exts);


   return exts;
}

static int loadExtensionsDLLS(XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf)
{
    char * pPath;
    char fullPath[2048];


    char dsoPath[4096];
    int ret = XPRMgetdsopath(dsoPath, 4096);
    //mm->printf(NULL,"DSO PATHS  = %s\n",dsoPath);

    pPath = strtok (dsoPath,":");
        while (pPath != NULL)
    {
        //mm->printf (NULL,"Looking in %s\n",pPath);
        //cptr += snprintf(cptr,4096,"Looking in %s\n",pPath);
        DIR *dp;
        struct dirent *ep;
        dp = opendir (pPath);
        if (dp != NULL)
        {
            while (ep = readdir (dp)) {
                if (strstr(ep->d_name,".so")) {
                    //mm->printf (NULL,"Trying to load %s : ", ep->d_name);
                    //cptr += snprintf(cptr,4096,"Trying to load %s : ", ep->d_name);
                    snprintf(fullPath,2048,"%s//%s\0",pPath,ep->d_name);
                    int nbext = 0;
                    if (! (nbext = loadExtensionDLL(fullPath,nifct,interver,libver,interf))) {
                        //mm->printf (NULL,"%s is not an Xpress-Kalis extension module !\n",fullPath);
                        //cptr += snprintf(cptr,4096,"%s is not an Xpress-Kalis extension module !\n",fullPath);
                    }
                }
            }
            (void) closedir (dp);
        }
        else {
            //return 1;
        }

        pPath = strtok (NULL, ":");
    }
    // mm->printf (NULL,"%s\n",cptr);
    return 0;

}


#endif

// ################################################ SOLARIS ##################################################"""
#ifdef SOLARIS
#include <dlfcn.h>      /* defines dlopen(), etc.       */
#include <stddef.h>
#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>		/* for directory listing */

#include <cstdlib>		/* defines getenv */

static void* hGetProcIDDLL;
NAMESPACE_STL::vector<void*> dllHandles;
NAMESPACE_STL::vector<pDoCleaning> dllCleaningFunctions;

static int cleanXpressKalisExtensions(void *libctx,bool closedll)
{
    try {
        //	printf("Cleaning dll extensions [%i]\n",dllHandles.size());
        int dllIndex = 0;
        for (dllIndex = 0; dllIndex < dllHandles.size(); dllIndex++) {
            void* cinstance = dllHandles[dllIndex];
            pDoCleaning doCleaning = dllCleaningFunctions[dllIndex];
            /* The actual call to the function contained in the dll */
            //printf("Cleaning dll extension %i\n",dllIndex);

            if (closedll) {
                //printf("Closing dll extension %i\n",dllIndex);
                dlclose(cinstance);
            } else {
                doCleaning(libctx);
            }
            //printf("Done Closing dll extension %i\n",dllIndex);
        }
        //dllHandles.clear();
        //dllCleaningFunctions.clear();

        nbextensionsfound = 0;
        loadedExtensions = 0;
        return 0;
    } catch (...) {
        printf("Unknown exception has occured in cleanXpressKalisExtensions!\n");
        return 0;
    }
}


static int loadExtensionDLL(char * fullPath,XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf)
{

    const char* error_msg = NULL;
    error_msg = dlerror();
    if (error_msg) {
        printf("$ Before loading  %s\n", error_msg);
        return 0;
    }
/*	printf("$ Trying to Load %s in memory\n",fullPath);
    hGetProcIDDLL = dlopen(fullPath, RTLD_NOLOAD);
    if (hGetProcIDDLL != NULL) {
//		printf("library %s has already been loaded in memory!\n",fullPath);
        return 0;
    }
    error_msg = dlerror();
    if (error_msg) {
        printf("$ RTLD_NOLOAD returned %s\n", error_msg);
        return 0;
    }*/

    //printf("$ Loading %s in memory\n",fullPath);
    hGetProcIDDLL = dlopen(fullPath, RTLD_LAZY);
    if (hGetProcIDDLL == NULL) {
        return 0;
    }



    error_msg = dlerror();
    if (error_msg) {
        printf("$ %s\n", error_msg);
        return 0;
    }
    //printf("$ Loading %s.getNumberOfXpressKalisExtensions in memory\n",fullPath);
    getNumberOfXpressKalisExtensions = (pGetNumberOfXpressKalisExtensions) dlsym(hGetProcIDDLL, "getNumberOfXpressKalisExtensions\0");

    /* check that no error occured */
    error_msg = NULL;
    error_msg = dlerror();
    if (error_msg) {
        printf("$ Impossible to find getNumberOfXpressKalisExtensions in %s [%s]\n", fullPath,error_msg);
        dlclose(hGetProcIDDLL);
        return 0;
    }

    int exts =  getNumberOfXpressKalisExtensions();
        //mm->dispmsg(NULL,"%i extensions\n",exts);

    //printf("$ Loading %s.getXpressKalisModuleDefinition in memory\n",fullPath);
        getXpressKalisModuleDefinition = (pGetXpressKalisModuleDefinition) dlsym(hGetProcIDDLL, "getXpressKalisModuleDefinition\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

    doCleaning = (pDoCleaning) dlsym(hGetProcIDDLL, "resetXpressKalisModule\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

    setNiFCT = (pSetNiFCT) dlsym(hGetProcIDDLL, "setNiFCT\0");

    /* check that no error occured */
    error_msg = dlerror();
    if (error_msg) {
        dlclose(hGetProcIDDLL);
        return 0;
    }

    //mm->printf (NULL,"%i extensions found\n",exts);
       //cptr += snprintf(cptr,4096,"%i extensions found\n",exts);
       dllHandles.push_back(hGetProcIDDLL);
       dllCleaningFunctions.push_back(doCleaning);
       // First set Interface function pointer
       setNiFCT( nifct, interver,libver, interf);

       // Load the extensions
       loadXpressKalisExtensions(nifct,interver,libver,interf,exts);


   return exts;
}

static int loadExtensionsDLLS(XPRMnifct nifct, u_iorp *interver,u_iorp *libver, XPRMdsointer **interf)
{
    char * pPath;
    char fullPath[2048];


    char dsoPath[4096];
    int ret = XPRMgetdsopath(dsoPath, 4096);
    //mm->printf(NULL,"DSO PATHS  = %s\n",dsoPath);

    pPath = strtok (dsoPath,":");
        while (pPath != NULL)
    {
        //mm->printf (NULL,"Looking in %s\n",pPath);
        //cptr += snprintf(cptr,4096,"Looking in %s\n",pPath);
        DIR *dp;
        struct dirent *ep;
        dp = opendir (pPath);
        if (dp != NULL)
        {
            while (ep = readdir (dp)) {
                if (strstr(ep->d_name,".so")) {
                    //mm->printf (NULL,"Trying to load %s : ", ep->d_name);
                    //cptr += snprintf(cptr,4096,"Trying to load %s : ", ep->d_name);
                    snprintf(fullPath,2048,"%s/%s\0",pPath,ep->d_name);
                    int nbext = 0;
                    if (! (nbext = loadExtensionDLL(fullPath,nifct,interver,libver,interf))) {
                        //mm->printf (NULL,"%s is not an Xpress-Kalis extension module !\n",fullPath);
                        //cptr += snprintf(cptr,4096,"%s is not an Xpress-Kalis extension module !\n",fullPath);
                    }
                }
            }
            (void) closedir (dp);
        }
        else {
            //return 1;
        }

        pPath = strtok (NULL, ":");
    }
    // mm->printf (NULL,"%s\n",cptr);
    return 0;

}
#endif
#endif	// XPRESS KALIS EXTENSIONS
