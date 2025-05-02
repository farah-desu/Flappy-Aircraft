from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random, time, math


WINDOW_W, WINDOW_H = 1000, 800

WORLD_W, WORLD_H, WORLD_D = 800.0, 600.0, 800.0   
SCROLL_S = 50.0                                   

N_STARS, N_PLANETS, N_ASTEROIDS, N_SHIPS = 400, 7, 30, 3
Planet_colour = [random.uniform(0.15, 0.55), random.uniform(0.05, 0.75)]

BG_TOP = (0.18, 0.38, 0.92)
BG_BOT = (0.01, 0.05, 0.25)


stars, planets, asteroids, ships = [], [], [], []
last_time = 0.0


def rand_pos(depth_scale=1.0):
    return [
        random.uniform(-WORLD_W / 2,  WORLD_W / 2),
        random.uniform(-WORLD_H / 2,  WORLD_H / 2),
        random.uniform(-WORLD_D / 4,  WORLD_D / 4) * depth_scale,
    ]


def populate_scene():
    stars[:] = [rand_pos() for _ in range(N_STARS)]
    planets[:] = [[rand_pos(0.6), random.uniform(15.0, 35.0)] for _ in range(N_PLANETS)]
    asteroids[:] = [[rand_pos(),   random.uniform(4.0,  9.0)]  for _ in range(N_ASTEROIDS)]
    ships[:]     = [rand_pos() for _ in range(N_SHIPS)]



def init():
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

 
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    light_pos = (500.0, 600.0, 800.0, 1.0)
    glLightfv(GL_LIGHT0, GL_POSITION,  light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,   (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,   (0.2, 0.2, 0.35, 1.0))


    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    populate_scene()


def reshape(w, h):
    glViewport(0, 0, max(1, w), max(1, h))


def set_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, WINDOW_W / WINDOW_H, 1.0, 2000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 300.0,  
              0.0, 0.0, 0.0, 
              0.0, 1.0, 0.0)   



def draw_gradient_background():
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(*BG_TOP); glVertex2f(0, 1); glVertex2f(1, 1)
    glColor3f(*BG_BOT); glVertex2f(1, 0); glVertex2f(0, 0)
    glEnd()


    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)



def draw_starfield():
    glDisable(GL_LIGHTING)     
    glPointSize(2.5)
    glColor3f(1, 1, 1)
    glBegin(GL_POINTS)
    for x, y, z in stars:
        glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_planets():
    global Planet_colour
    for (x, y, z), r in planets:
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(Planet_colour[0], Planet_colour[1], 1.0)  
        glutSolidSphere(r, 50, 50)
        glPopMatrix()


def draw_asteroids():
    glColor3f(0.55, 0.55, 0.55)
    for (x, y, z), r in asteroids:
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef((x + y) * 3.5 % 360, 1, 1, 0)
        glutSolidSphere(r, 18, 18)
        glPopMatrix()


def draw_ships():
    glColor3f(0.8, 0.25, 0.25)
    for x, y, z in ships:
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef((x + z) * 11 % 360, 0, 1, 0)
        glutSolidCube(12)
        glPopMatrix()



def scroll_list(lst, pair=False, dt=0.016):
    if pair:
        for item in lst:
            item[0][0] -= SCROLL_S * dt
            if item[0][0] < -WORLD_W / 2:
                item[0][0] += WORLD_W
    else:
        for pos in lst:
            pos[0] -= SCROLL_S * dt
            if pos[0] < -WORLD_W / 2:
                pos[0] += WORLD_W


def idle():
    global last_time
    now = time.time()
    if last_time == 0.0:
        last_time = now
    dt = now - last_time
    last_time = now

    scroll_list(stars,     dt=dt)
    scroll_list(planets,   pair=True, dt=dt)
    scroll_list(asteroids, pair=True, dt=dt)
    scroll_list(ships,     dt=dt)

    glutPostRedisplay()



def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    draw_gradient_background()  

    set_camera()

    draw_starfield()
    draw_planets()
    draw_asteroids()
    draw_ships()

    glutSwapBuffers()



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"")

    init()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
