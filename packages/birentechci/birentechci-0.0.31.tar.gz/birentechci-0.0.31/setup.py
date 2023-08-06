import setuptools 
import os
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 

def _process_requirements():
    packages = open('./brci/requirements.txt').read().strip().split('\n')
    requires = []
    for pkg in packages:
        if pkg.startswith('git+ssh'):
            return_code = os.system('pip install {}'.format(pkg))
            assert return_code == 0, 'error, status_code is: {}, exit!'.format(return_code)
        else:
            requires.append(pkg)
    return requires


setuptools.setup(
    name="birentechci", 
    version="0.0.31",    
    author="br_infra",    
    author_email="br_infra@birentech.com",    
    description="biren ci sdk",
    long_description=long_description,    
    long_description_content_type="text/markdown",
    url="https://gitlab.birentech.com/software/br_ci_db",    
    packages=setuptools.find_packages(),
    # 希望被打包的文件
    package_data={
        '':['*.env'],
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6', 
    install_requires=_process_requirements(),
    include_package_data=True,
        entry_points={
        'console_scripts': [
            'brci-cmd = brci.run:main',
        ],
        }
)
