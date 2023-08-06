import setuptools
import sys
# package internal only when running with --config-setting internal flag
internal_flag = False
# Check if the argument is present
if "-C" in sys.argv:
    arg_value = sys.argv[sys.argv.index("-C") + 1]
    if arg_value == 'internal':
        internal_flag = True
packages = setuptools.find_packages() if internal_flag else setuptools.find_packages(exclude=['*.internal.*', 'internal.*', '*.internal'])

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='wiliot-deployment-tools',
                 use_scm_version={
                     'git_describe_command': "git describe --long --tags --match [0-9]*.[0-9]*.[0-9]*",
                     'write_to': "wiliot_deployment_tools/version.py",
                     'write_to_template': '__version__ = "{version}"',
                     'root': ".",
                 },
                 setup_requires=['setuptools_scm'],
                 author='Wiliot',
                 author_email='support@wiliot.com',
                 description="A library for interacting with Wiliot's Deployment Tools",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url='',
                 project_urls={
                     "Bug Tracker": "https://WILIOT-ZENDESK-URL",
                 },
                 license='MIT',
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 packages=packages,
                #  add all support files to the installation
                #  package_data={"": ["*.*"]},
                 install_requires=[
                     'setuptools_scm==7.1.0',
                     'wiliot-core==4.0.9',
                     'wiliot-api==4.1.2',
                     'bitstruct==8.17.0',
                     'bokeh==2.4.1',
                     'boto3==1.26.77',
                     'colorama==0.4.6',
                     'jsonpickle==3.0.1',
                     'numpy==1.24.2',
                     'pandas==1.5.3',
                     'plotly==5.13.0',
                     'pytz==2022.7.1',
                     'requests==2.28.1',
                     'setuptools==65.6.3',
                     'setuptools_scm==7.1.0',
                     'tabulate==0.8.10',
                     'backports.zoneinfo==0.2.1',
                     'tinytuya==1.10.2',
                     'pyserial==3.5',
                     'GitPython==3.1.31',
                     'tzdata==2023.3'
                 ],
                 zip_safe=False,
                 python_requires='>=3.6',
                #  include_package_data=False,
                #  exclude_package_data={
                #      "": ['*.internal.*', '*.internal', 'internal', 'internal.*']},
                 entry_points={'console_scripts': [
                     'wlt-firmware=wiliot_deployment_tools.firmware_update.firmware_update_cli:main_cli',
                     'wlt-power-mgmt=wiliot_deployment_tools.power_mgmt.power_mgmt_cli:main_cli',
                     'wlt-config=wiliot_deployment_tools.automatic_configuration_tool.configuration_tool_cli:main_cli',
                     'wlt-log=wiliot_deployment_tools.log_viewer.log_viewer_cli:main_cli']},
                 )
