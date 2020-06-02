from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, time
import math

class gameState:
    currentState = 1
    playing = 0
    start = 1
    reset = 2
    gameover = 3
    clickedP = False

    def updateState():
        if gameState.currentState == gameState.start:
            Text.drawString(" A S T E R O I D S", 1500, 1850, 0.4, 3)
            Text.drawString("  P R E S S  P  T O  P L A Y ", 3250, 1650, 0.2, 3)
            Text.drawString(" P R E S S   E S C   T O  E X I T", 3150, 3450, 0.2, 3)
            Text.drawString("CREDITS", 200, 800, 0.2, 3)
            Text.drawString("MOSTAFA ELSAYED MOHAMED REDA ABOELNAGA", 400, 1250, 0.1, 3, 2)
            Text.drawString("MOSTAFA MOHAMED RAGAB MOHAMED", 400, 1050, 0.1, 3, 2)
            Text.drawString("MOAZ AHMED ABDELSALAM IBRAHIM", 400, 850, 0.1, 3, 2)
            Text.drawString("RAWAN ELWY ALI HAMED HUSSIEN ", 400, 650, 0.1, 3, 2)
            spawnBlocks.draw()

            if gameState.clickedP:
                gameState.currentState = gameState.reset
                gameState.clickedP = False
                

        elif gameState.currentState == gameState.gameover:
            Score.updateMax()
            Text.drawString(" G A M E O V E R", 1525, 1850, 0.4, 3)
            Text.drawString(" YOUR SCORE IS :  " + str(Score.currentScore), 1500, 1550, 0.4, 3)
            Text.drawString(" HIGHEST SCORE :  " + str(Score.maxScore), 1500, 1350, 0.4, 3)
            Text.drawString("   P R E S S  P  T O  P L A Y  A G A I N ", 2750, 1650, 0.2, 3)
            Text.drawString("   P R E S S  E S C  T O  E X I T ", 3050, 1350, 0.2, 3)
            
            if gameState.clickedP == True:
                gameState.currentState = gameState.reset
                gameState.clickedP = False

        elif gameState.currentState == gameState.reset:
            spawnBlocks.reset()
            Player.reset()
            Score.resetCurrent()
            Lives.reset()
            gameState.currentState = gameState.playing


        elif gameState.currentState == gameState.playing:
            Player.draw()
            Player.shootBullets()
            spawnBlocks.draw()
            Score.updateScore()
            Lives.updateLives()


