# altershield-monitorCheck Quick Start「中文版」
## 服务部署
### 镜像构建&上传
#### 1、镜像构建
> 注意：
> 
> 1、首先保证本地安装有Docker
> 
> 2、需要在 altershield-monitorCheck 项目根目录中执行镜像构建命令

```shell
docker build -t batch_monitor_check:V1.0 .
```
#### 2、镜像上传
将构建好的镜像打好tag，上传至镜像仓库「保证该仓库镜像可以从K8S集群中拉取」即可。
```shell
docker tag localImage:tag ***.altershield.com/altershield/batch_monitor_check:V1.0
```
```shell
docker push ***.altershield.com/altershield/batch_monitor_check:V1.0
```
镜像地址为：***.altershield.com/altershield/batch_monitor_check:V1.0

### K8S 集群部署
首先，需要确定本地可以连接上K8S集群，执行以下命令可进行验证集群连通性。如果能成功连接，此命令将显示集群服务的基本信息。
```shell
kubectl cluster-info
```
接下来开始服务部署：
#### 1、修改 image 地址
修改 deployment 文件配置的镜像地址「deployment 使用 alter_shidle_batch_monitor/deployment.yaml」
```yaml
image: ***.altershield.com/altershield/batch_monitor_check:V1.0
```
#### 2、创建 deployment
```shell
kubectl apply -f ~/.alter_shidle_batch_monitor/deployment.yaml
```
#### 3、创建 svc
本地创建 bmc-svc.yaml 文件「可自行修改 svc 配置」
```yaml
apiVersion: v1
kind: Service
metadata:
  name: bmc-test-svc
  namespace: bmc-test
spec:
  ports:
  - port: 8083
    protocol: TCP
    targetPort: 8083
  selector:
    app: bmc-test-v3 # 这里需要绑定app
  type: ClusterIP
```
在集群中创建 svc
```shell
kubectl apply -f bmc-svc.yaml
```
查看 svc 是否创建，列表中包含bmc-test-svc表示创建成功 
```shell
kubectl get service
```
#### 4、服务更新
编辑 deployment 配置，触发自动更新
```shell
kubectl edit deployment bmc-test
```
可通过查看 Pod 状态，以及相关日志判断 Pod 启动是否成功，以及失败信息。
### Docker 容器部署
本地执行以下命令启动 docker 容器，部署成功后即可进行调试。
> 本机8080端口绑定容器8083端口
```shell
docker run -d -p 8080:8083 batch_monitor_check:V1.0
```
## 测试验证
### 本地测试
以本地Docker启动为例，Port=8083

