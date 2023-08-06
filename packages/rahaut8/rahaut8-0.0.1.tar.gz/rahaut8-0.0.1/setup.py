import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="rahaut8",
    version="0.0.1",
    author="fox",
    author_email="abcdef1234567890user@gmail.com",
    packages=["rahaut8"],
    description="A sample test package",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/ARISTODUMES/LP6",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)