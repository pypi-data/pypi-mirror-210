from setuptools import setup, find_packages

setup(
    name='yc-stable-diffusion',
    version='0.0.15',
    description='',
    author='soumnshe',
    author_email='soumnshe@gmail.com',
    packages=find_packages(),
    install_requires=[
        'torch',
        'numpy',
        'tqdm',
    ],
)