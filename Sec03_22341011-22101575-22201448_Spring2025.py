from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random, time, math


WINDOW_W, WINDOW_H = 1000, 800
WORLD_W, WORLD_H, WORLD_D = 800.0, 600.0, 800.0   
SPEEDS = {
    "stars":  50 * 0.1,
    "planets": 50 * 0.3,
    "asteroids": 50 * 0.5,
    "ships": 50 * 0.75,
    "obstacles": 50,
}

N_STARS, N_PLANETS, N_ASTEROIDS, N_SHIPS, N_OBSTACLES = 400, 5, 20, 3, 20
if N_OBSTACLES == 0:
    N_OBSTACLES = 30


BG_TOP = [0.18, 0.38, 0.92]
BG_BOT = [0.01, 0.05, 0.25]


stars, planets, asteroids, ships, obstacles = [], [], [], [], []
projectiles = []


paused = False
in_start_screen = True
last_time = 0.0
ufo_pos_x = -150.0
ufo_pos_y = 0
ufo_pos_z = 0.0
ufo_rotation_angle = 0.0
ufo_rotation_speed = 0.8
gun_rotation_angle = 0.0  
is_firing = False
is_first_person = False 

score = 0
gameOver = False
level = 1
lives = 3
bullet_fired = 0

bullets = []
bullet_speed = 2
health = 100

class Obstacle:
    global is_first_person
    def __init__(self, z_offset=0.0):
        self.x = WORLD_W / 2 + z_offset
        self.y = random.uniform(-100.0, 100.0)
        self.z = random.uniform(-50, 50)
        self.rotation = random.uniform(0, 360)
        self.type = random.choice(['A', 'B', 'C'])

        if self.type == 'A':
            self.scale = (2.0, 2.0, 1.8)
            self.rotation_speed = random.uniform(0.5, 1.0)
            base_radius = 6.0  # Sphere radius before scaling
            self.size = base_radius * max(self.scale[0], self.scale[2])

        elif self.type == 'B':
            self.scale = (15, 25, 10)
            self.rotation_speed = random.uniform(0.1, 0.3)
            self.rotation_speed = random.uniform(0.1, 0.3)
            base_radius = 1.5  # Approx bounding radius for a tetrahedron
            self.size = base_radius * max(self.scale)

        elif self.type == 'C':
            self.scale = (5, 5, 5)
            self.rotation_speed = random.uniform(1, 2)
            base_radius = 1.2  # Approx bounding radius for an icosahedron
            self.size = base_radius * max(self.scale)


    
        sx, sy, sz = self.scale
        self.size = base_radius * max(sx, sy, sz)


    def move(self, dt):
        if not paused:
            self.x -= 50 * 1.5 * dt
            if self.x < -WORLD_W / 2:
                self.x += WORLD_W + 300.0
                self.y = random.uniform(-100.0, 100.0)
                #self.z = random.uniform(-50, 50)
                self.type = random.choice(['A', 'B', 'C'])
            #self.rotation += self.rotation_speed

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(*self.scale)
        glRotatef(self.rotation, 0.3, 1.0, 0.7)
        if self.type == 'A':
            glColor3f(0.5, 0, 0.5)
            glutSolidSphere(6, 20, 20)
        elif self.type == 'B':
            glColor3f(0.85, 0.44, 0.84)
            glutSolidCube(1)
        elif self.type == 'C':
            glColor3f(1, 1, 1)
            gluCylinder(gluNewQuadric(), 3, 0, 5, 10, 10) # radius, top radius, height, slices, stacks
        glPopMatrix()

class Bullet:
    def __init__(self, x, y, z, angle):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.speed = bullet_speed * 0.85  # Optional tweak

        
    # def move(self):
    #     rad = math.radians(-self.angle)
    #     self.x += self.speed * math.cos(rad)
    #     self.z += self.speed * math.sin(rad)
    def move(self, delta_time=1.0):
        rad = math.radians(-self.angle)
        self.x += self.speed * delta_time * math.cos(rad)
        self.z += self.speed * delta_time * math.sin(rad)

        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle, 0, 1, 0)
        glColor3f(1, 0.0, 0.0)
        glScalef(2, 3, 2)
        glutSolidSphere(1.0, 8, 8)  
        glPopMatrix()

    def is_offscreen(self):
        return abs(self.x) > WORLD_W / 2 or abs(self.y) > WORLD_H / 2 or abs(self.z) > WORLD_D / 2


