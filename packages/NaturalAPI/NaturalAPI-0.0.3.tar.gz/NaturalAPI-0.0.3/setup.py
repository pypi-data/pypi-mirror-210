import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
  name="NaturalAPI",
  version="0.0.3",
  author="yydshmcl@outlook.com",
  author_email="yydshmcl@outlook.com",
  description="API for a small studio",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/Buelie/Natural",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)