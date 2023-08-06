from setuptools import setup

setup(
    name='py_search_game_algo',
    version='1.0',
    description='py_search_game_algo',
    packages=['py_search_game_algo', 'py_search_game_algo.searches', 'py_search_game_algo.utile'],
    install_requires=[
        'numpy',
        'networkx',
        'matlab',
    ],
)