def check_bullet_collision(bullet):
    global score, gameOver
    if not gameOver:
        projectile_radius = 2.0
        for obs in obstacles:
            if obs.type == 'A':
            
                dx = (bullet.x - obs.x) / obs.scale[0]
                dy = (bullet.y - obs.y) / obs.scale[1]
                dz = (bullet.z - obs.z) / obs.scale[2]

                
                dist_squared = dx * dx + dy * dy + dz * dz
                if dist_squared < (6.0 + projectile_radius) ** 2:  # 6.0 is base_radius
                    # Handle collision
                    obs.x = WORLD_W + 300.0
                    obs.y = random.uniform(-100.0, 100.0)
                    obs.type = random.choice(['B', 'C'])
                    obs.rotation = random.uniform(0, 360)

                    bullets.remove(bullet)
                    score += 1
                    if score % 3 == 0:
                        update_level()
                    return True
            else:
               
                dx = bullet.x - obs.x
                dy = bullet.y - obs.y
                dz = bullet.z - obs.z
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)

                if dist < obs.size + projectile_radius:
                    # Handle collision
                    obs.x = WORLD_W + 300.0
                    obs.y = random.uniform(-100.0, 100.0)
                    obs.type = random.choice(['B', 'C'])
                    obs.rotation = random.uniform(0, 360)

                    bullets.remove(bullet)

                    score += 1
                    if score % 3 == 0:
                        update_level()
                    return True
        return False


def shoot_bullet():
    global bullets, ufo_pos_y, ufo_pos_z, ufo_pos_x, ufo_rotation_angle, gameOver

    if not gameOver:
        rad = math.radians(-gun_rotation_angle)
        bullet_x = ufo_pos_x
        bullet_z = ufo_pos_z
        bullet_y = ufo_pos_y

        bullet = Bullet(bullet_x, bullet_y, bullet_z, ufo_rotation_angle)
        bullets.append(bullet)

        # Checks for immediate collision
        check_bullet_collision(bullet)


def animate_bullet():
    global bullets
    steps = 4 
    new_bullets = []
    for bullet in bullets:
        collided = False
        for _ in range(steps):
            bullet.move(delta_time=0.9 / steps)
            if check_bullet_collision(bullet):
                collided = True
                break  
        if not collided and not bullet.is_offscreen():
            new_bullets.append(bullet)
    bullets[:] = new_bullets

def draw_paused_text():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WINDOW_W, 0, WINDOW_H, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 0)
    draw_text(WINDOW_W // 2 - 30, WINDOW_H // 2, "PAUSED", GLUT_BITMAP_HELVETICA_18)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def rand_pos(depth_scale=1.0, z_range=(-800.0, -300.0)):
    return [
        random.uniform(-WORLD_W / 2, WORLD_W / 2),
        random.uniform(-WORLD_H / 2, WORLD_H / 2),
        random.uniform(*z_range) * depth_scale,
    ]
    
def random_color():
    return (
        random.uniform(0.12, 0.55),
        random.uniform(0.05, 0.75),
        1.0
    )

def populate_scene():
    stars[:] = [rand_pos(z_range=(-500.0, 500.0)) for _ in range(N_STARS)]
    planets[:] = [[rand_pos(depth_scale=0.6, z_range=(-500.0, -200.0)), random.uniform(15.0, 35.0), random_color()] for _ in range(N_PLANETS)]
    asteroids[:] = [[rand_pos(z_range=(-700.0, -400.0)), random.uniform(4.0, 9.0)] for _ in range(N_ASTEROIDS)]
    ships[:] = [rand_pos(z_range=(-700.0, -500.0)) for _ in range(N_SHIPS)]

    spacing = 100.0
    
    for i in range(N_OBSTACLES):
        obstacles.append(Obstacle(z_offset=i * spacing))

def draw_ufo(pos_x=0, pos_y=0, pos_z=0, scale=1.0):
    glPushMatrix()
    glTranslatef(pos_x, pos_y, pos_z)
    glRotatef(ufo_rotation_angle, 0, 1, 0)  # Rotate UFO around Y-axis
    glScalef(scale, scale, scale)

    # UFO body
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glScalef(1.0, 0.25, 1.0)
    quadric = gluNewQuadric()
    gluSphere(quadric, 60.0, 32, 32)
    glPopMatrix()

    # Cockpit
    glColor3f(0.2, 0.5, 0.8)
    glPushMatrix()
    glTranslatef(0.0, 15.0, 0.0)
    glScalef(0.5, 0.3, 0.5)
    gluSphere(gluNewQuadric(), 60.0, 32, 16)
    glPopMatrix()

    # Bottom section
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0.0, -10.0, 0.0)
    glScalef(0.7, 0.15, 0.7)
    gluSphere(gluNewQuadric(), 60.0, 32, 16)
    glPopMatrix()
    
    #gun
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(60, 0, 0.0)
    glRotatef(90, 0, 1, 0)  # Rotate to align with X-axis
    gluCylinder(gluNewQuadric(), 2.0, 1.5, 30.0, 12, 4)  #radius, top radius, height, slices, stacks
    glPopMatrix()
    


    # Legs
    glColor3f(0.3, 0.3, 0.3)
    for i in range(3):
        angle = i * 120
        x = 40 * math.cos(math.radians(angle))
        z = 40 * math.sin(math.radians(angle))
        glPushMatrix()
        glTranslatef(x, -15.0, z)
        glRotatef(60, -z, 0, x)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5.0, 5.0, 30.0, 8, 8)
        glPopMatrix()
        glTranslatef(0.0, -30.0, 0.0)
        glColor3f(0.2, 0.2, 0.2)
        glutSolidSphere(8.0, 8, 8)
        glPopMatrix()
    

    glPopMatrix()
    
