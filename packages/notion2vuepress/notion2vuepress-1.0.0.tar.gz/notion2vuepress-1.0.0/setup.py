from distutils.core import setup
import setuptools

packages = ['notion2vuepress']  # 唯一的包名，自己取名
setup(
      name='notion2vuepress',
      version='1.0.0',
      description='notion2vuepress',
      author='YiZhang-You',
      author_email='yyz18071720400@163.com',
      packages=packages,
      package_dir={'notion2vuepress': 'notion2vuepress'},
      url="https://github.com/YiZhang-You/notion2vuepress.git",

      )