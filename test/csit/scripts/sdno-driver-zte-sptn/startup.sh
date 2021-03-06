#!/bin/bash
#
# Copyright 2016-2017 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $1 nickname for the CATALOG instance
# $2 IP address of MSB
echo $@

#Start openoint/sdno-driver-huawei-l3vpn
run-instance.sh openoint/sdno-driver-huawei-l3vpn i-driver-huawei-l3vpn " -i -t -e MSB_ADDR=$2"
for i in {1..25}; do
    str=`curl -sS http://$2/openoapi/drivermgr/v1/drivers | grep -v "\[\]"`
    if [[ ! -z $str ]] ; then echo "Service started"; break; fi
    echo "sdno-driver-huawei-l3vpn wait" sleep $i
    sleep $i
done
