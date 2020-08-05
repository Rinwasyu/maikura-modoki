# MIT License
# Copyright (c) 2020 Rinwasyu
# 
# https://github.com/Rinwasyu/maikura-modoki

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random


cnt_tick = 0
ry = 0
rx = 90

window_width = 800
window_height = 600

world_width = 100
world_height = 100
world_depth = 100

light0_position = [100,80,100,1]
light0_diffuse = [1.0, 1.0, 1.0, 1.0]
light0_ambient = [0.3, 0.3, 0.3, 0.3]
light1_position = [100,100,-60,1]
light1_diffuse = [0.2, 0.2, 0.2, 0.2]
light1_ambient = [0, 0, 0, 0]

block_size = 1
block_color = (
		(0,0,0,0), (1,0,0,1), (0,1,0,1), (0.2,0.2,1,1), (1,1,0,1), (1,0,1,1),
		(0,1,1,1), (1,1,1,1), (0.5,0.5,1,1), (0.5,0,0.5,1)
	)

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
		self.eyeshot = 12
		self.hand_anim = 0
		self.height = 1.9
		self.holding = 1
		self.radius = 0.15 # (player.radius < 1)
		self.speed = 0.01
	def tick(self):
		global keystat, cnt_tick, player
		
		self.vx *= 0.5
		self.vz *= 0.5
		diff_sin_ry = player.speed * math.sin(ry*math.pi/180)
		diff_cos_ry = player.speed * math.cos(ry*math.pi/180)
		if keystat.FORWARD:
			self.vx += diff_sin_ry
			self.vz -= diff_cos_ry
		if keystat.BACK:
			self.vx -= diff_sin_ry
			self.vz += diff_cos_ry
		if keystat.LEFT:
			self.vx -= diff_cos_ry
			self.vz -= diff_sin_ry
		if keystat.RIGHT:
			self.vx += diff_cos_ry
			self.vz += diff_sin_ry
		if keystat.JUMP:
			self.vy = 0.025
			keystat.JUMP = False
		else:
			self.vy -= 0.0003
		if keystat.LAND:
			if self.vy > 0:
				self.vy *= -1
			self.vy -= 0.001
		
		if player.hand_anim > 0:
			player.hand_anim -= 1
		if mousestat.LEFT:
			if player.hand_anim == 0:
				remove_block()
				player.hand_anim = 45
		elif mousestat.RIGHT:
			if player.hand_anim == 0:
				create_block()
				player.hand_anim = 45
		
		next_x = self.x + self.vx
		next_y = self.y + self.vy
		next_z = self.z + self.vz
		if next_x - player.radius < 0 or next_x + player.radius >= world_width:
			self.vx = 0
			next_x = self.x
		if next_y < 0 or next_y + player.height >= world_height:
			self.vy = 0
			next_y = self.y
		if next_z - player.radius < 0 or next_z + player.radius >= world_depth:
			self.vz = 0
			next_z = self.z
		
		radius = (-player.radius, player.radius)
		height = (0, 1, player.height)
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
		self.LAND = False

class Mousestat:
	def __init__(self):
		self.RIGHT = False
		self.LEFT = False
		self.x = -1
		self.y = -1

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glRotated(rx, 1.0, 0.0, 0.0)
	glRotated(ry, 0.0, 1.0, 0.0)
	glTranslated(-player.x * block_size, (-player.y-player.height*0.9) * block_size, -player.z * block_size)
	light()
	cloud()
	scene()
	hand()
	menu()
	glFlush()
	glfw.swap_buffers(window)

def light():
	glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
	glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
	glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
	#glLightfv(GL_LIGHT0, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
	glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
	glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
	glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
	#glLightfv(GL_LIGHT1, GL_SPECULAR, (0, 0, 0, 0))

