

# to get an EBRAINS token, go to lab.ebrains.eu, start a Jupyter notebook, and type:
#
# clb_oauth.get_token()
#
# copy and paste the token below \/

import os
from ebrains_drive import BucketApiClient

#client = BucketApiClient(token="<insert an EBRAINS token here>")
client = BucketApiClient(token="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJfNkZVSHFaSDNIRmVhS0pEZDhXcUx6LWFlZ3kzYXFodVNJZ1RXaTA1U2k0In0.eyJleHAiOjE2NzYyODA2OTEsImlhdCI6MTY3NTY3NTg5MSwiYXV0aF90aW1lIjoxNjc1MzI1MzAxLCJqdGkiOiIwMWU1NDlhNS03Nzk5LTQyODktOTdlYi02MWMzZThjMjUxMzAiLCJpc3MiOiJodHRwczovL2lhbS5lYnJhaW5zLmV1L2F1dGgvcmVhbG1zL2hicCIsImF1ZCI6WyJpbWdfc3ZjIiwidHV0b3JpYWxPaWRjQXBpIiwieHdpa2kiLCJqdXB5dGVyaHViLWpzYyIsInRlYW0iLCJwbHVzIiwiZ3JvdXAiXSwic3ViIjoiYzU0ODdjNWItYjVkNi00MWIxLWI1MDYtNzczYTA0YTc0ZDAzIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoianVweXRlcmh1YiIsInNlc3Npb25fc3RhdGUiOiIzMWU5NzM4ZC00NTA0LTQzMTMtYjA2MS01YjExMGJmOTM0ZGMiLCJhY3IiOiIwIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vanVweXRlcmh1Yi5hcHBzLmpzYy5oYnAuZXUvIiwiaHR0cHM6Ly9sYWIuZWJyYWlucy5ldS8iLCJodHRwczovL2xhYi5qc2MuZWJyYWlucy5ldS8iXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIl19LCJzY29wZSI6ImNvbGxhYi5kcml2ZSBwcm9maWxlIG9mZmxpbmVfYWNjZXNzIGNsYi53aWtpLndyaXRlIGdyb3VwIGNsYi53aWtpLnJlYWQgdGVhbSBxdW90YSBlbWFpbCByb2xlcyBvcGVuaWQiLCJzaWQiOiIzMWU5NzM4ZC00NTA0LTQzMTMtYjA2MS01YjExMGJmOTM0ZGMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZ2VuZGVyIjoiMCIsIm5hbWUiOiJBbmRyZXcgRGF2aXNvbiIsIm1pdHJlaWQtc3ViIjoiMjA3MTQ5IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWRhdmlzb24iLCJnaXZlbl9uYW1lIjoiQW5kcmV3IiwiZmFtaWx5X25hbWUiOiJEYXZpc29uIiwiZW1haWwiOiJhbmRyZXcuZGF2aXNvbkBjbnJzLmZyIn0.o-OQPKA4yhqwx5ng053V2DLjyUIaFeebg4EzJTUWn4SPmLUSk4XWM2-uvrOf76C2xH4sDx03HQXUpP88gaOYxugInrgcdRJQKmTxW8LXo-jbHUOMBuXncdmHBmreOtT9ZobA9EZ7pb93bubr6XVaszy8PvR3vx1I-7dP45QmqEyHS4D0fSeQyop7TJ-kzDG0W3KZ9pawJLbcgXoxiU4Eur59ITbMRlpQIi8WLOfev74QNbDQdXNlRiAXEx_WQAxWptEd48qCaLLhTPn4CereQWpb3Rxmc_Vq4J6gGBmoHM6FdwKD-uoqoG0q-BJa-XiuqrAKSJq3-MxbBtsF3FAIng")

# access existing bucket
#bucket = client.buckets.get_bucket("human-ca1-hippocampus")
bucket = client.buckets.get_bucket("myspace")

# upload new file
for (dirpath, dirnames, filenames) in os.walk("."):
    # this will upload all files in the current directory and below
    #print(dirpath, dirnames, filenames)
    for filename in filenames:
        local_path = os.path.join(dirpath, filename)
        #print(path)
        remote_path = local_path[2:]
        print(remote_path)
        bucket.upload(local_path, remote_path)
