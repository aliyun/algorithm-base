import os
from setuptools import setup, find_packages

try:
    os.symlink(os.getcwd() + '/spark_jars', os.getcwd() + '/src/ab/spark_jars')
except:
    pass

setup(
    packages=find_packages('src', exclude='dist'),
    package_dir={'': 'src'},
    package_data={
        "ab": ['spark_jars/*.jar', 'keys/*.so', './abt.sh']
    },
)
try:
    os.unlink('src/ab/spark_jars')
except:
    pass
