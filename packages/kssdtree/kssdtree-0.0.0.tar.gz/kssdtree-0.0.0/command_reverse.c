#include "kssdheaders/command_reverse.h"
#include "kssdheaders/global_basic.h"
#include "kssdheaders/command_shuffle.h"
#include "kssdheaders/command_dist.h"
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

int co_rvs2kmer_byreads(reverse_opt_val_t *opt_val) {
    dim_shuffle_t *shuf_arr = read_dim_shuffle_file(opt_val->shufile);
    int shuf_arr_len = 1LLU << (4 * shuf_arr->dim_shuffle_stat.subk);
    unsigned int rev_shuf_arr[MIN_SUBCTX_DIM_SMP_SZ];
    int count = 0;
    for (unsigned int i = 0; i < shuf_arr_len; i++) {
        if (shuf_arr->shuffled_dim[i] < MIN_SUBCTX_DIM_SMP_SZ) {
            rev_shuf_arr[shuf_arr->shuffled_dim[i]] = i;
            count++;
        }
    }
    if (count != MIN_SUBCTX_DIM_SMP_SZ)
        err(errno, "count %d not match MIN_SUBCTX_DIM_SMP_SZ %d", count, MIN_SUBCTX_DIM_SMP_SZ);
    int comp_code_bits = shuf_arr->dim_shuffle_stat.k - shuf_arr->dim_shuffle_stat.drlevel > COMPONENT_SZ
                         ? 4 * (shuf_arr->dim_shuffle_stat.k - shuf_arr->dim_shuffle_stat.drlevel - COMPONENT_SZ) : 0;
    int inner_ctx_bits = shuf_arr->dim_shuffle_stat.subk * 4;
    int half_outer_ctx_bits = (shuf_arr->dim_shuffle_stat.k - shuf_arr->dim_shuffle_stat.subk) * 2;
    int pf_bits = (shuf_arr->dim_shuffle_stat.subk - shuf_arr->dim_shuffle_stat.drlevel) * 4;
    int TL = shuf_arr->dim_shuffle_stat.k * 2;
    if (!(opt_val->num_remaining_args == 1))
        err(errno, "need speficy one query path");
    const char *qryco_dstat_fpath = NULL;
    qryco_dstat_fpath = test_get_fullpath(opt_val->remaining_args[0], co_dstat);
    if (qryco_dstat_fpath == NULL)
        err(errno, "%s is not a valid query folder", opt_val->remaining_args[0]);
    FILE *qry_co_stat_fp;
    if ((qry_co_stat_fp = fopen(qryco_dstat_fpath, "rb")) == NULL) err(errno, "qry co stat file:%s", qryco_dstat_fpath);
    char *qryco_dname = opt_val->remaining_args[0];
    co_dstat_t co_qry_dstat;
    fread(&co_qry_dstat, sizeof(co_dstat_t), 1, qry_co_stat_fp);
    FILE *cbd_fcode_comp_index_fp;
    char co_cbd_fcode[PATHLEN];
    char co_cbd_index_fcode[PATHLEN];
    struct stat fstat;
    sprintf(co_cbd_index_fcode, "%s/combco.index.0", qryco_dname);
    stat(co_cbd_index_fcode, &fstat);
    llong readn = fstat.st_size / sizeof(size_t) - 1;
    size_t **cbd_fcode_index_mem = (size_t **) malloc(co_qry_dstat.comp_num * sizeof(size_t *));
    FILE **cbd_fcode_comp_fp = (FILE **) malloc(co_qry_dstat.comp_num * sizeof(FILE *));
    for (int j = 0; j < co_qry_dstat.comp_num; j++) {
        cbd_fcode_index_mem[j] = (size_t *) malloc((readn + 1) * sizeof(size_t));
        sprintf(co_cbd_index_fcode, "%s/combco.index.%d", qryco_dname, j);
        if ((cbd_fcode_comp_index_fp = fopen(co_cbd_index_fcode, "rb")) == NULL)
            err(errno, "co_rvs2kmer_btreads()::%s", co_cbd_index_fcode);
        fread(cbd_fcode_index_mem[j], sizeof(size_t), readn + 1, cbd_fcode_comp_index_fp);
        fclose(cbd_fcode_comp_index_fp);
        sprintf(co_cbd_fcode, "%s/combco.%d", qryco_dname, j);
        if ((cbd_fcode_comp_fp[j] = fopen(co_cbd_fcode, "rb")) == NULL)
            err(errno, "co_rvs2kmer_btreads()::%s[%d]", co_cbd_fcode, j);
    }
    char *kstring = malloc(TL + 1);
    kstring[TL] = '\0';
    unsigned int ind;
    for (llong n = 0; n < readn; n++) {
        printf(">read %llu\n", n + 1);
        for (int j = 0; j < co_qry_dstat.comp_num; j++) {
            for (llong k = 0; k < cbd_fcode_index_mem[j][n + 1] - cbd_fcode_index_mem[j][n]; k++) {
                fread(&ind, sizeof(unsigned int), 1, cbd_fcode_comp_fp[j]);
                llong unituple = core_reverse2unituple(ind, j, comp_code_bits, pf_bits, inner_ctx_bits,
                                                       half_outer_ctx_bits, rev_shuf_arr);
                for (int i = 0; i < TL; i++) {
                    kstring[TL - i - 1] = Mapbase[unituple % 4];
                    unituple >>= 2;
                }
                printf("%s\n", kstring);
            }
        }
    }
    for (int j = 0; j < co_qry_dstat.comp_num; j++) {
        fclose(cbd_fcode_comp_fp[j]);
        free(cbd_fcode_index_mem[j]);
    }
    free(cbd_fcode_index_mem);
    free(cbd_fcode_comp_fp);
    return 1;
}

