# algorithm-base框架上传文件demo

## java调用demo接口示例
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("multipart/form-data; boundary=--------------------------994702659308423812684350");
RequestBody body = new MultipartBody.Builder().setType(MultipartBody.FORM)
  .addFormDataPart("more_args", "777")
  .addFormDataPart("the_uploaded_file","f.txt",
    RequestBody.create(MediaType.parse("application/octet-stream"),
    new File("/private/tmp/f.txt")))
  .build();
Request request = new Request.Builder()
  .url("localhost:2333/api/algorithm/demo")
  .method("POST", body)
  .addHeader("Content-Type", "multipart/form-data; boundary=--------------------------994702659308423812684350")
  .build();
Response response = client.newCall(request).execute();
```

## curl调用demo接口示例
```
curl --location --request POST 'localhost:2333/api/algorithm/demo' \
--header 'Content-Type: multipart/form-data; boundary=--------------------------994702659308423812684350' \
--form 'more_args=777' \
--form 'the_uploaded_file=@/private/tmp/f.txt'
```
