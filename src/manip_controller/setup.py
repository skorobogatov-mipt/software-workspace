from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'manip_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    package_data={package_name: ["*.so"]},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.json')),

    ],
    install_requires=[
        'setuptools', 
        'pin', 
        'pin-pink', 
        'qpsolvers[open_source_solvers]',
        'meshcat_shapes'
    ],
    zip_safe=True,
    maintainer='root',
    maintainer_email='skorobogatov.ev@phystech.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # f'camera_listener = {package_name}.camera_subscriber:main',
            # f'ikwalk_publisher = {package_name}.actuator_publisher',
            # f'ikwalk_publisher_and_tuner = {package_name}.actuator_publisher_tuner:main',
            # f'vision_node = {package_name}.vision_node:main',
            # f'motion_node = {package_name}.motion_node:main',
            # f'control_toolbox = {package_name}.control_toolbox:main',
            # f'checker_node = {package_name}.checker_node:main',
            f'ik_node = {package_name}.ik_node:main'
        ],
    },
)
