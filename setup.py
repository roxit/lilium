from setuptools import setup, find_packages


setup(
    name = 'lilybbs',
    version = '2.0testing',
    description = "Python SDK for Nanjing University's Lily BBS",
    author = 'Shanshi Shi',
    author_email = 'shishanshi@gmail.com',
    url = 'https://github.com/superock/lilium',

    packages = ['lilybbs'],
    include_package_data = True,
    install_requires = ['BeautifulSoup']
)

