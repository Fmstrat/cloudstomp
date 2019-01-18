# Cloudstomp - Automated deployment of instances on EC2 via plugin for high CPU/GPU applications at the lowest price

Cloudstomp is a python application *that is in active development* and built to make deployment of high CPU/GPU applications in Amazon EC2 as spot instances for affordable, quick, and easy data analysis.

Plugins can be created in the `json` format that enable users to quickly deploy applications. Two plugins are included for demonstration, one for a `hello world` application, and one for `hashcat`.

## Install

Installation can be completed with Docker or natively. For a native local installation, start by downloading cloudstomp:
```
# cd /usr/bin
# wget https://raw.githubusercontent.com/Fmstrat/cloudstomp/master/cloudstomp.py
# chmod +x cloudstomp.py
```
or, if you would like to use Docker:
```
# alias cloudstomp.py='docker run -it --rm --name=cloudstomp -v ${HOME}/.cloudstomp:/data cloudstomp /cloudstomp.py'
```
## Plugins
The current documentation for plugins and avaialable plugins can be found at https://github.com/Fmstrat/cloudstomp-plugins and are:
* Hello World - The example shown below
* Hashcat - Password cracking in the cloud

## AWS Credentials
To use `Cloudstomp` you must provide AWS credentials. To set up your credentials at the AWS Management Console:
* Sign in at https://console.aws.amazon.com/iam/
* Go to `Users`
* Then `Add User`
* Add the user `cloudstomp`
* Check the box for `Programmatic access`
* Click `Next: Permissions`
* If the `Administrators` group doesn't exist, click `Add group`
* Enter `Administrators` for `Group name`
* Check `Administrator Access`
* Click `Create group` which will return you to the add user screen                                                                                                                            
* Back on the add user screen, choose `Add user to group` and check `Administrators`
* Click `Next: Tags`
* Click `Next: Review`
* Click `Create user`
* `Access key ID` and `Secret access key` are displayed which are required for configuration of `Cloudstomp`

## Usage

First, we need to download the latest plugins:
```
# cloudstomp.py --update
```
This will download all of the preconfigured plugins into the ~/cloudstomp folder (or the folder specified in the Docker command).

Then, we fire up cloudstomp:
```
# cloudstomp.py
```
The first time `Cloudstomp` runs, it requires the AWS credentials. This sets up a credentials file completely seperate from those used in your normal AWS administration to reduce conflicts.
<pre>
AWS CLI is not configured, would you like to do this now? [y/N]: <i><b>y</b></i>
Access key, Secret key, and default region must all be configured.
AWS Access Key ID [None]: <i><b>*********</b></i>
AWS Secret Access Key [None]: <i><b>*********</b></i>
Default region name [None]: <i><b>us-east-1</b></i>
Default output format [None]: 
</pre>

Then, follow the prompts:
<pre>

Sessions:
-------------------------------------------
 c) Create
 q) Quit
-------------------------------------------
Select session: <i><b>c</b></i>

Creating a new session.
Plugins:
-------------------------------------------
 1) Hashcat
 2) Hello World
-------------------------------------------
Please select a plugin: <i><b>2</b></i>

</pre>
The first time you choose a plugin, the AMI that instances will be created from needs to be built. This is a one-time item and the AMI is stored on S3 as they always are for faster future deployment.
<pre>

The AMI for hello world needs to be built.
Would you like to build it now? [Y/n]: <i><b>y</b></i>

[2019-01-18 10:57:47] Build will take place on a t2.nano instance.
[2019-01-18 10:57:47] Checking availability zones for t2.nano...
[2019-01-18 10:57:48] Getting subnet...
[2019-01-18 10:57:49]   Using subnet subnet-0bea6a005f7f8dbed.
[2019-01-18 10:57:49] Checking VPC...
[2019-01-18 10:57:50]   Using VPC vpc-02d8172ca01a496de.
[2019-01-18 10:57:50] Checking security group...
[2019-01-18 10:57:50]   Creating new security group.
[2019-01-18 10:57:51]   Adding rules...
[2019-01-18 10:57:52]     Added port 22.
[2019-01-18 10:57:52]   Using security group sg-019fedf5084f3e068.
[2019-01-18 10:57:54] Instance i-06f82a99547d8d66e started.
[2019-01-18 10:57:54] Waiting for boot to complete...
[2019-01-18 10:57:54]   Instance in pending state, sleeping 15s...
[2019-01-18 10:58:10] Instance has public IP of 18.212.124.241.
[2019-01-18 10:58:10] Checking for SSH connectivity...
[2019-01-18 10:58:13]   Waiting for SSH to start, sleeping 15s...
[2019-01-18 10:58:28]   Waiting for SSH to start, sleeping 15s...
[2019-01-18 10:58:46] Starting build scripts...
[2019-01-18 10:58:46]   Running build.sh...
[2019-01-18 10:58:48]     Uploaded.
Get:1 http://security.ubuntu.com/ubuntu bionic-security InRelease [83.2 kB]
Hit:2 http://archive.ubuntu.com/ubuntu bionic InRelease
Get:3 http://archive.ubuntu.com/ubuntu bionic-updates InRelease [88.7 kB]
Get:4 http://archive.ubuntu.com/ubuntu bionic-backports InRelease [74.6 kB]

