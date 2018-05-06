# functions and variables for pipe AI and functions that communicate with manager through pipes
# don't modify this file

import sys
import win32api
import win32event
import win32console
import win32process
import pywintypes

DEBUG      = False
ABOUT_FUNC = True
DEBUG_EVAL = True

# information about a game - you should use these variables
"""the board size"""
width, height = None, None
"""time for one turn in milliseconds"""
info_timeout_turn = 30000
"""total time for a game"""
info_timeout_match = 1000000000
"""left time for a game"""
info_time_left = 1000000000
"""maximum memory in bytes, zero if unlimited"""
info_max_memory = 0
"""0: human opponent, 1: AI opponent, 2: tournament, 3: network tournament"""
info_game_type = 1
"""0: five or more stones win, 1: exactly five stones win"""
info_exact5 = 0
"""0: gomoku, 1: renju"""
info_renju = 0
"""0: single game, 1: continuous"""
info_continuous = 0
"""return from brain_turn when terminateAI > 0"""
terminateAI = None
"""tick count at the beginning of turn"""
start_time = None
"""folder for persistent files"""
dataFolder = ""

event1, event2 = None, None

# you have to implement these functions
def brain_init():
	"""create the board and call pipeOut("OK") or pipeOut("ERROR Maximal board size is ..")"""
	raise NotImplementedError
def brain_restart():
	"""delete old board, create new board, call pipeOut("OK")"""
	raise NotImplementedError
def brain_turn():
	"""choose your move and call do_mymove(x,y), 0 <= x < width, 0 <= y < height"""
	raise NotImplementedError
def brain_my(x, y):
	"""put your move to the board"""
	raise NotImplementedError
def brain_opponents(x, y):
	"""put opponent's move to the board"""
	raise NotImplementedError
def brain_block(x, y):
	"""square [x,y] belongs to a winning line (when info_continuous is 1)"""
	raise NotImplementedError
def brain_takeback(x, y):
	"""clear one square, return value: 0: success, 1: not supported, 2: error"""
	raise NotImplementedError
def brain_end():
	"""delete temporary files, free resources"""
	raise NotImplementedError
def brain_eval(x, y):
	"""display evaluation of square [x,y]"""
	raise NotImplementedError
"""AI identification (copyright, version)"""
infotext = ""
def brain_about():
	"""call pipeOut(" your AI info ")"""
	raise NotImplementedError


def pipeOut(what):
	"""write a line to sys.stdout"""
	ret = len(what)
	print(what)
	sys.stdout.flush()

def do_mymove(x, y):
	brain_my(x, y)
	pipeOut("{},{}".format(x,y))

def suggest(x, y):
	"""send suggest"""
	pipeOut("SUGGEST {},{}".format(x,y))

def safeInt(v):
	"""helper function for parsing strings to int"""
	try:
		ret = int(v)
		return ret
	except:
		return None

def get_line():
	"""read a line from sys.stdin"""
	return sys.stdin.readline().strip()

def parse_coord(param):
	"""parse coordinates x,y"""
	if param.count(",") != 1:
		return None
	x, comma, y = param.partition(',')
	x, y = [safeInt(v) for v in (x, y)]
	if any(v is None for v in (x,y)):
		return None, None
	if x < 0 or y < 0 or x >= width or y >= height:
		return None, None
	return x, y

def parse_3int_chk(param):
	"""parse coordinates x,y and player number z"""
	if param.count(',') != 2:
		return None, None, None
	x, y, z = param.split(',')
	x, y, z = [safeInt(v) for v in (x,y,z)]
	if any(v is None for v in (x,y,z)):
		return None, None, None
	return x, y, z

def get_cmd_param(command, input):
	"""return word after command if input starts with command, otherwise return None"""
	cl = command.lower()
	il = input.lower()
	n1 = len(command)
	n2 = len(input)
	if n1 > n2 or not il.startswith(cl):
		return None # it is not command
	return input[n1:].lstrip()

def threadLoop():
	"""main function for the working thread"""
	while True:
		win32event.WaitForSingleObject(event1, win32event.INFINITE)
		brain_turn()
		win32event.SetEvent(event2)

def turn():
	"""start thinking"""
	global terminateAI
	terminateAI = 0
	win32event.ResetEvent(event2)
	win32event.SetEvent(event1)

def stop():
	"""stop thinking"""
	global terminateAI
	terminateAI = 1
	win32event.WaitForSingleObject(event2, win32event.INFINITE)

def start():
	global start_time
	start_time = win32api.GetTickCount()
	stop()
	global width, height
	if not width:
		width = height = 20
		brain_init()

