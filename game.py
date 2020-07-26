# MIT License
# Copyright (c) 2020 Rinwasyu
# 
# https://github.com/Rinwasyu/maikura-modoki

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math


cnt_tick = 0
ry = 0
rx = 90

window_width = 800
window_height = 600

world_width = 100
world_heihgt = 50
world_depth = 100

cursor_x = -1
cursor_y = -1

block_size = 1
block_color = (
		(0,0,0,0), (1,0,0,1), (0,1,0,1), (0.2,0.2,1,1), (1,1,0,1), (1,0,1,1),
		(0,1,1,1), (1,1,1,1), (0.5,0.5,1,1), (0.5,0,0.5,1)
	)

player_height = 1.9
player_speed = 0.01
player_radius = 0.1 # player_radius <= 1
player_holding = 1
player_eyeshot = 12

LOOP_4 = (0, 1, 2, 3)
LOOP_9 = (0, 1, 2, 3, 4, 5, 6, 7, 8)

class Player:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		self.vx = 0
		self.vy = 0
		self.vz = 0
	def tick(self):
		global keystat, cnt_tick
		
		# out of range
		if self.x < 0 or self.y < 0 or self.z < 0 or self.x >= world_width or self.y >= world_heihgt or self.z >= world_depth:
			return
		
		self.vx *= 0.5
		self.vz *= 0.5
		if keystat.FORWARD:
			self.vx += player_speed * math.sin(ry/180*math.pi)
			self.vz -= player_speed * math.cos(ry/180*math.pi)
		if keystat.BACK:
			self.vx -= player_speed * math.sin(ry/180*math.pi)
			self.vz += player_speed * math.cos(ry/180*math.pi)
		if keystat.LEFT:
			self.vx -= player_speed * math.sin((ry+90)/180*math.pi)
			self.vz += player_speed * math.cos((ry+90)/180*math.pi)
		if keystat.RIGHT:
			self.vx += player_speed * math.sin((ry+90)/180*math.pi)
			self.vz -= player_speed * math.cos((ry+90)/180*math.pi)
		if keystat.JUMP:
			self.vy = 0.025
			keystat.JUMP = False
		else:
			self.vy -= 0.0003
		
		next_x = self.x + self.vx
		next_y = self.y + self.vy
		next_z = self.z + self.vz
		if next_x - player_radius < 0 or next_x + player_radius >= world_width:
			self.vx = 0
			next_x = self.x
		if next_y < 0 or next_y + player_height >= world_heihgt:
			self.vy = 0
			next_y = self.y
			# next_y += world_heihgt-player_height
			# self.y = next_y
		if next_z - player_radius < 0 or next_z + player_radius >= world_depth:
			self.vz = 0
			next_z = self.z
		
		radius = (-player_radius, player_radius)
		height = (0, 1, player_height)
		for i in radius:
			for j in height:
				for k in radius:
					if block[int(next_x + i)][int(self.y + j)][int(self.z + k)] > 0:
						self.vx = 0
						next_x = self.x
		for i in radius:
			for j in height:
				for k in radius:
					if block[int(next_x + i)][int(next_y + j)][int(self.z + k)] > 0:
						self.vy = 0
						next_y = self.y
		for i in radius:
			for j in height:
				for k in radius:
					if block[int(next_x + i)][int(next_y + j)][int(next_z + k)] > 0:
						self.vz = 0
						next_z = self.z
		
		self.x += self.vx
		self.y += self.vy
		self.z += self.vz
		
		if int(self.x) != int(self.x-self.vx)\
				or int(self.y) != int(self.y-self.vy)\
				or int(self.z) != int(self.z-self.vz):
			update_render()
		
		cnt_tick += 1

class Keystat:
	def __init__(self):
		self.FORWARD = False
		self.BACK = False
		self.LEFT = False
		self.RIGHT = False
		self.JUMP = False

#TODO: class Mousestat

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glRotated(rx, 1.0, 0.0, 0.0)
	glRotated(ry, 0.0, 1.0, 0.0)
	glTranslated(-player.x * block_size, (-player.y-player_height*0.9) * block_size, -player.z * block_size)
	light()
	scene()
	menu()
	glFlush()
	glfw.swap_buffers(window)

def light():
	glLightfv(GL_LIGHT0, GL_POSITION, (100,80,100,1))
	glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
	glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 0.3))
	glLightfv(GL_LIGHT0, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
	glLightfv(GL_LIGHT1, GL_POSITION, (100,100,-60,1))
	glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.2, 0.2, 0.2, 0.2))
	glLightfv(GL_LIGHT1, GL_AMBIENT, (0, 0, 0, 0))
	glLightfv(GL_LIGHT1, GL_SPECULAR, (0, 0, 0, 0))

