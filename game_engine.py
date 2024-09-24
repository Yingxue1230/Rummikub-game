from solve_tiles import SolveTiles
from set_generator import SetGenerator
import random
from console import Console
from util import subtract_tiles


class RummikubGame:

    def __init__(self):
        '''这段代码是一个类的构造方法(__init__)。
        它用特定的值初始化几个实例变量(board, winner, sg, solver, con, bag)。
        它还实例化了三个对象(SetGenerator、SolveTiles、Console)，并将它们赋值给相应的实例变量(sg、solver、con)。
        最后，它调用sg对象的方法(generate_tiles)，并将结果赋值给bag实例变量。'''
        self.board = []
        self.winner = None
        self.sg = SetGenerator(numbers=15,jokers=2) # 实例化set生成器
        self.solver = SolveTiles(self.sg) #instantiate the solver
        self.con = Console() #instantiate the console
        self.bag = self.sg.generate_tiles() #generate the tiles with the set generator


    def select_starting_player(self):
        '''该函数通过随机绘制2个方块并比较它们的值来确定起始玩家。
        这段代码是一个Python类中的函数，名为select_starting_player。
        它从一个袋子中随机选择两个牌，并比较它们的值以确定开始的玩家。
        如果第一个图案的值大于第二个图案，玩家就开始游戏。
        如果第一个图案的值小于第二个图案的值，则启动计算机。
        如果两个值相同，就重复这个过程，直到绘制出不同的平铺图案。
        这个函数返回一个布尔值，表示玩家是否开始。'''
        starting_player_selected = False
        player_starts = None
        while not starting_player_selected: #as long as a starting player has not been determined
            two_tiles = []
            for i in range(2):
                random_tile = random.choice(self.bag) #draw a random tile
                while random_tile[0] == 5: #if we draw a joker, draw again
                    print('drew joker, drawing again...')
                    random_tile = random.choice(self.bag)
                two_tiles.append(random_tile)
            print(f'You drew {self.con.print_colored_tile(two_tiles[0])}, computer drew: {self.con.print_colored_tile(two_tiles[1])}')
            if two_tiles[0][1] > two_tiles[1][1]: #compare the values
                print('You start!')
                starting_player_selected = True
                player_starts = True
            if two_tiles[0][1] < two_tiles[1][1]:
                print('Computer starts.')
                starting_player_selected = True
                player_starts = False
            elif two_tiles[0][1] == two_tiles[1][1]:
                print('Same values, drawing again...')
        return player_starts

    def draw_tile(self, rack=[], tile_amount=1):
        '''这个函数允许我们绘制瓷砖。
        它接受rack作为参数，将绘制的图案添加到rack中，并返回更新后的rack。
        通过参数tile_amount，我们可以指定绘制多少个图像块，这就允许我们使用这个函数
        既用于绘制单个瓷砖，也用于绘制起始机架。
        这段代码定义了一个名为draw_tile的函数，它接受三个形参:self、rack和tile_amount。
        它允许从包中绘制瓷砖，并将它们附加到机架上。
        rack参数用于存储绘制的图形，tile_amount参数指定绘制的图形数量。
        该函数返回更新后的机架。它可以用来绘制单个瓷砖和起始机架。'''
        temprack = rack
        temprack.extend(self.bag[:tile_amount])
        self.bag = self.bag[tile_amount:]
        return temprack

    def return_tile(self, tile):
        '''这段代码定义了一个名为return_tile的方法，它接受一个参数tile。
        它将瓷砖添加到一个名为bag的列表中，该列表属于同一个对象。'''
        self.bag.append(tile)

    def take_player_turn(self, board, rack):
        '''这段代码定义了一个名为take_player_turn的函数，表示游戏中玩家的回合。
        它首先打印出桌子上的瓷砖和玩家的架子。
        然后，它会询问玩家是否想要使用解算器找到最佳移动。
        如果玩家选择使用解算器，它将使用解算器解决最佳移动。
        方法并提示玩家是否玩最佳解决方案。如果玩家选择玩最好的解决方案，
        该函数更新相应的棋盘和机架。如果玩家选择不采用最佳解决方案，它将绘制一个方块并返回更新后的机架和棋盘。
        如果玩家选择不使用求解器，该函数目前没有手动选择图案的功能，而是绘制一个图案。'''
        print('Your turn! These tiles are on the table:')

        self.con.board_pretty_print(board) #print the board
        self.con.rack_pretty_print(rack)   #print the rack

        find_best_move = self.con.text_gui('Do you want to find the best move?', 'yes', 'no')
        if find_best_move == 'yes': #if player wants to use the solver
            solutions = self.solver.solve_tiles(board, rack)
            best_solution = self.find_best_solution(solutions)
            if best_solution == []:
                print('No move was possible, drawing a tile.')
                self.draw_tile(rack, tile_amount=1)
                return rack, board

            self.con.solution_pretty_print(best_solution)

            con_play = self.con.text_gui('Play the best solution?', 'yes', 'no')

            if con_play == 'yes':
                board = best_solution['sets']
                rack = best_solution['hand']
                return rack, board
            if con_play == 'no':
                self.draw_tile(rack, tile_amount=1)
                print('no play has been made, drawing a tile')
                return rack, board

        if find_best_move == 'no':
            what_play = self.con.text_gui('Which tiles do you want to play? (THIS IS NOT IMPLEMENTED, PLEASE USE SOLVER <3')
            #TODO: manual tile input

        else:
            self.draw_tile(rack, tile_amount=1)
            print('no play has been made, drawing tile')
            return rack, board

    def take_computer_turn(self, board, rack):
        '''这段代码定义了函数take_computer_turn，表示在游戏中轮到计算机了。

        它首先检查计算机的机架是否为空，如果是空的，它会将计算机声明为获胜者。
        然后，它使用solver对象来找到使用机架中的瓷砖在棋盘上玩瓷砖的所有可能的解决方案。
        它从解列表中选择最佳解。
        如果找到了最好的解决方案，它就用最好的解决方案中的瓷砖更新棋盘和机架，并打印出计算机玩的瓷砖。
        如果没有找到最佳解决方案，它就绘制一个图案并结束回合。
        最后，它返回更新后的rack和board。

        这是轮到计算机的功能。它使用solve_tiels来找到最佳解决方案，并在可能的情况下播放它。
        如果不能，它就画一个瓷砖并结束它的回合。'''
        print('Computers turn')
        print('Computer is calculating best move...')
        if len(rack) == 0:
            self.winner = 'computer'

        solutions = self.solver.solve_tiles(board, rack)
        best_solution = self.find_best_solution(solutions)

        if best_solution == []:
            print('Computer could not make a move, draws a tile')
            self.draw_tile(rack, tile_amount=1)
            return rack, board

        else:
            board = best_solution['sets']
            rack = best_solution['hand']
            print('Computer plays tiles:')
            self.con.solution_pretty_print(best_solution)
            return rack, board

    def take_computer_turn2(self, board, rack):
        '''这段代码定义了函数take_computer_turn2，它表示在游戏中轮到计算机了。
        它使用solve_tiles函数来找到最佳解决方案，并尽可能播放它。
        如果不可能，它就绘制一个瓷砖并结束它的回合。该函数在转弯后返回更新后的rack和board。'''
        solution,play_tiles = self.solver.find_play(board, rack)
        if not play_tiles:
            self.draw_tile(rack, tile_amount=1)
            return rack, board
        else:
            return subtract_tiles(rack,play_tiles), solution
    
    def check_play(self,rack):
        '''这段代码定义了一个名为check_play的方法，它接受两个实参:self和rack。
        它从传入self的solver对象中调用另一个名为check_play的方法。Board和rack作为参数，并返回结果。'''
        return self.solver.check_play(self.board,rack)

    def initial_meld(self, board, rack):
        '''这段代码定义了一个名为initial_meld的方法，它接受三个形参:self、board和rack。

        在这个方法内部，它对self对象调用了一个名为solve_tiles的方法。
        求解器，传递一个空列表和机架参数作为参数。它将返回的解存储在变量solutions中。

        然后，它通过筛选解决方案列表，只包含得分大于或等于30的解决方案，创建一个名为score_solutions的新列表。

        接着，初始化一个名为best_solution的空列表。
        如果score_solutions的长度大于0，它将使用max函数找到得分最高的解决方案，并将其存储在best_solution中。

        如果best_solution仍然是一个空列表，则返回rack和board参数。
        否则，它使用best_solution中的集合扩展board列表，并将best_solution的hand属性赋值给rack。
        然后，对一个名为self的对象调用方法solution_pretty_print。
        用best_solution作为参数。最后，它返回机架和板。'''

        solutions = self.solver.solve_tiles([], rack)
        score_solutions = [solution for solution in solutions if solution['score'] >= 30] #make a new list of scoring solutions
        best_solution = []
        if(len(score_solutions)>0):
            best_solution = max(score_solutions, key=lambda x:x['score']) #filter solutions by score and find highest score

        if best_solution == []:
            #self.draw_tile(rack, tile_amount=1)
            return rack, board
        else:
            board.extend(best_solution['sets'])
            rack = best_solution['hand']
            self.con.solution_pretty_print(best_solution)
            return rack, board

    def find_best_solution(self, solutions):
        '''该函数通过检查解是否包含所有的棋盘图案来检查最佳解的有效性
        这段代码定义了一个函数find_best_solution，它接受一个解决方案列表作为输入。
        它根据分数标准对解进行筛选，然后对筛选后的解进行迭代，以找到最佳解。
        最好的解决方案是通过检查它是否包含一个板上的所有瓷砖来确定。
        该函数返回找到的最佳解决方案。'''
        score_solutions = [solution for solution in solutions if solution['score'] > 0] #make a new list of scoring solutions
        best_solution = [] #把最好的解决方案保存在这里
        if self.board == []: #如果黑板上什么都没有
            try:
                best_solution = max(score_solutions, key=lambda x:x['score']) #按分数过滤解决方案并找到最高分数
                return best_solution
            except: #只有当解决方案为空时，才会触发异常
                return []
        else: #如果我们在黑板上有瓷砖
            best_score = 0 # 最佳记分器
            best_solution = [] # 保存最佳解决方案
            flat_board = [tile for set in self.board for tile in set] # 将board中的所有元组创建一个扁平列表
            for solution in score_solutions: # 过滤列表中的每个解决方案
                # 将solution中与board相同的所有元组创建一个平面列表
                check_intersection = [tile for set in solution['sets'] for tile in set if tile in flat_board]
                # 创建一个平面列表，其中包含解决方案的所有瓦片
                flat_solution = [tile for set in solution['sets'] for tile in set]

                if len(check_intersection) == len(flat_solution): # 如果解的长度和交点相同
                    continue # 我们不添加任何新的瓷砖与这个解决方案，去下一个
                elif len(check_intersection) < len(flat_board): # 如果交叉路口的瓦片比棋盘上的瓦片少
                    # 那么我们没有使用所有的棋盘图案，请转到下一个解决方案
                    continue
                else: # 如果所有的面板贴片都被使用了，并且我们使用这个解决方案添加新的贴片:
                    if solution['score'] > best_score: # 如果它的分数比我们的最佳解决方案更高
                        best_score = solution['score'] # 保存分数
                        best_solution = solution # 保存解决方案
            return best_solution # 返回最佳解决方案
    def reset(self):
        self.bag = self.sg.generate_tiles()
        self.board.clear()
        self.winner = None


