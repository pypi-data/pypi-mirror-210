# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tailwind_colors']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tailwind-colors',
    'version': '1.2.1',
    'description': 'Use the default color palette from TailwindCSS (https://tailwindcss.com/docs/customizing-colors) in your python code for plotting, image generation, etc.',
    'long_description': "# Python Tailwind Colors\n\nUse the default color palette from TailwindCSS (https://tailwindcss.com/docs/customizing-colors) in your python code for plotting, image generation, etc..\n\n<br/>\n\n**Installation:**\n\n```bash\npoetry add tailwind_colors\n# or\npip install tailwind_colors\n```\n\n<br/>\n\n**Usage:**\n\n```python\nfrom tailwind_colors import TAILWIND_COLORS_HEX, TAILWIND_COLORS_RGB\n\nprint(TAILWIND_COLORS_HEX.FUCHSIA_600)  # prints '#c026d3'\nprint(TAILWIND_COLORS_RGB.FUCHSIA_600)  # prints (192, 38, 211)\n```\n",
    'author': 'Moritz Makowski',
    'author_email': 'moritz@dostuffthatmatters.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/dostuffthatmatters/python-tailwind-colors',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
