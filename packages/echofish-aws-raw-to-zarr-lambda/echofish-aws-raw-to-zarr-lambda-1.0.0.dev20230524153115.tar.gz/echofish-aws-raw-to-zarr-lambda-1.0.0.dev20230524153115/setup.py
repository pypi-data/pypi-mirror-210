import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setuptools.setup(
  name="echofish-aws-raw-to-zarr-lambda",
  version="1.0.0.dev20230524153115",
  description="",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ci-cmg/echofish-aws-raw-to-zarr-lambda",
  package_dir={'': 'src'},
  packages=setuptools.find_packages('src'),
  classifiers=[
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
  ],
  python_requires='>=3.9',
  install_requires=[req for req in requirements if req[:2] != "# "]
)