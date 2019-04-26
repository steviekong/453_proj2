import hashlib
def checksum(msg):
   return hashlib.sha256(msg).hexdigest()


print(checksum(b'The Project Gutenberg EBo'))