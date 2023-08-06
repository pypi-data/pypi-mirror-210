from distutils.core import setup

setup(name='pennylane-noisy-qubit',
      version='0.1',
      author='Frederic Magniette',
      author_email='frederic.magniette@llr.in2p3.fr',
      description='A noisy qubit for Pennylane with adjustable systematic error',
      #packages=['noisy_qubit'],
      install_requires=['pennylane','numpy'],
      entry_points={'pennylane.plugins': ['noisy.qubit = noisy_qubit:noisy_qubit']}
)
