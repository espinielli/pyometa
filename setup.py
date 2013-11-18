from distutils.core import setup

DESCRIPTION = 'Pattern-matching language based on OMeta'

LONG_DESCRIPTION = None
LICENSE = None
try:
    LONG_DESCRIPTION = open('README.md').read()
    LICENSE = open('LICENSE').read()
except:
    pass

setup(name='pyometa',
	version="1.0.0",
	packages=['pyometa'],
	author='Enrico Spinielli',
	author_email='enrico.spinielli@gmail.com',
	maintainer='Enrico Spinielli',
	maintainer_email='enrico.spinielli@gmail.com',
	url='https://github.com/espinielli/pyometa',
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	platforms=['any'],
	license=LICENSE
)