def menu():
	glPushMatrix()
	x = player.x + math.sin(ry/180*math.pi) * math.cos(rx/180*math.pi) * 0.1
	y = (player.y+player_height*0.9) - math.sin(rx/180*math.pi) * 0.1
	z = player.z - math.cos(ry/180*math.pi) * math.cos(rx/180*math.pi) * 0.1
	glTranslated(x * block_size, y * block_size, z * block_size)
	glRotated(-ry, 0, 1, 0)
	glRotated(-rx, 1, 0, 0)
	glCallList(list_plus)
	glPopMatrix()
	
	glPushMatrix()
	r_x = rx + 19
	x = player.x+ math.sin(ry/180*math.pi) * math.cos(r_x/180*math.pi) * 0.1
	y = (player.y+player_height*0.9) - math.sin(r_x/180*math.pi) * 0.1
	z = player.z - math.cos(ry/180*math.pi) * math.cos(r_x/180*math.pi) * 0.1
	glTranslated(x * block_size, y * block_size, z * block_size)
	glRotated(-ry, 0, 1, 0)
	glRotated(-rx, 1, 0, 0)
	for i in LOOP_9:
		glPushMatrix()
		glTranslated(0.011*i - 0.044, 0, 0)
		glMaterialfv(GL_FRONT, GL_EMISSION, (0,0,0,0))
		glCallList(list_selectionmenu_block_wireframe)
		glMaterialfv(GL_FRONT, GL_EMISSION, block_color[i+1])
		glCallList(list_selectionmenu_block)
		if player_holding == i+1:
			glMaterialfv(GL_FRONT, GL_EMISSION, (1, 1, 1, 1))
		else:
			glMaterialfv(GL_FRONT, GL_EMISSION, (0.5,0.5,0.5,1))
		glCallList(list_selectionmenu_button)
		glMaterialfv(GL_FRONT, GL_EMISSION, (0,0,0,0))
		glMaterialfv(GL_FRONT, GL_AMBIENT, (0,0,0,0))
		glMaterialfv(GL_FRONT, GL_DIFFUSE, (0,0,0,0))
		glPopMatrix()
	glPopMatrix()
	
	return

def gen_glList():
	global list_block
	# block
	bv = (
			(0, 0, block_size), (0,0,0), (block_size,0,0),(block_size,0,block_size),
			(0, block_size,block_size), (0,block_size,0), (block_size,block_size,0),(block_size,block_size,block_size)
		)
	bf = (
			(0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)
		)
	bn = (
			(0,-1,0), (0,1,0), (-1,0,0), (0,0,-1), (1,0,0), (0,0,1)
		)
	list_block = glGenLists(1)
	glNewList(list_block, GL_COMPILE)
	bf_n = len(bf)
	for i in range(bf_n):
		glBegin(GL_POLYGON)
		glNormal3dv(bn[i])
		for j in LOOP_4:
			glVertex3dv(bv[bf[i][j]])
		glEnd()
	
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0,0,0))
	bf_n = len(bf)
	for i in range(bf_n):
		glBegin(GL_LINE_LOOP)
		glNormal3dv(bn[i])
		for j in LOOP_4:
			glVertex3dv(bv[bf[i][j]])
		glEnd()
	glEndList()
	
	# "+"
	global list_plus
	list_plus = glGenLists(1)
	glNewList(list_plus, GL_COMPILE)
	pv = (
			(0.0001,-0.0001,0), (0.001,-0.0001,0), (0.001,0.0001,0), (0.0001,0.0001,0),
			(0.0001,0.001,0), (-0.0001,0.001,0), (-0.0001,0.0001,0), (-0.001,0.0001,0),
			(-0.001,-0.0001,0), (-0.0001,-0.0001,0), (-0.0001,-0.001,0), (0.0001,-0.001,0)
		)
	pf = (
			(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, 9), (9, 10, 11, 0)
		)
	glMaterialfv(GL_FRONT, GL_EMISSION, (1,1,1,1))
	glBegin(GL_POLYGON)
	pf_n = len(pf)
	for i in range(pf_n):
		for j in LOOP_4:
			glVertex3dv(pv[pf[i][j]])
	glEnd()
	glMaterialfv(GL_FRONT, GL_EMISSION, (0,0,0,0))
	glEndList()
	
	global list_selectionmenu_button
	list_selectionmenu_button = glGenLists(1)
	glNewList(list_selectionmenu_button, GL_COMPILE)
	sv = (
			(0.005, -0.005, 0), (0.005, 0.005, 0), (-0.005, 0.005, 0), (-0.005, -0.005, 0),
		)
	sf = (
			(0, 1, 2, 3), (0, 1, 2, 3)
		)
	glBegin(GL_POLYGON)
	sf_n = len(sf)
	for i in range(sf_n):
		for j in LOOP_4:
			glVertex3dv(sv[sf[i][j]])
	glEnd()
	glEndList()
	
	global list_selectionmenu_block
	list_selectionmenu_block = glGenLists(1)
	glNewList(list_selectionmenu_block, GL_COMPILE)
	mbv = (
			(0, 0, 0), (0, -0.005, 0), (0.004, -0.0025, 0), (0.004, 0.0025, 0),
			(-0.004, 0.0025, 0), (-0.004, -0.0025, 0), (0, 0.005, 0)
		)
	mbf = (
			(0, 1, 2, 3), (0, 3, 6, 4), (0, 4, 5, 1)
		)
	glBegin(GL_POLYGON)
	mbf_n = len(mbf)
	for i in range(mbf_n):
		for j in LOOP_4:
			glVertex3dv(mbv[mbf[i][j]])
	glEnd()
	glEndList()
	
	global list_selectionmenu_block_wireframe
	list_selectionmenu_block_wireframe = glGenLists(1)
	glNewList(list_selectionmenu_block_wireframe, GL_COMPILE)
	glBegin(GL_LINE_LOOP)
	mbf_n = len(mbf)
	for i in range(mbf_n):
		for j in LOOP_4:
			glVertex3dv(mbv[mbf[i][j]])
	glEnd()
	glEndList()
	
	update_render()

