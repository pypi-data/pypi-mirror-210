from setuptools import setup, find_packages


setup(
    name='edaplore',
    version='0.2.1',
    author='Maksim Zabelin',
    author_email='mzabelin8@mail.ru',
    description='EDA helper',
    long_description='',
    license='MIT',
    url='https://github.com/mzabelin8/explore_hse',
    packages=find_packages(),
    install_requires=[
        'Jinja2==3.1.2',
        'matplotlib==3.7.1',
        'numpy==1.24.3',
        'pandas==1.5.3',
        'scikit_learn==1.2.2',
        'seaborn==0.12.2',
        'setuptools==66.0.0',
        'tqdm==4.65.0',
    ],
    python_requires='>=3.6'
)
