import setuptools

with open("r.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apkupload",
    version="0.0.14",
    author="malinkang",
    author_email="linkang.ma@gmail.com",
    description="apk 上传",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://malinkang.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ["apkupload = apkupload.upload:main"],
    },
)
