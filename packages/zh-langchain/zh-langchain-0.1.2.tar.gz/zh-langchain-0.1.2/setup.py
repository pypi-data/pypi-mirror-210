from setuptools import setup, find_packages

setup(
    name='zh-langchain',
    version='0.1.2',
    description='Chinese language processing library',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/imClumsyPanda/langchain-ChatGLM.git',
    packages=find_packages(include=['zh_langchain', 'zh_langchain.*']),
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)