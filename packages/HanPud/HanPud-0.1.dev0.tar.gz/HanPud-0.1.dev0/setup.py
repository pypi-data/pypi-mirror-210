# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.md","r",encoding="utf-8-sig") as f:
    readme = f.read()

requirements = [
    "pythainlp>=4.0.0",
    "transformers",
    "sentencepiece"
]

setup(
    name="HanPud",
    version="0.1dev0",
    description="Han Pud (ห่าน พูด): Thai super large generative model",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Wannaphong",
    author_email="wannaphong@yahoo.com",
    url="https://github.com/wannaphong/HanPud",
    packages=find_packages(),
    # test_suite="tests",
    python_requires=">=3.8",
    package_data={},
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords=[
        "Thai",
        "NLP",
        "natural language processing",
        "text analytics",
        "text processing",
        "localization",
        "computational linguistics",
        "Thai language",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: General",
        "Topic :: Text Processing :: Linguistic",
    ],
    project_urls={
        # "Documentation": "https://github.com/wannaphong/HanPud/wiki",
        "Source": "https://github.com/wannaphong/HanPud",
        "Bug Reports": "https://github.com/wannaphong/HanPud/issues",
    },
)
