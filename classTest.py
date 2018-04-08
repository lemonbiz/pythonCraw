class Cat(object):
	"""docstring for Cat"""
	def __init__(self, name, color, age):
		self.name = name
		self.color = color
		self.age = age
	def __call__(self, name, color, age):
		self.name = name
		self.age = age
		self.color = color
	def getName(self):
		return self.name

cat = Cat('tom', 'yellow', 11)
print cat.getName()
cat('mike','yellow', 12)
print cat.getName()