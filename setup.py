from setuptools import setup, find_packages
import arise

setup(
    name='arise',
    version=arise.__version__,
    packages=find_packages(),
    license='Apache 2.0 License',
    description='ML-based performance prediction for AI workloads configuration management',
    install_requires=[
        'pandas~=2.1.3',
        'PyYaml',
        'scikit-learn==1.5.1',
        'numpy',
        'scipy',
        'numpyencoder',
        'linear-tree',
        'stopit',
        'kneed',
        'ConfigArgParse',
        'matplotlib',
        'xgboost==2.1.1',
        'catboost',
    ],
    include_package_data=True,
)
