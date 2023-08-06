from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="we_report",
    version="0.0.1.10",
    author="Xia Zeyu",
    author_email="xiazeyu@wealthengine.cn",
    description="Wealth Engine ReportData Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://192.168.1.7:10600/xiazeyu/we_report.git",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.yml'],
        'data': ["*.xlsx"],
    },
    install_requires=[
        'numpy>=1.15',
        'pandas>=1.0.3',
        'arrow>=0.17.0',
        'sqlalchemy>=1.3.18',
        'scikit-learn',
        'matplotlib',
        'xlsxwriter',
        'scipy',
        'statsmodels',
        'six',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    zip_safe=False,
)
