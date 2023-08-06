import re 
import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()
    
with open('pyrosexmod/__init__.py') as fp:
    version = re.search('__version__ = "(.+?)"', fp.read())[1]


setuptools.setup(
    name="pyrosexmod",
    version=version,
    author="OTH",
    author_email="oth@pyrosex.org",
    license="LGPLv3+",
    description="A monkeypatcher add-on for Pyrosex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OTHFamily/pyrosexmod",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["pyrosex>=0.0.3", "yt-dlp"],
)
