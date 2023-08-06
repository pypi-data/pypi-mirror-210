import argparse
import quicktree
# from Bio import Phylo
# import matplotlib.pyplot as plt


def main():
    # 创建命令行解析器
    parser = argparse.ArgumentParser(description='buildtree')
    # 添加位置参数
    parser.add_argument('-i', type=str, default='kssd_dist_matrix.phy', required=True,
                        help='input file is a distance matrix in phylip format.')
    parser.add_argument('-o', type=str, default='kssdtree.nwk', required=True,
                        help='output file is a tree in Newick format.')
    # 解析命令行输入
    args = parser.parse_args()
    i = args.i
    o = args.o
    state = quicktree.buildtree(i, o)
    # # 读取并解析nwk文件
    # tree = Phylo.read(o, "newick")
    # # 可视化并保存图片
    # Phylo.draw(tree)
    # Phylo.draw_ascii(tree)
    # # 保存树图像
    # plt.axis('off')
    # plt.gcf().set_size_inches(10, 10)
    # plt.savefig("kssdtree.png", dpi=300, bbox_inches='tight', pad_inches=0)
    if state == 1:
        print('buildtree finished!')
