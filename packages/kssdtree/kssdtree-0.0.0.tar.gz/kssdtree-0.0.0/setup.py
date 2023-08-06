from setuptools import setup, Extension

MOD1 = 'kssd'
MOD2 = 'quicktree'
sources1 = ['co2mco.c',
            'iseq2comem.c',
            'command_dist_wrapper.c',
            'mytime.c',
            'global_basic.c',
            'command_dist.c',
            'command_shuffle.c',
            'command_set.c',
            'command_reverse.c',
            'command_composite.c',
            'pykssd.c']
sources2 = ['pyquicktree.c',
            'align.c',
            'cluster.c',
            'distancemat.c',
            'util.c',
            'tree.c',
            'buildtree.c',
            'sequence.c']
include_dirs1 = ['kssdheaders']
include_dirs2 = ['quicktreeheaders']

setup(
    name='kssdtree',
    ext_modules=[
        Extension(MOD1, sources=sources1, include_dirs=include_dirs1),
        Extension(MOD2, sources=sources2, include_dirs=include_dirs2)
    ],
    py_modules=['main', 'create_distance_matrix'],
    entry_points={
        "console_scripts": [
            "kssdtree = main:main",
        ]
    }
)

# mean1:
# cd kssdtree
# python3 setup.py build
# python3 setup.py install

# python3 main.py shuffle -k 8 -s 5 -l 2 (default.shuf) (完成)
# python3 main.py shuffle -k 10 -s 6 -l 3 -o L3K10 (完成)

# python3 main.py sketch -L 3 -k 10 -r seqs -o reference (完成)
# python3 main.py sketch -L default.shuf -r seqs -o reference (完成)

# python3 main.py dist -r reference -o distout reference -distance-matrix kssd_dist_matrix (完成)

# python3 main.py buildtree -i kssd_dist_matrix.phy -o kssdtree.nwk (完成)


# mean2:
# cd kssdtree
# pip install wheel
# pip install --upgrade setuptools wheel
# python3 setup.py bdist_wheel
# pip install kssdtree-0.0.0-cp39-cp39-linux_x86_64.whl

# kssdtree shuffle -k 8 -s 5 -l 2 (default.shuf) (完成)
# kssdtree shuffle -k 10 -s 6 -l 3 -o L3K10 (完成)

# kssdtree sketch -L 3 -k 10 -r seqs -o reference
# kssdtree sketch -L default.shuf -r seqs -o reference (完成)

# kssdtree dist -r reference -o distout reference -distance-matrix kssd_dist_matrix (完成)

# kssdtree buildtree -i kssd_dist_matrix.phy -o kssdtree.nwk (完成)