typedef unsigned int ctx_obj_ct_t;

int co_reverse2kmer(reverse_opt_val_t *opt_val) {
    dim_shuffle_t *shuf_arr = read_dim_shuffle_file(opt_val->shufile);
    int shuf_arr_len = 1LLU << (4 * shuf_arr->dim_shuffle_stat.subk);
    unsigned int rev_shuf_arr[MIN_SUBCTX_DIM_SMP_SZ];
    int count = 0;
    for (unsigned int i = 0; i < shuf_arr_len; i++) {
        if (shuf_arr->shuffled_dim[i] < MIN_SUBCTX_DIM_SMP_SZ) {
            rev_shuf_arr[shuf_arr->shuffled_dim[i]] = i;
            count++;
        }
    }
    if (count != MIN_SUBCTX_DIM_SMP_SZ)
        err(errno, "count %d not match MIN_SUBCTX_DIM_SMP_SZ %d", count, MIN_SUBCTX_DIM_SMP_SZ);
    int comp_code_bits = shuf_arr->dim_shuffle_stat.k - shuf_arr->dim_shuffle_stat.drlevel > COMPONENT_SZ
                         ? 4 * (shuf_arr->dim_shuffle_stat.k - shuf_arr->dim_shuffle_stat.drlevel - COMPONENT_SZ) : 0;
    int inner_ctx_bits = shuf_arr->dim_shuffle_stat.subk * 4;
    int half_outer_ctx_bits = (shuf_arr->dim_shuffle_stat.k - shuf_arr->dim_shuffle_stat.subk) * 2;
    int pf_bits = (shuf_arr->dim_shuffle_stat.subk - shuf_arr->dim_shuffle_stat.drlevel) * 4;
    int TL = shuf_arr->dim_shuffle_stat.k * 2;
    if (!(opt_val->num_remaining_args > 0))
        err(errno, "need speficy the query path");
    const char *qryco_dstat_fpath = NULL;
    qryco_dstat_fpath = test_get_fullpath(opt_val->remaining_args[0], co_dstat);
    if (qryco_dstat_fpath == NULL)
        err(errno, "%s is not a valid query folder", opt_val->remaining_args[0]);
    FILE *qry_co_stat_fp;
    if ((qry_co_stat_fp = fopen(qryco_dstat_fpath, "rb")) == NULL) err(errno, "qry co stat file:%s", qryco_dstat_fpath);
    char *qryco_dname = opt_val->remaining_args[0];
    co_dstat_t co_qry_dstat;
    fread(&co_qry_dstat, sizeof(co_dstat_t), 1, qry_co_stat_fp);
    ctx_obj_ct_t *qry_ctx_ct_list = malloc(co_qry_dstat.infile_num * sizeof(ctx_obj_ct_t));
    fread(qry_ctx_ct_list, sizeof(ctx_obj_ct_t), co_qry_dstat.infile_num, qry_co_stat_fp);
    char (*cofname)[PATHLEN] = malloc(co_qry_dstat.infile_num * PATHLEN);
    fread(cofname, PATHLEN, co_qry_dstat.infile_num, qry_co_stat_fp);
    fclose(qry_co_stat_fp);
    FILE *cbd_fcode_comp_fp, *cbd_fcode_comp_index_fp;
    struct stat cbd_fcode_stat;
    size_t *fco_pos = malloc(sizeof(size_t) * (co_qry_dstat.infile_num + 1));
    char co_cbd_fcode[PATHLEN];
    char co_cbd_index_fcode[PATHLEN];
    llong **kmer = malloc(co_qry_dstat.infile_num * sizeof(llong *));
    int *filled_len = calloc(co_qry_dstat.infile_num, sizeof(int));
    for (int k = 0; k < co_qry_dstat.infile_num; k++) {
        kmer[k] = malloc(sizeof(llong) * qry_ctx_ct_list[k]);
    }
    int p_fit_mem = opt_val->p;
    for (int j = 0; j < co_qry_dstat.comp_num; j++) {
        sprintf(co_cbd_fcode, "%s/combco.%d", qryco_dname, j);
        if ((cbd_fcode_comp_fp = fopen(co_cbd_fcode, "rb")) == NULL) err(errno, "co_reverse2kmer()::%s", co_cbd_fcode);
        stat(co_cbd_fcode, &cbd_fcode_stat);
        unsigned int *cbd_fcode_mem = malloc(cbd_fcode_stat.st_size);
        fread(cbd_fcode_mem, sizeof(unsigned int), cbd_fcode_stat.st_size / sizeof(unsigned int), cbd_fcode_comp_fp);
        fclose(cbd_fcode_comp_fp);
        sprintf(co_cbd_index_fcode, "%s/combco.index.%d", qryco_dname, j);
        if ((cbd_fcode_comp_index_fp = fopen(co_cbd_index_fcode, "rb")) == NULL)
            err(errno, "co_reverse2kmer()::%s", co_cbd_index_fcode);
        fread(fco_pos, sizeof(size_t), co_qry_dstat.infile_num + 1, cbd_fcode_comp_index_fp);
        fclose(cbd_fcode_comp_index_fp);
#pragma omp parallel for num_threads(p_fit_mem) schedule(guided)
        for (int k = 0; k < co_qry_dstat.infile_num; k++) {
            if (qry_ctx_ct_list[k] == 0) continue;
            char *kstring = malloc(TL + 1);
            kstring[TL] = '\0';
            for (int n = 0; n < fco_pos[k + 1] - fco_pos[k]; n++) {
                unsigned int ind = cbd_fcode_mem[fco_pos[k] + n];
                kmer[k][filled_len[k] + n] = core_reverse2unituple(ind, j, comp_code_bits, pf_bits, inner_ctx_bits,
                                                                   half_outer_ctx_bits, rev_shuf_arr);
            }
            filled_len[k] += (fco_pos[k + 1] - fco_pos[k]);
        }
    }
#pragma omp parallel for num_threads(p_fit_mem) schedule(guided)
    for (int k = 0; k < co_qry_dstat.infile_num; k++) {
        if (qry_ctx_ct_list[k] == 0) continue;
        char *kstring = malloc(TL + 1);
        kstring[TL] = '\0';
        char *filename;
        (filename = strrchr(cofname[k], '/')) ? ++filename : (filename = cofname[k]);
        char fullname[PATHLEN];
        sprintf(fullname, "%s/%s", opt_val->outdir, filename);
        FILE *kmerf;
        if ((kmerf = fopen(fullname, "w")) == NULL) err(errno, "%s", filename);
        for (int n = 0; n < qry_ctx_ct_list[k]; n++) {
            llong unituple = kmer[k][n];
            for (int i = 0; i < TL; i++) {
                kstring[TL - i - 1] = Mapbase[unituple % 4];
                unituple >>= 2;
            }
            fprintf(kmerf, "%s\n", kstring);
        }
        fclose(kmerf);
    }
    return co_qry_dstat.infile_num;
}

llong core_reverse2unituple(unsigned int kid, int compid, int compbit, int pf_bits, int inner_ctx_bits,
                            int half_outer_ctx_bits, unsigned int *rev_shuf_arr) {
    llong drtuple = (((llong) kid) << compbit) + compid;
    unsigned int ind = rev_shuf_arr[drtuple % MIN_SUBCTX_DIM_SMP_SZ];
    llong tuple = ((drtuple >> pf_bits) << inner_ctx_bits) + (llong) ind;
    llong half_outer_ctx_mask = ((1LLU << half_outer_ctx_bits) - 1) << inner_ctx_bits;
    llong unituple = (tuple & (half_outer_ctx_mask << half_outer_ctx_bits))
                     + ((tuple & half_outer_ctx_mask) >> inner_ctx_bits)
                     + ((tuple & ((1LLU << inner_ctx_bits) - 1)) << half_outer_ctx_bits);
    return unituple;
}