Path: 
```json
/api/check/batch_monitor_detect
```
Body:
```json
{
    "app": "addata",
    "changeStart": 1675255200000,
    "changeEnd": 1675255260000,
    "period": 1675255620000,
    "bizAlgKargs": {
        "detectRouterType": "statisticMultiByAtomic"
    },
    "datasourceKargs": {
        "datasourceType": "mt",
        "isConverged": false
    },
    "isTest": true,
    "isPlot": false,
    "isPrint": false,
    "detect_series": {
        "keySeriesList": [
            {
                "dsId": "error@pod",
                "field": "count",
                "tagStr": "app$=$addata$&$pod$=$addata-42-22.et2.altershield.com",
                "series": {
                    "1675254120000": 0,
                    "1675254180000": 0,
                    "1675254240000": 0,
                    "1675254300000": 0,
                    "1675254360000": 0,
                    "1675254420000": 0,
                    "1675254480000": 0,
                    "1675254540000": 0,
                    "1675254600000": 0,
                    "1675254660000": 0,
                    "1675254720000": 0,
                    "1675254780000": 0,
                    "1675254840000": 0,
                    "1675254900000": 0,
                    "1675254960000": 0,
                    "1675255020000": 0,
                    "1675255080000": 0,
                    "1675255140000": 0,
                    "1675255200000": 0,
                    "1675255260000": 0,
                    "1675255320000": 0,
                    "1675255380000": 1,
                    "1675255440000": 10,
                    "1675255500000": 11,
                    "1675255560000": 12,
                    "1675255620000": 11
                }
            },
            {
                "dsId": "error@pod",
                "field": "count",
                "tagStr": "app$=$addata$&$pod$=$addata-40-8.em14.altershield.com",
                "series": {
                    "1675254120000": 0,
                    "1675254180000": 0,
                    "1675254240000": 0,
                    "1675254300000": 0,
                    "1675254360000": 0,
                    "1675254420000": 0,
                    "1675254480000": 0,
                    "1675254540000": 0,
                    "1675254600000": 0,
                    "1675254660000": 0,
                    "1675254720000": 0,
                    "1675254780000": 0,
                    "1675254840000": 0,
                    "1675254900000": 0,
                    "1675254960000": 0,
                    "1675255020000": 0,
                    "1675255080000": 0,
                    "1675255140000": 0,
                    "1675255200000": 0,
                    "1675255260000": 0,
                    "1675255320000": 0,
                    "1675255380000": 0,
                    "1675255440000": 0,
                    "1675255500000": 0,
                    "1675255560000": 0,
                    "1675255620000": 0
                }
            },
            {
                "dsId": "error@pod",
                "field": "count",
                "tagStr": "app$=$addata$&$pod$=$addata-42-123.et2.altershield.com",
                "series": {
                    "1675254120000": 0,
                    "1675254180000": 0,
                    "1675254240000": 0,
                    "1675254300000": 0,
                    "1675254360000": 0,
                    "1675254420000": 0,
                    "1675254480000": 0,
                    "1675254540000": 0,
                    "1675254600000": 0,
                    "1675254660000": 0,
                    "1675254720000": 0,
                    "1675254780000": 0,
                    "1675254840000": 0,
                    "1675254900000": 0,
                    "1675254960000": 0,
                    "1675255020000": 0,
                    "1675255080000": 0,
                    "1675255140000": 0,
                    "1675255200000": 0,
                    "1675255260000": 0,
                    "1675255320000": 0,
                    "1675255380000": 1,
                    "1675255440000": 10,
                    "1675255500000": 12,
                    "1675255560000": 11,
                    "1675255620000": 11
                }
            }
        ]
    }
}
```
Response:「其中 verdict=Fail 表示校验不通过」
```json
{
    "code": 200,
    "data": {
        "algorithmMessage": "1、inscommunitybff 应用的指标 servicePod-fail 从变更前 0.25 上涨到变更后 1.60 - [详细信息：app=inscommunitybff; pod=inscommunitybff-42-22.et2.altershield.com]; \n",
        "costTime": 1.6063780784606934,
        "resultCode": 0,
        "rootCauseMsg": "",
        "verdict": "FAIL"
    },
    "message": "success",
    "timeout": "2.154"
}
```
### 集群测试「Curl」
AlterShield 主端和「智能分批监控校验」服务是独立部署，通过集群内「ClusterIp」服务调用完成时序异常校验，所以如果想在集群内验证算法服务和连通性，需要在集群容器内操作。
「前提：AlterShield、BatchMonitorCheck 服务均成功部署在同一集群」随便进入一个 AlterShield 容器，执行以下curl命令：「需要更换 IP 为 BatchMonitorCheck Service 的 Cluster IP，获取方式见后续补充」
```shell
curl --location --request POST 'http://***.***.***.***:8083/api/check/batch_monitor_detect' \
--header 'Content-Type: application/json' \
--data '{
    "app": "addata",
    "changeStart": 1675255200000,
    "changeEnd": 1675255260000,
    "period": 1675255620000,
    "bizAlgKargs": {
        "detectRouterType": "statisticMultiByAtomic"
    },
    "datasourceKargs": {
        "datasourceType": "mt",
        "isConverged": false
    },
    "isTest": true,
    "isPlot": false,
    "isPrint": false,
    "detect_series": {
        "keySeriesList": [
            {
                "dsId": "error@pod",
                "field": "count",
                "tagStr": "app$=$addata$&$pod$=$addata-42-22.et2.altershield.com",
                "series": {
                    "1675254120000": 0,
                    "1675254180000": 0,
                    "1675254240000": 0,
                    "1675254300000": 0,
                    "1675254360000": 0,
                    "1675254420000": 0,
                    "1675254480000": 0,
                    "1675254540000": 0,
                    "1675254600000": 0,
                    "1675254660000": 0,
                    "1675254720000": 0,
                    "1675254780000": 0,
                    "1675254840000": 0,
                    "1675254900000": 0,
                    "1675254960000": 0,
                    "1675255020000": 0,
                    "1675255080000": 0,
                    "1675255140000": 0,
                    "1675255200000": 0,
                    "1675255260000": 0,
                    "1675255320000": 0,
                    "1675255380000": 1,
                    "1675255440000": 10,
                    "1675255500000": 11,
                    "1675255560000": 12,
                    "1675255620000": 11
                }
            },
            {
                "dsId": "error@pod",
                "field": "count",
                "tagStr": "app$=$addata$&$pod$=$addata-40-8.em14.altershield.com",
                "series": {
                    "1675254120000": 0,
                    "1675254180000": 0,
                    "1675254240000": 0,
                    "1675254300000": 0,
                    "1675254360000": 0,
                    "1675254420000": 0,
                    "1675254480000": 0,
                    "1675254540000": 0,
                    "1675254600000": 0,
                    "1675254660000": 0,
                    "1675254720000": 0,
                    "1675254780000": 0,
                    "1675254840000": 0,
                    "1675254900000": 0,
                    "1675254960000": 0,
                    "1675255020000": 0,
                    "1675255080000": 0,
                    "1675255140000": 0,
                    "1675255200000": 0,
                    "1675255260000": 0,
                    "1675255320000": 0,
                    "1675255380000": 0,
                    "1675255440000": 0,
                    "1675255500000": 0,
                    "1675255560000": 0,
                    "1675255620000": 0
                }
            },
            {
                "dsId": "error@pod",
                "field": "count",
                "tagStr": "app$=$addata$&$pod$=$addata-42-123.et2.altershield.com",
                "series": {
                    "1675254120000": 0,
                    "1675254180000": 0,
                    "1675254240000": 0,
                    "1675254300000": 0,
                    "1675254360000": 0,
                    "1675254420000": 0,
                    "1675254480000": 0,
                    "1675254540000": 0,
                    "1675254600000": 0,
                    "1675254660000": 0,
                    "1675254720000": 0,
                    "1675254780000": 0,
                    "1675254840000": 0,
                    "1675254900000": 0,
                    "1675254960000": 0,
                    "1675255020000": 0,
                    "1675255080000": 0,
                    "1675255140000": 0,
                    "1675255200000": 0,
                    "1675255260000": 0,
                    "1675255320000": 0,
                    "1675255380000": 1,
                    "1675255440000": 10,
                    "1675255500000": 12,
                    "1675255560000": 11,
                    "1675255620000": 11
                }
            }
        ]
    }
}'
```

Cluster IP 获取方式：
```shell
kubectl get service
```
可在列表中查看对应服务的 Cluster IP

<!-- LICENSE -->
## 开源许可

根据Apache2.0许可证分发。更多信息请查看 LICENSE。




<!-- CONTACT -->
## Contact
- 邮箱地址: traas_stack@antgroup.com / altershield.io@gmail.com
- 钉钉群 [二维码](./docs/dingtalk.png)
- 微信公众号 [二维码](./docs/wechat.jpg)
- <a href="https://altershield.slack.com/"><img src="https://img.shields.io/badge/slack-AlterShield-0abd59?logo=slack" alt="slack" /></a>
