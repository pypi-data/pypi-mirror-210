# lazynovel
![](https://img.shields.io/badge/Python-3.8.6-green.svg)


#### 介绍
对接小说分销平台的接口封装方法，方便调用

支持列表：
- 常读（番茄）: open_changdu
- 迈步书城（开放平台接口）: open_mbookcn
- 迈步书城（非开放平台接口）: crawler_mbookcn
- 阅文: open_yuewen
- 网易文鼎: open_reading163
- 点众分销平台: open_dianzhong（已升级为https协议）

#### 软件架构
软件架构说明

- open_yuewen
```text
阅文开放平台
coop_id：合作方式代码
    1：微信分销
    9：陌香快应用（共享包）
    11：快应用（独立包）
```


#### 安装教程

1.  pip安装
```shell script
pip3 install lazynovel
```

2.  pip安装（使用阿里镜像加速）
```shell script
pip3 install lazynovel -i https://mirrors.aliyun.com/pypi/simple
```


#### 使用说明


#### changelog
1.  2022-08-01 changdu模块更名为open_changdu，原模块不再维护
