from setuptools import setup, find_packages

setup(
    name='routeml',
    version='0.3.0',
    description='Python package for CVRP utilities',
    author='Your Name',
    author_email='jkschin@mit.edu',
    url='https://github.com/jkschin/routeml',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "hygese"
        # Add any dependencies required by your package
    ],
)
