from setuptools import setup

setup(
    name='Smart_Solver',
    version='1.0',
    description='Smart Solver for games with AI search Algorithms',
    packages=['Smart_Solver', 'Smart_Solver.searches', 'Smart_Solver.utile'],
    install_requires=[
        'numpy',
    ],
)
