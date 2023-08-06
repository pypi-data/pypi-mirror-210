import setuptools
with open(r'C:\Users\Имя\Desktop\pyth_library\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='rppt',
	version='1.1.2',
	author='Rand0mLit3ral',
	author_email='randomliteral@mail.ru',
	description='a library that simplifies writing code using "random" library',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Rand0mLit3ral/rppt-v1.1.0/tree/main',
	packages=['rppt'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)