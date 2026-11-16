from setuptools import find_packages, setup

package_name = 'pushbot_tasks'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sameer Kishore',
    maintainer_email='S.kishore@mdx.ac.ae',
    description='Python task nodes for PushBot (PDE4430)',
    license='MIT',
    entry_points={
        'console_scripts': [
            'go_to_pose = pushbot_tasks.go_to_pose:main',
            'waypoints = pushbot_tasks.waypoints:main',
        ],
    },
)
