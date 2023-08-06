import random
import os
import requests
from tqdm import tqdm
import datetime
import sys
from win32com.client import Dispatch


class File:
	class Size:
		def find_file_size(self, path="C:\\", max_or_min="max"):
			size_path, size_list = self.__get_all_size(path)
			if max_or_min == "max":
				fsize = size_path[size_list.index(max(size_list))][0]
			elif max_or_min == "min":
				fsize = size_path[size_list.index(min(size_list))][0]
			else:
				raise ValueError("max_or_min参数只能填max或min")
			return self.__size_small(fsize, size_path, size_list)

		def __get_all_size(self, path):
			size_path = []
			for path, file_dir, files in os.walk(path):
				for file_name in files:
					size_path.append([os.path.getsize(os.path.join(path, file_name)), os.path.join(path, file_name)])
				for dir in file_dir:
					size_path.append([os.path.getsize(os.path.join(path, dir)), os.path.join(path, dir)])
			size_list = []
			for i in range(len(size_path)):
				size_list.append(size_path[i][0])
			return [size_path, size_list]

		def __size_small(self, fsize, size_path, size_list):
			if fsize < 1024:
				return [str(round(fsize, 2)) + 'B', size_path[size_list.index(max(size_list))][1]]
			else:
				KBX = fsize / 1024
				if KBX < 1024:
					return [str(round(KBX / 1024, 2)) + 'K', size_path[size_list.index(max(size_list))][1]]
				else:
					MBX = KBX / 1024
					if MBX < 1024:
						return [str(round(KBX / 1024, 2)) + 'M', size_path[size_list.index(max(size_list))][1]]
					else:
						GBX = MBX / 1024
						if GBX < 1024:
							return [str(round(MBX / 1024, 2)) + 'G', size_path[size_list.index(max(size_list))][1]]
						else:
							return [str(round(GBX / 1024, 2)) + 'T', size_path[size_list.index(max(size_list))][1]]

		def all_file_size(self, path="C:\\"):
			size_path, size_list = self.__get_all_size(path)
			for i in range(len(size_path)):
				size_path[i][0] = str(self.__size_small(int(size_path[i][0]), size_path, size_list)[0])
			return size_path

		def big_and_not_be_used(self,path="C:\\"):
			size_path = self.__get_all_size(path)[0]
			path_list = [i[1] for i in size_path]
			filelist = []
			path_with_time = []
			for i in range(0, len(path_list)):
				filelist.append(path_list[i])

			for i in range(0, len(filelist)):
				a_path = path_list[i]
				timestamp = os.path.getmtime(a_path)
				date = datetime.datetime.fromtimestamp(timestamp)
				path_with_time.append(["\\".join([item for item in filelist[i].split("\\") if not item in path.split("\\")]), date.strftime('%Y-%m-%d %H:%M:%S')])
			return path_with_time


class Download:
	def Download_with_progress_bar(self,url,fname):
		resp = requests.get(url, stream=True)
		total = int(resp.headers.get('content-length', 0))
		with open(fname, 'wb') as file, tqdm(
				desc=fname,
				total=total,
				unit='iB',
				unit_scale=True,
				unit_divisor=1024,
		) as bar:
			for data in resp.iter_content(chunk_size=1024):
				size = file.write(data)
				bar.update(size)

def cipher(*args,note):
	if type(*args) == list:
		if note != "*" and note != "+":
			return False
		else:
			if note == "+":
				return sum(*args)
			else:
				num = 1
				for i in list(*args):
					num *= i
				return num
	else:
		if note != "-" and note != "/":
			return False
		else:
			if note == "-":
				return sum(*args[0])-sum(*args[1])
			else:
				if sum(*args[0]) / sum(*args[1]) % 1 == 0:
					return int(sum(*args[0]) / sum(*args[1]))
				else:
					return sum(*args[0]) / sum(*args[1])

def printer(*args,end="",flush=False):
	if flush:
		print(*args,"\r",end=end)
		sys.stdout.flush()
	else:
		print(*args,end=end)


def random_number():
	return random.random() * 100


class PPT(Dispatch("PowerPoint.Application")):
	def __init__(self,PPT=None):
		self.PPT = PPT
		self.Visible = 1
		self.DisplayAlerts = 0


file = File
size = file.Size()
download = Download()
ppt = PPT()