from setuptools import setup

setup(
    name="custom-py-docx",
    version="1.0.3",
    description="My package for creating Word documents with images and plots.",
    packages=["custom-py-docx"],
    install_requires=[
        "python-docx",
        "docxcompose",
        "plotly",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "custom-py-docx=custom-py-docx.__main__:main",
        ],
    },
)