def update_render():
	global list_render
	range_x_min = max(0,int(player.x)-player_eyeshot)
	range_x_max = min(world_width,int(player.x)+player_eyeshot)
	range_y_min = max(0,int(player.y)-player_eyeshot)
	range_y_max = min(world_heihgt,int(player.y)+player_eyeshot)
	range_z_min = max(0,int(player.z)-player_eyeshot)
	range_z_max = min(world_depth,int(player.z)+player_eyeshot)
	LOOP_X = range(range_x_min, range_x_max)
	LOOP_Y = range(range_y_min, range_y_max)
	LOOP_Z = range(range_z_min, range_z_max)
	list_render = glGenLists(1)
	glNewList(list_render, GL_COMPILE)
	for i in LOOP_X:
		for j in LOOP_Y:
			for k in LOOP_Z:
				if block[i][j][k] > 0:
					color = block_color[block[i][j][k]]
					glPushMatrix()
					glTranslated(block_size * (i), block_size * (j), block_size * (k))
					glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
					glMaterialfv(GL_FRONT, GL_AMBIENT, (color[0]*0.2, color[1]*0.2, color[2]*0.2, 0.2))
					glCallList(list_block)
					glPopMatrix()
	glMaterialfv(GL_FRONT, GL_AMBIENT, (0, 0, 0, 0))
	glEndList()

def create_block():
	x = player.x
	y = player.y + player_height*0.9
	z = player.z
	step = 0.01
	distance_limit = 50
	distance = 0
	while distance <= distance_limit:
		distance += step
		bx = x
		by = y
		bz = z
		x += math.sin(ry/180*math.pi) * math.cos(rx/180*math.pi) * step
		y -= math.sin(rx/180*math.pi) * step
		z -= math.cos(ry/180*math.pi) * math.cos(rx/180*math.pi) * step
		if x-player_radius < 0 or x+player_radius >= world_width\
				or y < 0 or y >= world_heihgt\
				or z-player_radius < 0 or z+player_radius >= world_depth:
			return
		if block[int(x)][int(y)][int(z)] > 0:
			if abs(int(x)+0.5 - bx) < abs(int(z)+0.5 - bz):
				bx = x
			else:
				bz = z
			if (int(player.x-player_radius) == int(bx) or int(player.x+player_radius) == int(bx))\
					and int(int(by)-player.y) < player_height and int(int(by)-player.y) >= 0\
					and (int(player.z-player_radius) == int(bz) or int(player.z+player_radius) == int(bz)):
				return
			else:
				block[int(bx)][int(by)][int(bz)] = player_holding
				print("created! (", int(bx), ",", int(by), ",", int(bz), ")")
				update_render()
			return

def remove_block():
	x = player.x
	y = player.y + player_height*0.9
	z = player.z
	step = 0.01
	distance_limit = 50
	distance = 0
	while distance <= distance_limit:
		distance += step
		x += math.sin(ry/180*math.pi) * math.cos(rx/180*math.pi) * step
		y -= math.sin(rx/180*math.pi) * step
		z -= math.cos(ry/180*math.pi) * math.cos(rx/180*math.pi) * step
		if x < 0 or x >= world_width or y < 0 or y >= world_heihgt or z < 0 or z >= world_depth:
			return
		if block[int(x)][int(y)][int(z)] > 0:
			block[int(x)][int(y)][int(z)] = 0
			print("removed (", int(x), ",", int(y), ",", int(z), ")")
			update_render()
			return

