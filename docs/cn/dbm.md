
# dbm动态穿透路由 Since v2.2.8
从v2.2.8开始，ab新增dbm机制，通过少量配置即可自动生成增删改查数据库中表内容的route。以template表为例：

template表结构：
```
CREATE TABLE `template` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT '',
  `data` longtext,
  `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP,
  `gmt_modified` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `gmt_run` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
```

配置方法如下：
```

DBM = [
    {'table_name': 'template',   # 想要暴露的表名
     'json_columns': 'data',     # 哪些字段是json格式，需要自动dump/load
     'list_columns': 'id,name,gmt_create,gmt_modified,gmt_run'  # 哪些字段需要在列表中显示。有些字段比如data或者二进制列比较大，不想在列表中返回
     'detail_columns': 'id,remark,pk_name', # 哪些字段需要在根据id查询详情的时候返回。有些字段如二进制数据是无法显示在json中的，可以用此字段控制。默认为'*'
     # 更多配置见config.py里说明，此处从略
     },
]
```

则会自动增加以下route:
### GET /api/table/template
根据条件分页读取表，返回list_columns里的字段

query string:
* page: 页码
* size: 每页条数
* 其它条件作为搜索条件

例：
```
GET /api/table/template?page=1&size=10&name=test
等价于执行 SELECT id,name,gmt_create,gmt_modified,gmt_run from template where name='test' limit 0, 10

GET /api/table/template?page=1&size=10&name:ne=test
等价于执行 SELECT id,name,gmt_create,gmt_modified,gmt_run from template where name != 'test' limit 0, 10

GET /api/table/template?page=1&size=10&name:contains=test
等价于执行 SELECT id,name,gmt_create,gmt_modified,gmt_run from template where name like '%test%' limit 0, 10

返回：
{
    code: 0,
    count: xx, // 总条数，用于分页
    data: [
        {
            id: 2,
            name: "test",
            gmt_create: "2019-09-18 11:32:38.000",
            gmt_modified: null,
            gmt_run: null
        }
    ]
}
```

### GET /api/table/template/2
根据id读取单条记录，返回该条记录的所有字段

例：
```
GET /api/table/template/2
等价于执行 SELECT id,name,gmt_create,gmt_modified,gmt_run from template where id = 2

返回：
{
    code: 0,
    data: {
            id: 2,
            name: "test",
            data: [],
            gmt_create: "2019-09-18 11:32:38.000",
            gmt_modified: null,
            gmt_run: null
        }
}
```

### POST /api/table/template
插入一条记录

request body:
```
{
    name: "test",
    data: []
    // 所有表中的字段都可以插入，从略
}
```

返回：
```
{
    code: 0,
    data: 3  # 新插入记录的id
}
```

### PUT /api/table/template/3
根据id更新一条记录

request body:
```
{
    name: "test",
    data: []
    // 所有表中的字段都可以更新，从略
}
```

返回：
```
{
    code: 0,
}
```

### DELETE /api/table/template/3
删除一条记录
返回：
```
{
    code: 0,
}
```
