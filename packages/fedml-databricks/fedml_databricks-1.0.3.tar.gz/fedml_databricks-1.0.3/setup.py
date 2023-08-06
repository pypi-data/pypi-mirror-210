import setuptools
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setuptools.setup(
    name="fedml_databricks",
    version="1.0.3",
    author="SAP SE",
    description="A python library for building machine learning models on Databricks using a federated data source",
    license='Apache License 2.0',
    license_files = ['LICENSE.txt'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "hdbcli","pandas","pyspark","ruamel.yaml","requests","mlflow","databricks-cli"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3",
    scripts=['src/fedml_databricks/kubectl_install_validate.sh', 'src/fedml_databricks/acr/acr_kyma_deploy.sh', 'src/fedml_databricks/ecr/ecr_kyma_deploy.sh', 'src/fedml_databricks/databricks_cli_configure.sh'],
    include_package_data=True
)