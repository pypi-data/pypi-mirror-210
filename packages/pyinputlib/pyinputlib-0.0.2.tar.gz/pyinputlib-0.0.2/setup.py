import setuptools

classfirs = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ]

setuptools.setup(
    name="pyinputlib",
    version="0.0.2",
    description="A Input Library",
    long_description="Usage\n-----\n - A Library For Nice Inputs, has A Function Named `funkyInput()` Which Takes 2 Arguments `ask_value` and `defaultVal`, `ask_value` for What Will Be Shown In The Input, `defaultVal` - (Optional), For The Default Value To Be Selected If The User Types Nothing",
    author="Monil",
    author_email="<monildarediya1@gmail.com>",
    packages=setuptools.find_packages(),
    requires=[],
    classifiers=classfirs
)