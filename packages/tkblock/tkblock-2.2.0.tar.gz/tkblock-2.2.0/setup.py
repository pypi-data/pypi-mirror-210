from setuptools import setup
from codecs import open
from os import path

package_name = "tkblock"
root_dir = path.abspath(path.dirname(__file__))
# requiwements.txtの中身を読み込む
def _requirements():
    return [
        name.rstrip()
        for name in open(path.join(root_dir, "requirements.txt")).readlines()
    ]


# README.mdをlong_discriptionにするために読み込む
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name=package_name,
    version="2.2.0",
    description="tkinter block framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kuri-pome/tkblock",
    author="kuri_pome",
    license="MIT",
    keywords="tkinter place widget easy",
    packages=[package_name],
    install_requires=_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
