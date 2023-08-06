# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_board']

package_data = \
{'': ['*'], 'pipen_board': ['frontend/build/*', 'frontend/build/assets/*']}

install_requires = \
['pipen-args>=0.9.7,<0.10.0',
 'pipen-log2file>=0.2.1,<0.3.0',
 'psutil>=5.9.5,<6.0.0',
 'quart>=0.18,<0.19',
 'websocket-client>=1.5,<2.0']

entry_points = \
{'pipen': ['board = pipen_board:pipen_board_plugin'],
 'pipen_cli': ['cli-board = pipen_board:PipenCliBoardPlugin']}

setup_kwargs = {
    'name': 'pipen-board',
    'version': '0.1.0',
    'description': 'Visualization configuration and running of pipen pipelines on the web',
    'long_description': "# pipen-board\n\nVisualize configuration and running of [pipen][1] pipelines on the web.\n\n## Installation\n\n```bash\npip install pipen-board\n```\n\n## Usage\n\n```bash\n$ pipen board --help\nUsage: pipen board [options] <pipeline> -- [pipeline options]\n\nVisualize configuration and running of pipen pipelines on the web\n\nRequired Arguments:\n  pipeline              The pipeline and the CLI arguments to run the pipeline. For the\n                        pipeline either `/path/to/pipeline.py:<pipeline>` or\n                        `<module.submodule>:<pipeline>` `<pipeline>` must be an instance of\n                        `Pipen` and running the pipeline should be called under `__name__ ==\n                        '__main__'.\n\nOptions:\n  -h, --help            show help message and exit\n  --port PORT           Port to serve the UI wizard [default: 18521]\n  --name NAME           The name of the pipeline. Default to the pipeline class name. You\n                        can use a different name to associate with a different set of\n                        configurations.\n  --additional FILE     Additional arguments for the pipeline, in YAML, INI, JSON or TOML\n                        format. Can have sections `ADDITIONAL_OPTIONS` and `RUNNING_OPTIONS`\n  --dev                 Run the pipeline in development mode. This will print verbosal\n                        logging information and reload the pipeline if a new instantce\n                        starts when page reloads.\n  --root ROOT           The root directory of the pipeline. [default: .]\n  --loglevel {auto,debug,info,warning,error,critical}\n                        Logging level. If `auto`, set to `debug` if `--dev` is set,\n                        otherwise `info` [default: auto]\n```\n\n[1]: https://github.com/pwwang/pipen\n",
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
