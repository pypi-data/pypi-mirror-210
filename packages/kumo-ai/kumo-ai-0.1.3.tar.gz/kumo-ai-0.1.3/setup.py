from setuptools import find_packages, setup

VERSION = '0.1.3'
DESCRIPTION = 'Kumo.ai Client SDK'
LONG_DESCRIPTION = """
SDK/API for Kumo.ai clients to allow programmatic access to Kumo.ai
"""

install_requires = [
    "pydantic==1.10.4",
    "requests==2.28.2",
]

setup(name="kumo-ai",
      url="https://kumo.ai",
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author="Kumo.ai",
      author_email="support@kumo.ai",
      license='MIT',
      packages=find_packages(),
      install_requires=install_requires,
      setup_requires=["setuptools_scm"],
      keywords=['kumo'],
      python_requires=">=3.8",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          'License :: OSI Approved :: MIT License',
          "Programming Language :: Python :: 3",
      ])