def menu():
	glPushMatrix()
	x = player.x + math.sin(ry*math.pi/180) * math.cos(rx*math.pi/180) * 0.1
	y = (player.y+player.height*0.9) - math.sin(rx*math.pi/180) * 0.1
	z = player.z - math.cos(ry*math.pi/180) * math.cos(rx*math.pi/180) * 0.1
	glTranslated(x * block_size, y * block_size, z * block_size)
	glRotated(-ry, 0, 1, 0)
	glRotated(-rx, 1, 0, 0)
	glCallList(list_plus)
	glPopMatrix()
	
	glPushMatrix()
	r_x = rx + 19
	x = player.x+ math.sin(ry*math.pi/180) * math.cos(r_x*math.pi/180) * 0.1
	y = (player.y+player.height*0.9) - math.sin(r_x*math.pi/180) * 0.1
	z = player.z - math.cos(ry*math.pi/180) * math.cos(r_x*math.pi/180) * 0.1
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
		if player.holding == i+1:
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

def hand():
	glPushMatrix()
	r_x = rx + 30
	x = player.x+ math.sin(ry/180*math.pi) * math.cos(r_x/180*math.pi) * 0.1
	y = (player.y+player.height*0.9) - math.sin(r_x/180*math.pi) * 0.1
	z = player.z - math.cos(ry/180*math.pi) * math.cos(r_x/180*math.pi) * 0.1
	glTranslated(x * block_size, y * block_size, z * block_size)
	glRotated(-ry, 0, 1, 0)
	glRotated(-rx, 1, 0, 0)
	glTranslated(0.06, -0.01, -0.01)
	glRotated(-20-player.hand_anim, 1, 0, 0)
	glRotated(20, 0, 0, 1)
	glCallList(list_hand)
	glPopMatrix()

def draw_object(vertices, faces, normals, primitive):
	face_n = len(faces)
	for i in range(face_n):
		glBegin(primitive)
		if normals:
			glNormal3dv(normals[i])
		for j in LOOP_4:
			glVertex3dv(vertices[faces[i][j]])
		glEnd()

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
	draw_object(bv, bf, bn, GL_POLYGON)
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0,0,0))
	draw_object(bv, bf, bn, GL_LINE_LOOP)
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
	draw_object(pv, pf, None, GL_POLYGON)
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
	draw_object(sv, sf, None, GL_POLYGON)
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
	draw_object(mbv, mbf, None, GL_POLYGON)
	glEndList()
	
	global list_selectionmenu_block_wireframe
	list_selectionmenu_block_wireframe = glGenLists(1)
	glNewList(list_selectionmenu_block_wireframe, GL_COMPILE)
	draw_object(mbv, mbf, None, GL_LINE_LOOP)
	glEndList()
	
	global list_cloud
	cv = (
			(0, 0, 0), (0, 0, -100), (50, 0, -100), (50, 0, 0), (50, 0, -150), (100, 0, -150), (100, 0, 0)
		)
	cf = ((0, 1, 2, 3), (3, 4, 5, 6))
	list_cloud = glGenLists(1)
	glNewList(list_cloud, GL_COMPILE)
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.9,0.9,0.9,1))
	glMaterialfv(GL_FRONT, GL_AMBIENT, (0.9,0.9,0.9,1))
	draw_object(cv, cf, None, GL_QUADS)
	glEndList()
	
	global list_hand
	list_hand = glGenLists(1)
	glNewList(list_hand, GL_COMPILE)
	hv = (
			(0, 0, 0), (0, 0, -0.015), (0.015, 0, -0.015), (0.015, 0, 0),
			(0, 0.05, 0), (0, 0.05, -0.015), (0.015, 0.05, -0.015), (0.015, 0.05, 0),
		)
	hf = (
			(0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)
		)
	hn = (
			(0, -1, 0), (0, 1, 0), (-1, 0, 0), (0, 0, -1), (1, 0, 0), (0, 0, 1)
		)
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.5, 0.5, 0.5, 1))
	draw_object(hv, hf, hn, GL_POLYGON)
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0, 0, 0, 0))
	glEndList()
	
	global list_render
	list_render = None
	
	update_render()

