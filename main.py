from tkinter import *
from PIL import ImageTk, Image
import random, os, time

#items/GUI inv display
window = Tk()
keys = [False,False,False,False,False,False, False, False, False, False, False]# w a s d " " "tab" 1 2 3 4
def clamp(value, min, max):
	if value > max:
		return max
	elif value < min:
		return min
	return value
def keyDown(event):
	global keys,loadTests
	if event.char == "w":
		keys[0] = True
	elif event.char == "a":
		keys[1] = True
	elif event.char == "s":
		keys[2] = True
	elif event.char == "d":
		keys[3] = True
	elif event.char == " ":
		keys[4] = True
	elif event.char == "\t":
		keys[5] = True
	elif event.char == "1":
		keys[6] = True
	elif event.char == "2":
		keys[7] = True
	elif event.char == "3":
		keys[8] = True
	elif event.char == "4":
		keys[9] = True
def keyUp(event):
	global keys,loadTests
	if event.char == "w":
		keys[0] = False
	elif event.char == "a":
		keys[1] = False
	elif event.char == "s":
		keys[2] = False
	elif event.char == "d":
		keys[3] = False
	elif event.char == " ":
		keys[4] = False
	elif event.char == "\t":
		keys[5] = False
	elif event.char == "1":
		keys[6] = False
	elif event.char == "2":
		keys[7] = False
	elif event.char == "3":
		keys[8] = False
	elif event.char == "4":
		keys[9] = False
velY = 0
jumping = False
def keyUpdate():
	global velX, velY, jumping,UI
	velY -= .7
	x = 0
	playerSpeed = 4 #default was 4
	if keys[1] == True:
		x += playerSpeed
	if keys[3] == True:
		x -= playerSpeed
	for block in blockList:
		if block.testCollision(x,0):
			x=0
	if keys[4] == True and jumping == False:
		jumping = True
		tVelY = velY
		for block in blockList:
			if block.testCollision(0,velY):
				if block.type == "jumpJuice":
					tVelY = 14
				else:
					tVelY = 8
		velY = tVelY
	elif velY < -15:
		velY = -15
	readyToJump = False
	for block in blockList:
		running = True
		while running:
			if block.testCollision(x,velY):
				if velY < 0:
					velY += .5
					readyToJump = True
					jumping = False
				elif velY > 0:
					velY -= .5
			else:
				running = False
	if readyToJump == False:
		jumping = True
	for block in blockList:
		block.move(x,round(velY))
	for index in range(len(itemList)-1, -1, -1):
		item = itemList[index]
		item.move(x, round(velY))
		if item.testCollision(player.x1, player.y1, player.x1+16, player.y1+56) and playerInventory.addItem(item.imgType):
			print(playerInventory.slots)
			item.pickUp()
	#infi gen
	max1 = max(block.x1 for block in blockList if block.type != "leaves")
	min1 = min(block.x1 for block in blockList if block.type != "leaves")
	if min1 > -60:
		player.genLeft(min1)
	if max1 < 380:
		player.genRight(max1)
	#UI set Up
	selected = 0
	if keys[6]:
		selected = 1
	if keys[7]:
		selected = 2
	if keys[8]:
		selected = 3
	if keys[9]:
		selected = 4
	playerInventory.select(selected)
	playerInventory.setTop()
def callbackRight(event):
	#test
	kg = float("+inf")
	for block in blockList:
		if block.type == "bedrock":
			if block.y1 < kg:
				kg = block.y1
	#print("PlayerY: "+str((kg-(player.y1+32))/32))
	#test
	x = event.x
	y = event.y
	placeBlock = True
	for block in blockList:
		if block.testClick(x, y):
			placeBlock = False
	if placeBlock and y > kg-120*32:
		yBed = float("inf")
		xPlace = -9999
		for block in [block for block in blockList if block.type == "bedrock"]:
			if yBed > block.y1:
				yBed = block.y1
			if block.x1 < x and block.x1+32 > x:
				xPlace = block.x1
		yPlace = int(yBed - int((yBed-y)/32+1)*32)
		if(xPlace != -9999):
			if 150 > xPlace-32 and 150 < xPlace+16 and 150 > yPlace-56 and 150 < yPlace+32:
				pass
			else:
				if playerInventory.removeItem():
					blockList.append(Block(xPlace, yPlace, playerInventory.itemSelected))
def callback(event):
	x = event.x
	y = event.y
	for block in blockList:
		if block.testClick(x, y):
			block.clicked()
#Canvas setup
canvas = Canvas(window, width=350, height=350)
allBlockImg = {}
allItemImg = {}
for file in os.listdir("resources/blocks"):
	allBlockImg[file.replace(".png", "")] = ImageTk.PhotoImage(Image.open(r"resources/blocks/"+file))
	allItemImg[file.replace(".png", "")] = ImageTk.PhotoImage(Image.open(r"resources/blocks/"+file).resize((8,8)))
