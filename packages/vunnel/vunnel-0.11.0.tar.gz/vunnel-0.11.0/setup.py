# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['vunnel',
 'vunnel.cli',
 'vunnel.providers',
 'vunnel.providers.alpine',
 'vunnel.providers.amazon',
 'vunnel.providers.chainguard',
 'vunnel.providers.debian',
 'vunnel.providers.github',
 'vunnel.providers.nvd',
 'vunnel.providers.oracle',
 'vunnel.providers.rhel',
 'vunnel.providers.sles',
 'vunnel.providers.ubuntu',
 'vunnel.providers.wolfi',
 'vunnel.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0',
 'SQLAlchemy>=1.4.46,<3.0',
 'click>=8.1.3,<9.0.0',
 'colorlog>=6.7.0,<7.0.0',
 'cvss>=2.6,<3.0',
 'dataclass-wizard>=0.22.2,<0.23.0',
 'defusedxml>=0.7.1,<0.8.0',
 'future>=0.18.3,<0.19.0',
 'ijson>=2.5.1,<3.0',
 'importlib-metadata>=6.1.0,<7.0.0',
 'mergedeep>=1.3.4,<2.0.0',
 'orjson>=3.8.6,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'rfc3339>=6.2,<7.0',
 'xxhash>=3.1.0,<4.0.0']

entry_points = \
{'console_scripts': ['vunnel = vunnel.cli:run']}

setup_kwargs = {
    'name': 'vunnel',
    'version': '0.11.0',
    'description': "vunnel ~= 'vulnerability data funnel'",
    'long_description': '# vunnel\n\nA tool for fetching, transforming, and storing vulnerability data from a variety of sources.\n\n![vunnel-demo](https://user-images.githubusercontent.com/590471/226942827-e19742ef-e66e-4e11-8f9b-fb74c40f1dee.gif)\n\nSupported data sources:\n- Alpine (https://secdb.alpinelinux.org)\n- Amazon (https://alas.aws.amazon.com/AL2/alas.rss & https://alas.aws.amazon.com/AL2022/alas.rss)\n- Debian (https://security-tracker.debian.org/tracker/data/json & https://salsa.debian.org/security-tracker-team/security-tracker/raw/master/data/DSA/list)\n- GitHub Security Advisories (https://api.github.com/graphql)\n- NVD (https://services.nvd.nist.gov/rest/json/cves/2.0)\n- Oracle (https://linux.oracle.com/security/oval)\n- RedHat (https://www.redhat.com/security/data/oval)\n- SLES (https://ftp.suse.com/pub/projects/security/oval)\n- Ubuntu (https://launchpad.net/ubuntu-cve-tracker)\n- Wolfi (https://packages.wolfi.dev)\n\n\n## Installation\n\nWith pip:\n\n```bash\npip install vunnel\n```\n\nWith docker:\n\n```bash\ndocker run \\\n  --rm -it \\\n  -v $(pwd)/data:/data \\\n  -v $(pwd)/.vunnel.yaml:/.vunnel.yaml \\\n    ghcr.io/anchore/vunnel:latest  \\\n      run nvd\n```\nWhere:\n  - the `data` volume keeps the processed data on the host\n  - the `.vunnel.yaml` uses the host application config (if present)\n  - you can swap `latest` for a specific version (same as the git tags)\n\nSee [the vunnel package](https://github.com/anchore/vunnel/pkgs/container/vunnel) for a full listing of available tags.\n\n\n## Getting Started\n\nList the available vulnerability data providers:\n\n```\n$ vunnel list\n\nalpine\namazon\ncentos\ndebian\ngithub\nnvd\noracle\nrhel\nsles\nubuntu\nwolfi\n```\n\nDownload and process a provider:\n\n```\n$ vunnel run wolfi\n\n2023-01-04 13:42:58 root [INFO] running wolfi provider\n2023-01-04 13:42:58 wolfi [INFO] downloading Wolfi secdb https://packages.wolfi.dev/os/security.json\n2023-01-04 13:42:59 wolfi [INFO] wrote 56 entries\n2023-01-04 13:42:59 wolfi [INFO] recording workspace state\n```\n\nYou will see the processed vulnerability data in the local `./data` directory\n\n```\n$ tree data\n\ndata\n└── wolfi\n    ├── checksums\n    ├── metadata.json\n    ├── input\n    │   └── secdb\n    │       └── os\n    │           └── security.json\n    └── results\n        └── wolfi:rolling\n            ├── CVE-2016-2781.json\n            ├── CVE-2017-8806.json\n            ├── CVE-2018-1000156.json\n            └── ...\n```\n\n*Note: to get more verbose output, use `-v`, `-vv`, or `-vvv` (e.g. `vunnel -vv run wolfi`)*\n\nDelete existing input and result data for one or more providers:\n\n```\n$ vunnel clear wolfi\n\n2023-01-04 13:48:31 root [INFO] clearing wolfi provider state\n```\n\nExample config file for changing application behavior:\n\n```yaml\n# .vunnel.yaml\nroot: ./processed-data\n\nlog:\n  level: trace\n\nproviders:\n  wolfi:\n    request_timeout: 125\n    runtime:\n      existing_input: keep\n      existing_results: delete-before-write\n      on_error:\n        action: fail\n        input: keep\n        results: keep\n        retry_count: 3\n        retry_delay: 10\n\n```\n\nUse `vunnel config` to get a better idea of all of the possible configuration options.\n\n\n## FAQ\n\n\n### Can I implement a new provider?\n\nYes you can! See [the provider docs](https://github.com/anchore/vunnel/blob/main/DEVELOPING.md#adding-a-new-provider) for more information.\n\n\n### Why is it called "vunnel"?\n\nThis tool "funnels" vulnerability data into a single spot for easy processing... say "vulnerability data funnel" 100x fast enough and eventually it\'ll slur to "vunnel" :).\n',
    'author': 'Alex Goodman',
    'author_email': 'alex.goodman@anchore.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/anchore/vunnel',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
