import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math


cnt_tick = 0
ry = 0
rx = 0

window_width = 800
window_height = 600

world_width = 10
world_heihgt = 10
world_depth = 10

cursor_x = -1
cursor_y = -1

block_size = 1

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
		self.vx *= 0.5
		self.vz *= 0.5
		if keystat.FORWARD:
			self.vx -= 0.01 * math.sin(ry/180*math.pi)
			self.vz += 0.01 * math.cos(ry/180*math.pi)
		if keystat.BACK:
			self.vx += 0.01 * math.sin(ry/180*math.pi)
			self.vz -= 0.01 * math.cos(ry/180*math.pi)
		if keystat.LEFT:
			self.vx += 0.01 * math.sin((ry+90)/180*math.pi)
			self.vz -= 0.01 * math.cos((ry+90)/180*math.pi)
		if keystat.RIGHT:
			self.vx -= 0.01 * math.sin((ry+90)/180*math.pi)
			self.vz += 0.01 * math.cos((ry+90)/180*math.pi)
		if keystat.JUMP:
			self.vy = 0.1
			keystat.JUMP = False
		else:
			self.vy -= 0.005
		
		next_x = self.x + self.vx
		next_y = self.y + self.vy
		next_z = self.z + self.vz
		if (-next_x) <= 0 or (-next_x) >= world_width:
			next_x = self.x
		if (next_y) <= 0 or next_y >= world_heihgt:
			next_y = self.y
		if (-next_z) <= 0 or (-next_z) >= world_depth:
			next_z = self.z
		
		if cnt_tick % 1000 == 0:
			print(int(-next_x), ", ", int(self.y), ", ", int(-self.z))
		if block[int(-next_x)][int(self.y)][int(-self.z)] == 0:
			self.x = next_x
		if block[int(-self.x)][int(next_y)][int(-self.z)] == 0:
			self.y = next_y
		else:
			self.vy = 0
		if block[int(-self.x)][int(self.y)][int(-next_z)] == 0:
			self.z = next_z
		#self.y += self.vy
		#if self.y < 0:
		#	self.y = 0
		
		
		"""self.x += self.vx
		#if self.y > 0:
		#	self.y += self.vy
		self.y = 5*block_size
		self.z += self.vz"""
		
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
	glTranslated(player.x * block_size, -player.y * block_size - 2, player.z * block_size)
	glLightfv(GL_LIGHT0, GL_POSITION, (100,100,100,1))
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
	"""
	for i in range(0, len(bf)):
		glBegin(GL_QUADS)
		glNormal3dv(bn[i])
		for j in range(0, len(bf[i])):
			glVertex3dv(bv[bf[i][j]])
	glEnd()"""
	
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (255,255,0))
	#glMaterialfv(GL_FRONT, GL_AMBIENT, (255,255,0))
	for i in range(0, len(bf)):
		glBegin(GL_POLYGON)
		glNormal3dv(bn[i])
		for j in range(0, 4):
			glVertex3dv(bv[bf[i][j]])
		glEnd()
	
	glMaterialfv(GL_FRONT, GL_DIFFUSE, (0,0,0))
	for i in range(0, len(bf)):
		glBegin(GL_LINE_LOOP)
		glNormal3dv(bn[i])
		for j in range(0, 4):
			glVertex3dv(bv[bf[i][j]])
		glEnd()
	glEndList()

def new_world():
	global block
	block = []
	for i in range(0, world_width):
		block.append([])
		for j in range(0, world_heihgt):
			block[i].append([])
			for k in range(0, world_depth):
				if j < 2 or (j == 3 and i == 7 and k == 7) or (i + j < 6):
					block[i][j].append(1)
				else:
					block[i][j].append(0)
	for i in range(3, 6):
		block[7][1][i] = 0
	
	global player
	player = Player(-5, 4, -1)

def render():
	for i in range(0, len(block)):
		for j in range(0, len(block[i])):
			for k in range(0, len(block[i][j])):
				if block[i][j][k] == 1:
					glPushMatrix()
					glTranslated(block_size * (i), block_size * (j), block_size * (k))
					glMaterialfv(GL_FRONT, GL_DIFFUSE, (128,255,0))
					glCallList(list_block)
					glPopMatrix()

def update():
	player.tick()
	display()

def scene():
	render()

def resize(window, width, height):
	if height == 0:
		return
	set_view(width, height)

def set_view(width, height):
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(30.0, width / height, 1.0, 100.0)
	glMatrixMode(GL_MODELVIEW)

def refresh(window):
	display()

def key_callback(window, key, scancode, action, mods):
	global keystat
	if key == glfw.KEY_UP or key == glfw.KEY_W:
		if action == glfw.PRESS:
			keystat.FORWARD = True
		elif action == glfw.RELEASE:
			keystat.FORWARD = False
	if key == glfw.KEY_DOWN or key == glfw.KEY_S:
		if action == glfw.PRESS:
			keystat.BACK = True
		elif action == glfw.RELEASE:
			keystat.BACK = False
	if key == glfw.KEY_LEFT or key == glfw.KEY_A:
		if action == glfw.PRESS:
			keystat.LEFT = True
		elif action == glfw.RELEASE:
			keystat.LEFT = False
	if key == glfw.KEY_RIGHT or key == glfw.KEY_D:
		if action == glfw.PRESS:
			keystat.RIGHT = True
		elif action == glfw.RELEASE:
			keystat.RIGHT = False
	if key == glfw.KEY_SPACE:
		if action == glfw.PRESS:
			keystat.JUMP = True
	if key == glfw.KEY_P:
		if action == glfw.RELEASE:
			print("player at (", int(player.x), ", ", int(player.y), ", ", int(player.z), ")")
	if key == glfw.KEY_ESCAPE:
		# show mouse cursor
		glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
	if key == glfw.KEY_Q:
		glfw.set_window_should_close(window, GL_TRUE)

def cursor_pos_callback(window, xpos, ypos):
	print("cursor_pos : ", xpos, ", ", ypos)
	global rx, ry, cursor_x, cursor_y
	if cursor_x == -1:
		cursor_x = xpos
		cursor_y = ypos
		return
	if xpos > cursor_x:
		ry += (xpos - cursor_x) * 0.5
	elif xpos < cursor_x:
		ry -= (cursor_x - xpos) * 0.5
	if ypos > cursor_y and rx < 90:
		rx += (ypos - cursor_y) * 0.5
	elif ypos < cursor_y and rx > -90:
		rx -= (cursor_y - ypos) * 0.5
	cursor_x = xpos
	cursor_y = ypos

def mouse_button_callback(window, button, action, mods):
	# hide mouse cursor
	glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
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
	
	# hide mouse cursor
	glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
	#glfw.glfw_disable(glfw.GLFW_MOUSE_CURSOR) # deprecated?
	
	glfw.set_window_size_callback(window, resize)
	glfw.set_window_refresh_callback(window, refresh)
	glfw.set_key_callback(window, key_callback)
	glfw.set_cursor_pos_callback(window, cursor_pos_callback)
	glfw.set_mouse_button_callback(window, mouse_button_callback)
	glfw.make_context_current(window)
	
	glClearColor(1.0, 1.0, 1.0, 1.0)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_CULL_FACE)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	
	init()
	
	set_view(window_width, window_height)
	display()

	while not glfw.window_should_close(window):
		glfw.poll_events()
		#glfw.wait_events_timeout(1e-3)
		update()
		display()

	glfw.terminate()

if __name__ == "__main__":
	main()