class Block:
    direction = playerPosition = []
    x = y = z = killZ = 0
    kill  = bulletCollided = split = False
    visible = True
    scaleFactor = 1
    blockID = None
    
    def __init__(self, playerX, playerY, x, y, z, blockID, scaleFactor):
        self.playerPosition = [playerX, playerY]
        self.x = x
        self.y = y
        self.z = z
        self.blockID = blockID
        self.scaleFactor = scaleFactor
        self.direction = [self.playerPosition[0] - self.x, self.playerPosition[1] - self.y]

    def updateMovement(self):
        self.x += 0.002*self.direction[0]
        self.y += 0.002*self.direction[1]

        # check if blocks disappeared, resets the postition
        if self.x >= 4.5 or self.x <= -4.5 or self.y >= 2.5 or self.y <= -2.5:
            if self.blockID == 1:
                    self.x = random.randrange(-4, 4)
                    self.y = random.randrange(2,5)
            elif self.blockID == 2:
                    self.x = random.randrange(-7, -4)
                    self.y = random.randrange(-2, 2)

    def draw(self):
        if self.visible:
            self.updateMovement()
            self.killAnimation()

            if not self.bulletCollided:
                self.detectBulletsCollision()
                self.splitBlock()
            if Player.collided:
                now = time.time()
                if now - Player.collisionTime >= 2:
                    Player.collided = False
            else:
                self.detectPlayerCollision()

            glPushMatrix()
            glLoadIdentity()

            if Player.darkMode:
                glColor(1,1,1,1)
            else:
                glColor(0,0,0,1)
            
            
            glTranslate(0, 0, self.killZ)
            glTranslate(self.x, self.y, self.z)
            
            glScale(self.scaleFactor, self.scaleFactor, 0)
            glScale(0.1, 0.1, 0)
            if Player.darkMode:
                glutWireDodecahedron()
            else:
                glutSolidDodecahedron()
            glPopMatrix()

    def detectBulletsCollision(self):
        for bullet in Player.renderedBullets:
            distance = math.sqrt((bullet.bulletPosition[0] - self.x)**2 + \
                                 (bullet.bulletPosition[1] - self.y)**2)
            if distance <= 0.212:
                self.bulletCollided = True
                bullet.visible = False

                self.split = True
                Score.currentScore += 1
                if Score.currentScore == 100:
                    Player.darkMode = True
                    
    
    def detectPlayerCollision(self):
        distance = math.sqrt((Player.xPos - self.x)**2 + (Player.yPos - self.y)**2)
        if distance <= 0.33*self.scaleFactor:
            Player.collisionTime = time.time()
            Player.collided = True
            Player.gradientUp = True
            Lives.totalLives -= 1
            if Lives.totalLives == 0:
                Player.kill = True
                gameState.currentState = gameState.gameover
                   
    def killAnimation(self):
        if self.kill:
            self.scaleFactor -= 0.1
            if self.scaleFactor <= 0:
                self.kill = False
                if self.blockID == 1:
                    self.x = random.randrange(-4, 4)
                    self.y = random.randrange(2,5)
                elif self.blockID == 2:
                    self.x = random.randrange(-7, -4)
                    self.y = random.randrange(-2, 2)
                self.scaleFactor = 1
                self.bulletCollided = False

    def splitBlock(self):
        if self.split:
            if self.scaleFactor == 1:
                self.scaleFactor = 0.5
                newBlock = Block(Player.xPos, Player.yPos, self.x + 0.2, self.y + 0.3, self.z, self.blockID, 0.5)
                
                spawnBlocks.spawned.append(newBlock)
                self.split = False
                self.bulletCollided = False
            else:
                self.split = False
                self.kill = True
        

