# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autocensus']

package_data = \
{'': ['*'], 'autocensus': ['resources/*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'fiona>=1.9.4.post1,<2.0.0',
 'geopandas>=0.13.0,<0.14.0',
 'httpx>=0.24.1,<0.25.0',
 'nest-asyncio>=1.5.6,<2.0.0',
 'pandas>=2.0.1,<3.0.0',
 'shapely>=2.0.1,<3.0.0',
 'socrata-py>=1.1.13,<2.0.0',
 'tenacity>=8.2.2,<9.0.0',
 'typing-extensions>=4.6.2,<5.0.0',
 'us>=2.0.2,<3.0.0',
 'yarl>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'autocensus',
    'version': '2.1.2',
    'description': 'A tool for collecting ACS and geospatial data from the Census API',
    'long_description': '# autocensus\n\nA Python package for collecting American Community Survey (ACS) data and associated geometry from the [Census API] in a [pandas] dataframe.\n\n[Census API]: https://www.census.gov/developers\n[pandas]: https://pandas.pydata.org\n\n## Contents\n\n- [Installation](#installation)\n- [Quickstart](#quickstart)\n- [Geometry](#geometry)\n  - [Points](#points)\n  - [Polygons](#polygons)\n    - [Shapefile resolution](#shapefile-resolution)\n    - [Shapefile caching](#shapefile-caching)\n\n## Installation\n\nautocensus requires Python 3.8 or higher. Install as follows:\n\n```sh\npip install autocensus\n```\n\nTo run autocensus, you must specify a [Census API key] via either the `census_api_key` keyword argument (as shown in the example below) or by setting the environment variable `CENSUS_API_KEY`.\n\n[Census API key]: https://api.census.gov/data/key_signup.html\n\n## Quickstart\n\n```python\nfrom autocensus import Query\n\n# Configure query\nquery = Query(\n    estimate=1,\n    years=[2017, 2018],\n    variables=[\'DP03_0025E\', \'S0103_C01_104E\'],\n    for_geo=\'county:033\',\n    in_geo=[\'state:53\'],\n    # Optional arg to add geometry: \'points\', \'polygons\', or None (default)\n    geometry=\'points\',\n    # Fill in the following with your actual Census API key\n    census_api_key=\'Your Census API key\'\n)\n\n# Run query and collect output in dataframe\ndataframe = query.run()\n```\n\nOutput:\n\n| name                    | geo_id         | geo_type | year | date       | variable_code  | variable_label                                                                             | variable_concept                                  | annotation |  value | geometry  |\n| :---------------------- | :------------- | :------- | ---: | :--------- | :------------- | :----------------------------------------------------------------------------------------- | :------------------------------------------------ | ---------: | -----: | :-------- |\n| King County, Washington | 0500000US53033 | county   | 2017 | 2017-12-31 | DP03_0025E     | Estimate!!COMMUTING TO WORK!!Mean travel time to work (minutes)                            | SELECTED ECONOMIC CHARACTERISTICS                 |            |   30.0 | POINT (…) |\n| King County, Washington | 0500000US53033 | county   | 2018 | 2018-12-31 | DP03_0025E     | Estimate!!COMMUTING TO WORK!!Workers 16 years and over!!Mean travel time to work (minutes) | SELECTED ECONOMIC CHARACTERISTICS                 |            |   30.2 | POINT (…) |\n| King County, Washington | 0500000US53033 | county   | 2017 | 2017-12-31 | S0103_C01_104E | Total!!Estimate!!GROSS RENT!!Median gross rent (dollars)                                   | POPULATION 65 YEARS AND OVER IN THE UNITED STATES |            | 1555.0 | POINT (…) |\n| King County, Washington | 0500000US53033 | county   | 2018 | 2018-12-31 | S0103_C01_104E | Estimate!!Total!!Renter-occupied housing units!!GROSS RENT!!Median gross rent (dollars)    | POPULATION 65 YEARS AND OVER IN THE UNITED STATES |            | 1674.0 | POINT (…) |\n\n## Geometry\n\nautocensus supports point- and polygon-based geometry data for many years and geographies by way of the Census Bureau\'s [Gazetteer Files] and [Cartographic Boundary Files].\n\nHere\'s how to add geometry to your data:\n\n[Gazetteer Files]: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html\n[Cartographic Boundary Files]: https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html\n\n### Points\n\nPoint data from the Census Bureau\'s Gazetteer Files is generally available for years from 2012 on in the following geographies:\n\n- Nation-level\n  - `urban area`\n  - `zip code tabulation area`\n  - `county`\n  - `congressional district`\n  - `metropolitan statistical area/micropolitan statistical area`\n  - `american indian area/alaska native area/hawaiian home land`\n- State-level\n  - `county subdivision`\n  - `tract`\n  - `place`\n  - `state legislative district (upper chamber)`\n  - `state legislative district (lower chamber)`\n\nExample:\n\n```python\nfrom autocensus import Query\n\nquery = Query(\n    estimate=5,\n    years=[2018],\n    variables=[\'DP03_0025E\'],\n    for_geo=[\'county:033\'],\n    in_geo=[\'state:53\'],\n    geometry=\'points\'\n)\ndataframe = query.run()\n```\n\n### Polygons\n\nPolygon data from the Census Bureau\'s Cartographic Boundary Shapefiles is generally available for years from 2013 on in the following geographies:\n\n- Nation-level\n  - `nation`\n  - `region`\n  - `division`\n  - `state`\n  - `urban area`\n  - `zip code tabulation area`\n  - `county`\n  - `congressional district`\n  - `metropolitan statistical area/micropolitan statistical area`\n  - `combined statistical area`\n  - `american indian area/alaska native area/hawaiian home land`\n  - `new england city and town area`\n- State-level\n  - `alaska native regional corporation`\n  - `block group`\n  - `county subdivision`\n  - `tract`\n  - `place`\n  - `public use microdata area`\n  - `state legislative district (upper chamber)`\n  - `state legislative district (lower chamber)`\n\nExample:\n\n```python\nfrom autocensus import Query\n\nquery = Query(\n    estimate=5,\n    years=[2018],\n    variables=[\'DP03_0025E\'],\n    for_geo=[\'county:033\'],\n    in_geo=[\'state:53\'],\n    geometry=\'polygons\'\n)\ndataframe = query.run()\n```\n\n#### Shapefile resolution\n\nBy default, autocensus will attempt to fetch almost all shapefiles at a resolution of 1 : 500,000 (`500k`). Some sources among the Cartographic Boundary Shapefiles are also available at the lower resolutions of 1 : 5,000,000 (`5m`) or 1 : 20,000,000 (`20m`). To attempt to download a shapefile at a specific resolution, pass a value to `Query`\'s optional `resolution` parameter:\n\n```python\nfrom autocensus import Query\n\nquery = Query(\n    estimate=5,\n    years=[2018],\n    variables=[\'DP03_0025E\'],\n    for_geo=[\'county:*\'],\n    in_geo=[\'state:53\'],\n    geometry=\'polygons\',\n    # Optional arg to set a specific resolution: \'500k\', \'5m\', or \'20m\'\n    resolution=\'20m\'\n)\n```\n\nSetting a specific resolution is only supported for polygon-based geometry.\n\n#### Shapefile caching\n\nTo improve performance across queries that include polygon-based geometry data, autocensus will cache Census shapefiles on disk by default. The cache directory location depends on your OS; you can look it up from `autocensus.constants.CACHE_DIRECTORY_PATH` like so:\n\n```shell\npython -c "import autocensus; print(autocensus.constants.CACHE_DIRECTORY_PATH)"\n```\n\nSometimes it is useful to clear this cache directory, especially if you\'re running into persistent shapefile-related problems. You can clear the cache by manually deleting the cache directory or by executing the `autocensus.clear_cache` function:\n\n```shell\npython -c "import autocensus; autocensus.clear_cache()"\n```\n',
    'author': 'Christopher Setzer',
    'author_email': 'cmsetzer.github@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/socrata/autocensus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
