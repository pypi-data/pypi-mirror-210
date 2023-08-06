import pathlib
from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='turandot',
    version='3.1.1',
    description='Turandot Markdown Converter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="GPLv3",
    author='Martin Obrist',
    author_email='dev@obrist.email',
    url='https://turandot.readthedocs.io',
    project_urls={
        'Documentation': 'https://turandot.readthedocs.io',
        'Source Code': 'https://gitlab.com/dinuthehuman/turandot',
        'Issue Tracker': 'https://gitlab.com/dinuthehuman/turandot/-/issues'
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Text Processing :: Markup :: Markdown',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='markdown, citeproc',
    packages=find_packages(where='.', exclude=['tests', 'tasks']),
    python_requires='>=3.10, <4',
    include_package_data=True,
    setup_requires=['wheel'],
    install_requires=[
        "beautifulsoup4",
        "colour",
        "jinja2",
        "lxml",
        "Mako",
        "Markdown",
        "markdown-katex",
        "md_citeproc",
        "Pygments",
        "python-frontmatter",
        "pyyaml",
        "requests",
        "ruamel.yaml",
        "sqlalchemy",
        "urllib3",
        "weasyprint>=53.0",
    ],
    extras_require={
        'tk': [
            "tkhtmlview",
            "bidict"
        ],
        'gtk': [
            "pygobject"
        ],
        'dev': ["gitpython", "mkdocs", "mkdocstrings", "twine", "pytest", "nose", "invoke"],
        'optional': ["gitpython", "qrcode"]
    }
)