... [ Output of setting up the instance (apt-get/etc) ] ...

Successfully built PyYAML
Installing collected packages: docutils, jmespath, six, python-dateutil, urllib3, botocore, PyYAML, pyasn1, rsa, colorama, futures, s3transfer, awscli
Successfully installed PyYAML-3.13 awscli-1.16.91 botocore-1.12.81 colorama-0.3.9 docutils-0.14 futures-3.2.0 jmespath-0.9.3 pyasn1-0.4.5 python-dateutil-2.7.5 rsa-3.4.2 s3transfer-0.1.13 six-1.12.0 urllib3-1.24.1
[2019-01-18 10:59:59] Stopping instance...
[2019-01-18 11:00:00]   Instance in stopping state, sleeping 15s...
[2019-01-18 11:00:16]   Instance in stopping state, sleeping 15s...
[2019-01-18 11:00:37] Creating AMI image...
[2019-01-18 11:00:38]   Build is in pending state, sleeping 15s...
[2019-01-18 11:00:54]   Build is in pending state, sleeping 15s...
[2019-01-18 11:01:09]   Build is in pending state, sleeping 15s...
[2019-01-18 11:01:25]   Build is in pending state, sleeping 15s...
[2019-01-18 11:01:41]   Build is in pending state, sleeping 15s...
[2019-01-18 11:01:57]   Build is in pending state, sleeping 15s...
[2019-01-18 11:02:13]   Build is in pending state, sleeping 15s...
[2019-01-18 11:02:33] Tagging with build version...
[2019-01-18 11:02:34] Terminating source image...
[2019-01-18 11:02:35] Build complete.

Returning to session creation.

</pre>
Once the build completes, we return to creating the new session. You will notice one of the questions below is about encryption. Output data is stored on S3 for later download when processes finish. This data can be encrypted with gocryptfs, that way if it is stored for a long period of time it is more secure. For the `Hello World` plugin, data is syncronized to S3 every 15 seconds. For other plugins, the reocmmendation is every `300` seconds.
<pre>

Would you like to run the instance On-Demand or as a Spot Instance? [o/S]: <i><b>s</b></i>
Instances:
-------------------------------------------
 1) 1 vCPU, 1GB RAM     [t2.micro]
 2) 1 vCPU, 2GB RAM     [t2.small]
-------------------------------------------
Please select an instance: <i><b>1</b></i>

Pricing:
--------------  ----------      ----------      ----------      ------------
Zone            Average         Latest          On Demand       Reccomended
--------------  ----------      ----------      ----------      ------------
1) us-east-1c   $0.003500       $0.003500       $0.011600       $0.004025 (best)
2) us-east-1f   $0.003500       $0.003500       $0.011600       $0.004025
3) us-east-1b   $0.003500       $0.003500       $0.011600       $0.004025
4) us-east-1a   $0.003500       $0.003500       $0.011600       $0.004025
5) us-east-1e   $0.003500       $0.003500       $0.011600       $0.004025
6) us-east-1d   $0.003500       $0.003500       $0.011600       $0.004025
--------------  ----------      ----------      ----------      ------------
(The default is 15% over the average past two week spot price to keep your instance active.)

Which zone would you like to run in? <i><b>1</b></i>
What is the max price you would pay for a spot instance? [0.004025]: 
What would you like to call this instance? <i><b>Testing</b></i>
How many seconds would you like to wait between printing 'hello world'? [10]: <i><b>10</b></i>
Enter a password for gocryptfs encrypted output (leave blank for no encryption): 
Session Testing created.

