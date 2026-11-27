from setuptools import setup

package_name = 'cg_solver'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ponderada',
    maintainer_email='student@inteli.edu.br',
    description='Navegação autônoma para o Culling Games',
    license='MIT',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'parte1 = cg_solver.parte1_node:main',
            'parte2 = cg_solver.parte2_node:main',
        ],
    },
)
