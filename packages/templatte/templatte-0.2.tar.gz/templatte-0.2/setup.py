from setuptools import setup, find_packages

setup(
    name='templatte',
    version='0.2',
    packages=find_packages(),
    url='https://github.com/cinegemadar/templatter',
    license='MIT',
    author='David Balogh',
    author_email='mail@davidbalogh.me',
    description='Easy to use SDK for beautiful PDF reports',
    install_requires=[
       "Jinja2",
       "pandas",
       "pdfkit",
       "openpyxl"
    ],
)
