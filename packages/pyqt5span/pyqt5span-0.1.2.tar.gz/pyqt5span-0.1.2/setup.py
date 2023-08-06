from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='pyqt5span',
    version='0.1.2',
    description='Span header for PyQt5',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Edwin Yllanes, Giovanni Lourenço',
    author_email='gvnl.developer@outlook.com',
    url='https://github.com/glourencoffee/pyqt5span',
    license='MIT',
    packages=['pyqt5span'],
    keywords=['pyqt5', 'spanning'],

    install_requires=['PyQt5'],

    python_requires='>=3.7'
)