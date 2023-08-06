from setuptools import setup, find_packages



VERSION = '1.2'
DESCRIPTION = 'Provide end-to-end control jwt token (Simple & Easy to Use)'


# Setting up
setup(
    name="jwt_django",
    version=VERSION,
    author="Momin Iqbal (Pakistan Dedov)",
    author_email="<mominiqbal1214@gmail.com>",
    description=DESCRIPTION,
    long_description="""
# jwt_django
## discontinue
jwt_django discontinue for some reasons <br>

include all the feature merge the webraft libarary https://github.com/MominIqbal-1234/webraft with new update <br>
pypi : https://pypi.org/project/webraft/ <br>
doc : https://webraft.mefiz.com <br>


Check Our Site : https://mefiz.com </br>
Developed by : Momin Iqbal


    """,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={'jwt_django': ['ktoken.cp37-win32.pyd']},
    install_requires=["django","djangorestframework","PyJWT"],
    keywords=['python', 'django', 'jwt', 'jwt for django','jwt for django','jwt_django','django_jwt'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
