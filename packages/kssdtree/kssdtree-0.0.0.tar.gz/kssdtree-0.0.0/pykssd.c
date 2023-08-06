#include <Python.h>
#include "kssdheaders/command_dist.h"
#include "kssdheaders/command_dist_wrapper.h"
#include "kssdheaders/command_shuffle.h"
#include "kssdheaders/global_basic.h"
#include <stdio.h>
#include <string.h>
#include <err.h>

dim_shuffle_stat_t dim_shuffle_stat = {
        0,
        8,
        5,
        2,
};
char shuf_out_file_prefix[PATHLEN] = "./default";

/* 把普通C语言实现的py_write_dim_shuffle_file()封装成Python可以调用的函数 */
static PyObject *py_write_dim_shuffle_file(PyObject *self, PyObject *args) {
    int k, s, l;
    char *o;

    /* 从 args 里解析实际参数 */
    if (!PyArg_ParseTuple(args, "iiis", &k, &s, &l, &o)) {
        return NULL;
    }
    dim_shuffle_stat.k = k;
    dim_shuffle_stat.subk = s;
    dim_shuffle_stat.drlevel = l;
    strcpy(shuf_out_file_prefix, o);

    /* 调用普通C语言实现的write_dim_shuffle_file() */
    int state = write_dim_shuffle_file(&dim_shuffle_stat, shuf_out_file_prefix);
    /* 把 int 转化为 PyObject* */
    return Py_BuildValue("i", state);
}

dist_opt_val_t dist_opt_val =
        {
                .k = 8,
                .p = 0,
                .dr_level = 2,
                .dr_file = "",
                .mmry = 0,
                .fmt = "mfa",
                .refpath = "",
                .fpath = "",
                .outdir = ".",
                .kmerocrs = 1,
                .kmerqlty = 0,
                .keepco = false,
                .stage2 = false,
                .num_neigb = 0,
                .mut_dist_max = 1,
                .metric = Jcd,
                .outfields = CI,
                .correction = false,
                .abundance = false,
                .pipecmd = "",
                .shared_kmerpath="",
                .keep_shared_kmer=false,
                .byread=false,
                .num_remaining_args = 0,
                .remaining_args = NULL
        };

/* 把普通C语言实现的add()封装成Python可以调用的函数 */
static PyObject *py_dist_dispatch(PyObject *self, PyObject *args) {
    char *str1, *str2, *str3;
    int k;
    int flag;
    /* 从 args 里解析实际参数 */
    if (!PyArg_ParseTuple(args, "isssi", &k, &str1, &str2, &str3, &flag)) {
        return NULL;
    }
    if (flag == 0) {
        if (k != 8) {
            dist_opt_val.k = k;
        }
        struct stat path_stat;
        if (stat(str1, &path_stat) >= 0 && S_ISREG(path_stat.st_mode)) {
            if (strlen(str1) < PATHLEN)
                strcpy(dist_opt_val.dr_file, str1);
            else
                err(errno, "-L argument path should not longer than %d", PATHLEN);
        } else {
            if (atoi(str1) >= dist_opt_val.k - 2 || atoi(str1) < 0)
                err(errno, "-L: dimension reduction level should never larger than Kmer length - 2,"
                           " which is %d here", dist_opt_val.k - 2);
            dist_opt_val.dr_level = atoi(str1);
        }
        strcpy(dist_opt_val.refpath, str2);
        strcpy(dist_opt_val.outdir, str3);
    } else {
        strcpy(dist_opt_val.refpath, str1);
        strcpy(dist_opt_val.outdir, str2);
        dist_opt_val.num_remaining_args = 1;
        dist_opt_val.remaining_args = &str3;
    }
    /* 调用普通C语言实现的dist_dispatch() */
    int state = dist_dispatch(&dist_opt_val);
    /* 把 int 转化为 PyObject* */
    return Py_BuildValue("i", state);
}

/* 定义模块的 method table */
static PyMethodDef KssdMethods[] = {
        {"write_dim_shuffle_file", py_write_dim_shuffle_file, METH_VARARGS, "shuffle"},
        {"dist_dispatch",          py_dist_dispatch,          METH_VARARGS, "sketch"},
        {NULL, NULL,                                          0, NULL}
};

/* 定义模块结构 */
static struct PyModuleDef kssdmodule = {
        PyModuleDef_HEAD_INIT,
        "kssd",           /* name of module */
        "A kssd module",  /* Doc string (may be NULL) */
        -1,                 /* Size of per-interpreter state or -1 */
        KssdMethods       /* Method table */
};


/* 模块初始化函数 */
PyMODINIT_FUNC PyInit_kssd(void) {
    return PyModule_Create(&kssdmodule);
}