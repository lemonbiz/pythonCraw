import threading
import time

fileWNames= ['1.txt', '2.txt', '3.txt', '4.txt']
fileRNames= ['1.txt', '2.txt', '3.txt', '4.txt']
def writeFile(num):
	fileWName = fileWNames.pop()
	num = str(num) * int(num)
	with open(fileWName, 'a') as fp:
		print fileWName + ' is writing'
		fp.write('hello world:'+num + '\n')

def readFile():
	while fileRNames:
		fileRName = fileRNames.pop()
		with open(fileRName, 'r') as fp:
			print fileRName + ' is reading'
			print fp.read()



def main():
	threads = []
	i = 1
	while threads or fileWNames:
		for thread in threads:
			if not thread.is_alive():
				threads.remove(thread)
		while len(threads) < 3 and fileWNames:
			i = i + 1
			thread = threading.Thread(target=writeFile, args=(i,))
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)
		

main()
readFile()
		

