import requests


r = requests.get('http://localhost:8000/api/algorithm/compress.zip')
print(r.status_code)
print(r.text)


"""
## gzip endpoint
## /api/algorithm/demo.zip

## auto decompress
r = request.get(url, params, compress=True)

# decompress auto
r.text 

"""
