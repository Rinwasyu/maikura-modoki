import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math


cnt_tick = 0
ry = 0
rx = 90

window_width = 800
window_height = 600

world_width = 10
world_heihgt = 50
world_depth = 10

cursor_x = -1
cursor_y = -1

block_size = 1
block_color = ((0,0,0,0), (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1), (1,0,1,1), (0,1,1,1), (1,1,1,1))

player_height = 2
player_speed = 0.005

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
		if -self.x < 0 or self.y < 0 or -self.z < 0 or self.x >= world_width or self.y >= world_heihgt or self.z >= world_depth:
			return
		
		self.vx *= 0.5
		self.vz *= 0.5
		if keystat.FORWARD:
			self.vx -= player_speed * math.sin(ry/180*math.pi)
			self.vz += player_speed * math.cos(ry/180*math.pi)
		if keystat.BACK:
			self.vx += player_speed * math.sin(ry/180*math.pi)
			self.vz -= player_speed * math.cos(ry/180*math.pi)
		if keystat.LEFT:
			self.vx += player_speed * math.sin((ry+90)/180*math.pi)
			self.vz -= player_speed * math.cos((ry+90)/180*math.pi)
		if keystat.RIGHT:
			self.vx -= player_speed * math.sin((ry+90)/180*math.pi)
			self.vz += player_speed * math.cos((ry+90)/180*math.pi)
		if keystat.JUMP:
			self.vy = 0.025
			keystat.JUMP = False
		else:
			self.vy -= 0.0003
		
		next_x = self.x + self.vx
		next_y = self.y + self.vy
		next_z = self.z + self.vz
		if (-next_x) < 0 or (-next_x) >= world_width:
			self.vx = 0
			next_x = self.x
		if (next_y) < 0 or next_y + player_height >= world_heihgt:
			self.vy = 0
			next_y = self.y
		if (-next_z) < 0 or (-next_z) >= world_depth:
			self.vz = 0
			next_z = self.z
		
		block_is_in_front_of_face = False
		#if cnt_tick % 1000 == 0:
		#	print("(", block[int(-self.x)][int(self.y)][int(-self.z)],")",int(-next_x), ", ", int(self.y), ", ", int(-self.z))
		for i in [0, player_height-1]:
			if block[int(-next_x)][int(self.y + i)][int(-self.z)] > 0:
				self.vx = 0
				next_x = self.x
				if i == player_height-1:
					block_is_in_front_of_face = True
		for i in [0, player_height-1]:
			if block[int(-next_x)][int(next_y + i)][int(-self.z)] > 0:
				self.vy = 0
				next_y = self.y
		for i in [0, player_height-1]:
			if block[int(-next_x)][int(next_y + i)][int(-next_z)] > 0:
				self.vz = 0
				next_z = self.z
				if i == player_height-1:
					block_is_in_front_of_face = True
		
		if block_is_in_front_of_face:
			self.x += self.vx * 0.5
			self.y += self.vy * 0.5
			self.z += self.vz * 0.5
		else:
			self.x += self.vx
			self.y += self.vy
			self.z += self.vz
		
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
	glTranslated(player.x * block_size, (-player.y-player_height*0.9) * block_size, player.z * block_size)
	glLightfv(GL_LIGHT0, GL_POSITION, (100,80,100,1))
	glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
	glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 0.3))
	glLightfv(GL_LIGHT0, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
	glLightfv(GL_LIGHT1, GL_POSITION, (100,100,-60,1))
	glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.2, 0.2, 0.2, 0.2))
	glLightfv(GL_LIGHT1, GL_AMBIENT, (0, 0, 0, 0))
	glLightfv(GL_LIGHT1, GL_SPECULAR, (0, 0, 0, 0))
	scene()
	menu()
	glFlush()

def menu():
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
	
	for i in range(0, len(bf)):
		glBegin(GL_POLYGON)
		glNormal3dv(bn[i])
		for j in range(0, len(bf[i])):
			glVertex3dv(bv[bf[i][j]])
		glEnd()
	
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0,0,0))
	for i in range(0, len(bf)):
		glBegin(GL_LINE_LOOP)
		glNormal3dv(bn[i])
		for j in range(0, len(bf[i])):
			glVertex3dv(bv[bf[i][j]])
		glEnd()
	glEndList()

