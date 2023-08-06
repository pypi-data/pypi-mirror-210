# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biaslyze', 'biaslyze.bias_detectors', 'biaslyze.results']

package_data = \
{'': ['*']}

install_requires = \
['bertopic==0.13.0',
 'bokeh>=3.1.0,<4.0.0',
 'eli5>=0.13.0,<0.14.0',
 'jupyterlab>=3.5.2,<4.0.0',
 'loguru>=0.6.0,<0.7.0',
 'matplotlib>=3.7.1,<4.0.0',
 'numpy==1.23.2',
 'pandas>=1.5.3,<2.0.0',
 'scikit-learn>=1.2.0,<2.0.0',
 'scipy==1.8.0',
 'spacy>=3.5.0,<4.0.0',
 'transformers>=4.26.1,<5.0.0',
 'umap-learn>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'biaslyze',
    'version': '0.0.4a0',
    'description': 'The NLP Bias Identification Toolkit',
    'long_description': '# biaslyze\nThe NLP Bias Identification Toolkit\n\n\n## Usage example\n\n```python\nfrom biaslyze.bias_detectors import CounterfactualBiasDetector\n\nbias_detector = CounterfactualBiasDetector()\n\n# detect bias in the model based on the given texts\n# here, clf is a scikit-learn text classification pipeline trained for a binary classification task\ndetection_res = bias_detector.process(\n    texts=texts,\n    predict_func=clf.predict_proba\n)\n\n# see a summary of the detection\ndetection_res.report()\n\n# visualize the counterfactual scores\ndetection_res.visualize_counterfactual_scores(concept="religion", top_n=10)\n```\n\nExample output:\n![](resources/hatespeech_dl_scores_religion.png)\n\n\n## Development setup\n\n- First you need to install poetry to manage your python environment: https://python-poetry.org/docs/#installation\n- Run `make install` to install the dependencies and get the spacy basemodels.\n- Now you can use `biaslyze` in your jupyter notebooks.\n\n\n### Adding concepts and keywords\n\nYou can add concepts and new keywords for existing concepts by editing [concepts.py](https://github.com/biaslyze-dev/biaslyze/blob/keyword-based-targeted-lime/biaslyze/concepts.py).\n\n## Preview/build the documentation with mkdocs\n\nTo preview the documentation run `make doc-preview`. This will launch a preview of the documentation on `http://127.0.0.1:8000/`.\nTo build the documentation html run `make doc`.\n\n\n## Run the automated tests\n\n`make test`\n\n\n## Style guide\n\nWe are using isort and black: `make style`\nFor linting we are running ruff: `make lint`\n\n## Contributing\n\nFollow the google style guide for python: https://google.github.io/styleguide/pyguide.html\n\nThis project uses black, isort and ruff to enforce style. Apply it by running `make style` and `make lint`.\n\n',
    'author': 'Tobias Sterbak & Stina Lohmüller',
    'author_email': 'hello@biaslyze.org',
    'maintainer': 'Tobias Sterbak',
    'maintainer_email': 'hello@tobiassterbak.com',
    'url': 'https://biaslyze.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