def health_bar():
    global health,lives,is_first_person,ufo_pos_x, ufo_pos_y, ufo_pos_z
    if lives==3:
        glColor3f(0, 1, 0)
    elif lives==2:
        glColor3f(1, 1, 0)
    elif lives==1:
        glColor3f(1, 0, 0)
    if not is_first_person:
        glPushMatrix()
        glTranslatef(100, 160, 0)
        glBegin(GL_QUADS)
        glVertex2f(-30, 0)
        glVertex2f(health, 0)
        glVertex2f(health, 5)
        glVertex2f(-30, 5)
        glEnd()
        glPopMatrix()
    elif is_first_person:
        glPushMatrix()
        glTranslatef(ufo_pos_x+250, ufo_pos_y+200, ufo_pos_z)
        glRotatef(-90, 0, 1, 0)  
        glBegin(GL_QUADS)
        glVertex2f(-30, 0)
        glVertex2f(health, 0)
        glVertex2f(health, 5)
        glVertex2f(-30, 5)
        glEnd()
        glPopMatrix()
    

def reshape(w, h):
    glViewport(0, 0, max(1, w), max(1, h))

def set_camera():
    """Set up the camera view based on current mode"""
    global is_first_person, ufo_pos_x, ufo_pos_y, ufo_pos_z
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    if is_first_person:
        # Use a wider field of view for cockpit perspective
        gluPerspective(75.0, WINDOW_W / WINDOW_H, 1.0, 2000.0)
    else:
        gluPerspective(60.0, WINDOW_W / WINDOW_H, 1.0, 2000.0)
        
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if is_first_person:
        
        gluLookAt(ufo_pos_x-10, ufo_pos_y+20, ufo_pos_z,  
                  ufo_pos_x, ufo_pos_y+20, ufo_pos_z,       
                  0.0, 1.0, 0.0)        
    else:
        
        gluLookAt(0.0, 0.0, 300.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

def draw_gradient_background():
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1) 

   
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    
    glBegin(GL_QUADS)
    glColor3f(*BG_TOP)      # Top color
    glVertex2f(0, 1)
    glVertex2f(1, 1)
    glColor3f(*BG_BOT)      # Bottom color
    glVertex2f(1, 0)
    glVertex2f(0, 0)
    glEnd()

    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_starfield():
    """Draw the stars in the background"""
    
    glPointSize(2.5)
    glColor3f(1, 1, 1)
    glBegin(GL_POINTS)
    for x, y, z in stars:
        glVertex3f(x, y, z)
    glEnd()
    
def draw_planets():
    """Draw the planets"""
    for (x, y, z), r, color in planets:
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(*color)
        glutSolidSphere(r, 50, 50)
        glPopMatrix()

def draw_asteroids():
    """Draw the asteroids"""
    glColor3f(0.05, 0.05, 0.05)
    for (x, y, z), r in asteroids:
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef((x + y) * 3.5 % 360, 1, 1, 0)
        glutSolidSphere(r, 18, 18)
        glPopMatrix()

def draw_ships():
    """Draw the enemy ships"""
    glColor3f(0.8, 0.25, 0.25)
    for x, y, z in ships:
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef((x + z) * 11 % 360, 0, 1, 0)
        glutSolidCube(12)
        glPopMatrix()

