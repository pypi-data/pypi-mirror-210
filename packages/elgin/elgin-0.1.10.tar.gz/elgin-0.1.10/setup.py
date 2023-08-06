from setuptools import find_packages, setup

with open('./README.md') as f:
    long_desc = f.read()

setup(
     name='elgin'
    ,version='0.1.10'
    ,description='Biblioteca responsavel por gerar o monitoramento dos processos da empresa elgin.'
    ,long_description=long_desc
    ,long_description_content_type='text/markdown'
    ,license="MIT"
    ,classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ]
    ,packages=['elgin']
    ,package_dir={'elgin': 'elgin'}
    ,package_data={'elgin': ['templates/*']}
    ,include_package_data=True
    ,install_requires=["requests","pymysql"]
)