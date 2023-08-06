import setuptools
with open(r'C:\Users\dmitr\OneDrive\Рабочий стол\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='himza_itcollege',
	version='1.0',
	author='DmytroHimzaITCollege',
	author_email='dhimza2020@itcollege.lviv.ua',
	description='Module for creating an email address',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['himza_itcollege'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)