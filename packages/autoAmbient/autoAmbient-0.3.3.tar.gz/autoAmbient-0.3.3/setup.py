from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="autoAmbient",
    version="0.3.3",
    author="Luis Arthur Rodrigues da Silva",
    author_email="luisarthurlards03@gmail.com",
    packages=["ambient", "ambient.tolls", "ambient.models"],

    url="https://github.com/luisArthurRodriguesDaSilva/automations-enviroment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    entry_points={
        "console_scripts": [
            "getFile=ambient.getFile:main",
            "createTagsFile=ambient.createTagsFile:main",
            "createAmbient=ambient.createAutoAmbient:main",
        ],
    },
    install_requires=[
        "PySimpleGUI==4.20.0",
        "botcity==1.8.1",
        "requests>=2.25.1"
    ],
    license='MIT',
)
