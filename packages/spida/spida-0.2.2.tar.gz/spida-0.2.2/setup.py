from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="spida",
    version="0.2.2",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A Stable Diffusion API Wrapper for AUTOMATIC1111/stable-diffusion-webui",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="h2see",
    url="https://github.com/h2see/spida",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=required_packages,
    python_requires=">=3.10, <3.11",
)
