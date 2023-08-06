import pandas as pd
import warnings
import os

warnings.filterwarnings('ignore')


def create(path, name):
    current_path = os.getcwd()
    print('dealing distance.out...')
    # 读取文件
    df = pd.read_csv(path, delimiter='\t')
    # 取出Qry、Ref、MashD三列数据
    new_df = df[['Qry', 'Ref', 'MashD']]
    # 对Qry列进行处理
    if '.fasta.gz' in new_df['Qry'][0]:
        new_df['Ref'] = new_df['Ref'].apply(lambda x: x.split('.')[-3].split('/')[-1])
        new_df['Qry'] = new_df['Qry'].apply(lambda x: x.split('.')[-3].split('/')[-1])
    else:
        new_df['Qry'] = new_df['Qry'].apply(lambda x: x.split('.')[-2].split('/')[-1].split('_')[0])
        new_df['Ref'] = new_df['Ref'].apply(lambda x: x.split('.')[-2].split('/')[-1].split('_')[0])
    # 保存为txt文件
    txt_path = current_path + '/kssd_distance.txt'
    new_df.to_csv(txt_path, index=False, sep='\t')
    # 读取Mash距离数据
    data = {}
    with open(txt_path, 'r') as f:
        next(f)  # 跳过表头
        for line in f:
            seq1, seq2, distance = line.strip().split()
            if seq1 not in data:
                data[seq1] = {}
            if seq2 not in data:
                data[seq2] = {}
            data[seq1][seq2] = float(distance)
            data[seq2][seq1] = float(distance)
    if os.path.exists(txt_path):
        os.remove(txt_path)
        # print("File deleted successfully")
    else:
        print(f"The file {txt_path} does not exist")
    # 将距离矩阵写出为phylip格式的文件
    n_seqs = len(data)
    seq_names = sorted(data.keys())
    '''
    Phylip格式的距离矩阵一般包含以下几个部分：
    序列数目和序列长度：第一行包含两个数，分别表示序列数目和序列长度，用空格分隔。
    序列名称和长度：接下来的每一行都包含一个序列的名称和其长度，用制表符（\t）分隔。
    距离矩阵：接下来的每一行都包含一个序列的名称和该序列到其余序列的距离值，用制表符（\t）分隔。对角线上的元素表示序列到其本身的距离，通常为0。
    下面是一个Phylip格式距离矩阵的例子：
    3
    Seq1         0.00000    0.10000    0.30000
    Seq2         0.10000    0.00000    0.20000
    Seq3         0.30000    0.20000    0.00000
    可以看出，该距离矩阵表示有3个长度为10的序列，它们的名称依次为Seq1、Seq2和Seq3。对角线上的元素为0，表示每个序列到自身的距离为0。距离值精确到小数点后五位，并使用制表符分隔。
    '''
    with open(current_path + '/' + name + '.phy', 'w') as f:
        f.write(str(len(seq_names)) + '\n')
        # 将距离矩阵写出到文件
        for i in range(n_seqs):
            f.write(seq_names[i])
            for j in range(n_seqs):
                if i == j:
                    f.write('\t{:.5f}'.format(0.0))
                else:
                    f.write('\t{:.5f}'.format(data[seq_names[i]][seq_names[j]]))
            f.write('\n')
    print('create distance_matrix finished!')
