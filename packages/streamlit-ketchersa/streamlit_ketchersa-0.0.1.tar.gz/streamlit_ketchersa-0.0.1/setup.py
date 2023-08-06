import setuptools

import os
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'streamlit_ketchersa/pypi_readme.md'), 'r') as f:
    long_des = f.read()

setuptools.setup(
    name="streamlit_ketchersa",
    version="0.0.1",
    author="Nicola Landro",
    author_email="nicolaxx94@live.it",
    description="This library is a streamlit app for chemical or medical use that open and draw small molecules",
    long_description=long_des,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nicolalandro/streamlit-ketchersa/-/tree/main/",
    keywords=['chemistry', 'molecule', 'streamlit'],
    project_urls={
        'Source': 'https://gitlab.com/nicolalandro/streamlit-ketchersa/-/tree/main/',
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
)
