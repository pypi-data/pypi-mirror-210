from setuptools import find_packages, setup

setup(
    name='spreadsheet-migrator',
    version='0.1',
    description='Plugin to migrate your data from spreadsheets',
    install_requires=[
        'openpyxl==3.1.1'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
