import pathlib
import json
import os
from setuptools import setup

with open('package.json') as f:
    package = json.load(f)

package_name = package["name"].replace(" ", "_").replace("-", "_")

HERE = pathlib.Path(__file__).parent
readme = (HERE / "README.md").read_text()

setup(
    name=package_name,
    version=package["version"],
    author=package['author'].get("name"),
    packages=[package_name],
    include_package_data=True,
    license=package['license'],
    description=package.get('description', package_name),
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers = [
        'Framework :: Dash',
    ],
    project_urls={
        'Home': 'https://glue42.com/',
        'Documentation': 'https://docs.glue42.com/getting-started/how-to/glue42-enable-your-app/dash/index.html'
    },
    python_requires=">=3.6"
)
