from setuptools import setup, find_packages

setup(
    name='Slpapy',
    version='0.3.23',
    author='yifan xu',
    author_email='xuyifan@westlake.edu.cn',
    description='Spatial_lipomic_and_proteomic_analysis',
    packages=find_packages(),
    install_requires=[
        'scanpy>=1.9.1',
        'anndata>=0.8.0',
        'numpy>=1.23.1',
        'scipy>=1.9.0',
        'pandas>=1.5.1',
        'scikit-learn>=1.2.1',
        'statsmodels>=0.13.1',
        'leidenalg>=0.8.7',
    ]
)