import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="django-events-framework",
    version="0.0.13",
    author="Alexandru Gheorghita",
    author_email="gheorghitacristian@mac.com",
    description="An events framework for logging and processing Django models events.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points="",
    url="https://github.com/Reve/django-events-framework",
    packages=setuptools.find_packages(exclude=("test_app*",)),
    include_package_data=True,
    install_requires=["django>=2.2", "django-jsonfield"],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
