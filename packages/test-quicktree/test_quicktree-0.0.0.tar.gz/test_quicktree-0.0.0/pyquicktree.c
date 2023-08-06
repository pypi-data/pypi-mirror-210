#include <Python.h>
#include "quicktreeheaders/util.h"
#include "quicktreeheaders/align.h"
#include "quicktreeheaders/cluster.h"
#include "quicktreeheaders/buildtree.h"
#include "quicktreeheaders/distancemat.h"
#include "quicktreeheaders/tree.h"


void buildtree(FILE *input) {
    struct DistanceMatrix *mat;
    struct Alignment *aln;
    struct Tree *myTree;
    struct ClusterGroup *group;

    mat = read_phylip_DistanceMatrix(input, &aln);
    fclose(input);
    print_DistanceMatrix(stdout, mat);
    int row, column;
    for (row = 0; row < mat->size; row++) {
        for (column = 0; column <= row; column++)
            printf("%10.5f", mat->data[row][column]);
        printf("\n");
    }
    group = alignment_to_ClusterGroup(aln, FALSE);
    group->matrix = mat;


    myTree = neighbour_joining_buildtree(group, FALSE);
    write_newhampshire_Tree(stdout, myTree, FALSE);
    aln = free_Alignment(aln);
    group = free_ClusterGroup(group);
    myTree = free_Tree(myTree);
}

/* 把普通C语言实现的quickkssdtree()封装成Python可以调用的函数 */
static PyObject *py_buildtree(PyObject *self, PyObject *args) {

    char *input_name;
    char *output_name;
    FILE *matrixfile;
    /* 从 args 里解析实际参数 */
    if (!PyArg_ParseTuple(args, "ss", &input_name, &output_name)) {
        return NULL;
    }
    matrixfile = fopen(input_name, "r");
    if (matrixfile == NULL)
        fatal_util("Could not open file %s for reading", input_name);
    buildtree(matrixfile);
    /* 把 int 转化为 PyObject* */
    return Py_BuildValue("i", 1);
}

/* 定义模块的 method table */
static PyMethodDef QuicktreeMethods[] = {
        {"buildtree", py_buildtree, METH_VARARGS, "Greatest common divisor"},
        {NULL, NULL,                0, NULL}
};

/* 定义模块结构 */
static struct PyModuleDef quicktreemodule = {
        PyModuleDef_HEAD_INIT,
        "quicktree",           /* name of module */
        "A quicktree module",  /* Doc string (may be NULL) */
        -1,                 /* Size of per-interpreter state or -1 */
        QuicktreeMethods       /* Method table */
};


/* 模块初始化函数 */
PyMODINIT_FUNC PyInit_quicktree(void) {
    return PyModule_Create(&quicktreemodule);
}