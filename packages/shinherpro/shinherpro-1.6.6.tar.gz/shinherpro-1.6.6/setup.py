from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        print("\033[98m 正在安裝shinher-pro...")
        install.run(self)
        print("shinherpro安裝完成！ \033[0m")

setup(
    name='shinherpro',
    version='1.6.6',
    description='shinher-pro 1.6.6',
    author='Yihuan',
    author_email='ivan17.lai@gmail.com',
    packages=['shinherpro'],
    install_requires=[
        'selenium',
        'beautifulsoup4',
        'keras',
        'opencv-python',
        'Pillow',
        'tensorflow',
        'requests',
        'numpy'
    ],
    long_description_content_type='text/markdown',
    cmdclass={
        'install': CustomInstallCommand,
    }
)
