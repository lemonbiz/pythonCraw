import os

from thread_post_prce_noce import threaded_crawler

def main():
	threaded_crawler()

if __name__ == '__main__':
	path = "province"
	if not os.path.exists(path):
		os.mkdir(path)
	main()