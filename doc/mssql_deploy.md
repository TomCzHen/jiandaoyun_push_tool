## 说明

## 运行环境

* [Microsoft® ODBC Driver 17 for SQL Server®](https://www.microsoft.com/zh-CN/download/details.aspx?id=56567)

## 配置数据库

注意：根据需要修改名称，配置文件中名字保持一致

```sql
/* Enable Service Broker */
USE master
ALTER DATABASE YourDatabase
SET ENABLE_BROKER; 

/* Creating a message type: */
USE YourDatabase
CREATE MESSAGE TYPE
[JDYPushMessage]
VALIDATION = NONE;

/* Creating a contract: */
CREATE CONTRACT [AnyContract]
([JDYPushMessage] SENT BY INITIATOR);
GO

/* Creating a message queue: */
CREATE QUEUE JDYPushMessageQueue WITH STATUS = ON,RETENTION = OFF,POISON_MESSAGE_HANDLING (STATUS = OFF);

/* Creating a service bind queue: */
CREATE SERVICE
[JDYPushService]
ON QUEUE JDYPushMessageQueue([AnyContract]);
```

## 测试

使用之前可以先通过 SQL 语句来验证数据库队列功能是否正常。

### 发送消息到队列
```sql
DECLARE @DlgHandle UNIQUEIDENTIFIER;
DECLARE @Message NVARCHAR(max);
SET  @Message = N'test message';

BEGIN DIALOG @DlgHandle
FROM SERVICE [JDYPushService]
  TO SERVICE N'JDYPushService', 'CURRENT DATABASE'
    ON CONTRACT [JDYPushMessageContract] WITH ENCRYPTION = OFF;

SEND ON CONVERSATION  @DlgHandle MESSAGE TYPE [JDYPushMessage]  ( @Message );
```

### 从队列接收消息

```sql
WAITFOR ( RECEIVE TOP(1) CONVERT(nvarchar(max),message_body) AS 'payload' FROM JDYPushQueue), TIMEOUT 0;
```

### 使用测试用例

执行 `test_mssqlQueue.py` 测试用例代码，可以验证代码是否正常。
