from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

DOCS_PATH = Path(__file__).parents[0] / "README.md"
PATH = Path("README.md")
if not PATH.exists():
    with open(DOCS_PATH, encoding="utf-8") as f1:
        with open(PATH, "w+", encoding="utf-8") as f2:
            f2.write(f1.read())

setup(
    name="notion2vuepress",
    version="1.0.1",
    description="notion2vuepress",
    long_description=open(PATH, encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YiZhang-You/notion2vuepress.git",
      author='YiZhang-You',
      author_email='yyz18071720400@163.com',
    packages=find_namespace_packages("notion2vuepress"),
    package_dir={"": "notion2vuepress"},
    install_requires=[
      "backports.zoneinfo==0.2.1",
      "beautifulsoup4==4.12.2",
      "bs4==0.0.1",
      "cached-property==1.5.2",
      "certifi==2023.5.7",
      "charset-normalizer==3.1.0",
      "commonmark==0.9.1",
      "dictdiffer==0.9.0",
      "idna==3.4",
      "notion==0.0.25",
      "notion-cobertos-fork==0.0.29",
      "python-slugify==8.0.1",
      "requests==2.31.0",
      "soupsieve==2.4.1",
      "text-unidecode==1.3",
      "tzdata==2023.3",
      "tzlocal==5.0.1",
      "urllib3==1.25.11",

    ],

)
