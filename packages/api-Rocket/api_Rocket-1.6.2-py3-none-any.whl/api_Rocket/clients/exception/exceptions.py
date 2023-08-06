class Unauthorized(Exception):
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		return '(Unauthorized): ваш токен не зарегистрирован'

class Forbidden(Exception):
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		return '(Forbidden): сервер понял запрос, но отказывается его выполнять. попробуйте использовать прокси!'

class Bad_Requests(Exception):
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		return '(Bad Requests): сервер не понял запрос из-за не действительного синтексиса'

class Server_Error(Exception):
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		return '(Server Error): сервер толкнулся с неожиданной ошибкой, которая помешала ему выполнить запрос'

class Not_Found(Exception):
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		return '(Not Found): сервер не может найти данные согласно запросу'

def check_exceptions(code=0):
	code = int(code)
	if code == 401:
		raise Unauthorized()
	if code == 403:
		raise Forbidden()
	if code == 400:
		raise Bad_Requests()
	if code == 404:
		raise Not_Found()
	if code == 500:
		raise Server_Error()