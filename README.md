### 起因
由于aws codedeploy Jenkins：https://github.com/awslabs/aws-codedeploy-plugin 没有CN-NORTHWEST-1 region，则自定义codedeployment.py 发版脚本。简陋版，能用即可。

### 流程

- Jenkins 定义变量；
- 打包zip压缩到S3 上传（根据Jenkins 定义的版本号变量命名）；
- 上传到响应目录调用Codedeploy Json实现蓝绿部署。（其他部署自行更改脚本）

#### 前提准备（蓝绿部署为例）
- 定义好appspec.yml 以及deploy脚本 在代码仓库里封装
- Jenkins使用version number 插件，响应Key如下：

>Envoroment Variable Name：BUILD_VERSION
Version Number Format String：${BUILD_DATE_FORMATTED,"yyyy-MM-dd"}_${BUILDS_TODAY,XX}
Skip Builds worse than：SUCCESS
Build Dispaly Name：√

##### Jenkins变量定义
```
HOME=`pwd`

export OLD_FILE_NAME_ENV='crm'
export FILE_NAME_ENV=${OLD_FILE_NAME_ENV}_${BUILD_VERSION}.zip
export FILE_PATH_ENV="${HOME}/"
export BUCKET_NAME_ENV='jenkins-project-depolyment'
export PREFIX_ENV=crmpower-prod/${OLD_FILE_NAME_ENV}

export APPNAME_ENV='CRM_PROD'
export DEPLOYNAME_ENV=$OLD_FILE_NAME_ENV

rm -f *.zip
zip -r $FILE_NAME_ENV ./*

#运行程序
/data/tool/codedeploy.py
```

>HOME：获取当前Jenkins需要打包上传的目录  
OLD_FILE_NAME_ENV：项目名  
FILE_NAME_ENV：项目包  
FILE_PATH_ENV：项目目录  
BUCKET_NAME_ENV：S3存储桶  
PREFIX_ENV：S3存储桶前缀  
APPNAME_ENV：Codedeploy 应用程序名  
DEPLOYNAME_ENV：Codedeploy部署组名
