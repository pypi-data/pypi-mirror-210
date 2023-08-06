from setuptools import setup


setup(
    name="PyNfeIntegration",
    version="1.0.1",
    author="Cristiano dos Santos Lemos",
    author_email='cristianolemos@somma-it.com',
    keywords=['nfe', 'sped'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'pynfeintegration',
        'pynfeintegration.nfe',
        'pynfeintegration.certificates'
    ],
    url='https://github.com/ADD01-TECH/py-nfe-integration',
    license='MIT',
    description='PyNfeIntegration is a library that implement consults to invoices generate against some CNPJ',
    # long_description=open('README.rst').read(),
    requires=[
        'lxml(>=4.9.2)',
        'pyOpenSSL(>=23.1.1)',
        'qrcode(>=5.3)',
        'requests(>=2.30.0)',
    ],
)
