import os
from setuptools import setup, Extension, find_packages
import subprocess
_VERSION = "1.1"

EBglmnet_lib = Extension(name='EBglmnet.EBglmnet',
                          sources=['EBglmnet/src/Binary.c',
                                    'EBglmnet/src/CVonePara.c',
                                    'EBglmnet/src/elasticNet.c',
                                    'EBglmnet/src/elasticNetBinary.c',
                                    'EBglmnet/src/elasticNetLinear.c',
                                    'EBglmnet/src/fEBBinaryNEG.c',
                                    'EBglmnet/src/fEBLinearNEG.c',
                                    'EBglmnet/src/Linear.c',
                                   'EBglmnet/src/NEG.c',
                                   ],
                          include_dirs=['EBglmnet/src',
                                        '/opt/intel/oneapi/mkl/2023.1.0/include'],
                          library_dirs=['/opt/intel/oneapi/mkl/2023.1.0/lib'],
                          libraries=['mkl_rt'],
                          extra_compile_args=['-std=c11', '-O2'])

EBglmnet_lib.name = 'EBglmnet'

if __name__ == "__main__":
    setup(
        name="EBglmnet",
        version=_VERSION,
        description="Python wrapper for EBglmnet",
        long_description_content_type="text/markdown",
        long_description=open('README.md').read(),
        author="Anhui Huang",
        author_email="anhuihuang@gmail.com",
        url="https://scholar.google.com/citations?user=WhDMZEIAAAAJ&hl=en",
        install_requires=[
            "numpy>=1.9.2",
            "matplotlib",
            "pandas",

        ],
        python_requires=">=3.6",
        setup_requires=["setuptools"],
        ext_modules=[EBglmnet_lib],
        packages=find_packages(),
        package_data={'EBglmnet': ['src/*.c','src/*.h', 'data/*', 'doc/*']},
        include_package_data=True,
        package_dir={'EBglmnet': 'EBglmnet'},
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3 :: Only',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Topic :: Scientific/Engineering'
        ]
    )


    # Add the install_name_tool command here



    #binary_path = os.path.join(os.getcwd(), 'EBglmnet', 'EBglmnet.cpython-311-darwin.so')
    #install_name_tool_cmd = ['install_name_tool', '-rpath', '/opt/intel/oneapi/mkl/2023.1.0/lib', binary_path]
    #subprocess.run(install_name_tool_cmd)

