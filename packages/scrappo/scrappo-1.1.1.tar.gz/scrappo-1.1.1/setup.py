from setuptools import setup
import pathlib

from scrappo.version.progsettings import get_version

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

version = get_version()

setup(
    name="scrappo",
    version=version,
    description="Download any video from a specific URL.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zaytiri/scrappo",
    project_urls={
        'GitHub': 'https://github.com/zaytiri/scrappo',
        'Changelog': 'https://github.com/zaytiri/scrappo/blob/main/CHANGELOG.md',
    },
    author="zaytiri",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    keywords="video, download, tool, scrapping, scrap, cli, url python",
    package_data={'scrappo': ['version/progsettings.yaml']},
    packages=["scrappo", "scrappo.utils", "scrappo.version", "scrappo.settings"],
    python_requires=">=3.10.6",
    install_requires=[
        "PyYAML~=6.0",
        "margument>=1.1.1",
        "requests>=2.31.0",
        "progress~=1.6",
    ],
    entry_points={
        "console_scripts": [
            "scrappo=scrappo:app.main",
        ],
    }
)
