import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yunpancli",
    entry_points={"console_scripts": ["yunpancli=yunpancli:main"]},
    version="0.0.2",
    author="Tang Yubin",
    author_email="tang-yu-bin@qq.com",
    description="cloud storage CLI (Command Line Interface)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/aierwiki/yunpancli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
