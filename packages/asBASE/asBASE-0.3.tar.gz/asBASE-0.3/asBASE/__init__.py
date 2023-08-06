import json, time

class asJSON:
	def __init__(self, filename):
		self.filename = filename
	def set(self, key, value):
		json_dict = self.read_json()
		json_dict[key] = value
		self.write_json(json_dict)
	def get(self, key):
		json_dict = self.read_json()
		if key in json_dict:
			if "time" in json_dict and "expire" in json_dict["time"] and key in json_dict["time"]["expire"]:
				if json_dict["time"]["expire"][key] < time.time():
					del json_dict["time"]["expire"][key]
					del json_dict[key]
					self.write_json(json_dict)
					return None
			return json_dict[key]
	def sismember(self, key, member):
		json_dict = self.read_json()
		return key in json_dict and member in json_dict[key]["set"]
	def expire(self, key, ttl):
		json_dict = self.read_json()
		if key in json_dict:
			if "time" not in json_dict:
				json_dict["time"] = {"expire": {}}
			json_dict["time"]["expire"][key] = time.time() + ttl
			self.write_json(json_dict)
			return True
		return False
	def sadd(self, key, *values):
		json_dict = self.read_json()
		if "set" in json_dict.get(key, {}):
			json_dict[key]["set"].extend(values)
		else:
			json_dict[key] = {"set": list(values)}
		self.write_json(json_dict)
	def smembers(self, key):
		json_dict = self.read_json()
		return json_dict.get(key, {}).get("set", [])
	def srem(self, key, value):
		json_dict = self.read_json()
		if "set" in json_dict.get(key, {}):
			if value in json_dict[key]["set"]:
				json_dict[key]["set"].remove(value)
				self.write_json(json_dict)
	def delete(self, key):
		json_dict = self.read_json()
		if key in json_dict:
			del json_dict[key]
			self.write_json(json_dict)
			return True
		return False
	def ttl(self, key):
		json_dict = self.read_json()
		if "time" in json_dict and "expire" in json_dict["time"] and key in json_dict["time"]["expire"]:
			ttl = json_dict["time"]["expire"][key] - time.time()
			return max(0, int(ttl))
		return None
	def read_json(self):
		try:
			with open(self.filename, "r") as f:
				json_str = f.read()
				return json.loads(json_str)
		except:
			return {}
	def write_json(self, json_dict):
		json_str = json.dumps(json_dict)
		with open(self.filename, "w") as f:
			f.write(json_str)