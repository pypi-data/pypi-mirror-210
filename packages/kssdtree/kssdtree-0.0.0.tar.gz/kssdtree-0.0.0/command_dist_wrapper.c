#include "kssdheaders/command_dist_wrapper.h"

#include <err.h>
#ifdef _OPENMP
#include <omp.h>
#else
#define omp_get_thread_num() 0
#endif

const char *mk_dist_rslt_dir(const char *parentdirpath, const char *outdirpath) {
    struct stat dstat;
    const char *outfullpath = malloc(PATHLEN * sizeof(char));
    sprintf((char *) outfullpath, "%s/%s", parentdirpath, outdirpath);
    if (stat(parentdirpath, &dstat) == 0 && S_ISDIR(dstat.st_mode)) {
        if (stat(outfullpath, &dstat) == 0) {
            errno = EEXIST;
            err(errno, "%s", outfullpath);
        } else {
            mkdir(outfullpath, 0777);
        }
    } else {
        mkdir(parentdirpath, 0777);
        mkdir(outfullpath, 0777);
    }
    return outfullpath;
};
