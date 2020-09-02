from datetime import datetime

class Domain():
	def __init__(self,nam_domain,int_time_limit_between_requests):
		self.time_last_access = datetime(1970,1,1)
		self.nam_domain = nam_domain
		self.int_time_limit_seconds  = int_time_limit_between_requests
	@property
	def time_since_last_access(self):
		pass

	def accessed_now(self):
		pass

	def is_accessible(self):
		return False

	def __hash__(self):
		return None

	def __eq__(self, domain):
		return None

	def __str__(self):
		return self.nam_domain

	def __repr__(self):
		return str(self)
