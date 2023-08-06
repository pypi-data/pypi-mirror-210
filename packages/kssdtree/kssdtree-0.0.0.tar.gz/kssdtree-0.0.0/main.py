import argparse
import kssd
import quicktree
import os
import create_distance_matrix


def shuffle(args):
    k = args.k
    s = args.s
    l = args.l
    o = args.o
    state = kssd.write_dim_shuffle_file(k, s, l, o)
    print('shuffle finished!')


def sketch(args):
    k = args.k
    L = args.L
    r = args.r
    o = args.o
    state = kssd.dist_dispatch(k, L, r, o, 0)
    print('sketch finished!')


def dist(args):
    k = args.k
    r = args.r
    o = args.o
    remaining_args = args.remaining_args
    distance_matrix = args.distance_matrix
    state = kssd.dist_dispatch(k, r, o, remaining_args, 1)
    if distance_matrix != '':
        file_path = os.path.join(os.getcwd(), o, "distance.out")
        create_distance_matrix.create(file_path, distance_matrix)
    print('dist finished!')


def buildtree(args):
    i = args.i
    o = args.o
    state = quicktree.buildtree(i, o)
    from Bio import Phylo
    import matplotlib.pyplot as plt
    # 读取并解析nwk文件
    tree = Phylo.read(o, "newick")
    # 可视化并保存图片
    Phylo.draw(tree)
    Phylo.draw_ascii(tree)
    # 保存树图像
    plt.axis('off')
    plt.gcf().set_size_inches(10, 10)
    plt.savefig("kssdtree.png", dpi=300, bbox_inches='tight', pad_inches=0)
    if state == 1:
        print('buildtree finished!')


def main():
    parser = argparse.ArgumentParser(description='Kssdtree')
    subparsers = parser.add_subparsers(help='subcommands', dest='subparser_name')
    # 添加 shuffle 命令的解析器
    parser_shuffle = subparsers.add_parser('shuffle', help='Shuffle')
    parser_shuffle.add_argument('-k', type=int, default=8, required=True,
                                help='a half of the length of k-mer. For proyakat genome, k = 8 is suggested; for mammals, k = 10 or 11 is suggested.')
    parser_shuffle.add_argument('-s', type=int, default=5, required=True,
                                help='a half of the length of k-mer substring.')
    parser_shuffle.add_argument('-l', type=int, default=2, required=True,
                                help='the level of dimensionality reduction, the expectation dimensionality reduction rate is 16^n if set -l = n.')
    parser_shuffle.add_argument('-o', type=str, default='default',
                                help="specify the output file name prefix, if not specify default shuffle named 'default.shuf' generated.")
    parser_shuffle.set_defaults(func=shuffle)

    # 添加 sketch 命令的解析器
    parser_sketch = subparsers.add_parser('sketch', help='Sketch')
    parser_sketch.add_argument('-k', type=int, default=8,
                               help='a half of the length of k-mer. For proyakat genome, k = 8 is suggested; for mammals, k = 10 or 11 is suggested.')
    parser_sketch.add_argument('-L', type=str, default='', required=True,
                               help='Dimension Reduction Level or provide .shuf file.')
    parser_sketch.add_argument('-r', type=str, default='', required=True,
                               help='reference genome/database search against.')
    parser_sketch.add_argument('-o', type=str, default='', required=True, help='folder path for results files.')
    parser_sketch.set_defaults(func=sketch)

    # 添加 dist 命令的解析器
    parser_dist = subparsers.add_parser('dist', help='Dist')
    parser_dist.add_argument('-k', type=int, default=8,
                             help='a half of the length of k-mer. For proyakat genome, k = 8 is suggested; for mammals, k = 10 or 11 is suggested.')
    parser_dist.add_argument('-r', type=str, default='', required=True,
                             help='reference genome/database search against.')
    parser_dist.add_argument('-o', type=str, default='', required=True, help='folder path for results files.')
    parser_dist.add_argument('remaining_args', type=str, default='', help='reference genome/database search against.')
    parser_dist.add_argument('-distance-matrix', type=str, default='kssd_dist_matrix', required=True,
                             help='create a distance matrix in phylip format.')
    parser_dist.set_defaults(func=dist)

    # 添加 buildtree 命令的解析器
    parser_buildtree = subparsers.add_parser('buildtree', help='Buildtree')
    parser_buildtree.add_argument('-i', type=str, default='kssd_dist_matrix.phy', required=True,
                                  help='input file is a distance matrix in phylip format.')
    parser_buildtree.add_argument('-o', type=str, default='kssdtree.nwk', required=True,
                                  help='output file is a tree in Newick format.')
    parser_buildtree.set_defaults(func=buildtree)
    # 解析命令行参数，并调用对应的子命令处理函数
    args = parser.parse_args()
    args.func(args)
