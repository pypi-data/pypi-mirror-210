import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="allbaro-chunilpathfinder",
    version="0.0.1",
    author="cuhong",
    author_email="hongcoilhouse@gmail.com",
    description="한국환경공단 올바로 시스템 스크래핑을 위한 파이썬 라이브러리",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chunil-energy/allbaro",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)