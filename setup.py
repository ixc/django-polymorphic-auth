import setuptools

from django_polymorphic_auth import __version__

setuptools.setup(
    name='django-polymorphic-auth',
    version=__version__,
    packages=setuptools.find_packages(),
    install_requires=[
        'django-polymorphic',
    ],
)
