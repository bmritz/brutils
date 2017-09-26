from setuptools import setup


setup(name="brutils", 
        version="0.1",
        description="Common utilities for data science",
        url="https://github.com/bmritz/brutils",
        author="Brian Ritz",
        author_email="bmritz@indiana.edu",
        license="",
        packages=["brutils"],
        install_requires = [
        'gitpython',
        'pandas',
        'numpy',
        'sklearn',
        'imblearn',
        'matplotlib',
        'seaborn',
        'ipywidgets',
        'Ipython',
        'traitlets'
        ],
        zip_safe=False
)