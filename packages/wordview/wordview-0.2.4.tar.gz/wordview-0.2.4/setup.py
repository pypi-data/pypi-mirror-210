# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wordview',
 'wordview.anomaly',
 'wordview.clustering',
 'wordview.mwes',
 'wordview.preprocessing',
 'wordview.text_analysis']

package_data = \
{'': ['*']}

install_requires = \
['langdetect>=1.0.9',
 'nltk==3.6.6',
 'pandas==2.0.1',
 'plotly==5.5.0',
 'scikit-learn==1.2.2',
 'scipy==1.10.0',
 'sentence-transformers==2.2.2',
 'tabulate==0.9.0',
 'tqdm==4.62.3',
 'wordcloud==1.9.1.1']

entry_points = \
{'console_scripts': ['script_download = '
                     'wordview.bin.downloads:download_nltk_req']}

setup_kwargs = {
    'name': 'wordview',
    'version': '0.2.4',
    'description': 'Wordview is a Python package for text analysis.',
    'long_description': "Wordview (Work In Progress)\n###########################\n\n|PyPI version|\n\n|Python 3.9|\n\nWordview is a Python package for Exploratory Data Analysis (EDA) and Feature Extraction for text.\nWordview's Python API is open-source and available under the `MIT\nlicense <https://en.wikipedia.org/wiki/MIT_License>`__. We, however,\noffer a framework on top of Wordview for enterprise use under a commercial license. See this page for\nmore information about this framework.\n\n|text_analysis_cover|\n\n\nUsage\n######\n\nInstall the package via ``pip``:\n\n``pip install wordview``\n\nTo explore various features and functionalities, consult the documentation pages. The following sections\npresent a high-level description of Wordview's features and functionalities. For details, tutorials and worked examples, corresponding \ndocumentation pages are linked in each section.\n\n\nExploratory Data Analysis (EDA)\n###############################\n\nWordview presents many statistics about your data in form of plots and tables allowing you to \nhave both a high-level and detailed overview of your data. For instance, which languages\nare present in your dataset, how many unique words and unique words are there in your dataset, what percentage \nof them are Adjectives, Nouns or Verbs, what are the most common POS tags, etc. Wordview also provides several statistics for labels in labeled datasets.\n\n\nText Analysis\n*************\nUsing this feature, you can have an overview of your text data in terms of various statistics, plots and distribution.\nSee `text analysis documentation pages <./docs/source/textstats.rst>`__  for usage and examples.\n\n\nLabel Analysis\n**************\nWordview calculates several statistics for labels in labeled datasets whether they are at document or sequence level.\nSee `label analysis documentation pages <./docs/source/labels.rst>`__ for usage and examples.\n\n\nFeature Extraction\n###################\n\nWordview has various functionalities for feature extraction from text, including Multiword Expressions (MWEs), clusters, anomalies and \noutliers, and more. See the following sections as well as the linked documentation page in each section for details.\n\nMultiword Expressions\n*********************\n\nMultiword Expressions (MWEs) are phrases that can be treated as a single\nsemantic unit. E.g. *swimming pool* and *climate change*. MWEs have\napplication in different areas including: parsing, language models,\nlanguage generation, terminology extraction, and topic models. Wordview can extract different types of MWEs from text.\nSee `MWEs documentation page <./docs/source/mwes.rst>`__ for usage and examples.\n\nAnomalies and Outliers\n**********************\n\nAnomalies and outliers have wide applications in Machine Learning. While in\nsome cases, you can capture them and remove them from the data to improve the\nperformance of a downstream ML model, in other cases, they become the data points\nof interest where we endeavor to find them in order to shed light into our data.\n\nWordview offers several anomaly and outlier detection functions.\nSee `anomalies documentation page <./docs/source/anomalies.rst>`__ for usage and examples.\n\n\nClusters\n*********\nClustering can be used to identify different groups of documents with similar information, in an unsupervised fashion.\nDespite it's ability to provide valuable insights into your data, you do not need labeled data for clustering. See\n`wordview`'s `clustering documentation page <./docs/source/clustering.rst>`__ for usage and examples.\n\n\nUtilities\n#########\n\nWordview offers a number of utility functions that you can use for common pre and post processing tasks in NLP. \nSee `utilities documentation page <./docs/source/utilities.rst>`__ for usage and examples.\n\nContributing\n############\n\nThank you for contributing to wordview! We and the users of this repo\nappreciate your efforts! You can visit the `contributing page <CONTRIBUTING.rst>`__ for detailed instructions about how you can contribute to Wordview.\n\n\n.. |PyPI version| image:: https://badge.fury.io/py/wordview.svg\n    :target: https://badge.fury.io/py/wordview\n\n.. |Python 3.9| image:: https://img.shields.io/badge/python-3.9-blue.svg\n   :target: https://www.python.org/downloads/release/python-390/\n.. |verbs| image:: docs/figs/verbs.png\n.. |nouns| image:: docs/figs/nouns.png\n.. |adjs| image:: docs/figs/adjectives.png\n.. |doclen| image:: docs/figs/doclen.png\n.. |wordszipf| image:: docs/figs/wordszipf.png\n.. |labels| image:: docs/figs/labels.png\n.. |cover| image:: docs/figs/abstract_cover_2.png\n.. |clustering_cover| image:: docs/figs/clustering_cover.png\n.. |text_analysis_cover| image:: docs/figs/text_analysis.png\n\n\n",
    'author': 'meghdadFar',
    'author_email': 'meghdad.farahmand@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
