from setuptools import setup

setup(
    name="serializers_for_lab3",
    version="0.1.1",
    description="Library for python serialization & deserialization in Json & Xml",
    url="https://github.com/Shakuriks/IgiLabs/tree/lab3",
    author="Legonkov Nikita",
    author_email="legonkovnikita77@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializers"],
    include_package_data=True,
    install_requires=["regex"]
)