def update_render():
	global list_render
	if list_render:
		glDeleteLists(list_render, 1)
	range_x_min = max(0,int(player.x)-player.eyeshot)
	range_x_max = min(world_width,int(player.x)+player.eyeshot)
	range_y_min = 0
	range_y_max = world_height
	range_z_min = max(0,int(player.z)-player.eyeshot)
	range_z_max = min(world_depth,int(player.z)+player.eyeshot)
	LOOP_X = range(range_x_min, range_x_max)
	LOOP_Y = range(range_y_min, range_y_max)
	LOOP_Z = range(range_z_min, range_z_max)
	list_render = glGenLists(1)
	glNewList(list_render, GL_COMPILE)
	for i in LOOP_X:
		for j in LOOP_Y:
			for k in LOOP_Z:
				if block_visibility[i][j][k] == 0 or block[i][j][k] == 0:
					continue
				else:
					color = block_color[block[i][j][k]]
					glPushMatrix()
					glTranslated(block_size * (i), block_size * (j), block_size * (k))
					glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
					glMaterialfv(GL_FRONT, GL_AMBIENT, (color[0]*0.2, color[1]*0.2, color[2]*0.2, 1))
					glCallList(list_block)
					glPopMatrix()
	glMaterialfv(GL_FRONT, GL_AMBIENT, (0, 0, 0, 0))
	glEndList()

def create_block():
	global block
	x = player.x
	y = player.y + player.height*0.9
	z = player.z
	step = 0.01
	diff_x = math.sin(ry*math.pi/180) * math.cos(rx*math.pi/180) * step
	diff_y = -math.sin(rx*math.pi/180) * step
	diff_z = -math.cos(ry*math.pi/180) * math.cos(rx*math.pi/180) * step
	distance = 0
	while distance <= player.eyeshot:
		distance += step
		bx = x
		by = y
		bz = z
		x += diff_x
		y += diff_y
		z += diff_z
		if x-player.radius < 0 or x+player.radius >= world_width\
				or y < 0 or y >= world_height\
				or z-player.radius < 0 or z+player.radius >= world_depth:
			return
		if block[int(x)][int(y)][int(z)] > 0:
			if abs(int(x)+0.5 - bx) < abs(int(z)+0.5 - bz):
				bx = x
			else:
				bz = z
			if (int(player.x-player.radius) == int(bx) or int(player.x+player.radius) == int(bx))\
					and int(int(by)-player.y) < player.height and int(int(by)-player.y) >= 0\
					and (int(player.z-player.radius) == int(bz) or int(player.z+player.radius) == int(bz)):
				return
			else:
				block[int(bx)][int(by)][int(bz)] = player.holding
				print("created! (", int(bx), ",", int(by), ",", int(bz), ")")
				block_visibility[max(0,int(bx)-1)][int(by)][int(bz)] -= 1
				block_visibility[min(world_width,int(bx)+1)][int(by)][int(bz)] -= 1
				block_visibility[int(bx)][max(0,int(by)-1)][int(bz)] -= 1
				block_visibility[int(bx)][min(world_height,int(by)+1)][int(bz)] -= 1
				block_visibility[int(bx)][int(by)][max(0,int(bz)-1)] -= 1
				block_visibility[int(bx)][int(by)][min(world_depth,int(bz)+1)] -= 1
				update_render()
			return

def remove_block():
	global block
	x = player.x
	y = player.y + player.height*0.9
	z = player.z
	step = 0.01
	diff_x = math.sin(ry*math.pi/180) * math.cos(rx*math.pi/180) * step
	diff_y = -math.sin(rx*math.pi/180) * step
	diff_z = -math.cos(ry*math.pi/180) * math.cos(rx*math.pi/180) * step
	distance = 0
	while distance <= player.eyeshot:
		distance += step
		x += diff_x
		y += diff_y
		z += diff_z
		if x < 0 or x >= world_width or y < 0 or y >= world_height or z < 0 or z >= world_depth:
			return
		if block[int(x)][int(y)][int(z)] > 0:
			block[int(x)][int(y)][int(z)] = 0
			print("removed (", int(x), ",", int(y), ",", int(z), ")")
			block_visibility[max(0,int(x)-1)][int(y)][int(z)] += 1
			block_visibility[min(world_width,int(x)+1)][int(y)][int(z)] += 1
			block_visibility[int(x)][max(0,int(y)-1)][int(z)] += 1
			block_visibility[int(x)][min(world_height,int(y)+1)][int(z)] += 1
			block_visibility[int(x)][int(y)][max(0,int(z)-1)] += 1
			block_visibility[int(x)][int(y)][min(world_depth,int(z)+1)] += 1
			update_render()
			return