class spawnBlocks:
    blocksNumber = 15
    spawned = []

    def init():
        for i in range(spawnBlocks.blocksNumber//2):
            block = Block(Player.xPos, Player.yPos, random.randrange(-4, 4),random.randrange(2, 5) , Player.zPos, 1, 1)
            spawnBlocks.spawned.append(block)
        for i in range(spawnBlocks.blocksNumber//2):
            block = Block(Player.xPos, Player.yPos, random.randrange(-7, -4),random.randrange(-2, 2) , Player.zPos, 2 , 1)
            spawnBlocks.spawned.append(block)

    def draw():
        for block in spawnBlocks.spawned:
            block.draw()
    def reset():
        spawnBlocks.spawned.clear()
        spawnBlocks.init()


class Bullet:
    firePosition = bulletPosition = [0, 0]
    direction = [0, 0]
    speed = 0.05
    visible = False

    def __init__(self, x, y, z, angle):
        self.firePosition = [x, y]
        self.direction = [math.cos((angle + 90) * math.pi / 180), math.sin((angle + 90) * math.pi / 180) ] 
        self.z = z
        self.visible = True

    def updateMovement(self, step = 0.05):
        self.firePosition[0] += step * self.direction[0]
        self.firePosition[1] += step * self.direction[1]
        self.bulletPosition = self.firePosition

        distance = math.sqrt((self.bulletPosition[0] - Player.xPos)**2 + (self.bulletPosition[1] - Player.yPos)**2 )
        if distance >= 9: #longest path
            self.visible = False

    def draw(self):
        if self.visible:
            self.updateMovement(self.speed)

            glPushMatrix()
            glLoadIdentity()

            if Player.darkMode:
                glColor(1-Player.redColor,1,1,1)
            else:
                glColor(Player.redColor,0,0,1)
            
            glTranslate(self.bulletPosition[0], self.bulletPosition[1] ,self.z)
            glutSolidCube(0.03)

            glPopMatrix()
        else:
            # throws bullets away
            self.firePosition[0] = 100
            self.firePosition[1] = 100


class Display:
    width = 1280
    height = 720
    title = b"Asteroids Game Project"
    FPS = 200
    fullScreen = False
    def init():
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(Display.width, Display.height)
        glutCreateWindow(Display.title)

        glutSetCursor(GLUT_CURSOR_CROSSHAIR)
        glutFullScreen()
        glutDisplayFunc(render)
        
        glutPassiveMotionFunc(handleMouse)
        glutKeyboardFunc(handleKeyboard)

        Display.perspectiveProjection()
        Display.setCamera()

    def perspectiveProjection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50,Display.width/Display.height, 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def orthographicProjection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, Display.width, 0, Display.height)
        glMatrixMode(GL_MODELVIEW)

    def setCamera():
        glLoadIdentity()
        gluLookAt(0, 0, 10,
                  0, 0, -5,
                  0, 1, 0 )


class Score:
    currentScore = maxScore = 0

    def updateScore():
        Text.drawString("Score : ", 300, 3200, 0.3)
        Text.drawString(str(Score.currentScore), 900, 3200, 0.3)
        Text.drawString("HIGH SCORE : ",610,6100,0.15)
        Text.drawString(str(Score.maxScore),1700,6100,0.15)

    def updateMax():
        Score.maxScore = max(Score.maxScore,Score.currentScore)
    
    def resetCurrent():
        Score.currentScore = 0


class Text:
    def drawString(text, xPos, yPos, scaleFactor, lineWidth = 1, fontID = 1):
        
        scaleFactor *= Display.width/1920

        text_encoded = text.encode()

        glLineWidth(lineWidth)

        if Player.darkMode:
            glColor(1,1,1,1)
        else:
            glColor(0,0,0,1)
        

        Display.orthographicProjection()
        glPushMatrix()
        glLoadIdentity()

        glScale(scaleFactor,scaleFactor,1)
        glTranslate(xPos, yPos, 1) 
        
        if fontID == 1:
            glutStrokeString(GLUT_STROKE_ROMAN, text_encoded)
        else:
            glutStrokeString(GLUT_STROKE_MONO_ROMAN, text_encoded)

        Display.perspectiveProjection()
        glPopMatrix()

class Lives:
    totalLives = 3

    def updateLives():
        Text.drawString("Lives : ", 575, 5500, 0.16)
        Text.drawString(str(Lives.totalLives), 1200, 5500, 0.16)

    def reset():
        Lives.totalLives = 3 

def handleMouse(x, y):
    mouseX = x
    mouseY = y
    mouseX -= Display.width/2
    mouseY -= Display.height/2
    mouseY *= -1

    mouseX *= (8/(Display.width))
    mouseY *= (4.2/(Display.height))

    direction = [mouseX - Player.xPos, mouseY - Player.yPos]
    angle = math.atan2(direction[0], direction[1])
    Player.rot_angle = -(angle*180/math.pi)
    

def handleKeyboard(key, x, y):
    now = time.time()
    if key == b"d" or key == b"D":
        Player.xPos += 0.1
        if Player.xPos >= 4.5:
            Player.xPos -=  9
        
    elif key == b"a" or key == b"A":
        Player.xPos -= 0.1
        if Player.xPos <= -4.5:
            Player.xPos += 9
    
    elif key == b"w" or key == b"W":
        Player.yPos += 0.1
        if Player.yPos >= 2.5:
            Player.yPos -= 5

    elif key == b"s" or key == b"S":
        Player.yPos -= 0.1
        if Player.yPos <= -2.5:
            Player.yPos += 5

    elif key == b" " and now - Player.lastShotTime >= Player.fireRate:
        Player.newBullet()
        Player.lastShotTime = now
        if Player.spaceNotification:
            Player.spaceNotification = False

    elif key == b"p" or key == b"P":
        if gameState.currentState != gameState.playing:
            gameState.clickedP = True

    elif key == b"\x1b": #escape button
        sys.exit(0)


class Player:
    firedBullets = []
    renderedBullets = []
    rot_angle = 0
    zPos = -5
    xPos = yPos = 0
    moveRight = moveLeft = moveUp = moveDown = False
    nextPositionX = nextPositionY = 0
    fireRate = 0.1 #in seconds
    lastShotTime = 0
    kill = gradientUp = gradientDown = collided = False           
    visible = True
    scaleFactor = 1
    redColor = 0
    collisionTime = 0
    darkMode = False
    spaceNotification = True

    def init():
        if Player.darkMode:
            glColor(1-Player.redColor,1,1,1)
        else:
            glColor(Player.redColor,0,0,1)
        glBegin(GL_POLYGON)
        glVertex3f(0, 0, 0)
        glVertex3f(0.5, -0.5, 0)
        glVertex3f(0, 1, 0)
        glVertex3f(-0.5, -0.5, 0)

        glEnd()

    def draw():
        if Player.visible:
            Player.notifyPlayer()
            Player.killPlayer()
            Player.gradientAnimation()
            glPushMatrix()
            glLoadIdentity()
            glTranslate(Player.xPos, Player.yPos, Player.zPos)
            glRotate(Player.rot_angle, 0, 0, 1)
            glScale(0.25, 0.25, 0.25)
            glScale(Player.scaleFactor, Player.scaleFactor, 0)
            Player.init()
            glPopMatrix()

    def newBullet():
        angle = Player.rot_angle % 360
        newBullet = Bullet(Player.xPos, Player.yPos, Player.zPos, Player.rot_angle)
        Player.firedBullets.append(newBullet)
        Player.renderedBullets = [bullet for bullet in Player.firedBullets if bullet.visible]
        Player.firedBullets = Player.renderedBullets


    def shootBullets():
        for bullet in Player.renderedBullets:
            bullet.draw()
    
    def killPlayer():
        if Player.kill:
            Player.scaleFactor -= 0.1
            if Player.scaleFactor <= 0:
                Player.kill = False
                Player.visible = False
                gameState.currentState = gameState.gameover

    def notifyPlayer():
        if Player.spaceNotification:
            Text.drawString("PRESS SPACE TO SHOOT ", 7500, 200, 0.2)

    def gradientAnimation():
        if Player.gradientUp:
            Player.redColor += 0.025
            if Player.redColor >= 0.8:
                Player.gradientDown = True
                Player.gradientUp = False
        if Player.gradientDown:
            Player.redColor -= 0.025
            if Player.redColor <= 0 :
                Player.gradientDown = False
                Player.gradientUp = False

    def reset():
        Player.firedBullets = []
        Player.renderedBullets = []
        Player.rot_angle = 0
        Player.zPos = -5
        Player.xPos = Player.yPos = 0
        Player.kill = Player.gradientUp = Player.gradientDown = Player.collided = False           
        Player.visible = True
        Player.scaleFactor = 1
        Player.redColor = 0
        Player.darkMode = False
        Player.spaceNotification = True


def timer(v):
    render()
    glutTimerFunc(1000//Display.FPS,timer,0)


def render():
    if Player.darkMode:
        glClearColor(0, 0, 0, 1)
    else:
        glClearColor(1, 1, 1, 1)
    
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    Display.width = glutGet(GLUT_WINDOW_WIDTH)
    Display.height = glutGet(GLUT_WINDOW_HEIGHT)

    gameState.updateState()

    glutSwapBuffers()

def main():
    Display.init()   
    spawnBlocks.init()
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

main()


