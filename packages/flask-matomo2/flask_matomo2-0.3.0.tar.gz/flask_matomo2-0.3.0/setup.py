# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_matomo2']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2,<3', 'httpx>=0.24.0,<0.25.0']

setup_kwargs = {
    'name': 'flask-matomo2',
    'version': '0.3.0',
    'description': 'Track requests to your Flask server with Matomo',
    'long_description': '# Flask-Matomo\n\n![](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)\n[![PyPI](https://img.shields.io/pypi/v/flask-matomo2.svg?style=flat-square&colorB=dfb317)](https://pypi.org/project/flask-matomo2/)\n<!-- [![Docs](https://img.shields.io/badge/docs-readthedocs-red.svg?style=flat-square)](https://flask-matomo.readthedocs.io) -->\n\nFlask-Matomo is a library which lets you track the requests of your Flask website using Matomo (Piwik).\n\nForked from [LucasHild/flask-matomo](https://github.com/LucasHild/flask-matomo).\n## Installation\n\n```\npip install flask-matomo2\n```\n\n## Using flask-matomo2 in your project\n\nSimply add `flask-matomo2` to your dependencies:\n\n```toml\n# pyproject.toml\ndependencies = [\n  "flask-matomo2",\n]\n\n```\n### Using Poetry\n\n```bash\npoetry add flask-matomo2\n```\n\n### Using PDM\n\n```bash\npdm add flask-matomo2\n```\n\n## Usage\n\n```python\nfrom flask import Flask, jsonify\nfrom flask_matomo2 import Matomo\n\napp = Flask(__name__)\nmatomo = Matomo(app, matomo_url="https://matomo.mydomain.com",\n                id_site=5, token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")\n\n@app.route("/")\ndef index():\n  return jsonify({"page": "index"})\n\nif __name__ == "__main__":\n  app.run()\n```\n\nIn the code above:\n\n1. The *Matomo* object is created by passing in the Flask application and arguments to configure Matomo.\n2. The *matomo_url* parameter is the url to your Matomo installation.\n3. The *id_site* parameter is the id of your site. This is used if you track several websites with one Matomo installation. It can be found if you open your Matomo dashboard, change to site you want to track and look for &idSite= in the url.\n4. The *token_auth* parameter can be found in the area API in the settings of Matomo. It is required for tracking the ip address.\n\n\n### Adding details to route\n\nYou can provide details to a route in 2 ways, first by using the `matomo.details` decorator:\n\n```python\nfrom flask import Flask, jsonify\nfrom flask_matomo2 import Matomo\n\napp = Flask(__name__)\nmatomo = Matomo(app, matomo_url="https://matomo.mydomain.com",\n                id_site=5, token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")\n\n@app.route("/foo")\n@matomo.details(action_name="Foo")\ndef foo():\n  return jsonify({"page": "foo"})\n\nif __name__ == "__main__":\n  app.run()\n```\n\nor by giving details to the Matomo constructor:\n```python\nfrom flask import Flask, jsonify\nfrom flask_matomo2 import Matomo\n\napp = Flask(__name__)\nmatomo = Matomo(\n  app,\n  matomo_url="https://matomo.mydomain.com",\n  id_site=5,\n  token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",\n  routes_details={\n    "/foo": {\n      "action_name": "Foo"\n    }\n  }\n)\n\n@app.route("/foo")\ndef foo():\n  return jsonify({"page": "foo"})\n\nif __name__ == "__main__":\n  app.run()\n```\n\n## Meta\n\nLucas Hild - [https://lucas-hild.de](https://lucas.hild.de)\nThis project is licensed under the MIT License - see the LICENSE file for details\n\n# Release Notes\n\n## Latest Changes\n\n## 0.3.0 - 2023-05-25\n\n### Added\n\n- Add PerfMsTracker. PR [#33](https://github.com/spraakbanken/flask-matomo2/pull/33) by [@kod-kristoff](https://github.com/kod-kristoff).\n\n## 0.2.0 - 2023-05-22\n### Changed\n\n- Track original IP address if request was forwarded by proxy. [Tanikai/flask-matomo](https://github.com/Tanikai/flask-matomo) by [@Tanakai](https://github.com/Tanakai).\n- Change ignored routes to compare against rules instead of endpoint. [MSU-Libraries/flask-matomo](https://github.com/MSU-Libraries/flask-matomo) by [@meganschanz](https://github.com/meganschanz).\n- Add ignored UserAgent prefix; set action to be url_rule. [MSU-Libraries/flask-matomo](https://github.com/MSU-Libraries/flask-matomo) by [@natecollins](https://github.com/natecollins).\n- Fix matomo.ignore decorator.\n- Handle request even if tracking fails. PR [#30](https://github.com/spraakbanken/flask-matomo2/pull/30) by [@kod-kristoff](https://github.com/kod-kristoff).\n- Ignore routes by regex. PR [#29](https://github.com/spraakbanken/flask-matomo2/pull/29) by [@kod-kristoff](https://github.com/kod-kristoff).\n- Make token_auth optional. PR [#28](https://github.com/spraakbanken/flask-matomo2/pull/28) by [@kod-kristoff](https://github.com/kod-kristoff).\n- Track dynamic request data. PR [#27](https://github.com/spraakbanken/flask-matomo2/pull/27) by [@kod-kristoff](https://github.com/kod-kristoff).\n- Also track request time. PR [#26](https://github.com/spraakbanken/flask-matomo2/pull/26) by [@kod-kristoff](https://github.com/kod-kristoff).\n- Extend tracked variables. PR [#25](https://github.com/spraakbanken/flask-matomo2/pull/25) by [@kod-kristoff](https://github.com/kod-kristoff).\n- fix matomo.details decorator. PR [#19](https://github.com/spraakbanken/flask-matomo2/pull/19) by [@kod-kristoff](https://github.com/kod-kristoff).\n\n\n## 0.1.0\n\n- Forked from [LucasHild/flask-matomo](https://github.com/LucasHild/flask-matomo).\n- Renamed to `flask-matomo2`.\n- Add test suite.\n- Setup CI with Github Actions.\n',
    'author': 'Kristoffer Andersson',
    'author_email': 'kristoffer.andersson@gu.se',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://spraakbanken.gu.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
