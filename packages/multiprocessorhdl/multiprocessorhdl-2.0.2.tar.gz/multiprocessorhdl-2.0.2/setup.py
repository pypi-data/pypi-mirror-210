import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "multiprocessorhdl",
    version = "2.0.2",
    author = "ORION_B",
    author_email = "obanarse@gmail.com",
    description = "short package description dmo version2",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["multiprocessorhdl","multiprocessorhdl.DL_PRACTICAL","multiprocessorhdl.HPC_Practical"],
    # packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires = ">=3.6",


    package_data={
    "multiprocessorhdl.HPC_Practical": ["*.txt", "*.rst","*.ipynb","*.csv","*.cpp","*.docx","*.exe"],
    "multiprocessorhdl.DL_PRACTICAL": ["*.txt", "*.rst","*.ipynb","*.csv","*.cpp","*.docx","*.exe"],

    "multiprocessorhdl.HPC_Practical": ["*.cpp","*.docx","*.exe"],
    }


)