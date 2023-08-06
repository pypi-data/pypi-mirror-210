from setuptools import setup, find_packages

setup(
    name="xgh_say_hello",
    author="xgh",
    version="0.0.2",
    description="Just for learning publish a python package",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "x-say-hello=say_hello.say_hello:main",
            "x-say-hi=say_hello.say_hello:hi",
        ]
    },
)
