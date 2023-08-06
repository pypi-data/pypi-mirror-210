def bin2hex(v):
	decimal = int(v)
	tmp = hex(decimal)
	return tmp

def hex2bin(v):
	decimal = int(v)
	tmp = bin(decimal)
	return tmp
	
#----------------------------------------------------------------------------------

def trim(v, chr = ''):
	v = str(v)
	if chr == '':
		return v.strip()
	else:
		return v.strip(chr)

def ltrim(v, chr = ''):
	v = str(v)
	if chr == '':
		return v.lstrip()
	else:
		return v.lstrip(chr)
	
def rtrim(v, chr = ''):
	v = str(v)
	if chr == '':
		return v.rstrip()
	else:
		return v.rstrip(chr)
	
#----------------------------------------------------------------------------------
def chunk_split(v, len):
	tmp = []
	arr = strcut(v, len)	
	if arr[1] == None:
		tmp.append(arr[0])
	else:
		tmp.append(arr[0])
		tmp.extend(chunk_split(arr[1], len))
	
	return tmp
#----------------------------------------------------------------------------------
def strlen(v):
	return len(v)
#----------------------------------------------------------------------------------
def strcut(v, len):
	length = strlen(v)
	if length > len:
		return [v[0:len],v[len:length]]
	else:
		return [v[0:len],None]
#----------------------------------------------------------------------------------
def echo(v):
	print(v)

#----------------------------------------------------------------------------------
def explode(chr, s, max = 0):
	if max == 0:
		return s.split(chr)
	else:
		return s.split(chr, max)

def split(chr, s, max = 0):
	return explode(chr, s, max)
#----------------------------------------------------------------------------------
def str_split(v):
	return list(v)
#----------------------------------------------------------------------------------
def implode(chr, arr):
	return chr.join(arr)

def join(chr, arr):
	return implode(chr, arr)
#----------------------------------------------------------------------------------
def lcfirst(s):
	arr = strcut(s, 1)
	return arr[0].lower() + arr[1]

def ucfirst(s):
	arr = strcut(s, 1)
	return arr[0].upper() + arr[1]
#----------------------------------------------------------------------------------
def strtolower(s):
	return s.lower()
	
def strtoupper(s):
	return s.upper()
#----------------------------------------------------------------------------------

def md5(s):
	import hashlib
	m = hashlib.md5(s.encode())
	return m.hexdigest()

def md5_file(file):
	f = open(file, "r", encoding='utf-8')
	s = f.read()
	f.close()
	return md5(s)
#----------------------------------------------------------------------------------

def number_format(v, num):
	return format(round(v, num), ',')

def money_format(chr, s):
	return format(s, chr)
#----------------------------------------------------------------------------------

def parse_url(s):
	from urllib import parse
	parse_res=parse.urlparse(s)
	return {"scheme":parse_res.scheme,"host":parse_res.netloc,"path":parse_res.path,"query":parse_res.query,"fragment":parse_res.fragment}
	
def parse_str(s):
	from urllib import parse
	obj = {}
	tmp = parse.parse_qs(s)
	for i in tmp:
		obj.setdefault(i, tmp[i][0])
	
	return obj;
#----------------------------------------------------------------------------------
def sha1(s):
	import hashlib
	m = hashlib.sha1(s.encode())
	return m.hexdigest()
	
def sha1_file(file):
	f = open(file, "r", encoding='utf-8')
	s = f.read()
	f.close()
	return sha1(s)
#----------------------------------------------------------------------------------
def str_ireplace(oldv, newv, s):
	import re
	return re.sub(r''+str(oldv), newv, s, 0, re.I)

def str_replace(oldv, newv, s):
	return s.replace(oldv, newv)
#----------------------------------------------------------------------------------

def str_shuffle(v):
	import random
	v = str_split(v)
	random.shuffle(v)
	return join('', v)
#----------------------------------------------------------------------------------
def strchr(s, v, bf = False):
	b,a = _split(v, s)
	return b if bf else a
	
def strstr(s, v, bf = False):
	return strchr(s, v, bf)
