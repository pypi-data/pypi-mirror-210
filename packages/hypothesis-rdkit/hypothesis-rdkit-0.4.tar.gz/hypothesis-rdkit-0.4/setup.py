from setuptools import setup, find_packages


setup(
    name="hypothesis-rdkit",
    version="0.4",
    maintainer="Steffen Hirte",
    maintainer_email="shirte@users.noreply.github.com",
    packages=find_packages(),
    url="https://github.com/shirte/hypothesis-rdkit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    license_files=("LICENSE",),
    install_requires=["hypothesis"],
    extras_require={"dev": ["black", "isort"]},
    entry_points={"hypothesis": {"_ = hypothesis_rdkit.hook:_hypothesis_setup_hook"}},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Framework :: Hypothesis",
        "License :: OSI Approved :: MIT License",
    ],
)
