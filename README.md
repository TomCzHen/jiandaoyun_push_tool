## 系统需求

* Oracle 数据库需要 [Oracle Advanced Queuing](https://docs.oracle.com/database/121/ADQUE/aq_intro.htm) 功能支持。
* SQL Server 数据库需要 [SQL Server Service Broker Queue](https://docs.microsoft.com/en-us/sql/database-engine/configure-windows/sql-server-service-broker) 功能支持。
* Python 3.6

## 配置数据库

* [Oracle]()
* [SQL Server]()

## 使用说明


### 运行逻辑

1. 推送的表单数据按约定的格式，以队列消息方式插入数据库队列。
1. 读取队列消息后，调用简道云 API 获取需要的表单结构信息，将字段转换为简道云 API 需要的 `widget_xxxx`，将结构转换为简道云 API 需要的结构。

### 队列消息

#### 格式要求

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

* `app_id`/`entry_id`

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

版本标识，用于提醒程序更新表单组件缓存数据

注意：生成的字符串需要进行是否符合 JSON 格式校验，下面是一个消息例子：

```json
{
    "app_id":"app_id",
    "entry_id":"entry_id",
    "data":{
        "单行文本":"单行文本测试数据",
        "数字":123.12,
        "日期时间":"2018-06-28",
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

如果数据库不支持 JSON 类型以及相关函数，那么只能使用字符串拼接的方式。

* Oracle

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