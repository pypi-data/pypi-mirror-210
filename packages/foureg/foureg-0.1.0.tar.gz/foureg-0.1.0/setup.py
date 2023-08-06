# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foureg']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21,<2.0', 'scipy>=1.7,<2.0']

setup_kwargs = {
    'name': 'foureg',
    'version': '0.1.0',
    'description': 'Fourier transform based image registration',
    'long_description': 'Foureg\n======\nImage registration using discrete Fourier transform.\n\n\nGiven two images, `foureg` calculates a similarity transformation that\ntransforms one image into the other.\n\nNOTE\n----\nTHIS IS STILL WIP AND INTERFACES MAY CHANGE WITHOU NOTICE\n\nExample\n-------\nThe example transforms an image with a user defined transformation and then rediscovers\nit using `foureg`.\n```python\nimport matplotlib.pyplot as plt\nimport numpy as np\nfrom PIL import Image  # Not a dependency from this pa\n\nfrom foureg import similarity, similarity_matrix, transform_img\n\n# 1) Make up some transformation\ntransformation = similarity_matrix(1.2, 15, (40, 60))\n\n# 2) Open the master image and transform it to generate the slave image\nmaster = np.asarray(Image.open("./resources/examples/sample1.png"))\nslave = transform_img(master, transformation)\n\n\n# 3) Use foureg to recover the transformation\nimreg_result = similarity(master, slave)\nslave_transformed = transform_img(slave, imreg_result["transformation"])\n\n4) Some plotting to verify everything is working\n_, axs = plt.subplots(1, 5, figsize=(13, 8))\nim_0 = axs[0].imshow(master)\nplt.colorbar(im_0, ax=axs[0])\nim_1 = axs[1].imshow(slave)\nplt.colorbar(im_1, ax=axs[1])\nim_2 = axs[2].imshow(slave_transformed)\nplt.colorbar(im_2, ax=axs[2])\nim_3 = axs[3].imshow(imreg_result["timg"])\nplt.colorbar(im_3, ax=axs[3])\nim_4 = axs[4].imshow(np.abs(imreg_result["timg"] - master))\nplt.colorbar(im_4, ax=axs[4])\n\nplt.show()\n```\n\nFeatures\n--------\n* Image pre-processing options (frequency filtration, image extension).\n* Under-the-hood options exposed (iterations, phase correlation filtration).\n* Permissive open-source license (3-clause BSD).\n\nOrigin story\n------------\nThis is a fork of the [imreg_dft](https://github.com/matejak/imreg_dft) borned of the\ndesire to achieve the following goals:\n- Ability to return the final transformation in matrix form as opposed to the angle,\ntranslation and scaling factor separately. The original code makes obtaining that\nmatrix really hard because it does some unorthodox resizings when performing the\nimage transformations.\n- Better performance and ultimately a Pytorch powered GPU implementation\n- A more focused codebase. The only goal here is to estimate similarity transformations\nbetween pairs of images.\n\n\nAcknowledgements\n----------------\nThe code was originally developed by Christoph Gohlke (University of California, Irvine, USA)\nand later on developed further by Matěj Týč (Brno University of Technology, CZ). This\nrepo wouldn\'t exist without them.\n',
    'author': 'Guillem Ballesteros',
    'author_email': 'guillem@maxwellrules.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/GCBallesteros/foureg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
