from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='api-console-solver',
    version='0.0.17',
    license='MIT License',
    author='Wesley Romualdo da Silva',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='romualdo@solvedigital.com.br',
    keywords='console api',
    description=u'Wrapper oficial da Plataforma Solver',
    packages=['Solver'],
    install_requires=['requests'],)