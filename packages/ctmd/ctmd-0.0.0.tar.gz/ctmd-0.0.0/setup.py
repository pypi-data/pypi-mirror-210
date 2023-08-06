import setuptools

with open("README.md", "r", encoding="utf-8", errors="ignore") as f:
    long_description = f.read()
setuptools.setup(
    name='ctmd',
    version='v0.0.0',
    author='Kaguya233qwq',
    author_email='1435608435@qq.com',
    keywords=["ctmd", "传统美德"],
    url='https://github.com/Kaguya233qwq/ctmd',
    description='''ctmd''',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Chinese (Simplified)"
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
    ])