def draw_obstacles():
    """Draw all obstacles"""
    for obs in obstacles:
        obs.draw()

def draw_bullets():
    """Draw all active bullets"""
    for bullet in bullets:
        bullet.draw()

def check_collisions():
    global bullets, obstacles, score, lives, ufo_pos_x, ufo_pos_y, ufo_pos_z, health, gameOver, level

    if not gameOver:
        ufo_pos = [ufo_pos_x, ufo_pos_y, ufo_pos_z]
        projectile_radius = 5
        ufo_radius = 20.0
    
        
        for obs in obstacles:
            obs_pos = [obs.x, obs.y, obs.z]
            obstacle_radius = obs.size
            
            # --- Bullet vs Obstacle ---
            for bullet in bullets:
                if bullet.is_offscreen():
                    continue
                bullet_pos = [bullet.x, bullet.y, bullet.z]
                dx = bullet_pos[0] - obs_pos[0]
                dy = bullet_pos[1] - obs_pos[1]
                dz = bullet_pos[2] - obs_pos[2]
                dist_proj = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if dist_proj < projectile_radius + obstacle_radius:
                    # Mark obstacle and bullet for removal
                    #obstacles.remove(obs)

                    # Respawn obstacle instead of removing
                    obs.x = WORLD_W + 300.0  # move it to far right
                    obs.y = random.uniform(-100.0, 100.0)
                    obs.type = random.choice(['B', 'C'])  # or use ['A', 'B', 'C'] if desired
                    obs.rotation = random.uniform(0, 360)

                    bullets.remove(bullet)
                    score += 1
                    if score % 3 == 0 and score != 0:
                        update_level()
                    print(f"Score: {score}  Level: {level}")
                    break  # Exit after hitting one bullet (only one hit per obstacle)

            # --- UFO vs Obstacle ---
            dx = ufo_pos[0] - obs_pos[0]
            dy = ufo_pos[1] - obs_pos[1]
            dz = ufo_pos[2] - obs_pos[2]
            dist_ufo = math.sqrt(dx**2 + dy**2 + dz**2)

            if dist_ufo < ufo_radius + obstacle_radius:
                obstacles.remove(obs)
                lives -= 1
                health -= 40
                print(f"UFO Hit! Lives remaining: {lives}  Health: {health}")
                if lives <= 0:
                    gameOver = True
                    print("GAME OVER")
                break  # Exit after hitting one obstacle (only one hit per frame)
    
def update_level():
    global score, level, BG_BOT, BG_TOP
    level += 1
    for i in range(3):
            BG_TOP[i] = min(1.0, BG_TOP[i] + 0.05)
            BG_BOT[i] = min(1.0, BG_BOT[i] + 0.02)
 
def scroll_list(lst, pair=False, dt=0.016, speed=50):
    if pair:
        for item in lst:
            item[0][0] -= speed * dt
            if item[0][0] < -WORLD_W / 2:
                item[0][0] += WORLD_W
    else:
        for pos in lst:
            pos[0] -= speed * dt
            if pos[0] < -WORLD_W / 2:
                pos[0] += WORLD_W

