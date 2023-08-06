import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='sababa',
    author='sababa',
    author_email='python@sababa.cloud',
    description='Sababa PyPI Package',
    keywords='sababa, pypi, package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sababacloud/sababa-python',
    project_urls={
        'Documentation': 'https://github.com/sababacloud/sababa-python',
        'Bug Reports':
        'https://github.com/sababacloud/sababa-python/issues',
        'Source Code': 'https://github.com/sababacloud/sababa-python',
        # 'Funding': '',
        # 'Say Thanks!': '',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        # 'Development Status :: 5 - Production/Stable',
        'Development Status :: 1 - Planning',

        'Intended Audience :: Developers',
        'Topic :: Software Development',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        # 'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # install_requires=['Pillow'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=sababa:main',
    # You can execute `run` in bash to run `main()` in src/sababa/__init__.py
    #     ],
    # },
)
