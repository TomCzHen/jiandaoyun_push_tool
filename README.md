## 使用说明

### 注意事项

* Oracle 数据库需要 [Oracle Advanced Queuing](https://docs.oracle.com/database/121/ADQUE/aq_intro.htm) 功能支持。
* SQL Server 数据库需要 [SQL Server Service Broker Queue](https://docs.microsoft.com/en-us/sql/database-engine/configure-windows/sql-server-service-broker) 功能支持。
* Python 3.6


复制 `config.examle.toml` 为 `config.toml`，修改需要的配置项。


### Payload 格式

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

* 'op'

支持 `create|update|delete`，分别对应表单三种操作

* `query_fields`

提交表单数据操作请求时，通过该字段先查询匹配条件的表单数据

* `data` 

表单数据

* `is_start_workflow`

表示是否发起流程单，相关限制请查看简道云 API 文档，非必要键，默认为 `false`

* `etag`

版本标识，用于提醒程序更新表单组件缓存数据

#### Example


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

###