PlayerImg = ImageTk.PhotoImage(Image.open(r"resources/Player.png"))
SlotImg = ImageTk.PhotoImage(Image.open(r"resources/inventorySlot.png"))
SlotSelectedImg = ImageTk.PhotoImage(Image.open(r"resources/inventorySlotSelected.png"))
	#window.bind('<Motion>', motion)
window.bind("<KeyPress>", keyDown)
window.bind("<KeyRelease>", keyUp)
window.title("Minecraft Python Edition")
canvas.bind("<Button-1>", callback)
canvas.bind("<Button-3>", callbackRight)
canvas.pack()
canvas.focus_set()
#classes
class Player:
	def __init__(self):
		self.x1 = 166
		self.y1 = 150
		self.x2 = self.x1 + 16
		self.y2 = self.y1 + 56
		self.treeCounterL = random.randint(1, 10)
		self.treeCounterR = random.randint(1, 10)
		self.info = canvas.create_image(self.x1,self.y1, anchor=NW, image=PlayerImg)
	def resetImg(self):
		canvas.delete(self.info)
		self.info = ""
		self.info = canvas.create_image(self.x1,self.y1, anchor=NW, image=PlayerImg)
	def findXblock(self):
		for block in blockList:
			if block.x1 <= self.x1 and block.x1+32 > self.x1:
				return block.x1
	def spawn(self):
		min = 999999999
		for block in blockList:
			if block.x1 == 162:
				if min > block.y1:
					min = block.y1
		change = 206 - min
		for block in blockList:
			block.move(0, change)
	def genLeft(self, min1):
		if len(blockDeadListL) > 0:
			y = max([block.y1 for block in blockList])
			for index in range(0,len(blockDeadListL[len(blockDeadListL)-1])):
				type1 = blockDeadListL[len(blockDeadListL)-1][index]
				if type1 != "":
					blockList.append(Block(-90,y,type1))
				y-=32
			blockDeadListL.pop(len(blockDeadListL)-1)
		else:
			self.treeCounterL -= 1
			tree = False
			if self.treeCounterL == 0:
				self.treeCounterL = random.randint(5,15)
				tree = True
			min2 = 999999999
			for block in blockList:
				if block.x1 == min1 and block.type == "grass":
					if min2 > block.y1:
						min2 = block.y1
			min2 += 32 * random.randint(-1,1)*random.randint(0,1)
			player.genChunk(min1-32, min2, tree)

		#unload
		unloadList = []
		for block in range(128):
			unloadList.append("")
		YorN = False
		max1 = max([block.y1 for block in blockList])
		for count in range(len(blockList)-1, -1, -1):
			block = blockList[count]
			if block.x1 == 454:
				index = int(round((max1-block.y1)/32))
				unloadList[index] = block.type
				block.delSelf()
				YorN = True
		if YorN == True:
			blockDeadListR.append(unloadList)
			
	def genRight(self, max1):
		if len(blockDeadListR) > 0:
			y = max([block.y1 for block in blockList])
			for index in range(0,len(blockDeadListR[len(blockDeadListR)-1])):
				type1 = blockDeadListR[len(blockDeadListR)-1][index]
				if type1 != "":
					blockList.append(Block(410,y,type1))
				y-=32
			blockDeadListR.pop(len(blockDeadListR)-1)
		else:
			self.treeCounterR -= 1
			tree = False
			if self.treeCounterR == 0:
				self.treeCounterR = random.randint(5,15)
				tree = True
			max2 = -999999999
			for block in blockList:
				if block.x1 == max1 and block.type == "grass":
					if max2 < block.y1:
						max2 = block.y1
			max2 += 32 * random.randint(-1,1)*random.randint(0,1)
			player.genChunk(max1+32, max2, tree)
		#unload
		unloadList = []
		for block in range(128):
			unloadList.append("")
		YorN = False
		max1 = max([block.y1 for block in blockList])
		for count in range(len(blockList)-1, -1, -1):
			block = blockList[count]
			if block.x1 == -134:
				index = int(round((max1-block.y1)/32))
				unloadList[index] = block.type
				block.delSelf()
				YorN = True
		if YorN == True:
			blockDeadListL.append(unloadList)

	def genChunk(self, x, y, tree):
		y = clamp(y, max([block.y1 for block in blockList])-32*90, max([block.y1 for block in blockList])-32*15)
		#Tree
		yLog = y-32
		xLog = x-32
		if tree:
			for log in range(random.randint(1,3)):
				blockList.append(Block(x,yLog, "log"))
				yLog -=32
			blockList.append(Block(xLog,yLog, "leaves"))
			blockList.append(Block(xLog+32,yLog, "leaves"))
			blockList.append(Block(xLog+64,yLog, "leaves"))
			blockList.append(Block(xLog,yLog-32, "leaves"))
			blockList.append(Block(xLog+32,yLog-32, "leaves"))
			blockList.append(Block(xLog+64,yLog-32, "leaves"))
			blockList.append(Block(xLog+32,yLog-64, "leaves"))

		#ground
		blockList.append(Block(x, y, "grass"))
		for dirt in range(3):
			y += 32
			blockList.append(Block(x,y, "dirt"))
		while y < max([block.y1 for block in blockList])-170:
			y += 32
			if y<max([block.y1 for block in blockList])-170:
				if random.randint(0,30) != 0:
					blockList.append(Block(x,y, "stone"))
				else:
					blockList.append(Block(x,y, "coal"))
			else:
				if random.randint(0,30) == 0:
					blockList.append(Block(x,y, "jumpJuice"))
				else:
					if random.randint(0,30) != 0:
						blockList.append(Block(x,y, "stone"))
					else:
						blockList.append(Block(x,y, "coal"))
		y+=32
		for amount in range(5):
			blockList.append(Block(x,y, "bedrock"))
			y += 32
		#Fun display
		total = 0
		for chunk in range(len(blockDeadListL)):
			total += len([block for block in blockDeadListL[chunk] if block != ""])
		for chunk in range(len(blockDeadListR)):
			total += len([block for block in blockDeadListR[chunk] if block != ""])
		print("All saved blocks = "+str(len(blockList)+total) +", Loaded blocks = "+str(len(blockList)))
