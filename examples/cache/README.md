## 要求
* ab >= v2.6.3
* config.REDIS

## curl调用例子
```
curl --location --request POST 'localhost:2333/api/algorithm/save' \
--header 'Content-Type: application/json' \
--data-raw '{
	"args": {"val": 2}
}'
```
