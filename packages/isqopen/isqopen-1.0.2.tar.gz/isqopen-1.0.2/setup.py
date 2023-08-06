from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = "isqopen",
    version = "1.0.2",
    keyword = {"isq", "quantum", "cor"},
    description = "isq quantum kernel",
    platforms='python 3.8+',
    long_description=long_description,
	long_description_content_type="text/markdown",
    author = "Lou Huazhe",
    author_email = "louhz@arclightquantum.com",

    package_data = {'':['*.txt']},
    install_requires = ['numpy>=1.21.3',
                        'ply>=3.11',
                        'scipy>=1.7.1',
                        'autograd',
                        'matplotlib'],
    packages = find_packages(),
    zip_safe=False
)