def idle():
    global last_time, ufo_rotation_angle, paused, gameOver
    if paused:
        glutPostRedisplay()
        return
    if not gameOver and not paused:
        now = time.time()
        if last_time == 0.0:
            last_time = now
        dt = now - last_time
        last_time = now

        scroll_list(stars, dt=dt, speed=SPEEDS["stars"])
        scroll_list(planets, pair=True, dt=dt, speed=SPEEDS["planets"])
        scroll_list(asteroids, pair=True, dt=dt, speed=SPEEDS["asteroids"])
        scroll_list(ships, dt=dt, speed=SPEEDS["ships"])

        for obs in obstacles:
            obs.move(dt)

        animate_bullet()
        check_collisions()


        glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_gradient_background()
    set_camera()
    if not gameOver:
        health_bar()
        draw_starfield()
        draw_planets()
        draw_asteroids()
        draw_ships()
        draw_obstacles()

        draw_bullets()
        draw_ufo(pos_x=ufo_pos_x, pos_y=ufo_pos_y, pos_z=ufo_pos_z, scale=0.4)
    
        if in_start_screen:
            draw_start_screen()
            return
        
        if paused:
            if is_first_person:
                glColor3f(1, 1, 0)
                draw_text(WINDOW_W // 2 - 30, WINDOW_H // 2, "PAUSED", GLUT_BITMAP_HELVETICA_18)
                glutSwapBuffers()
                return
            else:
                draw_paused_text()
                glutSwapBuffers()
                return
 
    if gameOver:
        draw_end_screen()
        return
    
    glutSwapBuffers()
    
def restart():
    global stars, planets, asteroids, ships, obstacles, bullets, projectiles, BG_BOT, BG_TOP
    global score, lives, health, gameOver, ufo_pos_x, ufo_pos_y, ufo_pos_z
    global ufo_rotation_angle, gun_rotation_angle, is_firing, last_time, paused

    stars.clear()
    planets.clear()
    asteroids.clear()
    ships.clear()
    obstacles.clear()
    bullets.clear()
    projectiles.clear()

    paused = False
    score = 0
    lives = 3
    health = 100
    gameOver = False
    ufo_pos_x = -150.0
    ufo_pos_y = 0
    ufo_pos_z = 0.0
    ufo_rotation_angle = 0.0
    gun_rotation_angle = 0.0
    is_firing = False
    last_time = 0.0
    BG_TOP = [0.18, 0.38, 0.92]
    BG_BOT = [0.01, 0.05, 0.25]

    populate_scene()

def draw_start_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WINDOW_W, 0, WINDOW_H, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(0.05, 0.1, 0.3)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_W, 0)
    glVertex2f(WINDOW_W, WINDOW_H)
    glVertex2f(0, WINDOW_H)
    glEnd()

    glColor3f(1, 1, 1)
    draw_text(WINDOW_W//2 - 60, WINDOW_H//2, "Flappy Aircraft", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(WINDOW_W//2 - 70, WINDOW_H//2 - 30, "Click anywhere to start", GLUT_BITMAP_HELVETICA_12)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

def draw_end_screen():
    
    global score, level
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WINDOW_W, 0, WINDOW_H, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(0.05, 0.1, 0.3)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_W, 0)
    glVertex2f(WINDOW_W, WINDOW_H)
    glVertex2f(0, WINDOW_H)
    glEnd()

    glColor3f(1, 1, 1)
    draw_text(WINDOW_W//2 - 60, WINDOW_H//2, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(WINDOW_W//2 - 70, WINDOW_H//2 - 80, f"Score: {score}, Level: {level}", GLUT_BITMAP_HELVETICA_12)
    draw_text(WINDOW_W//2 - 70, WINDOW_H//2 - 30, "Click anywhere to restart", GLUT_BITMAP_HELVETICA_12)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()
    
def draw_text(x, y, text, font):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
        
def key_pressed(key, x, y):
    global ufo_pos_y, gun_rotation_angle, ufo_rotation_angle, ufo_rotation_speed, is_first_person,  ufo_pos_z, rotation_speed
    offset = 10.0
    rotation_speed = 5.0  # Degrees to rotate per key press

    if key == GLUT_KEY_UP:  # Move UFO up
        ufo_pos_y += 5
        ufo_pos_y = min(ufo_pos_y, (WORLD_H-280) / 2 - offset)

    elif key == GLUT_KEY_DOWN:  # Move UFO down
        ufo_pos_y -= 5
        ufo_pos_y = max(ufo_pos_y, (-WORLD_H+295) / 2 + offset)
        
    if  is_first_person:
        if key == GLUT_KEY_RIGHT:  
            ufo_pos_z += 5
            ufo_pos_z = min(ufo_pos_z, (WORLD_W-580) / 2 - offset)
                
        elif key == GLUT_KEY_LEFT: 
            ufo_pos_z -= 5
            ufo_pos_z = max(ufo_pos_z, (-WORLD_W+580) / 2 - offset)

def keyboard(key, x, y):
    global is_firing, is_first_person, paused, last_time
    
    if key == b' ':

        shoot_bullet()
        is_firing = True
    
    elif key == b'f' or key == b'F': 
        is_first_person = not is_first_person
        
    elif key in [b'p', b'P']:
        paused = not paused
        last_time = time.time()
        
    elif key == b'q' or key == b'\x1b':  
        glutLeaveMainLoop()
        
def mouse_listener(button, state, x, y):
    global in_start_screen, gameOver
    if in_start_screen and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        in_start_screen = False
    if gameOver and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        gameOver = False
        restart()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Flappy Aircraft")
    populate_scene()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(key_pressed)
    glutMouseFunc(mouse_listener)

    glutMainLoop()


if __name__ == "__main__":
    main()