import pygame
from pygame.locals import *
import sys
import random
import time
from game_engine import RummikubGame
from player import Player
from button import Button
import traceback
import threading
from util import subtract_tiles

TILE_WIDTH = 50
SMALL_TILE_WIDTH = 35
TILE_HEIGHT = 60
SMALL_TILE_HEIGHT = 45
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
MAX_SEARCH_TIME = 30
MIN_PLAY_TIME = 3

def compare_func(tile):
    '''这段代码定义了一个名为compare_func的函数，它接受一个tile形参。
    它计算并返回tile的第一个元素乘以15再加上第二个元素的结果。'''
    return tile[0]*15 + tile[1]

class RummiGui:
    def __init__(self,computer_num=1):
        '''这段代码使用Pygame库初始化了一个游戏窗口，并设置了游戏的初始状态。
        创建玩家、按钮和各种与游戏相关的变量。
        这段代码还定义了这些变量的初始值，如玩家数量、当前玩家和游戏状态。'''
        pygame.init()
        pygame.font.init()
        
        #pygame.mixer.init()
        self.screen = pygame.display.set_mode([WINDOW_WIDTH,WINDOW_HEIGHT])
        self.colors = ['Black','Blue','Cyan','Red','Yellow','Joker']

        pygame.display.set_caption('Rummi')
        self.game = RummikubGame()
        self.background_color = (20, 20, 55)
        self.players = []
        self.players.append(Player(rack=self.game.draw_tile(rack=[],tile_amount=14)))

        for i in range(computer_num):
            self.players.append(Player(rack=self.game.draw_tile(rack=[],tile_amount=14),auto_play=True))
        self.load_images()
        self.show_all_tile = False
        self.buttons = []

        play_button = Button("Play",pygame.Rect(750,700,40,30))
        play_button.perform_mouse_up = self.do_play
        self.buttons.append(play_button)

        show_all_tile_button = Button("Show All Tiles",pygame.Rect(800, 700, 60, 30))
        show_all_tile_button.perform_mouse_up = lambda: (
            setattr(self, 'show_all_tile', not self.show_all_tile)
        )
        self.buttons.append(show_all_tile_button)

        play_for_me_button = Button("Play For Me",pygame.Rect(870,700,60,30))
        play_for_me_button.perform_mouse_up = lambda: (
            setattr(self, 'auto_play', not self.auto_play)
        )
        self.buttons.append(play_for_me_button)

        draw_tile_button = Button("Draw Tiles",pygame.Rect(940,700,60,30))
        draw_tile_button.perform_mouse_up = self.draw_tile
        self.buttons.append(draw_tile_button)

        new_round_button = Button("New Round",pygame.Rect(500,500,60,30))
        new_round_button.perform_mouse_up = self.new_round
        new_round_button.show = False
        new_round_button.enable = False
        self.buttons.append(new_round_button)

        self.font = pygame.font.SysFont(None, 12)

        self.running = True
        self.current_player = random.randrange(0,len(self.players))
        self.auto_play = False
        self.thinking = False
        self.thinking_positions = [pygame.Rect(580,630,30,30),pygame.Rect(170,430,30,30),pygame.Rect(580,150,30,30),pygame.Rect(1000,430,30,30)]

        self.selected_tiles=[]
        self.candidate_tiles = []
        self.status = 0
        self.begin_thinking_time = int(time.perf_counter())
        
    def load_images(self):
        '''
        Load tile images from disk.
        这段代码定义了一个方法load_images，它从磁盘加载瓦片图像，并将它们存储在self.images and self.small_images 列表。
        它迭代self。Colors列表并使用嵌套循环加载每个颜色的平铺图像。
        它还单独加载小丑图像。
        然后，使用pygame.transform.scale将加载的图像缩放到特定的尺寸，并将其附加到相应的列表中。
        最后，加载并缩放一个反向图像，并将其赋值给self.tile_back_image。
        '''
        self.images = [] # tile images
        self.small_images = [] # small tile images draw on the table
        for i in range(len(self.colors)-1):
            tile_images = []
            small_tile_images = []
            for j in range(1,16):
                tile_image = pygame.image.load(f'images/{self.colors[i]}_{j}.png').convert_alpha()
                tile_image = pygame.transform.scale(tile_image, (TILE_WIDTH, TILE_HEIGHT))
                small_tile_image = pygame.transform.scale(tile_image, (SMALL_TILE_WIDTH, SMALL_TILE_HEIGHT))
                tile_images.append(tile_image)
                small_tile_images.append(small_tile_image)
            self.images.append(tile_images)
            self.small_images.append(small_tile_images)
        joker_images = []
        small_joker_images = []
        for j in range(1,3):
            joker_image = pygame.image.load(f'images/Joker_{j}.png').convert_alpha()
            joker_image = pygame.transform.scale(joker_image, (TILE_WIDTH, TILE_HEIGHT))
            small_joker_image = pygame.transform.scale(joker_image, (SMALL_TILE_WIDTH, SMALL_TILE_HEIGHT))
            joker_images.append(joker_image)
            small_joker_images.append(small_joker_image)
        self.images.append(joker_images)
        self.small_images.append(small_joker_images)

        back_image = pygame.image.load(f'images/back.png').convert_alpha()
        back_image = pygame.transform.scale(back_image, (TILE_WIDTH, TILE_HEIGHT))
        self.tile_back_image = back_image

    def turn_next_player(self):
        '''
        这个函数更新回合顺序，并允许下一个玩家进行移动。
        这段代码定义了一个名为turn_next_player的函数，它更新回合顺序，并允许回合中的下一个玩家进行移动。
        它检查游戏状态是否为100，如果是，则不做任何更改地返回。
        否则，它将begin_thinking_time设置为当前时间，并将current_player更新为旋转中的下一个播放器。
        '''
        if(self.status==100):
            return
        self.begin_thinking_time = int(time.perf_counter())
        self.current_player = (self.current_player+1)%len(self.players)

    def draw_bottom_rack(self,rack):
        '''
        在游戏屏幕底部绘制人类玩家持有的方块。
        架(rack):代表人类玩家所持有的方块的架。

        这段代码定义了一个名为draw_bottom_rack的方法，它是一个类的一部分。
        这个方法接受一个名为rack的参数，表示人类玩家持有的方块。

        这个方法的目的是在游戏屏幕上绘制人类玩家持有的方块。
        它使用循环遍历机架中的每个块，并根据其索引计算每个块的位置。
        最后，它使用blit方法在屏幕上计算出的位置绘制图案。
        '''
        left_span = (WINDOW_WIDTH-(TILE_WIDTH+2)*15)/2
        top_span = WINDOW_HEIGHT-TILE_HEIGHT*2.5
        for i in range(len(rack)):
            tile = rack[i]
            x = left_span+(i%15)*(TILE_WIDTH+2)
            y = top_span + (i//15)*(TILE_HEIGHT+2)
            self.screen.blit(self.images[tile[0]-1][tile[1]-1],(x,y))

    def draw_candidate_tiles(self):
        '''
        从绘制堆中绘制两个方块，并将它们呈现给用户以供选择。
        这段代码定义了一个名为draw_candidate_tiles的方法，负责从一个绘制堆中绘制两个图像块，并将它们呈现给用户以供选择。
        它根据瓷砖的尺寸和机架的当前状态计算每个瓷砖在屏幕上的位置。
        然后，它使用screen对象的blit方法在每个贴片对应的位置绘制图像。
        '''
        left_span = (WINDOW_WIDTH-(TILE_WIDTH+2)*2)/2
        top_span = WINDOW_HEIGHT-TILE_HEIGHT*3.8
        rack = self.candidate_tiles
        for i in range(len(rack)):
            tile = rack[i]
            x = left_span+i*(TILE_WIDTH+2)
            y = top_span
            self.screen.blit(self.images[tile[0]-1][tile[1]-1],(x,y))

    def draw_left_rack(self,rack):
        '''
        在游戏屏幕的左侧绘制由计算机控制的方块。
        机架:代表由左侧计算机持有的瓷砖的机架。

        这段代码定义了函数draw_left_rack，负责绘制计算机持有的游戏屏幕左侧的方块。它接受一个rack参数，表示左侧计算机持有的磁块。

        该函数使用循环遍历机架中的每个贴片，并计算每个贴片在屏幕上的位置(x和y)。

        如果自我。show_all_tile为True时，该函数使用blit方法根据瓷砖的类型(瓷砖[0]和[1])在屏幕上绘制实际的图像。否则，它将绘制一个平铺的背面图像。
        '''
        left_span = TILE_WIDTH*2.5
        top_span = (WINDOW_HEIGHT-(TILE_HEIGHT+2)*10)/2
        for i in range(len(rack)):
            tile = rack[i]
            y = top_span+(i%10)*(TILE_HEIGHT+2)
            x = left_span - (i//10)*(TILE_WIDTH+2)
            if self.show_all_tile:
                self.screen.blit(self.images[tile[0]-1][tile[1]-1],(x,y))
            else:
                self.screen.blit(self.tile_back_image,(x,y))

    def draw_top_rack(self,rack):
        '''
        这段代码定义了一个名为draw_top_rack的方法，负责在游戏屏幕上绘制瓷砖。
        它接受一个名为rack的参数，它表示计算机在屏幕顶部持有的方块。
        这段代码根据每个图案在rack列表中的索引计算其位置(x和y)，然后使用blit()方法在屏幕上绘制图案。
        如果self.show_all_tile为True时，使用对应的图像作为图案，否则使用图案的背面图像。
        '''
        left_span = (WINDOW_WIDTH-(TILE_WIDTH+2)*15)/2
        top_span = TILE_HEIGHT*0.5
        for i in range(len(rack)):
            tile = rack[i]
            x = left_span+(i%15)*(TILE_WIDTH+2)
            y = top_span + (i//15)*(TILE_HEIGHT+2)
            if self.show_all_tile:
                self.screen.blit(self.images[tile[0]-1][tile[1]-1],(x,y))
            else:
                self.screen.blit(self.tile_back_image,(x,y))

    def draw_right_rack(self,rack):
        '''
        在游戏屏幕的右侧绘制由计算机控制的方块。
        机架:代表由正确的计算机持有的瓷砖的机架。
        这段代码定义了一个名为draw_right_rack的方法，用于在游戏屏幕右侧绘制计算机所持有的方块。
        该方法接受一个名为rack的参数，该参数表示由正确的计算机持有的瓦片。

        该方法使用left_span和top_span变量，根据每个瓷砖在rack列表中的索引计算其在屏幕上的位置。
        然后，它使用blit方法，根据show_all_tile属性的值，使用瓦片图像或瓦片背面图像在屏幕上绘制这些瓦片。
        '''
        left_span = WINDOW_WIDTH-TILE_WIDTH*2.5
        top_span = (WINDOW_HEIGHT-(TILE_HEIGHT+2)*10)/2
        for i in range(len(rack)):
            tile = rack[i]
            y = top_span+(i%10)*(TILE_HEIGHT+2)
            x = left_span + (i//10)*(TILE_WIDTH+2)
            if self.show_all_tile:
                self.screen.blit(self.images[tile[0]-1][tile[1]-1],(x,y))
            else:
                self.screen.blit(self.tile_back_image,(x,y))

    def check_select_tiles(self):
        '''
        检查用户点击了哪个贴图，并将其添加到选中的贴图列表中以供下一步操作。
        这段代码定义了一个名为check_select_tiles的方法，该方法检查用户单击了哪些瓷片，并将它们添加到选中的瓷片列表中以进行进一步操作。
        这个方法使用pygame库获取鼠标位置，并创建矩形来表示屏幕上的图案。
        如果鼠标位置在图案的矩形范围内，图案就会被添加到选定图案的列表中，或者从选定图案的列表中删除。
        此外，该方法从一个牌组中选择两个候选块，并根据用户的选择执行一些操作。
        '''
        mouse_pos = pygame.mouse.get_pos()
        left_span = (WINDOW_WIDTH-(TILE_WIDTH+2)*15)/2
        top_span = WINDOW_HEIGHT-TILE_HEIGHT*2.5
        rack = self.players[0].rack
        for i in range(len(rack)):
            tile = rack[i]
            x = left_span+(i%15)*(TILE_WIDTH+2)
            y = top_span + (i//15)*(TILE_HEIGHT+2)
            rect = pygame.Rect(x,y,TILE_WIDTH,TILE_HEIGHT)
            if(rect.collidepoint(mouse_pos)):
                if i not in self.selected_tiles:
                    self.selected_tiles.append(i)
                else:
                    self.selected_tiles.remove(i)
        
        # select the candidate 2 tiles draw from deck
        left_span = (WINDOW_WIDTH-(TILE_WIDTH+2)*2)/2
        top_span = WINDOW_HEIGHT-TILE_HEIGHT*3.8
        rack = self.candidate_tiles
        for i in range(len(rack)):
            tile = rack[i]
            x = left_span+i*(TILE_WIDTH+2)
            y = top_span
            rect = pygame.Rect(x,y,TILE_WIDTH,TILE_HEIGHT)
            if(rect.collidepoint(mouse_pos)):
                self.players[0].add_tile(tile)#add selected tile to player's rack
                #return the other tile to the game deck
                if(i==0):
                    self.game.return_tile(self.candidate_tiles[1])
                else:
                    self.game.return_tile(self.candidate_tiles[0])
                self.candidate_tiles.clear()
                self.turn_next_player()
                break

    def draw_selected_tiles(self):
        '''
        在选定的方块上画一个小的绿色点
        这段代码定义了一个名为draw_selected_tiles的方法，它在选中的图案上绘制一个绿色的小点。
        它根据瓷砖的索引以及窗口和瓷砖的大小计算每个瓷砖的位置。
        然后，它使用pygame.draw.rect函数在计算的位置绘制一个绿色矩形。
        '''
        left_span = (WINDOW_WIDTH-(TILE_WIDTH+2)*15)/2
        top_span = WINDOW_HEIGHT-TILE_HEIGHT*2.5
        rack = self.players[0].rack
        for i in self.selected_tiles:
            if(i>=len(rack)):
                break
            tile = rack[i]
            x = left_span+(i%15)*(TILE_WIDTH+2)
            y = top_span + (i//15)*(TILE_HEIGHT+2)
            pygame.draw.rect(self.screen, pygame.Color("green"), pygame.Rect(x+TILE_WIDTH/2-4,y,8,8), 4)

    def computer_play(self):
        '''
        自动为当前玩家打贴图。
如果`   auto_play `标志设置为true，它也可以为人类玩家玩拼图。
        这段代码定义了一个名为computer_play的方法，负责在游戏中自动为当前玩家玩纸牌。
        它首先检查当前玩家是否已经打过任何方块。如果没有，它会执行一次初始的合并，并在必要时绘制一个新的贴片。
        否则，它会正常地玩游戏。
        在玩完这些方块之后，它会更新玩家的机架，前进到下一个玩家，并将思考标志设置为false。
        '''
        self.thinking = True
        player = self.players[self.current_player]
        if(self.current_player==0):
            self.selected_tiles.clear()
        rack=[]
        # If the player has not played any tiles yet, they must perform an initial_meld first.
        if(player.status==0):
            rack, self.game.board = self.game.initial_meld(self.game.board, player.rack.copy())
            if len(rack)==len(player.rack):
                rack = self.game.draw_tile(player.rack)
            else:
                player.status=1
        else:
            # play tiles normally
            rack, self.game.board = self.game.take_computer_turn2(self.game.board, player.rack)
            if(len(rack)==len(player.rack)) and len(self.game.bag)==0:
                player.status = 100
        if time.perf_counter()-self.begin_thinking_time<MIN_PLAY_TIME:
            time.sleep(time.perf_counter()-self.begin_thinking_time<MIN_PLAY_TIME)
        player.update_rack(rack)
        self.turn_next_player()
        
        self.thinking = False

    def do_play(self):
        '''
        Do play action for the human player
        这段代码定义了一个名为do_play的方法，在游戏中为人类玩家执行play操作。
        它首先检查当前玩家是否不是人类玩家，或者是否启用了自动游戏，在这种情况下，它不执行任何操作就返回。
        然后它检查人类玩家的状态是否为0，如果是，就调用computer_play方法并返回。

        如果没有选中方块，它就打印一条消息，让玩家选择方块并返回。
        否则，它根据selected_tiles列表中的索引从人类玩家的机架中检索磁片。
        然后，它调用game对象的check_play方法，检查选中的方块是否符合游戏规则。

        如果方块有效，它就更新游戏面板，通过删除已玩的方块更新人类玩家的机架，清除selected_tiles列表，并让回合提前到下一个玩家。

        如果方块无效，它会打印一条消息，指出选中的方块不符合规则，
        并打印游戏棋盘的当前状态和选中的方块。
        '''
        if(self.current_player!=0 or self.auto_play):
            return
        if(self.players[0].status==0):
            self.computer_play()
            return 
        play_tiles = []
        if(len(self.selected_tiles)==0):
            print("Please select tiles!")
            return
        for i in self.selected_tiles:
            play_tiles.append(self.players[0].rack[i])
        s = self.game.check_play(play_tiles)
        if s:
            self.game.board = s
            self.players[0].update_rack(subtract_tiles(self.players[0].rack,play_tiles))
            self.selected_tiles.clear()
            self.turn_next_player()
        else:
            print("The selected tiles do not conform to the rules for playing.")
            print("board",self.game.board)
            print("play_tile",play_tiles)
    
    def draw_tile(self):
        '''
        Do draw tile action for the human player
        这段代码定义了一个名为draw_tile的方法，负责在游戏中为人类玩家执行绘制瓷砖的操作。
        它检查当前玩家是否不是人类玩家，或者是否启用了自动游戏，如果是，则不做任何操作返回。
        然后它检查是否有可供选择的图案，如果没有，就打印一条消息，让玩家选择一个图案。
        最后，它调用游戏对象的draw_tile方法，传入一个空列表作为第一个参数，贴图数量为2，
        并将结果赋值给对象的candidate_tiles属性。
        '''
        if(self.current_player!=0 or self.auto_play):
            return
        if(len(self.candidate_tiles)!=0):
            print("Please choose one tile")
            return
        self.candidate_tiles = self.game.draw_tile([],tile_amount=2)
    
    def new_round(self):
        '''
        Reset the game and start a new round.
        这段代码定义了一个名为new_round的方法，用于重置游戏并开始新一轮游戏。
        它重置游戏状态，重置每个玩家，并更新他们的格子架。
        它还根据按钮的文本更新按钮的可见性和启用情况。
        '''
        self.game.reset()
        self.status = 0
        for player in self.players:
            player.reset()
            player.update_rack(self.game.draw_tile([],tile_amount=14))
        for button in self.buttons:
            if button.text =="New Round":
                button.show = False
                button.enable = False
            else:
                button.show=True
                button.enable=True

    def draw_center_board(self,board):
        '''
        在桌子上画瓷砖。
        这段代码定义了一个函数draw_center_board，它接受一个板作为输入，并在表格上绘制图案。
        它对棋盘进行迭代，检查当前列(col)加上瓦片数(tiles_num)加上当前机架的长度(rack)是否超过最大瓦片数(max_tile)。
        如果是，则增加行(row)并重置列和平铺的数量。
        然后，它根据瓦片在机架中的行、列和索引计算每个瓦片的x和y坐标。
        最后，它会根据计算出的坐标在屏幕上块移(即绘制)图案。
        '''
        max_tile = 20
        left_span = (WINDOW_WIDTH-(SMALL_TILE_WIDTH+2)*max_tile)/2
        top_span =TILE_HEIGHT*4
        row = 0
        col = 0
        tiles_num = 0
        for i in range(len(board)):
            rack = board[i]
            if(col+tiles_num+len(rack)>max_tile):
                row = row + 1
                col = 0
                tiles_num = 0
            for i in range(len(rack)):
                tile = rack[i]
                x = left_span+((tiles_num+col+i)%max_tile)*(SMALL_TILE_WIDTH+2)
                y = top_span + row*(SMALL_TILE_HEIGHT+2)
                self.screen.blit(self.small_images[tile[0]-1][tile[1]-1],(x,y))
            col = col+1
            tiles_num = tiles_num+len(rack)
    
    def draw_thinking_label(self):
        '''
        显示当前玩家的剩余秒数。
        这段代码定义了一个名为draw_thinking_label的方法，负责在屏幕上显示一个计时器。
        它首先检查当前玩家的时间是否已经用完。然后，它使用Pygame库在屏幕上绘制一个矩形。
        它通过从玩家开始思考的时间减去当前时间来计算剩余的秒数。
        最后，它将剩余的秒数渲染为文本并显示在屏幕上。
        '''
        self.check_time_out()
        pygame.draw.rect(self.screen, pygame.Color("lightgray"), self.thinking_positions[self.current_player])
        text = self.font.render(str(MAX_SEARCH_TIME-int(time.perf_counter()-self.begin_thinking_time)), True, pygame.Color("black"))
        text_rect = text.get_rect(center=self.thinking_positions[self.current_player].center)
        self.screen.blit(text, text_rect)

    def draw_score(self):
        '''
        在每一轮结束时显示分数。
        这段代码定义了一个名为draw_score的方法，负责在每一轮结束时显示得分。
        它使用Pygame库在屏幕上渲染分数。
        这个方法遍历游戏中的每个玩家，并创建一个文本字符串，其中包含玩家的名字、输赢状态和得分。
        然后使用指定的字体和颜色渲染文本，并使用blit方法将渲染的文本定位在屏幕上。
        '''
        left_span = 400
        top_span = 400
        font = pygame.font.SysFont(None, 24)

        for i in range(len(self.players)):
            text = ""
            if i == 0:
                text = text + "You   "
            else:
                text = text + "Bot"+str(i)+"  "
            if i ==self.current_player:
                text = text + "Win  "
            else:
                text = text + "Lost "
            text = text + str(self.players[i].score)
            text = font.render(text, True, pygame.Color("yellow"))
            text_rect = text.get_rect(center=(left_span+75,top_span+i*30))
            self.screen.blit(text, text_rect)

    def draw_remain_tiles(self):
        '''
        显示牌组中剩余的平铺数量。
        这段代码定义了一个名为draw_remain_tiles的方法，用于在屏幕上显示deck对象中剩余的瓦片数量。
        它使用screen对象的blit方法来显示瓷砖的图像，然后使用font对象的render方法将剩余的瓷砖数量渲染为文本。
        然后，通过调用另一个blit方法将文本显示在屏幕上。
        '''
        self.screen.blit(self.tile_back_image,((WINDOW_WIDTH-TILE_WIDTH)/2+2*TILE_WIDTH,2.5*TILE_HEIGHT))
        font = pygame.font.SysFont(None, 24)
        text = font.render(str(len(self.game.bag)), True, pygame.Color("yellow"))
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2+2*TILE_WIDTH,3.4*TILE_HEIGHT))
        self.screen.blit(text, text_rect)

    def check_time_out(self):
        '''
        检查当前玩家是否超时，并在超时发生时自动执行操作。
        这段代码定义了一个方法check_time_out，它检查当前玩家是否超时，并在超时发生时自动执行一个操作。
        如果auto_play标志设置为True，或者current_player不等于0，该方法将不执行任何操作返回。
        否则，如果自开始思考以来经过的时间超过MAX_SEARCH_TIME，并且有可用的候选卡片，
        该方法将第一个候选卡片添加到玩家的卡片中，将第二个候选卡片返回游戏，并移动到下一个玩家。
        如果没有可用的方块，就调用computer_play方法。

        '''
        if(self.auto_play or self.current_player!=0):
            return
        if(time.perf_counter()-self.begin_thinking_time>MAX_SEARCH_TIME):
            if(len(self.candidate_tiles)>0):
                self.players[0].add_tile(self.candidate_tiles[0])
                self.game.return_tile(self.candidate_tiles[1])
                self.turn_next_player()
            else:
                self.computer_play()
                
    def refresh_screen(self):
        self.screen.fill(self.background_color)
        for button in self.buttons:
            button.refresh(self.screen)
        if self.status==100:
            self.draw_score()
            return

        for i in range(len(self.players)):
            if i == 0:
                self.draw_bottom_rack(self.players[i].rack)
            elif i == 1:
                self.draw_left_rack(self.players[i].rack)
            elif i == 2:
                self.draw_top_rack(self.players[i].rack)
            elif i == 3:
                self.draw_right_rack(self.players[i].rack)

        self.draw_center_board(self.game.board)
        self.draw_thinking_label()
        self.draw_selected_tiles()
        self.draw_candidate_tiles()
        self.draw_remain_tiles()
    
    def check_game_status(self):
        '''
        Check if the game has ended.
        '''
        end_num = 0
        for i,player in enumerate(self.players):
            if len(player.rack)==0:
                self.status = 100
                self.calculate_player_score()
                return
            if player.status==100:
                end_num = end_num+1
        if(end_num==len(self.players)):
            self.status = 100
            self.calculate_player_score()
    
    def calculate_player_score(self):
        '''
        Calculate the player’s score at the end of a round.
        '''
        for button in self.buttons:
            if button.text == "New Round":
                button.show = True
                button.enable = True
            else:
                button.show = False
        min_value = self.players[0].get_tiles_value()
        self.current_player = 0
        for i in range(len(self.players)):
            player = self.players[i]
            if player.get_tiles_value()<min_value:
                self.current_player = i
                min_value = player.get_tiles_value()
        win_player = self.players[self.current_player]
        for i in range(len(self.players)):
            player = self.players[i]
            if i != self.current_player:
                player.score = 0 - (player.get_tiles_value()-win_player.get_tiles_value())
                win_player.score = win_player.score - player.score

    def main(self):
        '''
        The main process of the game.
        '''
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.check_select_tiles()

                for button in self.buttons:
                    button.handle_event(event)
            if(self.status!=100):
                self.check_game_status()
            if not self.thinking:
                if self.current_player != 0 or self.auto_play:
                    thread = threading.Thread(target=self.computer_play)
                    thread.start()
            rummi.refresh_screen()
            pygame.display.flip()
            clock.tick(60)

if __name__ == '__main__':
    try:
        rummi = RummiGui(computer_num=3)
        rummi.main()
            
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
