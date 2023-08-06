from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='dd8',
      version='0.0.12',
      description='Package for Application of Data Science in Finance',
      long_description=long_description,
      url='https://github.com/AiRiFiEd/dd8',
      author='yqlim',
      author_email='yuanqing87@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)