def create_block():
	print("viewing from (", player.x, ",", (player.y + player_height*0.9), ",", player.z, ")")
	print("rx : ", rx, ", ry : ", ry)
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
		x -= math.sin(ry/180*math.pi) * math.cos(rx/180*math.pi) * step
		y -= math.sin(rx/180*math.pi) * step
		z += math.cos(ry/180*math.pi) * math.cos(rx/180*math.pi) * step
		print("(", x, ",", y, ",", z, ")")
		if -x < 0 or -x >= world_width or y < 0 or y >= world_heihgt or -z < 0 or -z >= world_depth:
			return
		if block[int(-x)][int(y)][int(-z)] > 0:
			print("hit : (", int(-x), ", ", int(y), ", ", int(-z), ")")
			if int(-player.x) == int(-bx) and int(by)-int(player.y) < player_height and int(by)-int(player.y) >= 0 and int(-player.z) == int(-bz):
				return
			else:
				block[int(-bx)][int(by)][int(-bz)] = 1
				print("created! (", int(-bx), ",", int(by), ",", int(-bz), ")")
			return

def new_world():
	global block
	block = []
	for i in range(0, world_width):
		block.append([])
		for j in range(0, world_heihgt):
			block[i].append([])
			for k in range(0, world_depth):
				if j < 2 or (i + j < 6):
					block[i][j].append(4)
				else:
					block[i][j].append(0)
	for i in range(3, 6):
		block[7][1][i] = 0
	block[7][3][7] = 5
	block[7][2][7] = 5
	block[8][2][7] = 5
	
	global player
	player = Player(-4.5, 5, -5.5)

def render():
	for i in range(0, len(block)):
		for j in range(0, len(block[i])):
			for k in range(0, len(block[i][j])):
				if block[i][j][k] > 0:
					color = block_color[block[i][j][k]]
					glPushMatrix()
					glTranslated(block_size * (i), block_size * (j), block_size * (k))
					glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
					glMaterialfv(GL_FRONT, GL_AMBIENT, (color[0]*0.2, color[1]*0.2, color[2]*0.2, 0.2))
					glCallList(list_block)
					glPopMatrix()

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
	gluPerspective(50, width / height, 0.001, 100.0)
	glMatrixMode(GL_MODELVIEW)

def window_refresh_callback(window):
	display()

def key_callback(window, key, scancode, action, mods):
	global keystat
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
	elif action == glfw.RELEASE:
		if key == glfw.KEY_UP or key == glfw.KEY_W:
			keystat.FORWARD = False
		elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
			keystat.BACK = False
		elif key == glfw.KEY_LEFT or key == glfw.KEY_A:
			keystat.LEFT = False
		elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
			keystat.RIGHT = False

def cursor_pos_callback(window, xpos, ypos):
	# print("cursor_pos : ", xpos, ", ", ypos)
	global rx, ry, cursor_x, cursor_y
	if cursor_x == -1:
		cursor_x = xpos
		cursor_y = ypos
		return
	if xpos > cursor_x:
		ry = (ry + (xpos - cursor_x) * 0.5) % 360
	elif xpos < cursor_x:
		ry = (ry - (cursor_x - xpos) * 0.5 + 360) % 360
	if ypos > cursor_y and rx < 90:
		rx += (ypos - cursor_y) * 0.5
	elif ypos < cursor_y and rx > -90:
		rx -= (cursor_y - ypos) * 0.5
	cursor_x = xpos
	cursor_y = ypos

def mouse_button_callback(window, button, action, mods):
	# hide mouse cursor
	if glfw.get_input_mode(window, glfw.CURSOR) == glfw.CURSOR_NORMAL:
		print("hide mouse cursor")
		glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
		return
	
	if action == glfw.PRESS:
		if button == glfw.MOUSE_BUTTON_RIGHT:
			create_block()
	
	return

def init():
	global keystat
	keystat = Keystat()
	new_world()
	gen_glList()

def main():
	if not glfw.init():
		return
	
	glfw.window_hint(glfw.DOUBLEBUFFER, glfw.FALSE)
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
		#glfw.poll_events()
		glfw.wait_events_timeout(1e-3)
		update()

	glfw.terminate()

if __name__ == "__main__":
	main()