def new_world():
	global block
	block = []
	width = range(world_width)
	height = range(world_heihgt)
	depth = range(world_depth)
	for i in width:
		block.append([])
		for j in height:
			block[i].append([])
			for k in depth:
				if j < 2 or (i + j < 6):
					block[i][j].append(4)
				else:
					block[i][j].append(0)
	for i in range(49, 51):
		block[52][1][i] = 0
	block[52][3][52] = 5
	block[52][2][52] = 5
	block[53][2][52] = 5
	
	global player
	player = Player(50, 10, 50)

def render():
	glCallList(list_render)

def update():
	player.tick()
	if cnt_tick % 2 == 0:
		display()

def scene():
	render()

def window_size_callback(window, width, height):
	if height == 0:
		return
	set_view(width, height)

def set_view(width, height):
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(50, width / height, 0.01, 100.0)
	glMatrixMode(GL_MODELVIEW)

def window_refresh_callback(window):
	display()
	return

def key_callback(window, key, scancode, action, mods):
	global keystat, player_holding
	if action == glfw.PRESS:
		if key == glfw.KEY_UP or key == glfw.KEY_W:
			keystat.FORWARD = True
		elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
			keystat.BACK = True
		elif key == glfw.KEY_LEFT or key == glfw.KEY_A:
			keystat.LEFT = True
		elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
			keystat.RIGHT = True
		elif key == glfw.KEY_SPACE:
			keystat.JUMP = True
		elif key == glfw.KEY_P: # For debugging
			print("player at (", int(player.x), ", ", int(player.y), ", ", int(player.z), ")")
		elif key == glfw.KEY_R:
			# recreate the world
			new_world()
		elif key == glfw.KEY_ESCAPE: # show mouse cursor
			cursor_x = -1
			cursor_y = -1
			glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
		elif key == glfw.KEY_Q: # close window
			glfw.set_window_should_close(window, GL_TRUE)
		elif key == glfw.KEY_1:
			player_holding = 1
		elif key == glfw.KEY_2:
			player_holding = 2
		elif key == glfw.KEY_3:
			player_holding = 3
		elif key == glfw.KEY_4:
			player_holding = 4
		elif key == glfw.KEY_5:
			player_holding = 5
		elif key == glfw.KEY_6:
			player_holding = 6
		elif key == glfw.KEY_7:
			player_holding = 7
		elif key == glfw.KEY_8:
			player_holding = 8
		elif key == glfw.KEY_9:
			player_holding = 9
		elif key == glfw.KEY_0:
			player_holding = 0
	elif action == glfw.RELEASE:
		if key == glfw.KEY_UP or key == glfw.KEY_W:
			keystat.FORWARD = False
		elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
			keystat.BACK = False
		elif key == glfw.KEY_LEFT or key == glfw.KEY_A:
			keystat.LEFT = False
		elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
			keystat.RIGHT = False
	return

def cursor_pos_callback(window, xpos, ypos):
	global rx, ry, cursor_x, cursor_y
	if cursor_x == -1:
		cursor_x = xpos
		cursor_y = ypos
		return
	if abs(rx + (ypos - cursor_y) * 0.5) <= 90:
		rx += (ypos - cursor_y) * 0.5
	ry = (ry + (xpos - cursor_x) * 0.5 + 360) % 360
	cursor_x = xpos
	cursor_y = ypos
	return

def mouse_button_callback(window, button, action, mods):
	# hide mouse cursor
	if glfw.get_input_mode(window, glfw.CURSOR) == glfw.CURSOR_NORMAL:
		print("hide mouse cursor")
		glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
		return
	if action == glfw.PRESS:
		if button == glfw.MOUSE_BUTTON_LEFT:
			remove_block()
		if button == glfw.MOUSE_BUTTON_RIGHT:
			create_block()
	return

def init():
	global keystat
	keystat = Keystat()
	new_world()
	gen_glList()

def main():
	global window
	
	if not glfw.init():
		return
	
	glfw.window_hint(glfw.DOUBLEBUFFER, glfw.TRUE)
	window = glfw.create_window(window_width, window_height, "game", None, None)
	
	if not window:
		glfw.terminate()
		return
	
	glfw.set_window_size_callback(window, window_size_callback)
	glfw.set_window_refresh_callback(window, window_refresh_callback)
	glfw.set_key_callback(window, key_callback)
	glfw.set_cursor_pos_callback(window, cursor_pos_callback)
	glfw.set_mouse_button_callback(window, mouse_button_callback)
	glfw.make_context_current(window)
	
	glClearColor(1.0, 1.0, 1.0, 1.0)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_CULL_FACE)
	glCullFace(GL_BACK)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_LIGHT1)
	
	init()
	
	set_view(window_width, window_height)
	display()

	while not glfw.window_should_close(window):
		glfw.wait_events_timeout(1e-3)
		update()

	glfw.terminate()

if __name__ == "__main__":
	main()
