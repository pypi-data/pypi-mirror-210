from setuptools import setup, find_packages

requirements =[
    'Pillow',
    'numpy',
    'tqdm',
    'gdown',
    'insightface',
    'opencv-python',
    
]

pypandoc_enabled = True
try:
    import pypandoc
    print('pandoc enabled')
    long_description = pypandoc.convert_file('README.md', 'rst')
except (IOError, ImportError, ModuleNotFoundError):
    print('WARNING: pandoc not enabled')
    long_description = open('README.md').read()
    pypandoc_enabled = False

setup(
    name="innerverz",
    version="0.0.13",
    author="Innerverz",
    author_email="study@innerverz.com",
    description="innerverz package",
    long_description=long_description,
    python_requires=">=3.6",
    install_requires=requirements,
    packages=find_packages()
    
    
)
