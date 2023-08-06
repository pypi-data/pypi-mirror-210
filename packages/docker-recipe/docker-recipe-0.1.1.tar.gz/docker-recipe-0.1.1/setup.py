from setuptools import setup, find_packages

setup(
    name="docker-recipe",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'pydantic~=1.10.8',
        'PyYaml~=6.0',
        'Jinja2~=3.1.2',
    ],
    author="Stephan Meijer",
    author_email="me@stephanmeijer.com",
    description="A way to cook multiple Dockerfiles",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/stephanmeijer/docker-recipe",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points={
        'console_scripts': [
            'docker-recipe=docker_recipe:main',  # map the docker-recipe command to a function
        ],
    },
)
