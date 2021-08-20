import dropbox
import json

ACCESS_TOKEN = 'ANsvqyLFWTgAAAAAAAAAAUoZeBSPTLOClyhncM7zK7ZmHofXpJb8qMAPqvmqMz52'
dbx = dropbox.Dropbox(ACCESS_TOKEN)

token = open("token.json", "r")
token = json.dumps(json.load(token))

data = dbx.files_upload(token.encode(), "/token.json", mode=dropbox.files.WriteMode.overwrite)
print(data)