from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='Loterias',
    version='0.0.11',
    license='MIT License',
    author='PKG',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='drjpp.drjpp@gmail.com',
    keywords='loterias CEF',
    description=u'Wrapper não oficial para pesquisa de dados lotéricos em thread',
    packages=['Loterias'],
    install_requires=['requests', 'pandas', 'urllib3'],)