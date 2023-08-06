from setuptools import setup, find_packages

setup(
    name='gitspyx',
    version='1.0.1',
    author='Alex Butler 🚩',
    author_email='mrhackerxofficial@gmail.com',
    description='Get Github user profile details',
    long_description='''GitSpyX: Simplify GitHub analysis with user profiles, repository details, contributor insights, and powerful visualizations. Effortlessly extract valuable information and gain insights for informed decision-making. Accelerate your GitHub repository analysis workflow with GitSpyX.''',
    long_description_content_type='text/plain',
    url='https://github.com/MrHacker-X/GitSpyX.git/',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
    'console_scripts': [
        'gitspyx = gitspyx.gitspyx:main',
    ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
