from setuptools import setup

setup(
    name='ma_fi',
    version='0.1.1',
    description='Library for accessing financial data of Moroccan stock exchange companies',
    author='Ali Talbi',
    author_email='alitalbi73@gmail.com',
    url='https://github.com/alitalbi/mfinance',
    packages=['ma_fi'],
    install_requires=[
        'pandas',
        'numpy',
        'requests',
        # Add any other dependencies required by your library
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
