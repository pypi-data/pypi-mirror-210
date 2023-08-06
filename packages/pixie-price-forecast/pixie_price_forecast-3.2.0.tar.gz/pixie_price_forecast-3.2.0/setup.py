import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pixie_price_forecast",
    version="3.2.0",
    author="Pixie Pixel",
    author_email="joseangel.mielgo@adevinta.com",
    description="Price forecast tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.mpi-internal.com/joseangel-mielgo/pixie-price-forecast",
    project_urls={
        "Bug Tracker": "https://github.mpi-internal.com/joseangel-mielgo/pixie-price-forecast",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["pandas",
                      "numpy",
                      "sqlalchemy",
                      "sshtunnel",
                      "matplotlib",
                      "statsmodels",
                      "scikit-learn",
                      "tensorflow",
                      "requests",
                      "beautifulsoup4",
                      "python-dateutil"
                      ]
)
