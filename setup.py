from setuptools import setup

__version__ = '1.0'

setup(
    name='MrWhatZitTooya',
    version=__version__,
    packages=['whatzittooya'],
    url='https://github.com/CodersClashS01/WhatZitTooya',
    license='MIT',
    author=[
        'Vale#5252',
        'Wambo#0800',
        'Leterax#6932',
        'itsBen#7718',
        'Snosh#2736'
    ],
    author_email='itisvale1@gmail.com',
    description='A Discord bot created for the CodersClash competition.',
    install_requires=[
        'git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]',
        'pillow',
        'giphypy',
        'asyncpg',
        'youtube_dl'
    ]
)
