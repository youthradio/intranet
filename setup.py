from setuptools import setup

__doc__ = "Youth Radio Central. More to come in this description later."

setup(
	name="YouthRadioCentral",
	author="Kurt Collins",
	version="0.2",
	long_description=__doc__,
	packages=["intranet"],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"Flask>=0.9",
		"flask-googleauth",
		"Flask-WTF",
		"beautifulsoup4",
		"wtforms",
		"validate_email",
		"pytz",
		"html5lib"
	]
)