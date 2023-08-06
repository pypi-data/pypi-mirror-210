# 介绍
```
默认会读取 以下 jenkins的环境变量
export JOB_NAME="test/test"
export JOB_BASE_NAME="test"
export BUILD_NUMBER="1"
export BUILD_URL="BUILD_URL"
export JENKINS_URL="JENKINS_URL"
export GIT_BRANCH="master"
export GIT_COMMIT="21a6fdgd"   
export BUILD_TAGS="debug,pref,pr,ngintly"  # 任意标签

python3 ./v2/sdk/run.py {func name} {params}
```

# 函数
## v2_add_pref_result

```
上传性能数据

python3 ./v2/sdk/run.py v2_add_pref_result  path/pref.txt

cat /path/pref.txt
>>
rn50_accu_accuracy:75.244
rn50_perf_performance:22331.52
rn50_perf_mean_latency:888937482721
bert_accu_accuracy:90.8876698049583
bert_perf_performance:2229.96
bert_perf_mean_latency:307503377511
```

```
上传pr, pr job数据

python3 ./v2/sdk/run.py v2_add_Merge_Request  path/pr.json
python3 ./v2/sdk/run.py v2_add_Merge_Request_job  path/pr_job.json

cat /path/pr.json
>>
{"pullRequestName" : "prname2", "component" : "brcc", "pullRequestNumber" : "100001"}

cat /path/pr_job.json
>>
{"component" : "brcc", "jobID" : "10001", "pullRequestCreatedBy" : "e00123", "jobId" : "http://", "pullLink" : "http://123"}
```


pdu 功能

```
install chrome 
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb 

查看chrome 版本 下载对应 chromedriver
http://chromedriver.storage.googleapis.com/index.html 

install chromedriver
wget http://chromedriver.storage.googleapis.com/105.0.5195.19/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver
sudo mv chromedriver /usr/local/share/chromedriver
```

# pypi打包
[aaa](https://blog.csdn.net/yifengchaoran/article/details/113447773)
python3 -m pip install  --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel
# pypi上传
python3 -m pip install --user --upgrade twine
python3 -m twine upload dist/*

