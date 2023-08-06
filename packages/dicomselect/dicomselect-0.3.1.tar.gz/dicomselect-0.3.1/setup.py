import setuptools

version = '0.3.1'

if __name__ == '__main__':
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    setuptools.setup(
        name='dicomselect',
        version=version,
        author_email='Stan.Noordman@radboudumc.nl',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/DIAGNijmegen/dicomselect',
        project_urls={
            "Bug Tracker": "https://github.com/DIAGNijmegen/dicomselect"
        },
        license='MIT License',
        packages=setuptools.find_packages('./dicomselect'),
    )
