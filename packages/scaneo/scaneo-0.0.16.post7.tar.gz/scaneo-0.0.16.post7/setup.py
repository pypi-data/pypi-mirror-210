# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scaneo', 'scaneo.cli', 'scaneo.routers']

package_data = \
{'': ['*'],
 'scaneo': ['ui/*',
            'ui/_app/*',
            'ui/_app/immutable/chunks/*',
            'ui/_app/immutable/entry/*',
            'ui/_app/immutable/nodes/*',
            'ui/kk/*']}

entry_points = \
{'console_scripts': ['scaneo = scaneo.main:app']}

setup_kwargs = {
    'name': 'scaneo',
    'version': '0.0.16.post7',
    'description': '',
    'long_description': '# scan-new\n\nThis repo contains the code for SCAN\n\n- scaneo: includes the cli, lib and api\n- ui: includes the web ui\n\nThe CLI runs the API, which in turns servers the static files for the UI.\n\nThe library can be installed with \n\n```\npip install scaneo\n```\t\n\n## Instructions\n\n### Developement\n\nRun the api with the cli\n\n```\ncd scaneo\npython main.py\n```\n\nThen, run the ui\n\n```\ncd ui\nyarn dev\n```\n\n### Production\n\nBuild the ui, copy the build inside scaneo and build the python package\n\n```\nmake build v=<version>\nmake publish\n```',
    'author': 'Juan Sensio',
    'author_email': 'it@earthpulse.es',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
