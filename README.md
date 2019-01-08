# 简道云推送工具

* 解决什么问题？

在无法对现有应用进行二次开发的前提下，通过数据库队列功能，实现推送表单数据到简道云。

* 下载下来就能直接实现推送？

不能。

程序只是读取数据库内置消息队列后推送到简道云，队列消息的生成、写入需要通过数据库编程实现（存储过程、触发器）。数据库队列功能依赖数据库版本、安装选项、访问用户权限、是否开启等限制。

## 系统需求

* Oracle 数据库需要 [Oracle Advanced Queuing](https://docs.oracle.com/database/121/ADQUE/aq_intro.htm) 功能支持。
* SQL Server 数据库需要 [SQL Server Service Broker Queue](https://docs.microsoft.com/en-us/sql/database-engine/configure-windows/sql-server-service-broker) 功能支持。
* Python 3.6

## 配置数据库

因为开启数据库队列功能操作存在很多限制，程序无法保证自动完成配置操作，请参考对应文档以及官方文档进行配置。

* [Oracle](/doc/oracle_deploy.md)
* [SQL Server](/doc/mssql_deploy.md)

## 使用说明

通过 API 操作表单有以下限制：

* 表单创建人固定为组织名称
* 网页端支持的约束检查在 API 无效（例如：唯一、必填等）
* 部分表单控件 API 不支持

复制 `config.example.toml` 为 `config.toml`，查看配置文件注释进行配置。

* 守护进程运行

Windows 部署 SQL Server 推荐使用代理作业随代理启动，或者使用 [NSSM - the Non-Sucking Service Manager](https://nssm.cc/) 添加为系统服务运行。

```bash
python run.py --daemon
```

* 通讯同步

使用系统计划任务定时运行。

```bash
python run.py --sync
```

### 运行逻辑

1. 推送的表单数据按约定的格式，以队列消息方式插入数据库队列。
1. 程序读取队列消息，调用简道云 API 获取需要的表单结构信息，将字段转换为简道云 API 需要的格式结构。

### 表单组件支持

控件名称|控件类型|数据类型
:---:|:---:|:---:
单行文本|text|String
多行文本|textarea|String
数字|number|Number
日期时间|datetime|String
单选按钮组|radiogroup|String
复选框组|checkboxgroup|Array
下拉框|combo|String
下拉复选框|combocheck|Array
成员单选|user|Array
成员多选|usergroup|Array
部门单选|dept|Array
部门多选|deptgroup|Array
子表单|subform|Array

注意：不支持的控件类型数据会丢失，同名字段数据会丢失。

#### 日期组件

API 仅接受标准 RFC3339 日期格式的 UTC 时间，大多数传统行业数据库应用肯定不是 UTC 时间，加上服务端、应用端时区问题。

简单来说，虽然可以在代码中实现日期转换，但是由于各种各样的原因（数据库时区设置错误、客户端时区/时间格式、数据库存储类型等等）。进行标准转换后的时间可能并不是预期的时间，因此，转换的处理交给数据库编程处理。

请自行查阅相关资料，将日期转换为对应格式字符串。

#### 成员部门组件

API 只接收成员或部门的 `id`，需要使用同步通讯录功能，将成员部门信息同步到数据库，生成表单数据时自行匹配 `id`。如果 `id` 不存在，API 不会因此报错，即使该字段为必填也会留空。

#### 队列消息格式

```json
{
    "app_id":"app_id",
    "entry_id":"entry_id",
    "op":"create",
    "query_fields":[],
    "data":{},
    "is_start_workflow":false,
    "etag": "etag_string"
}
```

* `app_id` `entry_id`

对应简道云的表单 `app_id` 与 `entry_id`

* `op`

支持 `create|update|delete`，分别对应表单三种操作

* `query_fields`

提交表单数据操作请求时，通过该字段先查询匹配条件的表单数据

* `data` 

表单数据

* `is_start_workflow`

表示是否发起流程单，相关限制请查看简道云 API 文档，非必要键，默认为 `false`

* `etag`

版本标识，用于提醒程序更新表单组件缓存数据，任意字符串

注意：生成的字符串需要进行是否符合 JSON 格式校验，下面是一个消息例子：

```json
{
    "app_id":"app_id",
    "entry_id":"entry_id",
    "data":{
        "单行文本":"单行文本测试数据",
        "多行文本":"单行文本测试数据",
        "数字":123.12,
        "日期时间":"2017-12-08T00:00:00.00Z",
        "单选按钮组": "单选选项",
        "成员单选":"user_id",
        "成员多选":[
            "user_id_1",
            "user_id_2"
        ],
        "部门单选":"dept_id",
        "部门多选":[
            "dept_id_1",
            "dept_id_2"
        ],
        "子表单":[
            {
                "单行文本":"子表单单行文本1",
                "数字":123.12
            },
            {
                "单行文本":"子表单单行文本2",
                "数字":123.12
            }
        ]
    },
    "op":"create",
    "query_fields":[
        "单行文本"
    ],
    "is_start_workflow":false,
    "etag": "20190107"
}
```

#### 何时生成

根据实际情况可以使用以下两种方法实现：

1. 修改现有业务对应存储过程，在业务执行完毕，数据库事务提交前插入队列
2. 在对应数据表使用 AFTER INSERT 或 AFTER UPDATE 触发器

一些提醒:

1. 将生成消息封装为单独的函数或存储过程进行调用
1. 子表单数据很多时，生成消息所需的时间会增加事务耗时
1. 注意变量数据类型、数据库对象数据类型的最大长度，避免数据较大时产生异常或截断

#### 如何生成

如果数据库不支持 JSON 类型以及相关函数，那么只能使用字符串拼接的方式生成。

* Oracle

使用 `format_message` 函数可以减轻一些工作量

```sql
declare
  json_fmt_string     VARCHAR2(512) := '{"app_id":"%s","entry_id":"%s","op":"%s","query_fields":%s,"data":%s,"is_start_workflow":false}';
  json_string         VARCHAR2(2048);
  data_string         VARCHAR2(512) := '{"单行文本":"单行文本测试数据","数字":123.12,"日期时间":"2018-06-28"}';
  query_fields_string VARCHAR2(128) := '["单行文本"]';
begin
  json_string := utl_lms.format_message(json_fmt_string,'app_id','entry_id','create',query_fields_string,data_string);
  dbms_output.put_line(json_string);
end;
```

* SQL Server

SQL Server 2012 或以上版本可以使用 `FORMATMESSAGE` 函数来实现，详细用法查看官方文档[FORMATMESSAGE (Transact-SQL)](https://docs.microsoft.com/en-us/sql/t-sql/functions/formatmessage-transact-sql)。

### 技术支持

Bug 、问题请提交 issue。其他方式只提供有偿技术支持。

