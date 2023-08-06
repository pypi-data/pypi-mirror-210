from setuptools import setup, find_packages

setup(
    name="Lab3py-farisey",
    version="0.1.0",
    description="serialization",
    author="yury farisey",
    author_email="fariseyd@mail.ru",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializer.src"],
    include_package_data=True
)
