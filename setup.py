from distutils.core import setup

setup(
    name='industrialucn',
    packages=['industrialucn'],
    version='0.1.3',
    license='MIT',
    description='Industrial UCN',
    author='Hernan Caceres',
    author_email='industrial@ucn.cl',
    url='https://industrial.ucn.cl',
    download_url='https://github.com/hernan-caceres/orlab-code/archive/0.1.3.tar.gz',
    keywords=['industrial', 'ucn', 'optimization', 'orlab', 'statistics'],
    install_requires=[
        'docplex',
        'numpy',
        'pandas',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7'
    ],
)
