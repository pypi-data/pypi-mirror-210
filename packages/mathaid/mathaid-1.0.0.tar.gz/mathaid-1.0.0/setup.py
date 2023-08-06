from setuptools import setup, find_packages

setup(
    name='mathaid',
    version='1.0.0',
    author='SpikyShade',
    author_email='codeswithdevesh@gmail.com',
    description='A package for mathematical utility functions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/spikyshade/mathaid',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
    install_requires=[
        # Add any dependencies required by your package
    ],
)
