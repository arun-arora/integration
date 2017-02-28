#!/usr/bin/env python
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
import sys, csv, subprocess, os, shutil, urllib2, argparse

parser = argparse.ArgumentParser(description='Generate docker image definition for a microservice.  The results will be placed under the target/ subdirectory.')
parser.add_argument('microservice', help='filename of microservice as entered in binaries.csv')
parser.add_argument('--build', default="snapshot", help='a specific build to use ("autorelease-????")')

args = parser.parse_args()

version = "1.1.0-SNAPSHOT"

root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).rstrip()
path = "{}/test/csit/docker".format(root)
url_template = "https://nexus.open-o.org/service/local/artifact/maven/redirect?r=snapshots&g={0}&a={1}&e={2}&c={3}&v=LATEST"

found = False

with open( "{}/autorelease/binaries.csv".format(root), "r" ) as f:
    reader = csv.DictReader(f)

    for row in reader:
        if row["filename"] == args.microservice:
            found = True
            print row["filename"]

            if row["classifier"]:
                file = "{}-{}-{}.{}".format(row["artifactId"], version, row["classifier"], row["extension"])
                dest = "{}-{}-{}.{}".format(row["filename"], version, row["classifier"], row["extension"])
            else:
                file = "{}-{}.{}".format(row["artifactId"], version, row["extension"])
                dest = "{}-{}.{}".format(row["filename"], version, row["extension"])

            dir = "{}/{}/target".format(path, row["filename"])

            try:
                shutil.rmtree(dir, True)
                os.makedirs(dir)
            except OSError:
                pass

            # create empty Dockerfile if not exists
            dockerfile=open( "{}/Dockerfile".format(dir), "a" )
            dockerfile.close()

            outfile = open( "{}/50-microservice.txt".format(dir), "w" )
            
            if args.build == "snapshot":
                response = urllib2.urlopen(url_template.format(row["groupId"], row["artifactId"], row["extension"], row["classifier"]))
                url = response.geturl()
            else:
                url = "https://nexus.open-o.org/content/repositories/{}/{}/{}/{}/{}".format(args.build, row["groupId"].replace(".","/"), row["artifactId"], version, file )

            outfile.write("# 50-microservice.txt - AUTOGENERATED, DO NOT MODIFY MANUALLY\n\n")   
            outfile.write("# Set up microservice\n")
            
            outfile.write("RUN wget -q -O {} \"{}\"".format(dest, url))
            # outfile.write("ADD \"{}\" {}\n".format(url, dest))

            unzip_opt = ""
            if row["extension"] == "tar.gz":
                if row["unzip-dir"]:
                    unzip_opt = " -C {}".format(row["unzip-dir"])
                outfile.write(" && tar -xf {}{}".format(dest, unzip_opt))
            elif row["extension"] == "zip":
                if row["unzip-dir"]:
                    unzip_opt = " -d {}".format(row["unzip-dir"])
                outfile.write(" && unzip -q -o -B {}{}".format(dest, unzip_opt))
            outfile.write(" && rm -f {}\n".format(dest))

            outfile.write("# Set permissions\n")
            outfile.write("RUN find . -type d -exec chmod o-w {} \;\n")
            outfile.write("RUN find . -name \"*.sh\" -exec chmod +x {} \;\n")
            
            if row["ports"]:
                ports = row["ports"].split()
                for port in ports:
                    outfile.write("EXPOSE {}\n".format(port))
            outfile.write("RUN echo Open-O {} {} \"{}\" > OPENO_VERSION\n".format(row["filename"], version, url))
            outfile.write("\n\n")
            
            outfile.close()


            def symlink(flag, template):
                try:
                    os.remove("{}/{}".format(dir, template))
                except OSError:
                    pass
                if flag:
                    os.symlink("../../templates/{}".format(template), "{}/{}".format(dir, template))

            symlink(True, "10-basebuild.txt")
            symlink(row["python"], "15-python.txt")
            symlink(row["mysql"], "20-mysql.txt")
            symlink(row["mongodb"], "25-mongodb.txt")
            symlink(row["tomcat"], "30-tomcat.txt")
            symlink(True, "90-entrypoint.txt")

if not found:
    print "Error: microservice {} not found in binaries.csv.".format(args.microservice)
    sys.exit(2)