def do_command(cmd):
	"""do command cmd"""
	global info_max_memory, info_timeout_match, info_timeout_turn, info_time_left, info_game_type, info_exact5, info_continuous, info_renju, dataFolder
	global width, height
	#
	param = get_cmd_param("info", cmd)
	if param is not None:
		info = get_cmd_param("max_memory", param)
		if info is not None:
			info_max_memory = int(info)
			return
		#
		info = get_cmd_param("timeout_match", param)
		if info is not None:
			info_timeout_match = int(info)
			return
		#
		info = get_cmd_param("timeout_turn", param)
		if info is not None:
			info_timeout_turn = int(info)
			return
		#
		info = get_cmd_param("time_left", param)
		if info is not None:
			info_time_left = int(info)
			return
		#
		info = get_cmd_param("game_type", param)
		if info is not None:
			info_game_type = int(info)
			return
		#
		info = get_cmd_param("rule", param)
		if info is not None:
			e = int(info)
			info_exact5 = e & 1
			info_continuous = (e >> 1) & 1
			info_renju = (e >> 2) & 1
			return
		#
		info = get_cmd_param("folder", param)
		if info is not None:
			dataFolder = info
			return
		#
		info = get_cmd_param("evaluate", param)
		if DEBUG_EVAL and info is not None:
			x, y = parse_coord(info)
			if x is not None and y is not None:
				brain_eval(x, y)
			return
		# unknown info is ignored
		return
	#
	param = get_cmd_param("start", cmd)
	if param is not None:
		width = safeInt(param)
		if width is None or width < 5:
			width = 0
			pipeOut("ERROR bad START parameter")
		else:
			height = width
			start()
			brain_init()
		return
	#
	param = get_cmd_param("rectstart", cmd)
	if param is not None:
		if param.count(',') != 1:
			width = height = 0
		else:
			width,c,height = param.partition(',')
			width,height = [safeInt(v) for v in (width,height)]
		if width is None or width < 5 or height is None or height < 5:
			width = height = 0
			pipeOut("ERROR bad RECTSTART parameters")
		else:
			start()
			brain_init()
		return
	#
	param = get_cmd_param("restart", cmd)
	if param is not None:
		start()
		brain_restart()
		return
	#
	param = get_cmd_param("turn", cmd)
	if param is not None:
		start()
		x, y = parse_coord(param)
		if x is None or y is None:
			pipeOut("ERROR bad coordinates")
		else:
			brain_opponents(x, y)
			turn()
		return
	#
	param = get_cmd_param("play", cmd)
	if param is not None:
		start()
		x, y = parse_coord(param)
		if x is None or y is None:
			pipeOut("ERROR bad coordinates")
		else:
			do_mymove(x, y)
		return
	#
	param = get_cmd_param("begin", cmd)
	if param is not None:
		start()
		turn()
		return
	#
	param = get_cmd_param("about", cmd)
	if param is not None:
		if ABOUT_FUNC:
			brain_about()
		else:
			pipeOut(infotext)
		return
	#
	param = get_cmd_param("end", cmd)
	if param is not None:
		stop()
		brain_end()
		sys.exit(0)
		return
	#
	param = get_cmd_param("board", cmd)
	if param is not None:
		start()
		while True: # fill the whole board
			cmd = get_line()
			x,y,who = parse_3int_chk(cmd)
			if who == 1:
				brain_my(x, y)
			elif who == 2:
				brain_opponents(x, y)
			elif who == 3:
				brain_block(x, y)
			else:
				if cmd.lower() != "done":
					pipeOut("ERROR x,y,who or DONE expected after BOARD")
				break
		turn()
		return
	#
	param = get_cmd_param("takeback", cmd)
	if param is not None:
		start()
		t = "ERROR bad coordinates"
		x, y = parse_coord(param)
		if x is not None and y is not None:
			e = brain_takeback(x, y)
			if e == 0:
				t = "OK"
			elif e == 1:
				t = "UNKNOWN"
		pipeOut(t)
		return
	#
	pipeOut("UNKNOWN command {}".format(cmd))

def main():
	"""main function for AI console application"""
	#
	handle = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)
	try:
		if handle.GetConsoleMode():
			pipeOut("MESSAGE Gomoku AI should not be started directly. Please install gomoku manager (http://sourceforge.net/projects/piskvork). Then enter path to this exe file in players settings.")
	except pywintypes.error:
		pass
	#
	global event1, event2
	event1 = win32event.CreateEvent(None, 0, 0, None)
	win32process.beginthreadex(None, 0, threadLoop, (), 0)
	event2 = win32event.CreateEvent(None, 1, 1, None)
	while True:
		cmd = get_line()
		do_command(cmd)
