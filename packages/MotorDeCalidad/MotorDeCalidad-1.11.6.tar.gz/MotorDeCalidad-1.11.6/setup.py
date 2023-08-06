from setuptools import setup
setup(name='MotorDeCalidad',
version='1.11.6',
description='Paquete demo de Motor de Calidad',
author='Enzo Ipanaque',
author_email='enzo.ipanaque@ms-peru.com',
long_description=open('README.md').read(),
long_description_content_type='text/markdown',
license='Management Solutions',
packages=['motordecalidad'],
install_requires=[
    'azure-storage-blob',
    'typing-extensions==4.5.0'
],
py_modules=['functions','constants','rules','utilities'],
zip_safe=False)