Sessions:
-------------------------------------------
 1) Testing
 c) Create
 q) Quit
-------------------------------------------
Select session: 
</pre>
Now you have the session `Testing` available. Next, we will start up an instance running the `Hello World` plugin.
<pre>
Sessions:
-------------------------------------------
 1) Testing
 c) Create
 q) Quit
-------------------------------------------
Select session: <i><b>1</b></i>

Testing:
-------------------------------------------
 1) Start
 2) Output
 s) Show variables
 d) Delete
 b) Back
-------------------------------------------
Choose an option: <i><b>1</b></i>

[2019-01-18 11:06:27] Getting subnet...
[2019-01-18 11:06:28]   Using subnet subnet-0bea6a005f7f8dbed.
[2019-01-18 11:06:28] Checking VPC...
[2019-01-18 11:06:29]   Using VPC vpc-02d8172ca01a496de.
[2019-01-18 11:06:29] Checking security group...
[2019-01-18 11:06:30]   Found existing security group.
[2019-01-18 11:06:30]   Using security group sg-019fedf5084f3e068.
[2019-01-18 11:06:31] Waiting on spot id sir-9jcg74mg...
[2019-01-18 11:06:31]   Spot request in open state, sleeping 15s...
[2019-01-18 11:07:03]   Instance in running state.
[2019-01-18 11:07:04] Instance has public IP of 54.88.86.34.
[2019-01-18 11:07:04] Checking for SSH connectivity...
[2019-01-18 11:07:07]   Waiting for SSH to start, sleeping 15s...
[2019-01-18 11:07:25] Uploading cloudstomp AWS credentials...
[2019-01-18 11:07:26] Uploading any supporting files...
[2019-01-18 11:07:26]   Complete.
[2019-01-18 11:07:26] Starting init script...
[2019-01-18 11:07:26]   Running remote.sh...
[2019-01-18 11:07:27]     Uploaded.
[2019-01-18 11:07:33] Launch complete.

Testing:
-------------------------------------------
 1) Status
 2) Connect
 3) Stop
 4) Output
 s) Show variables
 d) Delete
 b) Back
-------------------------------------------
Choose an option: 
</pre>
Now we can check on the status of our instance, connect to it and attach to the `screen` session, stop the instance, or show the outputs from S3. Outputs are available even after the instance is stopped.
<pre>
Testing:
-------------------------------------------
 1) Status
 2) Connect
 3) Stop
 4) Output
 s) Show variables
 d) Delete
 b) Back
-------------------------------------------
Choose an option: <i><b>1</b></i>
[2019-01-18 11:09:59] Instance has public IP of 54.88.86.34.
[2019-01-18 11:09:59] Checking for SSH connectivity...
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Testing:
-------------------------------------------
 1) Status
 2) Connect
 3) Stop
 4) Output
 s) Show variables
 d) Delete
 b) Back
-------------------------------------------
Choose an option: <i><b>3</b></i>
[2019-01-18 11:10:28] Instance has public IP of 54.88.86.34.
[2019-01-18 11:10:28] Checking for SSH connectivity...
There is no screen to be resumed matching helloworld.
There is no screen to be resumed matching sync.
upload: cloudstomp/plain/output.txt to s3://cloudstomp-testing/output.txt
upload: cloudstomp/plain/sync.txt to s3://cloudstomp-testing/sync.txt
Connection to 54.88.86.34 closed.

Sessions:
-------------------------------------------
 1) Testing     [shutting-down]
 c) Create
 q) Quit
-------------------------------------------
Select session: <i><b>1</b></i>

Testing:
-------------------------------------------
 1) Output
 s) Show variables
 d) Delete
 b) Back
-------------------------------------------
Choose an option: <i><b>1</b></i>

download: s3://cloudstomp-testing/output.txt to ../../../tmp/cloudstomp-testing/plain/output.txt
download: s3://cloudstomp-testing/sync.txt to ../../../tmp/cloudstomp-testing/plain/sync.txt
Starting hello world...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
Hello world!
Sleeping 10 seconds...
^C
-------------------------------------------

Testing:
-------------------------------------------
 1) Output
 s) Show variables
 d) Delete
 b) Back
-------------------------------------------
Choose an option: 
</pre>

Many of these options can also be executed from the command line (check with `cloudstomp.py --help`) for automation.

