from setuptools import setup, find_packages

setup(
    name='jupyter-converter',
    version='0.0.1',
    description='Jupyter Notebook exam generator written by TeddyNote',
    author='teddylee777',
    author_email='teddylee777@gmail.com',
    url='https://github.com/teddylee777',
    install_requires=['json', 'codecs'],
    packages=find_packages(exclude=[]),
    keywords=['teddynote', 'teddylee777', 'jupyter notebook converter', 'exam generator'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)