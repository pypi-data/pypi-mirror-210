import setuptools
import wheel
with open("README.md", "r") as fh:
	description = fh.read()

setuptools.setup(
	name="test-package-harsha-tries",
	version="0.0.1",
	author="Harsha",
	author_email="geopktd350@wemail.pics",
	packages=["test_package"],
	description="A sample test package",
	long_description=description,
	long_description_content_type="text/markdown",
	url="https://github.com/HarshaD-1/package",
	#url="https://github.com/gituser/test-tackage",
	license='MIT',
	python_requires='>=3.8',
	install_requires=[]
)
