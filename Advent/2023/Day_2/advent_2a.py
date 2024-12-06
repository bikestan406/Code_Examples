#Russell Stanbery
#advent of code 2023, day 2, part 1

#12 red cubes, 13 green cubes, 14 blue cubes

#--------Functions
def fun(string,color,number):
	temp = string.replace(color,'')
	if int(temp) <= number:
		return True
	else:
		return False


def line_reader(line):
	chunks = line.split(';')

	for i,chunk in enumerate(chunks):
		if i == 0:
			nums = chunk.split(': ')[1].split(',')
			game_num = chunk.split(': ')[0].replace('Game ','')
		else:
			nums = chunk.split(',')

		
		for n in nums:
			for color in colors.keys():
				if color in n:
					t = fun(n,color,colors[color])
					if t == False:
						return


	return int(game_num)


def result(lines):
	games = []
	for line in lines:
		game = line_reader(line)
		if game:
			games.append(game)

	return sum(games)
	
#---------MAIN


filepath = '/Users/russell/Desktop/Career/Python_Practice/Advent_2023/advent_2a.txt'

with open(filepath,'r') as f:
	lines = f.readlines()
	f.close()

colors = {' red' : 12,
 ' blue' : 14,
 ' green' : 13}

print(result(lines))