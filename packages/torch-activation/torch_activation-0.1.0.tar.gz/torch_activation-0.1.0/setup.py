# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_activation']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.0.0']

setup_kwargs = {
    'name': 'torch-activation',
    'version': '0.1.0',
    'description': 'A library of new activation function implement in PyTorch to save time in experiment and have fun',
    'long_description': '# PyTorch Activation Collection\n\nA collection of new, un-implemented activation functions for the PyTorch library. This project is designed for ease of use during experimentation with different activation functions (or simply for fun!). \n\n\n## Installation\n\n```bash\n$ pip install torch-activation\n```\n\n## Usage\n\nTo use the activation functions, simply import from `torch_activation`:\n\n```python\nfrom torch_activation import ShiLU\n\nm = ShiLU(inplace=True)\nx = torch.rand(1, 2, 2, 3)\nm(x)\n```\n\n\n## Available Functions\n\n| Activation Function   | Equation |\n|-----------------------|----------------|\n| ShiLU [[1]](#1)       |                |\n| DELU [[1]](#1)        |                |\n| CReLU [[2]](#2)       |                |\n| GCU [[3]](#3)         |                |\n| CosLU [[1]](#1)       |                |\n| CoLU [[4]](#4)        |                |\n| ReLUN [[1]](#1)       |                |\n| SquaredReLU [[5]](#5) |                |\n| ScaledSoftSign [[1]](#1) |              |\n| ReGLU [[6]](#6)       |                |\n| GeGLU [[6]](#6)       |                |\n| SwiGLU [[6]](#6)      |                |\n| SeGLU                 |                |\n| LinComb [[7]](#7)     |                |\n| NormLinComb [[7]](#7) |                |\n| SinLU                 |                |\n| DReLUs                |                |\n  \n## Future features\n* Activations:\n  * DReLUs\n  * ...\n* Layers:\n  * Depth-wise Convolution\n  * ...\n\n## References\n<a id="1">[1]</a>\nPishchik, E. (2023). Trainable Activations for Image Classification. Preprints.org, 2023010463. DOI: 10.20944/preprints202301.0463.v1.\n\n<a id="2">[2]</a>\nShang, W., Sohn, K., Almeida, D., Lee, H. (2016). Understanding and Improving Convolutional Neural Networks via Concatenated Rectified Linear Units. arXiv:1603.05201v2 (cs).\n\n<a id="3">[3]</a>\nNoel, M. M., Arunkumar, L., Trivedi, A., Dutta, P. (2023). Growing Cosine Unit: A Novel Oscillatory Activation Function That Can Speedup Training and Reduce Parameters in Convolutional Neural Networks. arXiv:2108.12943v3 (cs).\n\n<a id="4">[4]</a>\nVagerwal, A. (2021). Deeper Learning with CoLU Activation. arXiv:2112.12078v1 (cs).\n\n<a id="5">[5]</a>\nSo, D. R., Mańke, W., Liu, H., Dai, Z., Shazeer, N., Le, Q. V. (2022). Primer: Searching for Efficient Transformers for Language Modeling. arXiv:2109.08668v2 (cs)\n\n<a id="6">[6]</a>\nNoam, S. (2020). GLU Variants Improve Transformer. arXiv:2002.05202v1 (cs)\n\n<a id="7">[7]</a>\nPishchik, E. (2023). Trainable Activations for Image Classification. Preprints.org, 2023010463. DOI: 10.20944/preprints202301.0463.v1',
    'author': 'Alan Huynh',
    'author_email': 'hdmquan@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
