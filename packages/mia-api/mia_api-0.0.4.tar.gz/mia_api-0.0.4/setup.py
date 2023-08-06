import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name='mia_api',
  version='0.0.4',
  author='MeteoIA',
  author_email='meteoia.consult@meteoia.com',
  description='A package to communicate with MIA API',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/meteoia-team/mia_api',
  project_urls = {
    "Bug Tracker": "https://github.com/meteoia-team/mia_api/issues"
  },
  install_requires=[
    'fastapi',
    'xarray',
    'netCDF4',
    'pandas',
    'tqdm',
    'tabulate',
    'requests',
  ],
  package_dir={"": "src"},
  packages=setuptools.find_packages(where="src"),
  python_requires=">=3.6",
)
