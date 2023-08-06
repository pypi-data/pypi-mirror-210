import	setuptools
import	re

with open("readme.txt", "r", encoding="utf-8") as f:
	long_description = f.read()


# 寻找特定的值
def find_value(text, key, default_value):
	value	= re.findall(r"^"+key+r"[\s]*(.*)", text, re.M)
	if not value:
		print(f"没找到{key}，使用默认值")
		value	= default_value
	else:
		value	= value[0].strip()
	return value
version	= find_value(long_description, 'version', '0.0.1')
brief	= find_value(long_description, 'brief', 'No brief')

setuptools.setup(
	name				= "spiritlong",
	version				= version,
	author				= "SpiritLong",
	author_email			= "arthuryang@spiritlong.com",
	maintainer			= "SpiritLong",
	maintainer_email		= "shun@spiritlong.com",
	description			= brief,
	long_description		= long_description,
	long_description_content_type	= "text/markdown",
	url				= "https://spiritlong-exon.com/pip",
	packages			= setuptools.find_packages(),
	classifiers			= [
						'Development Status :: 3 - Alpha',
						"Programming Language :: Python :: 3",
						'Intended Audience :: Developers',
						'Operating System :: OS Independent',
					],
	python_requires			= '>=3.7',
	install_requires		= [
						'openpyxl',
						'mysqlclient',
						#'psycopg2',
						'dbutils',
						'python-docx',
						'redis',
					],
)

# python setup.py sdist bdist_wheel
# twine upload dist/* -u spiritlong