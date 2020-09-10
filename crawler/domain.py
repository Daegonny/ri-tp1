from datetime import datetime, timedelta

class Domain():
	def __init__(self,nam_domain,int_time_limit_between_requests):
		self.time_last_access = datetime(1970,1,1)
		self.nam_domain = nam_domain
		self.int_time_limit_seconds  = int_time_limit_between_requests
	@property
	def time_since_last_access(self):
		return datetime.now() - self.time_last_access 

	def accessed_now(self):
		self.time_last_access = datetime.now()

	def is_accessible(self):
		return timedelta(seconds=self.int_time_limit_seconds) < self.time_since_last_access

	def __hash__(self):
		return hash(self.nam_domain)

	def __eq__(self, domain):
		return (self.__class__ == domain.__class__ and self.nam_domain == domain.nam_domain) or self.nam_domain == domain

	def __str__(self):
		return self.nam_domain

	def __repr__(self):
		return str(self)
