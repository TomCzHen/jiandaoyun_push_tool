## 说明

## 运行环境

需要手动安装客户端连接驱动，请参考官方文档进行安装。

[ODPI-C Installation](https://oracle.github.io/odpi/doc/installation.html)

## 配置数据库

注意：根据需要修改名称，配置文件中名字保持一致

```sql
/* Creating a message type: */
CREATE TYPE JDY_PUSH_MSG AS object ( payload  CLOB );

/* Creating a object type queue table and queue: */
BEGIN
    DBMS_AQADM.CREATE_QUEUE_TABLE(
        queue_table =>'JDY_PUSH_MSG_Q_TB',
        queue_payload_type  => 'JDY_PUSH_MSG'
    );
    DBMS_AQADM.CREATE_QUEUE(
        queue_name => 'JDY_PUSH_MSG_Q',
        queue_table => 'JDY_PUSH_MSG_Q_TB',
        max_retries => 65535
    );
    DBMS_AQADM.START_QUEUE(
        queue_name => 'JDY_PUSH_MSG_Q'
    );
END;
```

## 测试

使用之前可以先通过 SQL 语句来验证数据库队列功能是否正常。

### 发送消息到队列

```sql
/* Enqueue to jdy_push_msg_queue: */
DECLARE
  enqueue_options    DBMS_AQ.enqueue_options_t;
  message_properties DBMS_AQ.message_properties_t;
  message_handle     RAW(16);
  message            JDY_PUSH_MSG;

BEGIN
  message := JDY_PUSH_MSG(
    'test message',
  );

  DBMS_AQ.enqueue(
    queue_name          => 'JDY_PUSH_MSG_Q',
    enqueue_options     => enqueue_options,
    message_properties  => message_properties,
    payload             => message,
    msgid               => message_handle
    );

  COMMIT;
END;
```

### 从队列接收消息

```sql
/* Dequeue from jdy_push_msg_queue: */
DECLARE
   dequeue_options     DBMS_AQ.dequeue_options_t;
   message_properties  DBMS_AQ.message_properties_t;
   message_handle      RAW(16);
   message             JDY_PUSH_MSG;

BEGIN
  DBMS_AQ.DEQUEUE(
    queue_name          => 'JDY_PUSH_MSG_Q',
    dequeue_options     => dequeue_options,
    message_properties  => message_properties,
    payload             => message,
    msgid               => message_handle
    );

  DBMS_OUTPUT.PUT_LINE ('Message: ' || message.PAYLOAD );
  COMMIT;
END;
```

### 使用测试用例

执行 `test_oracleQueue.py` 测试用例代码，可以验证代码是否正常。