class Block:
	def __init__(self, x, y, type1):
		self.x1 = x
		self.y1 = y
		self.type = type1
		self.breakable = True
		self.collision = False
		self.setType()
		player.resetImg()
	def clicked(self):
		if self.breakable == True:
			itemList.append(Item(self.x1+12, self.y1+12, self.type))
			self.delSelf()
	def delSelf(self):
		canvas.delete(self.info)
		blockList.pop(blockList.index(self))
	def testClick(self, clickX, clickY):
		if clickX > self.x1 and clickX <= self.x1+32 and clickY > self.y1 and clickY <= self.y1+32:
			return True
		else:
			return False
	def setCollision(self, x1, y1, x2, y2):
		self.cx1 = x1
		self.cy1 = y1
		self.cx2 = x2
		self.cy2 = y2
		self.collision = True
	def testCollision(self, changeX, changeY):
		if self.collision == True:
			x1 = self.x1 + self.cx1 - 32 + changeX
			y1 = self.y1 + self.cy1 - 56 + changeY
			x2 = self.x1 + self.cx2 + changeX - 16
			y2 = self.y1 +self.cy2 + changeY
			if 150 > x1 and 150 < x2 and 150 > y1 and 150 < y2:
				#print(x1,y1,x2,y2)
				return True
			else:
				return False
	def testCollision2(self, x1, y1, x2, y2):
		if(self.y1 > y2 or self.x1 > x2):
			return False
		elif(self.x1+32 < x1 or self.y1+32 < y1):
			return False
		else:
			return True
	def move(self, changeX, changeY):
		self.x1 += changeX
		self.y1 += changeY
		if self.info != "":
			canvas.move(self.info,changeX,changeY)
	def setType(self):
		self.info = ""
		self.img = ""
		#full blocks
		basicBlocks = ["plank", "stone", "dirt", "grass", "cobble", "coal","jumpJuice"]
		if self.type == "bedrock":
			self.img = allBlockImg[self.type]
			self.breakable = False
		for block in basicBlocks:
			if self.type == block:
				self.img = allBlockImg[self.type]
		if str(self.img) != "":
			self.setCollision(0,0,32,32)
		#no collision
		if self.type == "log" or self.type == "leaves":
			self.img = allBlockImg[self.type]
		#Fail test
		if str(self.img) == "":
			raise ValueError
		#finishing paste
		self.info = canvas.create_image(self.x1,self.y1, anchor=NW, image=self.img)
	def delType(self):
		canvas.delete(self.info)
		self.info = ""
