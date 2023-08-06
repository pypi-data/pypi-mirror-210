from setuptools import setup, find_packages

setup(
    name='ths-quant',
    version='0.1.0',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Quant tool',
    long_description=open('README.md').read(),
    setup_requires=[
        'safetensors==0.3.0',
        'datasets==2.10.1',
        'sentencepiece',
        'accelerate==0.17.1',
        'triton==2.0.0',
        'texttable',
        'toml',
        'numpy',
        'protobuf==3.20.2',
    ],
    dependency_links=[
        'https://github.com/huggingface/transformers',
    ],
    entry_points={
        'console_scripts': [
            'ths-quant = llama:main'
        ]
    },
    author='ths-nmt&llm',
    author_email='qinbo@myhexin.com'
)
