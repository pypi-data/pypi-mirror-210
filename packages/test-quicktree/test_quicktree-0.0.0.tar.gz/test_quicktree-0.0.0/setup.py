from setuptools import setup, Extension

MOD1 = 'quicktree'
sources1 = ['align.c',
            'buildtree.c',
            'cluster.c',
            'distancemat.c',
            'pyquicktree.c',
            'sequence.c',
            'tree.c',
            'util.c']
include_dirs1 = ['quicktreeheaders']

setup(
    name='test_quicktree',
    ext_modules=[
        Extension(MOD1, sources=sources1, include_dirs=include_dirs1)
    ],
    py_modules=['main'],
    entry_points={
        "console_scripts": [
            "tquicktree = main:main",
        ]
    },
    include_package_data=True,
    package_data={
        'test_quicktree': ['quicktreeheaders/*.h'],
    }
)
# python3 setup.py bdist_wheel
# python3 setup.py sdist
# tquicktree -i kssd_dist_matrix.phy -o kssdtree.nwk