def new_world():
	global block, block_visibility
	block = [[[0] * world_depth for i in range(world_height)] for j in range(world_width)]
	block_visibility = [[[0] * world_depth for i in range(world_height)] for j in range(world_width)]
	width = range(world_width)
	height = range(world_height)
	depth = range(world_depth)
	for i in width:
		for j in height:
			for k in depth:
				if j < 20:
					block[i][j][k] = int(random.randrange(1,9))
				if j < 19:
					block_visibility[i][j][k] = 0
				elif j == 19:
					block_visibility[i][j][k] = 1
				else:
					block_visibility[i][j][k] = 6
	
	global player
	player = Player(50, 20, 50)

def cloud():
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.9,0.9,0.9,1))
	for i in range(0, 5):
		glPushMatrix()
		glTranslated(cnt_tick % 200 + (200*(i+1)) - 500, 150, 10)
		glCallList(list_cloud)
		glPopMatrix()

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
	gluPerspective(50, width / height, 0.01, 1000)
	glMatrixMode(GL_MODELVIEW)

def window_refresh_callback(window):
	display()
	return

def key_callback(window, key, scancode, action, mods):
	global keystat, player
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
		elif key == glfw.KEY_LEFT_SHIFT:
			keystat.LAND = True
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
			player.holding = 1
		elif key == glfw.KEY_2:
			player.holding = 2
		elif key == glfw.KEY_3:
			player.holding = 3
		elif key == glfw.KEY_4:
			player.holding = 4
		elif key == glfw.KEY_5:
			player.holding = 5
		elif key == glfw.KEY_6:
			player.holding = 6
		elif key == glfw.KEY_7:
			player.holding = 7
		elif key == glfw.KEY_8:
			player.holding = 8
		elif key == glfw.KEY_9:
			player.holding = 9
		elif key == glfw.KEY_0:
			player.holding = 0
	elif action == glfw.RELEASE:
		if key == glfw.KEY_UP or key == glfw.KEY_W:
			keystat.FORWARD = False
		elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
			keystat.BACK = False
		elif key == glfw.KEY_LEFT or key == glfw.KEY_A:
			keystat.LEFT = False
		elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
			keystat.RIGHT = False
		elif key == glfw.KEY_SPACE:
			keystat.JUMP = False
		elif key == glfw.KEY_LEFT_SHIFT:
			keystat.LAND = False
	return

def cursor_pos_callback(window, xpos, ypos):
	global rx, ry, mousestat
	if mousestat.x != -1:
		if abs(rx + (ypos - mousestat.y) * 0.5) <= 90:
			rx += (ypos - mousestat.y) * 0.5
		ry = (ry + (xpos - mousestat.x) * 0.5 + 360) % 360
	mousestat.x = xpos
	mousestat.y = ypos
	return

def mouse_button_callback(window, button, action, mods):
	global mousestat
	if glfw.get_input_mode(window, glfw.CURSOR) == glfw.CURSOR_NORMAL:
		print("hide mouse cursor")
		glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED) # hide mouse cursor
		return
	if action == glfw.PRESS:
		if button == glfw.MOUSE_BUTTON_LEFT:
			mousestat.LEFT = True
		elif button == glfw.MOUSE_BUTTON_RIGHT:
			mousestat.RIGHT = True
	elif action == glfw.RELEASE:
		if button == glfw.MOUSE_BUTTON_LEFT:
			mousestat.LEFT = False
		elif button == glfw.MOUSE_BUTTON_RIGHT:
			mousestat.RIGHT = False
	return

def init():
	global keystat, mousestat
	keystat = Keystat()
	mousestat = Mousestat()
	new_world()
	gen_glList()

def main():
	global window
	
	if not glfw.init():
		return
	
	glfw.window_hint(glfw.DOUBLEBUFFER, glfw.TRUE)
	window = glfw.create_window(window_width, window_height, "maikura-modoki", None, None)
	
	if not window:
		glfw.terminate()
		return
	
	glfw.set_window_size_callback(window, window_size_callback)
	glfw.set_window_refresh_callback(window, window_refresh_callback)
	glfw.set_key_callback(window, key_callback)
	glfw.set_cursor_pos_callback(window, cursor_pos_callback)
	glfw.set_mouse_button_callback(window, mouse_button_callback)
	glfw.make_context_current(window)
	
	glClearColor(0.5, 0.8, 1.0, 1.0)
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
