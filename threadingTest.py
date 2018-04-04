import threading
import time

def target():
	print 'the curent threading is %s is running' % threading.current_thread().name
	time.sleep(5)
	print 'the curent threading is %s is ended' % threading.current_thread().name


def main():
	print 'the curent threading is %s is running' % threading.current_thread().name

	for i in range(5):
		t = threading.Thread(target = target)
		t.setDaemon(True)
		t.start()

	time.sleep(3)
	print 'the curent threading is %s is ended' % threading.current_thread().name

a = 10
lock = threading.Lock()

def operation_1():
	lock.acquire()
	global a
	time.sleep(2)
	try:
		a = a - 5
	finally:
		lock.release()

def operation_2():
	lock.acquire()
	global a
	a = a * 3
	lock.release()

thread_1 = threading.Thread(target=operation_1)
thread_2 = threading.Thread(target=operation_2)
for thread in [thread_1, thread_2]:
	thread.start()

for thread in [thread_1, thread_2]:
	thread.join()

print a
'''
local = threading.local()
def func(name):
    print 'current thread:%s' % threading.currentThread().name
    local.name = name
    print "%s in %s" % (local.name,threading.currentThread().name)
t1 = threading.Thread(target=func,args=('haibo',))
t2 = threading.Thread(target=func,args=('lina',))
t1.start()
t2.start()
t1.join()
t2.join()
'''
