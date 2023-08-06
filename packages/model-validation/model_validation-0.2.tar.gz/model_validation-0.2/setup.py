from setuptools import setup, find_packages

setup(
    name="model_validation",
    version="0.2",
    description="Model validation tools",
    url="http://github.com/Alexandre-Papandrea/model_validation",
    author="Alexandre Papandrea",
    author_email="alexandre@dadosinteligentes.com",
    packages=find_packages(),
    install_requires=[
        "ipywidgets",
        "pandas",
        "numpy",
        "plotly",
        "scikit-learn",
        "scipy",
        "statsmodels",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)