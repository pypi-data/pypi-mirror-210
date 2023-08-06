import sys,os

from setuptools import setup, find_packages, Extension
#from setuptools_cuda_cpp import CUDAExtension, BuildExtension, find_cuda_home_path

#import pybind11

#import subprocess

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read UAMMD environment variables

UAMMD_PATH = os.environ.get('UAMMD_PATH')
if UAMMD_PATH is None:
    logger.error('UAMMD_PATH environment variable not set')
    sys.exit(1)

UAMMD_STRUCTURED_PATH = os.environ.get('UAMMD_STRUCTURED_PATH')
if UAMMD_STRUCTURED_PATH is None:
    logger.error('UAMMD_STRUCTURE_PATH environment variable not set')
    sys.exit(1)

########## UAMMD ##########

logger.info('UAMMD_PATH: {}'.format(UAMMD_PATH))
logger.info('UAMMD_STRUCTURED_PATH: {}'.format(UAMMD_STRUCTURED_PATH))

###########################

#NVCC_PATH = os.path.join(find_cuda_home_path(), 'bin', 'nvcc')
#
#try:
#
#    # Get the current list gpu capturing nvcc output
#    p = subprocess.Popen([NVCC_PATH, '--list-gpu-code'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    out, err = p.communicate()
#
#    archs = out.decode('utf-8').split('\n')[0:-1]
#    archs = [arch.split("_")[-1] for arch in archs]
#
#    gencode = []
#    for arch in archs:
#        gencode += ['-gencode','arch=compute_{},code=sm_{}'.format(arch, arch)]
#except:
#    raise RuntimeError('Could not run nvcc')


###########################

#ext_modules = [
#    CUDAExtension(
#        name='pyUAMMD.utils.launcher.UAMMDlauncher',
#        sources=['pyUAMMD/utils/launcher/UAMMDlauncher.cu'],
#        include_dirs=[os.path.join(UAMMD_PATH,'src'),
#                      os.path.join(UAMMD_PATH,'src/third_party'),
#                      UAMMD_STRUCTURED_PATH,
#                      pybind11.get_include()],
#        define_macros=[('MAXLOGLEVEL', '5'),
#                       ('UAMMD_EXTENSIONS',None)],
#        extra_compile_args={
#            'nvcc': ['--expt-relaxed-constexpr','--expt-extended-lambda',
#                     '-O3',
#                     '-Xcompiler=-O3 -march=native -fPIC',
#                     '-ccbin','g++'] + gencode,
#        }
#    )
#]

#setup(
#    packages=find_packages(),
#    ext_modules=ext_modules,
#    cmdclass={'build_ext': BuildExtension},
#    url="https://github.com/PabloIbannez/pyUAMMD",
#)

setup(
    packages=find_packages(),
    url="https://github.com/PabloIbannez/pyUAMMD",
)
