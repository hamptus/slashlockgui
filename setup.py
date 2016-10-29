from setuptools import setup

setup(
    name='slashlockgui',
    version='0.2.3',
    description='SlashlockGUI - A simple GUI for Slashlock',
    url='https://github.com/wookalar/slashlockgui',
    author='Doc Tart',
    author_email='doc.tart@wookalar.io',
    license='AGPLv3',
    entry_points={'gui_scripts': [
        'slashgui = slashlock.gui:main',
    ]},
    setup_requires=[
        'Cython>=0.24.1',
    ],
    install_requires=[
        'slashlock==0.1.5',
        'Cython==0.24.1',
        'Kivy==1.9.1',
        'Kivy-Garden==0.1.4',
    ],
    install_package_data=True,
    py_modules=['slashlockgui'],
    package_data={
        'slashlock': ['gui.kv'],
    }
)
