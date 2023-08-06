import os
import random


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
		return size_path, size_list

	def __size_small(self, fsize, size_path, size_list):
		if fsize < 1024:
			return str(round(fsize, 2)) + 'B', size_path[size_list.index(max(size_list))][1]
		else:
			KBX = fsize / 1024
			if KBX < 1024:
				return str(round(KBX / 1024, 2)) + 'K', size_path[size_list.index(max(size_list))][1]
			else:
				MBX = KBX / 1024
				if MBX < 1024:
					return str(round(KBX / 1024, 2)) + 'M', size_path[size_list.index(max(size_list))][1]
				else:
					GBX = MBX / 1024
					if GBX < 1024:
						return str(round(MBX / 1024, 2)) + 'G', size_path[size_list.index(max(size_list))][1]
					else:
						return str(round(GBX / 1024, 2)) + 'T', size_path[size_list.index(max(size_list))][1]

	def all_file_size(self, path="C:\\Users\\sunhui\\Desktop"):
		size_path, size_list = self.__get_all_size(path)
		for i in range(len(size_path)):
			size_path[i][0] = str(self.__size_small(int(size_path[i][0]), size_path, size_list)[0])
		return size_path


class Math:
	def __init__(self):
		self.pi_string = "3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
		self.pi = float(self.pi_string)
		self.tau = 2 * self.pi_string

	def evolution(self, number):
		return number ** 0.5

	def power(self, number, num):
		return number ** num

	def cipher(*args, note):
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
					return sum(*args[0]) - sum(*args[1])
				else:
					if sum(*args[0]) / sum(*args[1]) % 1 == 0:
						return int(sum(*args[0]) / sum(*args[1]))
					else:
						return sum(*args[0]) / sum(*args[1])


class Random:
	def random_number(self):
		return random.random() * 100

	def random_choice(self, list):
		return random.choice(list)

	def random_number_with_step(self, first=0, end=100, step=1):
		while True:
			num = random.randint(first, end)
			if (num - first) % step == 0:
				return num


def printer(*args, end="", flush=False):
	if flush:
		print(*args, "\r", end=end)
		sys.stdout.flush()
	else:
		print(*args, end=end)


math = Math()
size = Size()
print(math.pi)
