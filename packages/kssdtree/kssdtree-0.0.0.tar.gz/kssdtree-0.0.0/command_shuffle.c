#include "kssdheaders/command_shuffle.h"
#include "kssdheaders/global_basic.h"
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <argp.h>
#include <argz.h>
#include <err.h>
#include <errno.h>
#include <math.h>


int *shuffle(int arr[], int len_arr) {
    if (len_arr > RAND_MAX)
        err(errno, "shuffling array length %d longer than RAND_MAX: %d", len_arr, RAND_MAX);
    srand(time(NULL));
    int j, temp;
    for (int i = len_arr - 1; i > 0; i--) {
        j = rand() % (i + 1);
        temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    return arr;
};

int *shuffleN(int n, int base) {
    int *arr;
    arr = malloc(n * sizeof(int));
    if (arr == NULL) err(errno, "shuffleN");
    for (int i = 0; i < n; i++)
        arr[i] = i + base;
    return shuffle(arr, n);
};

int add_len_drlevel2subk(void) {
    int min_smp_len = 0, min_subctx_dim_smp_sz;
    min_subctx_dim_smp_sz = MIN_SUBCTX_DIM_SMP_SZ;
    while (min_subctx_dim_smp_sz >>= 1) { min_smp_len++; };
    return ceil((float) min_smp_len / 4);
};

int write_dim_shuffle_file(dim_shuffle_stat_t *dim_shuffle_stat, char *outfile_prefix) {
    if (dim_shuffle_stat->k < dim_shuffle_stat->subk)
        err(errno, "write_dim_shuffle_file(): half-context len: %d"
                   "should larger than half-subcontext len (or dimension reduce level + 2) %d",
            dim_shuffle_stat->k, dim_shuffle_stat->subk);
    if (dim_shuffle_stat->subk >= 8)
        err(errno, "write_dim_shuffle_file(): subk shoud smaller than 8");
    int dim_after_reduction = 1 << 4 * (dim_shuffle_stat->subk - dim_shuffle_stat->drlevel);
    if (dim_after_reduction < MIN_SUBCTX_DIM_SMP_SZ)
        warnx("dimension after reduction %d is smaller than the suggested minimal"
              " dimension sample size %d, which might cause loss of robutness, -s %d is suggested", dim_after_reduction,
              MIN_SUBCTX_DIM_SMP_SZ, dim_shuffle_stat->drlevel + 3);
    if (strlen(outfile_prefix) + strlen(".shuf") > PATHLEN)
        err(errno, "output path name %s should less than %d characters", outfile_prefix, PATHLEN);
    char outfile[PATHLEN];
    sprintf(outfile, "%s.shuf", outfile_prefix);
    FILE *shuf_out;
    if ((shuf_out = fopen(outfile, "wb")) == NULL)
        err(errno, "write_dim_shuffle_file(): open file %s failed", outfile);
    srand(time(NULL));
    dim_shuffle_stat->id = rand();
    int *shuffled_dim = shuffleN(1 << 4 * dim_shuffle_stat->subk, 0);
    shuffled_dim = shuffle(shuffled_dim, 1 << 4 * dim_shuffle_stat->subk);
    int ret = fwrite(dim_shuffle_stat, sizeof(dim_shuffle_stat_t), 1, shuf_out)
              + fwrite(shuffled_dim, sizeof(int), 1 << 4 * dim_shuffle_stat->subk, shuf_out);
    fclose(shuf_out);
    free(shuffled_dim);
    return ret;
};

dim_shuffle_t *read_dim_shuffle_file(char *dim_shuffle_file) {
    int basename_len = strlen(dim_shuffle_file) - strlen(".shuf");
    if (strcmp((dim_shuffle_file + basename_len), ".shuf") != 0)
        err(errno, "read_dim_shuffle_file(): input file %s is not .shuf file", dim_shuffle_file);
    FILE *shuf_in;
    if ((shuf_in = fopen(dim_shuffle_file, "rb")) == NULL)
        err(errno, "read_dim_shuffle_file(): open file %s failed", dim_shuffle_file);
    dim_shuffle_t *dim_shuffle = malloc(sizeof(dim_shuffle_t));
    fread(&(dim_shuffle->dim_shuffle_stat), sizeof(dim_shuffle_stat_t), 1, shuf_in);
    int shuf_arr_len = 1 << 4 * dim_shuffle->dim_shuffle_stat.subk;
    dim_shuffle->shuffled_dim = malloc(sizeof(int) * shuf_arr_len);
    fread(dim_shuffle->shuffled_dim, sizeof(int) * shuf_arr_len, 1, shuf_in);
    fclose(shuf_in);
    return dim_shuffle;
}
