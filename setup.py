from setuptools import setup

setup(
    name="move-imports",
    version="0.2",
    description="""Refactor modules to move import statements to the header""",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="Martín Gaitán",
    author_email="gaitan@gmail.com",
    url="https://github.com/mgaitan/move-imports",
    py_modules=["move_imports"],
    include_package_data=True,
    install_requires=[""],
    extras_require={"isort": ["isort"]},
    tests_require=["pytest"],
    license="MIT",
    zip_safe=False,
    keywords="ast, refactor",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points={"console_scripts": ["move-imports=move_imports:main"],},
)
