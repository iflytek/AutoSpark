# AutoSpark支持docker化插件设计


## 概述

当前插件仅支持Python形式的Github仓库，需要开发者开发python代码，明确python代码依赖，然后在Autospark/SuperAGI启动过程中注册进系统

缺点:

* 插件缺乏实时性，需要动态注册
* 插件比较局限仅支持github 以及python

## Docker化插件思路

* 前端注册插件时，提供注册Docker形式插件， 需要用户提供如下信息
    - Docker Image (初步定义为公有的镜像，暂不计划支持需要认证的镜像源)
    - 支持的命令列表以及对应的参数列表，每个命令，以及命令的每个参数需要用户提供明确的 Description描述
