#Russell Stanbery
#advent day 2 part 2
# find minimum number of cubes to make each game possible

#strategy: find max of each color for each line, multiply each color_max to each other, then add up all products

colors = {' red' : 12,
 ' blue' : 14,
 ' green' : 13}


def color_record(elements,color):
	temp = []

	for i in elements:
		if color in i:
			val = i.replace(color,'')

			temp.append(int(val))
		else:
			temp.append(0)

	return temp

def line_reader(line):
	chunks = line.split(': ')[1].split(';')

	data = {' red' : [],
	' green' : [],
	' blue' : []}

	max_dict = {}


	for color in colors:
		for chunk in chunks:
			elements = chunk.split(',')
			data[color] += color_record(elements,color)

		max_dict[color] = max(data[color])

	product = max_dict[' red'] * max_dict[' green'] * max_dict[' blue']


	return product

def main():
	with open('/Users/russell/Desktop/Career/Python_Practice/Advent_2023/advent_2a.txt','r') as f:
		lines = f.readlines()
		f.close()

	products = []
	for line in lines:
		products.append(line_reader(line))

	print(sum(products))


	return



#----
if __name__ == "__main__":
	main()

colors = [' red', ' green', ' blue']