class Item:
	def __init__(self, x, y, imgType):
		self.x1 = x
		self.y1 = y
		self.velY = 0
		self.info = canvas.create_image(self.x1,self.y1, anchor=NW, image=allItemImg[imgType])
		self.imgType = imgType
		player.resetImg()
		print("Total Items: "+str(len(itemList)+1))
	def testCollision(self, x1, y1, x2, y2):
		if(self.y1 > y2 or self.x1 > x2):
			return False
		elif(self.x1+8 < x1 or self.y1+8 < y1):
			return False
		else:
			return True
	def pickUp(self):
		canvas.delete(self.info)
		itemList.pop(itemList.index(self))
	def move(self, changeX, changeY):
		newX = self.x1 + changeX
		newY = self.y1 + changeY
		#lag circuit: for item gravity
		if newX > -32 and newX < 382:
			self.velY += .7
			for block in [block for block in blockList if block.x1+12 == newX]:
				running = 0
				while running<100:
					running +=1
					if block.testCollision2(newX, newY+self.velY, newX+8, newY+8+self.velY):
						if self.velY < 0:
							self.velY += .5
						elif self.velY > 0:
							self.velY -= .5
					else:
						running = 100
		self.x1 += changeX
		self.y1 += changeY + round(self.velY)
		if self.info != "":
			canvas.move(self.info,changeX,changeY+round(self.velY))
class Inventory:
	def __init__(self):
		self.slotElements = []
		for x in range(4):
			self.slotElements.append(canvas.create_image(x*32+10,10, anchor=NW, image=SlotImg))
		self.selectedElement = canvas.create_image(10,10, anchor=NW, image=SlotSelectedImg)
		self.selected = 1
		self.slots = [["",0,"",0],["",0,"",0],["",0,"",0],["",0,"", 0]]#name,quantity,canvas element block, canvas element number
		self.itemSelected = ""
		self.monitors = canvas.create_text(1,1, text="Total Time: {:<10d} FPS: {:4d}".format(0, 0), fill="black", font=('Helvetica 6'), anchor="nw")
	def setTop(self):
		for element in self.slotElements:
			canvas.tag_raise(element, "all")
		canvas.tag_raise(self.selectedElement, "all")
		for slot in self.slots:
			if slot[2] !="":
				canvas.tag_raise(slot[2], "all")
				canvas.tag_raise(slot[3], "all")
		canvas.tag_raise(self.monitors, "all")
	def select(self, slot):
		if slot != 0:
			canvas.moveto(self.selectedElement, 10+(slot-1)*32, 10)
			self.selected = slot
	def addItem(self,itemType): #returns True is successful
		for slot in self.slots:
			if slot[0] == itemType and slot[1]<99:
				slot[1]+=1
				canvas.itemconfig(slot[3],text=str(slot[1]))
				return True
		for slot in self.slots:
			if slot[1]==0:
				slot[1]+=1
				slot[0] = itemType
				slot[2] = canvas.create_image(22+self.slots.index(slot)*32,22, anchor=NW, image=allItemImg[itemType])
				slot[3] = canvas.create_text(29+self.slots.index(slot)*32,29, text="1", fill="black", font=('Helvetica 7'), anchor="nw")
				return True
		return False#no space available
	def removeItem(self): #returns True is successful
		for slot in self.slots:
			if slot[0] == self.getItemSelected() and slot[1]>0:
				slot[1]-=1
				canvas.itemconfig(slot[3],text=str(slot[1]))
				self.itemSelected = self.getItemSelected()
				if slot[1]==0:
					canvas.delete(slot[2])
					canvas.delete(slot[3])
					slot[0],slot[2] = "",""
				return True
		return False
	def getItemSelected(self):
		return self.slots[(self.selected-1)][0]
#start
player = Player()
blockList = []
blockDeadListR = []
blockDeadListL = []
itemList = []
playerInventory = Inventory()
x=-30
yStart = -50
for column in range(12):
	yStart += 32 * random.randint(-1,1) * random.randint(0,1)
	y = yStart
	blockList.append(Block(x,y, "grass"))
	for dirt in range(3):
		y += 32
		blockList.append(Block(x,y, "dirt"))
	while y < 1000:
		y += 32
		if y<1000:
			if random.randint(0,30) != 0:
				blockList.append(Block(x,y, "stone"))
			else:
				blockList.append(Block(x,y, "coal"))
		else:
			if random.randint(0,30) == 0:
				blockList.append(Block(x,y, "jumpJuice"))
			else:
				if random.randint(0,30) != 0:
					blockList.append(Block(x,y, "stone"))
				else:
					blockList.append(Block(x,y, "coal"))
	for amount in range(5):
		y += 32
		blockList.append(Block(x,y, "bedrock"))
	x += 32

player.spawn()
tTime,frames,sec = 0,0,0
fpsCap = 40 #default 40
def fps():
	global tTime,frames,delta,sec
	tTime+=(delta+max(1./fpsCap - delta, 0))
	frames+=1
	if tTime >=0.5: #update speed
		sec+=round(tTime,1)
		canvas.itemconfig(playerInventory.monitors, text="Total Time: {:<10s} FPS: {:4s}".format(str(sec), str(round(frames/tTime,1))))
		frames = 0
		tTime=0
while True:
	start = time.time()
	keyUpdate()
	window.update()
	delta = (time.time() - start)
	time.sleep(max(1./fpsCap - delta, 0))
	fps()