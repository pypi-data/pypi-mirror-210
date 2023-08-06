from distutils.core import setup


setup(
    name='livestream_monitor_classifier',
    packages=['livestream_monitor_classifier'],
    version='0.0.2',
    license='MIT',
    description='A Machine Learning Classifier that used to for my personal thesis project called livestream monitor',   # Give a short description about your library
    author='Rahmad Firmansyah',                   # Type in your name
    author_email='rahmadfirmansyah.id@gmail.com',      # Type in your E-Mail
    url='https://github.com/rfirmansyh/livestream_monitor_classifier',   # Provide either the link to your github or to your website
    download_url='https://github.com/rfirmansyh/livestream_monitor_classifier/archive/refs/tags/v0.0.2.tar.gz',    # I explain this later on
    keywords=['rfirmansyh', 'livestream_monitor_classifier'],   # Keywords that define your package best
    install_requires=[            # I get to this in a second
        'sklearn',
        'pandas',
        'joblib',
        'sastrawi',
        'unidecode',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    include_package_data=True,
    package_data={
        'helper': ['preprocess'],
        'models': [
            'model/sklearn_MNB.model'
        ],
        'data': [
             'data/stopwords-custom.txt',
        ],
    },
)