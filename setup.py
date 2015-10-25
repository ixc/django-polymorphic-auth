from __future__ import print_function

import setuptools
import sys

version = '0.1.dev0'

# Convert README.md to reStructuredText.
if {'bdist_wheel', 'sdist'}.intersection(sys.argv):
    try:
        import pypandoc
    except ImportError:
        print('WARNING: You should install `pypandoc` to convert `README.md` '
              'to reStructuredText to use as long description.',
              file=sys.stderr)
    else:
        print('Converting `README.md` to reStructuredText to use as long '
              'description.')
        long_description = pypandoc.convert('README.md', 'rst')

setuptools.setup(
    name='django-polymorphic-auth',
    version=version,
    author='Interaction Consortium',
    author_email='studio@interaction.net.au',
    url='https://github.com/ixc/django-polymorphic-auth',
    description='Polymorphic user model with plugins for common options, plus '
                'abstract and mixin classes to create your own.',
    long_description=locals().get('long_description', ''),
    license='MIT',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'coverage',
        'Django',
        'django-dynamic-fixture',
        'django-nose',
        'django-polymorphic',
        'django-webtest',
        'nose-progressive',
        'WebTest',
    ],
    extras_require={
        'dev': ['ipdb', 'ipython'],
    },
)
