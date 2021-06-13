import re



JSON_STRING_ESCAPE_CHAR_REGEX=re.compile(r'([\\"]|[^\x20-\x7e])')
JSON_STRING_ESCAPE_CHAR_BYTES_REGEX=re.compile(br'([\\"]|[^\x20-\x7e])')



def _encode_json_str(m):
	c=ord(m.group(0))
	if (c<256):
		return f"\\x{c:02x}"
	if (c<0x10000):
		return f"\\u{c:04x}"
	c-=0x10000
	return f"\\u{0xd800|((c>>10)&0x3ff):04x}\\u{0xdc00|(c&0x3ff):04x}"



def _encode_json_str_bytes(m):
	c=ord(m.group(0))
	if (c<256):
		return bytes(f"\\x{c:02x}","utf-8")
	if (c<0x10000):
		return bytes(f"\\u{c:04x}","utf-8")
	c-=0x10000
	return bytes(f"\\u{0xd800|((c>>10)&0x3ff):04x}\\u{0xdc00|(c&0x3ff):04x}","utf-8")



def encode_json(e):
	if (type(e)==dict):
		return b"{"+b",".join([b"\""+(bytes(JSON_STRING_ESCAPE_CHAR_REGEX.sub(_encode_json_str,k),"utf-8") if type(k)==str else JSON_STRING_ESCAPE_CHAR_BYTES_REGEX.sub(_encode_json_str_bytes,k))+b"\":"+encode_json(v) for k,v in e.items()])+b"}"
	elif (type(e)==list or type(e)==tuple):
		return b"["+b",".join([encode_json(k) for k in e])+b"]"
	elif (type(e)==str):
		return b"\""+bytes(JSON_STRING_ESCAPE_CHAR_REGEX.sub(_encode_json_str,e),"utf-8")+b"\""
	elif (type(e)==bytes):
		return b"\""+JSON_STRING_ESCAPE_CHAR_BYTES_REGEX.sub(_encode_json_str_bytes,e)+b"\""
	elif (type(e)==int or type(e)==float):
		return bytes(str(e),"utf-8")
	elif (e is True):
		return b"true"
	elif (e is False):
		return b"false"
	elif (e is None):
		return b"null"
	else:
		raise RuntimeError(f"Unable to Serialize Type '{e.__class__.__name__}'")



def decode_json(e):
	raise RuntimeError("Unimplemented")



dt={"key":["value",10,-842.9e200,{"a":["c",30,"d☼",b"\n\x01"]},True,False,None]}
print(encode_json(dt),decode_json(encode_json(dt)))