#----------------------------------------------------------------------------------
def strtr(s, arr):
	return s.maketrans(arr.keys(), arr.values())
#----------------------------------------------------------------------------------
def substr_count(s, v):
	return s.count(v)
#----------------------------------------------------------------------------------
def substr(s, start, len = 0):
	len = len if len > 0 else strlen(s)
	return s[start:start+len]
#----------------------------------------------------------------------------------

def substr_replace(s, v, start, len = 0):
	sub = substr(s, start, len)
	return str_replace(sub, v, s)
#----------------------------------------------------------------------------------
def ucwords(s):
	return s.title()
#----------------------------------------------------------------------------------
def strpos(s, chr, offser):
	stat = s.find(chr, offser)
	return False if stat==-1 else stat

def stripos(s, chr):
	import re
	match = re.search(r''+str(chr), s, re.I)
	return match.span()[0] if match != None else False
#----------------------------------------------------------------------------------
def strtotime(s):
	import time
	return ceil(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')))
	
		
		
		
#----------------------------------------------------------------------------------

# has chr
# has ord

def convert_cyr_string(v):
	pass

def convert_uudecode(v):
	pass

def convert_uuencode(v):
	pass

def count_chars(str):
	pass

def crc32():
	pass

def crypt():
	pass

def fprintf():
	pass
	
def get_html_translation_table():
	pass

def hebrev():
	pass

def hebrevc():
	pass

def html_entity_decode():
	pass

def htmlentities():
	pass

def htmlspecialchars_decode():
	pass

def htmlspecialchars():
	pass

def levenshtein():
	pass

def localeconv():
	pass

def metaphone():
	pass

def printf():
	pass

def quoted_printable_decode():
	pass

def quoted_printable_encode():
	pass

def quotemeta():
	pass

def setlocale():
	pass

def similar_text():
	pass

def soundex():
	pass

def sprintf():
	pass

def sscanf():
	pass

def str_getcsv():
	pass

def str_rot13():
	pass

def str_word_count():
	pass

def strcasecmp():
	pass

def strncasecmp():
	pass

def strtok():
	pass

def substr_compare():
	pass

def vfprintf():
	pass

def vprintf():
	pass

def vsprintf():
	pass

def wordwrap():
	pass
def ceil(i):
	import math
	return math.ceil(i)
#----------------------------------------------------------------------------------
def floor(i):
	import math
	return math.ceil(i)
#----------------------------------------------------------------------------------
def rand(min, max):
	import random
	return round((max - min) * random.random()) + min;
#----------------------------------------------------------------------------------
def nowtime():
	import time
	return ceil(time.time())
#----------------------------------------------------------------------------------
def date(s, t = ''):
	import time
	if empty(t):
		t = nowtime()
	
	return time.strftime(s, time.localtime(t))
#----------------------------------------------------------------------------------
def print_r(vv):
	import pprint
	pprint.pprint(vv)
#----------------------------------------------------------------------------------


def is_array(v):
	v = str(type(v))
	return True if v == ("<class 'list'>" or "<class 'tuple'>" or "<class 'range'>" or "<class 'dict'>" or "<class 'frozenset'>" or "<class 'set'>") else False
#----------------------------------------------------------------------------------
def is_dict(v):
	v = str(type(v))
	return True if v == "<class 'dict'>" else False
#----------------------------------------------------------------------------------
def is_list(v):
	v = str(type(v))
	return True if v == "<class 'list'>" else False
#----------------------------------------------------------------------------------

def is_string(v):
	v = str(type(v))
	return True if v == "<class 'str'>" else False
#----------------------------------------------------------------------------------

def is_float(v):
	v = str(type(v))
	return True if v == "<class 'float'>" else False
#----------------------------------------------------------------------------------

def is_int(v):
	v = str(type(v))
	return True if v == "<class 'int'>" else False
#----------------------------------------------------------------------------------

def is_function(v):
	v = str(type(v))
	return True if v == "<class 'function'>" else False
#----------------------------------------------------------------------------------

def is_numeric(v):
	if is_int(v) or is_float(v):
		return True
	
	if is_string(v):
		try:
			int(v)
		except:
			try:
				float(v)
			except:
				return False
	
	return True
#----------------------------------------------------------------------------------
def is_bool(v):
	v = str(type(v))
	return True if v == "<class 'bool'>" else False
#----------------------------------------------------------------------------------

def is_null(v):
	return None == v
#----------------------------------------------------------------------------------

def is_object(v):
	v = str(type(v))
	return True if v == "<class 'dict'>" else False
#----------------------------------------------------------------------------------

def isset(arr, v):
	if is_int(v):
		try:
			arr[v]
		except:
			return False
		
		return True
	else:
		return True if v in arr else False
#----------------------------------------------------------------------------------

def is_empty(v):
	if is_function(v):
		return False
	
	if is_object(v):
		return len(v) == 0
	
	if is_array(v):
		return len(v) == 0
	
	if is_null(v): return True
	if v == 0: return True
	if v == '': return True
	if v == '0': return True
	
	return False;
#----------------------------------------------------------------------------------

def empty(v):
	return is_empty(v)

def array_change_key_case(arr, type):
	tmp = {}
	for x in arr:
		if type=='up':
			y = strtouper(x)
		else:
			y = strtolower(x)
		
		tmp[y] = arr[x]
		
	return tmp
#----------------------------------------------------------------------------------
def array_values(arr):
	return list(arr.values())

def array_keys(arr):
	return list(arr.keys())
#----------------------------------------------------------------------------------
def count(v):
	return len(v)
#----------------------------------------------------------------------------------

def array_chunk(arr, size):
	import numpy
	return numpy.array_split(arr, size)
#----------------------------------------------------------------------------------

def array_combine(kk,vv):
	tmp = {}
	for k,v in enumerate(kk):
		tmp[v] = vv[k]
	
	return tmp
#----------------------------------------------------------------------------------
def array_diff_assoc(arr1, arr2):
	tmp = {}
	
	if is_list(arr1):
		arr = array_diff(arr1, arr2)
		for k,v in enumerate(arr1):
			if v in arr:
				tmp[k] = v
			
	else:
		v1 = array_values(arr1)
		v2 = array_values(arr2)
		arr = array_diff(v1, v2)
		
		for k,v in arr1.items():
			if v in arr:
				tmp[k] = v
	
	return tmp
#----------------------------------------------------------------------------------
def array_diff_key(arr1, arr2):
	tmp = {}
	v1 = array_keys(arr1)
	v2 = array_keys(arr2)
	arr = array_diff(v1, v2)
	for k,v in arr1.items():
		if k in arr:
			tmp[k] = v
	
	return tmp
#----------------------------------------------------------------------------------

def array_diff(arr1, arr2):
	import numpy
	return numpy.setdiff1d(arr1,arr2)
#----------------------------------------------------------------------------------

def array_intersect_assoc(arr1, arr2):
	tmp = {}
	
	if is_list(arr1):
		arr = array_intersect(arr1, arr2)
		for k,v in enumerate(arr1):
			if v in arr:
				tmp[k] = v
			
	else:
		v1 = array_values(arr1)
		v2 = array_values(arr2)
		arr = array_intersect(v1, v2)
		
		for k,v in arr1.items():
			if v in arr:
				tmp[k] = v
	
	return tmp
#----------------------------------------------------------------------------------

def array_intersect_key(arr1, arr2):
	tmp = {}
	v1 = array_keys(arr1)
	v2 = array_keys(arr2)
	arr = array_intersect(v1, v2)
	for k,v in arr1.items():
		if k in arr:
			tmp[k] = v
	
	return tmp
#----------------------------------------------------------------------------------

def array_intersect(arr1, arr2):
	import numpy
	return numpy.intersect1d(arr1,arr2)
#----------------------------------------------------------------------------------

def array_fill_keys(keys, vv):
	tmp = {}
	for k,v in enumerate(keys):
		tmp[v] = vv
	
	return tmp
	
#----------------------------------------------------------------------------------
def array_fill(start, num, vv):
	tmp = {}
	for v in list(range(start,start+num)):
		tmp[v] = vv
	
	return tmp
#----------------------------------------------------------------------------------
def array_filter(arr):

	if is_list(arr):
		tmp = []
		for k,v in enumerate(arr):
			vv = trim(v)
			if not empty(vv):
				tmp.append(v)
			
	else:
		tmp = {}
		for k,v in arr.items():
			vv = trim(v)
			if not empty(vv):
				tmp[k] = v
		
	return tmp

#----------------------------------------------------------------------------------

def array_flip(arr):
	tmp = {}
	for k,v in arr.items():
			tmp[v] = k
	
	return tmp
#----------------------------------------------------------------------------------
def array_key_exists(key, arr):
	return isset(arr, key)
#----------------------------------------------------------------------------------
def array_map(arr, func):
	return list(map(func, arr))
	
#----------------------------------------------------------------------------------
def array_merge(dict1, dict2):
	if is_list(dict1):
		return dict1+dict2
	else:
		return {**dict1, **dict2}

#----------------------------------------------------------------------------------
def array_pad(arr, l, vv):
	arr1 = arr.copy();
	ll = count(arra)
	tmp = range(l - ll, l)
	for i in tmp:
		array_push(arra, vv)
	
	return arr1
#----------------------------------------------------------------------------------
def array_push(arr, vv):
	arr.append(vv)
	return
#----------------------------------------------------------------------------------

def array_pop(arr):
	vv = arr.pop()
	return vv
#----------------------------------------------------------------------------------

def array_shift(arr):
	vv = arr.pop(0)
	return vv
#----------------------------------------------------------------------------------

def array_unshift(arr, vv):
	arr.insert(0, vv)
	return
#----------------------------------------------------------------------------------

def array_rand(arr):
	tmp = array_shuffle(arr)
	if is_list(tmp):
		return [tmp[0]]
	else:
		for k,v in tmp.items():
			return {k:v}
#----------------------------------------------------------------------------------

def array_shuffle(arr):
	import random
	arr1 = arr.copy()
	if is_list(arr1):
		random.shuffle(arr1)
		return arr1
	else:
		arr2 = array_keys(arr1)
		random.shuffle(arr2)
		tmp = {}
		for k in arr2:
			tmp[k] = arr1.get(k)
		return tmp
#----------------------------------------------------------------------------------
def array_search(vv, arr):
	
	if is_list(arr1):
		for k,v in enumerate(arr):
			if vv == v:
				return k
	else:
		for k,v in arr.items():
			if vv == v:
				return k
	
	return False
#----------------------------------------------------------------------------------

def in_array(vv, arr):
	v = array_search(vv, arr)
	return False if (is_bool(v) and v==False) else True
#----------------------------------------------------------------------------------
def array_slice(arr, start, l):
	return arr[start:start+l]

#----------------------------------------------------------------------------------
def array_splice(arr, start, l, vv):
	if is_string(vv):
		vv = [vv]
	
	arr[start:start+l] = vv
	return
#----------------------------------------------------------------------------------
def array_insert(arr, index, vv):
	arr.insert(index, vv)
#----------------------------------------------------------------------------------
def array_sum(arr):
	import numpy
	return numpy.sum(arr)
#----------------------------------------------------------------------------------
def array_unique(arr):
	import numpy
	return numpy.unique(arr)
#----------------------------------------------------------------------------------

def array_reverse(arr):
	arr1 = arr.copy()
	arr1.reverse()
	return arr1
#----------------------------------------------------------------------------------

def array_sort(arr):
	import numpy
	return list(numpy.sort(arr))
#----------------------------------------------------------------------------------

def array_rsort(arr):
	arr = array_sort(arr)
	return array_reverse(arr)
#----------------------------------------------------------------------------------
def array_range(low, high, step = 1):
	return list(range(low, high, step))
#----------------------------------------------------------------------------------

def array_ksort(dct):
	pass
#----------------------------------------------------------------------------------

def array_krsort(dct):
	pass
#----------------------------------------------------------------------------------

def array_asort():
	pass
def array_arsort():
	pass

def array_count_values():
	pass

def array_merge_recursive():
	pass

def array_multisort():
	pass

def array_product():
	pass

def array_walk():
	pass

