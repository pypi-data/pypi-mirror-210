from setuptools import setup

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(name='stlock',
      version='0.0.7.1',
      description='oauth2.0 stlock',
      packages=['stlock'],
      author_email='office@stl.im',
      zip_safe=False,
      install_requires=["requests", "pyjwt"],
      long_description=long_description,
      long_description_content_type="text/markdown")
