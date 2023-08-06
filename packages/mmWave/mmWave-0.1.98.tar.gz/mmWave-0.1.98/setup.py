# (1)   $export PATH=$PATH:$HOME/.local/bin
# (2)   $python3 setup.py sdist bdist_wheel
#
# run Twine to upload all of the archives under dist:
# (3)   $twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
#  if file HTTPError: 400 Client Error: File already exists.
#
#  Use this ******
# (3.1) $twine upload --skip-existing dist/*
# (4)   $sudo pip install mmWave -U
#
# if error: invalid command 'bdist_wheel'
# $pip3 install wheel
#
#
# vitalSign.py v0.0.8
#              v0.0.9
#              v0.0.10 :2020/02/04
#
# highAccuracy v0.0.4
#       v0.0.4 fix for Jetson nano
#
# peopleMB : v0.0.3
#           v0.0.4    :2019/12/06  fix for Jetson nano
#           v0.0.5    :2020/04/21  fix for Jetson nano
#
# srradar.py : v0.0.1 :2019/10/03
# v0.1.19 : add srradar.py
#
# people3D.py : v0.0.2 :2019/10/22
#               v0.0.3 :2019/10/23
#               v0.0.4 :2019/10/24
#
# pc3d.py     : v0.0.1 :2019/11/26
#               v0.0.2 :2019/11/27
#               v0.0.3 :2019/12/02
#
# pc3d_kv.py  : v0.0.1 :2019/11/25
#               v0.0.2 :2019/12/02
#
# lpdISK.py   : v0.0.1 :2019/12/04
#               v0.0.2 2023/02/03 lpdISK firmware: 0910 and 0985 (added EC16,g,confi)
#               v0.0.3 2023/02/04 combine: v0.0.1 & v0.0.2
#
# lpdISK_kv.py: v0.0.1 :2019/12/06
#
# vehicleOD.py   : v0.0.1 :2020/02/11
#
# trafficMD_kv.py :v0.0.2 :2020/03/18
# Original name: trafficMD.py :v0.0.1 :2020/03/18
#
# surfaceVD.py :v0.0.1 :2020/04/17
#
# trafficMD.py :v0.0.1 :2020/04/30
#               v0.1.0 :2021/04/21 add DataFrame output @v1.0.48
#
# droneRD.py   :v0.0.1 :2020/05/13
# droneRN.py   :v0.0.2 :2020/05/13 (change name from droneRD.py)
#
# pc3.py       :v0.0.1 :2020/06/19     added for v0.1.42
#               v0.1.1 :2021/04/21     add DataFrame output @v1.0.48
#               v0.1.2 :2021/05/06     add frameNumber and field change @v1.0.51
#               v0.1.3 :2021/05/06     revised dataframe dtype @v1.0.52
#               v0.1.4 :2021/10/12     doppler and range swap
#
# zoneOD.py    :v0.0.1 :2020/07/21     added for v1.0.43 removed at v1.0.44
#
# vehicleODHeatMap.py :v0.0.1 :2020/07/21 add for v0.1.44
#
# vitalsign_kv.py :v0.0.1: 2020/10/20 
#
# vehicleODR.py :v0.0.1 :2021/01/07 v0.1.47
#
# roadwayTMD_kv :v0.1.0 :2021/04/21 @v0.1.49
#               :v0.1.1 :2020/05/02 @v0.1.50 add getRecordData(self,frameNum):
#                                                readFile(self,fileName):
#               :v0.1.2 :2020/05/04 @v0.1.51 bug fix
#
# pc3OVH        :v0.1.0 :2021/05/18
#               :v0.1.1 :2021/08/12
#               :v0.1.2 :2021/09/16 @v7 in dataFrame 'tid' move to front of 'ec0'
#               :v1.0.0 :2022/07/18 @v6 add tilt, install height and (sx,sy,sz) in raw data mode
#               :v1.0.1 :2022/07/19 @v6 added v6 fetech time
#               :v1.0.2 2022/07/20 @v6 raw data: (elv,azi,ran,dop,snr,sx,sy,sz)..
#
# lpdFDS        :v0.1.0 :2021/05/26 dataFrame/raw 
#               :v0.1.1 :2021/05/26 message change
#               :v0.1.2 :2021/05/26 bug fix
#
# trafficMD_I480.py :v0.1.0 :2021/09/16
#
#
# mrRadar.py    :v0.0.1 :2021/12/31 First release @v0.1.62
#               :v0.0.2 :2022/02/07 format revised @v0.1.63
#               :v0.1.0 :2022/06/02 tune to fit v3 data
#               :v1.0.0 :2022/06/08 change get Uart Data Method
#               :v1.0.1 :2022/06/09 added headerShowAll()
# pc3_oob.py    :v0.0.1 :2022/03/01 @v0.1.64
#	            :v0.0.2 :2022/03/01 @v0.1.65 bug fix
#               :v0.0.3 :2022/03/03 @v1.0.66
#               :v0.0.4 :2023/05/25 @v1.0.97 add v7, playback
#               :v0.0.5 :2023/05/25 @v1.0.98 bug fix
#
# @v1.0.67 modified description
#
# @v1.0.68
# pc3_vsd.py    :v0.0.1 :2022/03/10 bata version
#
# @v1.0.70
# pc3_v2.py     :v2.0 :2022/04/19
#
# @v1.0.71
# trafficMD_I480 :v2.0.1 :2022/04/28 (output data posZ,velZ,accZ position change)
#
# @v1.0.72 (remove)
# trafficMD_I480 :v2.0.2 added tlvRead status, chk: {0:'EMPTY',1:'inData',10:'IDLE',99:'FALSE'}
#
# @v1.0.73
# trafficMD_I480 :v2.0.2 added tlvRead status, chk: {0:'EMPTY',1:'inData',10:'IDLE',99:'FALSE'}
#
# @v1.0.74
# trafficMD_I480 :v2.0.4 revised v8,v9 as dictionary data type
#
# @v1.0.75
# mrRadar : modify for fit v3 data
#
# @v1.0.76
# mrRadar : change get Uart method
# @v1.0.77
# mrRadar : added headerShowAll()
#
# @v1.0.78
# pc3_v2: v2.0.1 added sx,sy,sz in v6
#
# @v1.0.79
# v2.0.2 2022/06/13 pc3_v2 added azimuth offset
#
# @v1.0.80
# v1.0.0 2022/07/18 pc3OVH added tilt, install height and (sx,sy,sz) in raw data mode
# @v1.0.81
# v1.0.1 2022/07/19 pc3OVH added v6 fetch time
# @v1.0.82/83
# v1.0.2 @v6 raw data: change to (elv,azi,ran,dop,snr,sx,sy,sz)..
#
# @v1.0.84
# v1.0.1 2022/08/16 pc3_360 added for integrate 3 sets of radar module to 360° FOV(first release)
#
# @1.0.85/86
#    v0.0.1 2022/09/12 pc3_vsd_v2 Bata version.
#
# @1.0.85/87
#    v0.0.2 2022/09/15 pc3_vsd_v2 swap dictionary: br & hr
#
# @1.0.88
#    v0.0.1 2022/11/03 lpdISK_v2 Bata version.
#
# @1.0.89
#    v0.0.1 2022/01/05 pc3_v1884R
#
# @1.0.90
#    v0.0.2 2023/02/03 lpdISK firmware: 0910 and 0985
#
# @1.0.91
#    v0.0.2 2023/02/04 lpdISK firmware: combine v7 struct v0.0.1 and v0.0.2
#
# @1.0.92/93
#    v2.0.0 2022/02/08  pct   People Counting 3D with Tilt(PCT) firmware: v4958
#    @93- v2.0.1 : modified dataframe type for playback
#
# @1.0.94
#    2023/02/10 trafficMD_I480 v2.0.4, revised v7 'tid' text position
#
# @1.0.95
#    2023/03/24 mrRadar   v1.0.2  header enable/disable in inital
#    2023/03/24 trafficMD v0.1.1  header enable/disable in inital
#    2023/03/24	trafficMD_I480   ver:2.0.6 header enable/disable in inital
#
# @1.0.96
#    2023/04/07 pc3_V1884R v0.0.2  add try..except in unpack
#
# @1.0.97
#   2023/05/25 pc3_oob v0.0.4 add v7 and playback
# @1.0.98
#   2023/05/25 pc3_oob v0.0.5 bug fix

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mmWave",
    version="0.1.98",
    author="Bighead Chen",
    author_email="zach_chen@joybien.com",
    description="Joybien mmWave (Batman-101/201/301/501/601) library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.joybien.com",
    download_url="https://pypi.org/project/mmWave",
    project_urls={
        "API Source Code": "https://github.com/bigheadG/mmWave",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
