import random

class Rlist:
	def __init__(self, list: list, blackList: list = []):
		self.list = list
		self.blackList = blackList
		self.outputList = []
		for i in self.list:
			if i not in self.blackList:
				self.outputList.append(i)
		self.output = self.outputList[random.randint(0, len(self.outputList) - 1)]

	def __str__(self):
		return str(self.output)

	def Rlist(self):
		self.outputList = []
		for i in self.list:
			if i not in self.blackList:
				self.outputList.append(i)
		self.output = self.outputList[random.randint(0, len(self.outputList) - 1)]

	def AppendMainList(self, *therest):
		therest = list(therest)
		for i in therest:
			if i not in self.list:
				self.list.append(i)

	def AppendBlackList(self, *therest):
		therest = list(therest)
		for i in therest:
			if i not in self.blackList:
				self.blackList.append(i)

	def SetSeed(seed: int):
		random.seed(seed)

	def SetOutput(self, setOut):
		self.output = str(setOut)

	def GetMainList(self, settype: str = 'list'):
		if settype == 'list':
			return self.list
		elif settype == 'str':
			return ', '.join(map(str, self.list))
		else:
			return 'None'

	def GetBlackList(self, settype: str = 'list'):
		if settype == 'list':
			return self.blackList
		elif settype == 'str':
			return ', '.join(map(str, self.blackList))
		else:
			return 'None'

	def GetList(self, settype: str = 'list'):
		if settype == 'list':
			return self.outputList
		elif settype == 'str':
			return ', '.join(map(str, self.outputList))
		else:
			return 'None'