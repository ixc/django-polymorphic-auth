import setuptools

from polymorphic_auth import __version__

setuptools.setup(
    name='django-polymorphic-auth',
    version=__version__,
    packages=setuptools.find_packages(),
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
)
