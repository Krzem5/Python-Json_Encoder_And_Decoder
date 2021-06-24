import re



JSON_STRING_ESCAPE_CHAR_REGEX=re.compile(r'([\\"]|[^\x20-\x7e])')
JSON_STRING_ESCAPE_CHAR_BYTES_REGEX=re.compile(br'([\\"]|[^\x20-\x7e])')



def _encode_json_str(m):
	c=ord(m.group(0))
	if (c<0x10000):
		return f"\\u{c:04x}"
	c-=0x10000
	return f"\\u{0xd800|((c>>10)&0x3ff):04x}\\u{0xdc00|(c&0x3ff):04x}"



def _encode_json_str_bytes(m):
	c=ord(m.group(0))
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



def _decode_json_str(e):
	i=0
	o=""
	while (e[i:i+1]!=b"\""):
		if (e[i:i+1]!=b"\\"):
			o+=chr(e[i])
		else:
			i+=1
			c=e[i:i+1]
			if (c in [b"\\'\""]):
				o+=chr(e[i])
			elif (c==b"b"):
				o+="\b"
			elif (c==b"f"):
				o+="\f"
			elif (c==b"n"):
				o+="\n"
			elif (c==b"r"):
				o+="\r"
			elif (c==b"t"):
				o+="\t"
			elif (c==b"v"):
				o+="\v"
			elif (c==b"x"):
				v=0
				i+=1
				for _ in range(0,2):
					v=v*16+(e[i]-48 if e[i]>47 and e[i]<58 else (e[i]-55 if e[i]>64 and e[i]<71 else e[i]-87))
					i+=1
				o+=chr(v)
				continue
			elif (c==b"u"):
				v=0
				i+=1
				for _ in range(0,4):
					v=v*16+(e[i]-48 if e[i]>47 and e[i]<58 else (e[i]-55 if e[i]>64 and e[i]<71 else e[i]-87))
					i+=1
				o+=chr(v)
				continue
			else:
				v=0
				while (e[i]>47 and e[i]<56):
					v=v*8+(e[i]-48)
					i+=1
				o+=chr(v)
				continue
		i+=1
	return (o,i)



def decode_json(e):
	if (e[:1]==b"{"):
		o={}
		i=1
		while (e[i:i+1]!=b"}"):
			while (e[i-1:i]!=b"\""):
				i+=1
			k,j=_decode_json_str(e[i:])
			i+=j+1
			while (e[i-1:i]!=b":"):
				i+=1
			v,j=decode_json(e[i:])
			o[k]=v
			i+=j
			while (e[i-1:i]!=b","):
				if (e[i:i+1]==b"}"):
					break
				i+=1
		return (o,i)
	if (e[:1]==b"["):
		o=[]
		i=1
		while (e[i:i+1]!=b"]"):
			k,j=decode_json(e[i:])
			i+=j
			o.append(k)
			while (e[i-1:i]!=b","):
				if (e[i:i+1]==b"]"):
					break
				i+=1
		return (o,i)
	if (e[:1]==b"\"" or e[:1]==b"'"):
		o,i=_decode_json_str(e[1:])
		return (o,i+1)
	if (e[:4]==b"true"):
		return (True,4)
	if (e[:5]==b"false"):
		return (False,5)
	if (e[:4]==b"null"):
		return (None,4)
	s=1
	i=0
	if (e[:1]==b"-"):
		s=-1
		i=1
	o=0
	while (e[i]>47 and e[i]<58):
		o=o*10+(e[i]-48)
		i+=1
	if (e[i:i+1]==b"."):
		pw=0.1
		i+=1
		while (e[i]>47 and e[i]<58):
			o+=pw*(e[i]-48)
			pw*=0.1
			i+=1
		if (e[i:i+1]==b"e"):
			i+=1
			pw_s=1
			if (e[i:i+1]==b"-"):
				pw_s=-1
				i+=1
			pw=0
			while (e[i]>47 and e[i]<58):
				pw=pw*10+(e[i]-48)
				i+=1
			o*=pow(10,pw*pw_s)
	o*=s
	return (o,i-1)



dt={"key":["value",10,-842.9e-200,{"a":["c",30,"d€",b"\n\x01"],"other":"else"},True,False,None]}
print(encode_json(dt))
print(decode_json(encode_json(dt))[0],decode_json(b"[\"\\00044\"]"))
