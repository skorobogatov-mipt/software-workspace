from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'referees'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.json')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jazzhands',
    maintainer_email='skorobogatov.ev@phystech.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            f'pickup_referee = {package_name}.pickup_referee:main',
            f'container_referee = {package_name}.container_referee:main',
            f'tally_referee = {package_name}.tally_referee:main'
        ],
    },
)
