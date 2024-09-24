from set_generator import SetGenerator
from itertools import combinations
from collections import defaultdict
from console import Console
from util import *
import time

INITIAL_MELD_PLAY = 0
NORMAL_PLAY = 1
CHECK_PLAY = 2

class SolveTiles:
    begin_time = time.time()
    max_search_time = 20

    def __init__(self,sg):
        '''这段代码为类定义了一个初始化方法(__init__)。
        它用特定的值初始化几个实例变量(yellow、cyan、black、red、blue、sg和con)。
        '''
        self.yellow = ['yellow_1', 'yellow_2']
        self.cyan = ['cyan_1', 'cyan_2']
        self.black = ['black_1', 'black_2']
        self.red = ['red_1', 'red_2']
        self.blue = ['blue_1', 'blue_2']
        #self.sg = SetGenerator()
        self.sg = sg
        self.con = Console()
        # self.begin_time = time.time()
        # self.max_search_time = 10

    def solve_tiles(self, board=[], rack=[]):
        ''' 这个函数将board和rack相互连接，然后在union上调用solution_finder .
        这段代码定义了一个名为solve_tiles的函数，它接受两个可选参数board和rack。
        该函数将board和rack列表组合成一个名为union的新列表，
        然后使用一些参数调用另一个名为solution_finder的函数。
        最后，它返回solution_finder函数调用的结果。
        '''
        SolveTiles.begin_time = time.time()
        union=[]
        for set in board:
            for tile in set:
                union.append(tile)
        union += rack
        solutions = self.solution_finder(1, [], union)
        return solutions

    def solution_finder(self, n=1, solutions=[], tiles=[]):
        '''这个解决方案查找器递归地查找每个块的组合。它从n=1开始，n=1代表瓷砖值
        因此，首先对所有值为1的方块进行计算。在n=1时，我们开始新的运行并创建新的组，然后创建
        这个函数用n+1来调用自己，并且到目前为止找到了所有的解。
        例如，在n=2时，我们再次找到新的运行和新的组，但我们也试图在现有的解决方案中找到新的组/运行。
        我们还尝试扩展以前的解决方案中的运行。所有这些新的解决方案/选项都被保存并递归。'''
        print(n)
        newsolutions = []
        if n > 1:
            newsolutions.extend(solutions)
        if time.time()-SolveTiles.begin_time>SolveTiles.max_search_time:
            return newsolutions

        # 这里，我们调用find_new_groups，根据当前的n值找到所有可能的新分组
        new_groups = self.find_new_groups(n, tiles)

        if len(new_groups) != 0:  # 如果发现了新的分组
            newsolutions.extend(new_groups)  # 将所有新的可能的组作为一个新的解决方案添加到新的解决方案中

        # 调用start_new_runs找到所有新的单图案解决方案
        new_run_starts = self.start_new_runs(tiles, n)

        if len(new_run_starts) != 0:  # 如果我们能开始新的行动
            newsolutions.extend(new_run_starts)  # 添加新启动的运行

        if n > 1:  # 只有当我们确实找到了解决方案时，才开始遍历解决方案

            #首先，我们通过添加组来填充要循环的解决方案
            #这样我们就可以循环遍历任何剩余的贴图
            loop_solutions = solutions.copy()
            for solution in solutions:
                # 对于每个解决方案，尽可能添加组
                solutions_with_groups = self.find_new_groups(n, solution['hand'], solution)
                loop_solutions.extend(solutions_with_groups)  # 将新的解决方案添加到循环解决方案中
                newsolutions.extend(solutions_with_groups)  # 添加到最终解决方案中

                # 对于每个解决方案，也在其中开始新的运行
                solutions_with_new_runs = self.start_new_runs(solution['hand'], n, solution)
                loop_solutions.extend(solutions_with_new_runs)
                newsolutions.extend(solutions_with_new_runs)
            for solution in loop_solutions:  # 对于目前找到的每一个解决方案
                newsolutions.extend(self.extend_runs(solution, n))  # 延长运行时间，将它们添加到新的解决方案中

        if n <= self.sg.numbers-1:
            return self.solution_finder(n + 1, newsolutions, tiles)
        else:
            return newsolutions

    def find_new_groups(self, n, tiles, input_solution=None):
        '''该函数查找所有新分组，将它们添加到一个新解中，并返回一个解列表
            如果有任何图案重复，我们还添加了一个解决方案，在新的运行中使用重复的图案
            
            这段代码定义了一个名为find_new_groups的函数。这个函数接受几个参数:
            self(指向一个类的实例)、n(一个整数)、tiles(一个列表)和input_solution(一个可选参数，默认设置为None)。

            这个函数的目的是在tiles列表中找到所有新的组，将它们添加到一个新的解决方案中，并返回一个解决方案列表。
            如果有任何重复的模式，则会添加一个额外的解决方案，以便在新的运行中使用重复的模式。

            该函数首先检查是否提供了input_solution以及它是否有效。否则，返回一个空列表。
            然后，该函数过滤tile列表，只保留值等于n或最大颜色值加1的tile。
            如果筛选后的图像块超过两个，该函数会找出唯一的图像块，并检查是否有重复的。

            如果至少有三个不同的平铺图，该函数会迭代平铺图的不同组合，
            检查它们是否组成一个有效的组，并通过将平铺图附加到input_solution或一个新解来创建一个新解。
            计算每个解的得分，并将所有解存储在tempsolutions列表中，该列表在函数结束时返回。

            总的来说，这个函数找到新的平铺图组，用这些组创建解决方案，并返回这些解决方案的列表。
            '''
        if input_solution is not None: # 如果我们正在处理一个输入解决方案
            if not self.check_validity(n, input_solution): # 检查输入解决方案的有效性
                return [] # 如果无效，则返回空列表
        tempsolutions = []

        filtertiles = list(filter(lambda tile: (tile[1] == n or tile[0] == self.sg.colors+1), tiles))  # 只保留value等于n的方块
        if len(filtertiles) > 2:
            # 在这里，我们找到当前值的组，并将它们附加到一个新解中
            unique_tiles = list(set(filtertiles))  # 新列表与所有独特的瓷砖
        else:
            return []
        if len(filtertiles) > len(unique_tiles):
            duplicate_tiles = list(set([i for i in filtertiles if filtertiles.count(i) > 1]))  # 新列表与所有受骗
            duplicates = True
        else:
            duplicates = False
        if len(unique_tiles) > 2:  # 组必须至少有3个贴图，如果没有超过2个不同的贴图，就不可能有组
            for i in range(3, self.sg.colors+1):  # 长度为3和4
                for item in combinations(filtertiles, i):  # 对于每一个瓷砖组合
                    tempitem = list(item) # 暂时将项目转换为一个列表
                    solution = defaultdict(list) # 制定新的解决方案
                    if not self.is_set_group(tempitem):
                        continue

                    if input_solution is None:  # 如果我们没有使用输入解决方案:
                        solution['sets'] += [tempitem]
                        solution['hand'] += self.copy_list_and_delete_tiles(tempitem, tiles)
                    else:
                        solution['sets'] = input_solution['sets'].copy()
                        solution['sets'] += [tempitem]
                        solution['hand'] = self.copy_list_and_delete_tiles(tempitem, tiles)
                    solution['score'] = self.calculate_score(solution['sets'])
                    tempsolutions.append(solution)
        return tempsolutions

    def find_all_groups(self, tiles):
        '''这段代码定义了一个名为find_all_groups的方法，它接受一个名为tiles的参数。它初始化一个名为groups的空列表。

        然后，它从1迭代到self.sg。
        然后使用tiles参数和i的当前值调用另一个名为find_all_groups_with_n的方法。
        然后使用extend方法将该方法调用的结果添加到groups列表中。

        最后，groups列表作为find_all_groups方法的结果返回。
        '''
        groups = []

        for i in range(1,self.sg.numbers+1):
            groups.extend(self.find_all_groups_with_n(tiles,i))
        return groups
    
    def find_all_groups_with_n(self,tiles,n):
        '''这段代码定义了一个函数find_all_groups_with_n，它接受两个参数:tiles和n。

        该函数过滤tiles列表，只保留值等于n或self.sg.colors + 1的最大值的tiles。

        如果筛选后的方块长度小于3，则返回一个空列表。

        否则，该函数将遍历所有可能的滤镜组合，其长度从3到self.sg.colors + 1。

        对于每个组合，它都使用is_set_group函数检查它是否是一个有效的组。如果是，则将组合添加到groups列表。

        最后，该函数返回groups列表。'''
        groups = []
        filtertiles = list(filter(lambda tile: (tile[1] == n or tile[0] == self.sg.colors+1), tiles))  # 只保留value等于n的方块
        if len(filtertiles) < 3:
            return []
        for i in range(3, self.sg.colors+1):  # for lengths 3 and 4
            for item in combinations(filtertiles, i):  # 对于每一个瓷砖组合
                tempitem = list(item) # 暂时将项目转换为一个列表
                if self.is_set_group(tempitem):
                    groups.append(tempitem)
        return groups

    def extend_runs(self, solution, n):
        '''这段代码定义了一个名为extend_runs的函数，它接受三个参数:self、solution和n。

        该函数尝试针对给定的解和给定的n值扩展运行时间。
        它通过过滤solution['hand']列表来做到这一点，只包含值等于n或值等于self.sg.colors+1的方块。

        如果该函数确定当前解决方案对给定的n值无效，则返回一个空列表。
        否则，如果解决方案中还有剩余的贴片，它将尝试通过将匹配的贴片附加到解决方案中的每个集合中来扩展解决方案中的每个集合。
        它使用扩展集创建一个新的解决方案，从手上删除使用过的瓷砖，计算分数，并将新的解决方案附加到extended_run_solutions列表。

        最后，它返回extended_run_solutions列表。'''
        '''In this function we try to extend runs for a given solution and a given n value.'''
        extended_run_solutions = []
        solution_tiles = list(filter(lambda tile: (tile[1] == n or tile[0] == self.sg.colors+1),
                                     solution['hand']))  # 只选择n值的tiles和jokers
        #在这里，我们检查当前尝试的解决方案是否包含有效的、可扩展的集合。
        #我们通过检查解决方案中未完成的集合在当前n值下是否仍然可扩展来实现
        #如果不是，我们不返回该解决方案
        #这使得算法明显更快
        if not self.check_validity(n, solution):
            return []

        if len(solution_tiles) > 0:  # 如果我们有剩余的瓷砖
            for tile_set in solution['sets']:  # 对于当前解中的每一个集合
                tempsolution = defaultdict(list)  # 创建一个新的解决方案
                tempsolution['sets'] = solution['sets'].copy()
                # 在这里，我们尝试扩展运行，如果这样做，我们将解决方案追加
                if not self.is_set_group(tile_set):  # 如果当前集合不是一个组
                    for tile in solution_tiles:  # 对于每个包含当前n值的方块
                        if self.can_extend(tile, tile_set):  # 检查该集合是否可以扩展
                            # extend it:
                            newset = tile_set.copy()
                            newset.append(tile)  # 扩展集合
                            solution_tiles.remove(tile)  # 移除瓷砖
                            tempsolution['sets'].remove(tile_set)
                            tempsolution['sets'] += [newset]  # 将新集合附加到解决方案
                            tempsolution['hand'] = self.copy_list_and_delete_tiles(tile, solution[
                                'hand'])  # 从手上取出用过的瓷砖
                            tempsolution['score'] = self.calculate_score(tempsolution['sets'])  # 计算分数
                            extended_run_solutions.append(tempsolution)  # 将新的解决方案附加到解决方案列表中
                            break  # 如果我们扩展了一个集合，就不需要检查其他贴图
                else:
                    continue
            tempsolution['score'] = self.calculate_score(tempsolution['sets'])  # 计算分数
            if tempsolution['score'] != 0:
                extended_run_solutions.append(tempsolution)  # 将新的解决方案附加到解决方案列表中
        return extended_run_solutions

    def start_new_runs(self, tiles, n, input_solution=None):
        '''In this function we start new runs.
        这段代码定义了一个名为start_new_runs的函数，它接受一个tiles列表、一个整数n和一个可选的input_solution。
        这个函数会根据特定的条件开始新的运行。

        首先，代码对tiles列表进行筛选，只包含第二个元素等于n或第一个元素等于self.sg.colors+1的tiles。

        接下来，通过调用check_validity函数检查是否提供了input_solution，以及它是否有效。
        如果input_solution无效，则返回一个空列表。

        然后，代码使用嵌套循环生成不同长度的滤镜组合。对于每个组合，都会创建一个新的解决方案。
        如果没有input_solution，则使用该组合创建一个集合，并将其添加到tempsolution中。
        通过删除集合中使用的tiles来更新tempsolution的hand属性，并基于集合计算score属性。
        最后，将临时解决方案添加到new_runs列表。

        如果存在input_solution，则将该input_solution中的集合复制到新的tempsolution中。
        该过程的其余部分与不使用input_solution的情况类似。

        该函数返回包含生成的解决方案的new_runs列表。'''
        new_runs = []
        filtertiles = list(filter(lambda tile: (tile[1] == n or tile[0] == self.sg.colors+1), tiles)) # 只选择值为n的tiles或jokers

        #这里我们再次检查我们正在使用的解决方案是否仍然有效
        #如果不是，我们不会返回它，也不会尝试在其中开始新的运行，因为它永远不会有效
        #这减少了我们尝试开始新运行的无用解决方案的数量

        if input_solution is not None: # 如果我们正在处理一个输入解决方案
            if not self.check_validity(n, input_solution): # 检查输入解决方案的有效性
                return [] # 如果无效，则返回空列表

        for i in range(1, len(filtertiles)+1): # 对于过滤器的长度从1到长度的组合:
            for item in combinations(filtertiles, i): # 找出每个长度为I的组合
                tempsolution = defaultdict(list) # 制定新的解决方案
                tempitem = list(item) # 将组合转换为列表
                if input_solution == None: # 如果没有输入解
                    if len(item) == 1: # 如果只有一个瓦片
                        set_to_append = [tempitem]
                    else:
                        set_to_append = []
                        for j in range(0, len(tempitem)):
                            set_to_append.append([tempitem[j]]) # 我们需要这样做以保持正确的格式

                    tempsolution['sets'] += set_to_append
                    tempsolution['hand'] = self.copy_list_and_delete_tiles(set_to_append, tiles)
                    tempsolution['score'] = self.calculate_score(tempsolution['sets'])
                    new_runs.append(tempsolution) # 添加找到的解决方案
                else: #if there is an input solution
                    tempsolution['sets'] = input_solution['sets'].copy() # 将解决方案中的集合复制到新的解决方案集中
                    if len(item) == 1:
                        set_to_append = [tempitem]
                    else:
                        set_to_append = []
                        for j in range(0, len(tempitem)):
                            set_to_append.append([tempitem[j]])
                    tempsolution['sets'] += set_to_append
                    tempsolution['hand'] = self.copy_list_and_delete_tiles(set_to_append, input_solution['hand'])
                    tempsolution['score'] = self.calculate_score(tempsolution['sets'])
                    new_runs.append(tempsolution)
        return new_runs

    @staticmethod
    def check_validity(n, input_solution,joker_color=6):
        '''如果解决方案仍然有效，则返回True，否则返回false
        这段代码定义了一个静态方法check_validity，它接受三个参数:n、input_solution和joker_color。
        它遍历input_solution字典中的'sets'键，并检查解决方案中的每个集合是否有效。
        如果一个集合的元素少于3个，它会根据集合的最后一个元素和n的值进行额外的检查。
        如果所有检查过后解仍然有效，该方法返回True，否则返回False。
        '''
        output = True
        for set in input_solution['sets']:  # 对于解中的每一个集合
            if len(set) < 3:  # 如果集合中只有2个或更少的图案
                if set[-1][0] == joker_color:  # 如果最后一块是小丑
                    if len(set) == 1:
                        continue
                    elif set[-2][0] == joker_color:
                        continue
                    elif n - set[-2][1] > 3:  # 如果在此之前的贴片比当前n低3(不再可扩展
                        output = False  # 返回一个空列表，不要进行新的运行
                elif n - set[-1][1] > 2:  # 如果集合的最后一个瓦片比当前n小2(不再可扩展)
                    output = False  # 返回一个空列表，不要进行新的运行
        return output
    @staticmethod
    def can_extend(tile, set,joker_color=6):
        '''如果输入的图案可以扩展输入的集合，这个函数返回true，否则返回false
        这段代码定义了一个名为can_extend的静态方法，该方法检查给定的瓦片是否可以扩展为给定的瓦片集合。
        如果图案可以扩展，这个方法返回True，否则返回False。
        这个方法接受3个参数:tile、set和joker_color，这是一个可选参数，默认值为6，
        前者表示要检查扩展的图案，后者表示要检查扩展的图案集合。
        这段代码使用了一系列条件语句，根据与瓦片值和小丑颜色相关的特定条件来确定是否可以扩展瓦片。
        '''
        if tile[0] == joker_color and set[-1][0] == joker_color: # jokers can always extend other jokers
            return True
        if tile[0] == joker_color and set[-1][1] < 15: # 小丑总是可以延长一个运行，但不能用作16的，因为他们不存在
            return True
        if len(set) == 1 and set[0][0] == joker_color and tile[1] > 1: #如果运行中只存在一个小丑，如果tile > 1，则可扩展，
            return True
        elif set[0][0] != tile[0]:  # 如果这张牌和第一张牌花色不同 (这绝不是 joker)
            return False
        elif set[-1][1] == tile[1] - 2:  # 如果集合中最后一个图案的值比这个图案小2，那么这个集合是可扩展的
            return True
        elif set[-1][0] == joker_color:  # 如果最后一块瓷砖是小丑
            if set[-2][0] == joker_color: # 如果瓷砖在前面的也是一个joker
                if len(set) > 2:
                    if set[-3][1] == tile[1]-3:
                        return True
            elif set[-2][1] == tile[1] - 2:  # 如果小丑之前的贴图与贴图-2具有相同的值，则set是可扩展的
                return True

        else:  # Set不可扩展
            return False

    @staticmethod
    def is_set_group(tiles,colors=5):
        '''This function returns true if the given set is a group, otherwise returns false
        这段代码定义了一个名为is_set_group的静态方法，该方法检查给定的一组瓦片是否组成一个组。
        一个组被定义为至少有3个颜色相同或值相同的贴图。
        如果集合是一个组，该函数返回True，否则返回False。'''
        if len(tiles) < 3:  # 组总是至少有3个瓷砖长，所以如果它更短，那返回错误
            return False
        if len(tiles) > colors:
            return False
        joker_color = colors+1
        # 因为我们从不在小组外使用joker，除非这是一个赢得比赛的动作，
        # 如果一个集合的第一个瓷砖和最后一个瓷砖的值相等，那么它就是一个组。
        color_set = set()
        value_set = set()
        joker_num = 0

        for tile in tiles:
            if tile[0] == joker_color:
                joker_num = joker_num+1
            else:
                color_set.add(tile[0])
                value_set.add(tile[1])
        if len(color_set)+joker_num != len(tiles):
            return False
        if len(value_set)>1:
            return False
        return True
    
    @staticmethod
    def find_all_runs(tiles):
        '''
        从给定的瓷砖中查找所有合法运行。
        这段代码定义了一个静态方法find_all_runs，它以一个图块列表作为输入。
        它创建了一个字典color_dict，用于按颜色对图像块进行分组。
        然后，它遍历字典中的每个颜色，并按对应的tile的第二个元素排序。
        然后，它检查第二个元素为2的连续图像块，并将它们添加到临时运行列表中。
        如果一次运行的长度至少为3，则将其附加到最终的运行列表中。
        最后，它返回在输入方块中找到的运行列表。
        '''
        color_dict = {}
        for tile in tiles:
            color = tile[0]
            if color not in color_dict:
                color_dict[color] = []
            color_dict[color].append(tile)
        
        runs = []

        for color, tiles_list in color_dict.items():
            sorted_tiles = sorted(tiles_list, key=lambda x: x[1])
            tempruns = []
            for i in range(len(sorted_tiles)):
                current_tile = sorted_tiles[i]
                for current_run in tempruns:
                    prev_tile = current_run[-1]
                    if current_tile[1] - prev_tile[1] == 2:
                        current_run.append(current_tile)
                        if(len(current_run)>=3):
                            runs.append(current_run.copy())
                tempruns.append([current_tile])
        return runs

    @staticmethod
    def find_all_sub_solutions(solutions, n):
        '''这段代码定义了一个名为find_all_sub_solutions的静态方法。它需要两个参数:列表solutions和数字n。

        这个方法首先在控制台打印一条消息。然后，它创建一个名为sub_solutions的空列表。
        它调用了SolveTiles类中的另一个方法subset_helper，传入了solutions、n、一个空列表和sub_solutions列表。

        最后，它返回sub_solutions列表。
        '''
        print("find_all_sub_solutions")
        sub_solutions = []
        SolveTiles.subset_helper(solutions, n, [], sub_solutions)
        return sub_solutions

    @staticmethod
    def subset_helper(solutions, n, current_subset, sub_solutions):
        '''这段代码定义了一个名为subset_helper的静态方法。它需要4个参数:solutions、n、current_subset和sub_solutions。

        该方法用于生成总长度为n的解列表的所有可能子集。它使用递归对解列表进行迭代，并构建解列表的子集。

        基线条件如下:

        如果n为0，意味着找到了一个有效的子集，因此它将current_subset附加到sub_solutions并返回。
        如果解列表为空或n为负，这意味着我们无法形成一个有效的子集，因此它返回。
        然后，该方法选择解的第一个元素，并检查其长度是否小于或等于n。
        如果小于，则递归调用剩余解的subset_helper，将n减去所选解的长度，并将current_subset附加到所选解上。

        最后，它递归地调用subset_helper，包括剩余的解、n、current_subset和sub_solutions，但不包括选中的解。

        这段代码是一个名为SolveTiles的类的一部分，但是如果没有更多的上下文，就不可能确定这段代码的目的或用途。
        '''
        if n == 0:  
            sub_solutions.append(current_subset)
            return
        if len(solutions) == 0 or n < 0:  
            return
        
        solution = solutions[0]
        remaining_solutions = solutions[1:]
        
        if len(solution) <= n:
            SolveTiles.subset_helper(remaining_solutions, n - len(solution), current_subset + [solution], sub_solutions)
        
        SolveTiles.subset_helper(remaining_solutions, n, current_subset, sub_solutions)

    def check_play(self,board,tiles):
        '''
        检查给定的瓷砖是否都可以在当前板状态下。
        这段代码定义了一个名为check_play的函数，它接受三个形参:self、board和tiles。
        它将SolveTiles类的begin_time属性设置为当前时间。
        然后，它调用另一个名为find_play的方法，传入参数board、tiles、n=2和play_type=CHECK_PLAY，
        并将返回值分配给solution和play_tiles。
        最后，它返回解决方案列表。
        '''
        SolveTiles.begin_time = time.time()
        solution = []
        solution,play_tiles = self.find_play(board,tiles,n=2,play_type=CHECK_PLAY)
        return solution

    def find_solution(self,board_tiles,tiles,solution=[],play_type=NORMAL_PLAY):
        '''
        根据当前板状态，从给定的瓷砖中找到有效的解决方案。
        这段代码定义了一个名为find_solution的函数，它接受几个参数，包括board_tiles、tiles、solution和play_type。
        该函数试图根据棋盘的当前状态和一组给定的方块找到一个有效的解决方案。
        如果找到有效的解决方案，则返回True。如果超过了最大搜索时间，则返回False。
        如果没有更多的图案或剩下的图案少于3个，它也返回False。
        然后，该函数生成所有可能的瓦片组合，并使用更新后的面板递归调用自己，并减去瓦片，
        直到找到有效的解决方案或尝试了所有组合。
        '''          
        if self.is_valid_new_solution(solution,board_tiles,tiles,play_type=play_type):
                return True
        if time.time()-SolveTiles.begin_time>SolveTiles.max_search_time:
            return False
        if(not tiles or len(tiles)<3):
            return False

        combinations = self.find_all_combinations(tiles)
        if combinations==[]:
            return False
        for c in combinations:
            solution.append(c)
            if self.find_solution(board_tiles,subtract_tiles(tiles,c),solution,play_type):
                return True
            elif len(solution)>0:
                solution.pop()
        return False

    def is_valid_new_solution(self,solution,board_tiles,tiles,play_type=NORMAL_PLAY):
        '''
       检查给定的解决方案作为新的解决方案是否合法。
       这段代码定义了一个方法is_valid_new_solution，
       它检查给定的解决方案是否有效。如果解决方案包含棋盘上的所有图案，
       并且解决方案中的图案数量大于棋盘图案的长度，则认为解决方案是有效的。
       根据游戏类型进一步检查有效性。如果播放类型是NORMAL_PLAY，则认为解决方案有效。
       如果游戏类型是CHECK_PLAY，并且没有方块了，那么该解决方案是有效的。
       如果游戏类型是INITIAL_MELD_PLAY，则计算解决方案的得分，如果得分大于或等于30，
       则解决方案有效。如果所有条件都不满足，则认为解决方案无效。
        '''
        if self.is_solution_contain_all_tiles(solution,board_tiles) and count_tile_in_solution(solution)>len(board_tiles):
            if play_type==NORMAL_PLAY:
                return True
            elif play_type==CHECK_PLAY and len(tiles)==0:
                return True
            elif play_type==INITIAL_MELD_PLAY:
                score = sum([tile[1] for tile in tiles_in_solution(solution)])
                if score>=30:
                    return True
        return False


    def is_solution_contain_all_tiles(self,solution,tiles):
        '''
        此函数以解决方案和瓷砖列表作为输入。 
        它检查解决方案是否包含所有提供的瓷砖。
        这段代码定义了一个函数is_solution_contain_all_tiles，它接受一个解决方案和一个tiles列表作为输入。
        它检查解决方案是否包含提供的所有瓷砖。
        它通过将提供的瓦片减去解决方案瓦片后剩余的瓦片的长度与解决方案瓦片的长度进行比较来实现这一点。
        如果这些长度的总和等于解决方案方块的长度，则返回True;否则，返回False。
        '''
        solution_tiles = tiles_in_solution(solution)
        remain_tiles = subtract_tiles(solution_tiles,tiles)
        return len(remain_tiles)+len(tiles)==len(solution_tiles)
            
    def find_all_combinations(self,tiles):
        '''
        查找所有合法组并从当前瓷砖集运行。
        这段代码定义了一个名为find_all_combinations的函数，它接受一个参数tiles。它从给定的图像块集合中找到所有图像块的有效组合。

        该函数首先调用另一个名为find_all_runs的函数，并将结果添加到名为solutions的列表中。
        然后，它调用另一个名为find_all_groups的函数，并再次将结果添加到解决方案列表中。
        最后，它返回solutions列表，其中包含所有方块的有效组合。
        '''
        solutions = []
        runs = self.find_all_runs(tiles)
        solutions.extend(runs)
        groups = self.find_all_groups(tiles)
        solutions.extend(groups)
        return solutions

    def find_play(self,board,tiles,n=2,play_type=NORMAL_PLAY):
        '''
        从当前牌集中查找要播放的牌的合法组合。
        这段代码定义了一个名为find_play的方法，它接受几个参数，包括board、tiles、n和play_type。

        该方法首先初始化一个名为sub_solutions的空列表。

        如果板的长度小于或等于n，则将板的副本附加到sub_solutions列表中。否则，它从面板中生成n个元素的所有可能组合，并将它们分配给sub_solutions列表。

        接下来，该方法遍历列表sub_solutions中的每个解。它创建了两个新的列表:s_tiles包含当前解决方案中的瓦片，而hand_tiles是瓦片列表与s_tiles组合后的副本。

        然后，它初始化一个名为solution的空列表，并使用s_tiles、hand_tiles、solution和play_type作为参数调用另一个名为find_solution的方法。如果find_solution返回True，它会执行一些操作来创建一个新的解决方案和一个要播放的方块列表。然后，它返回新的解决方案和贴片列表。

        如果没有找到有效的解决方案，该方法对新的解决方案和瓷砖列表都返回None。

        这种方法的目的似乎是根据给定的棋盘和方块找到一个有效的方块组合。
        '''
        SolveTiles.begin_time = time.time()
        sub_solutions = []
        if(len(board)<=n):
            sub_solutions.append(board.copy())
        else:
            sub_solutions = combinations(board,n)
        for s in sub_solutions:
            s_tiles = tiles_in_solution(s)
            hand_tiles = [tile for tile in tiles]
            hand_tiles.extend(tiles_in_solution(s))
            solution = []
            if self.find_solution(s_tiles,hand_tiles,solution,play_type):
                new_solution = subtract_solution(board,s)
                new_solution.extend(solution)
                board_tiles = tiles_in_solution(board)
                solution_tiles = tiles_in_solution(new_solution)
                item = subtract_tiles(solution_tiles,board_tiles)
                # print("tiles",tiles)
                # print("board",board)
                # print("solution",solution)
                # print("new_solution",new_solution)
                # print("s",s)
                # print("play_tiles",item)
                return new_solution,item
        return None,None
    
    def initial_meld(self,tiles):
        '''
        找到最初的融合解决方案。
        这段代码定义了一个名为initial_meld的函数，它接受一个参数tiles。
        它会找到所有组，并在tiles列表中运行，并将它们添加到解决方案列表中。
        然后，遍历解列表，找到长度最大的解并返回。
        '''
        solutions = []
        groups = self.find_all_groups(tiles)
        solutions.extend(groups)
        runs = self.find_all_runs(tiles)
        solutions.extend(runs)
        index = 0
        max_len = 0
        for i in range(solutions):
            if len(solutions[i])>max_len:
                max_len = len(solutions[i])
                index = i
        return solutions[i]

    def compare_two_solutions(self,solution1,solution2):
        '''
        比较两个解决方案以检查它们是否包含相同的瓷砖。
        这段代码定义了一个函数compare_two_solutions，它接受两个方案作为参数。
        它比较解决方案，以检查它们是否包含相同的方块。
        该函数遍历每个解决方案，并将平铺的图块分成两个单独的列表。
        然后，它根据自定义的比较函数对列表进行排序。
        如果两个列表的长度不相等，则返回False。
        否则，比较两个列表中的每个图案，检查它们是否相同。如
        果有图案不一样，就返回False。如果所有的图案都一样，则返回True。
        '''
        tiles1 = []
        tiles2 = []
        for tiles in solution1:
            tiles1.extend(tiles)
        for tiles in solution2:
            tiles2.extend(tiles)
        tiles1 = sorted(tiles1,key=compare_func)
        tiles2 = sorted(tiles2,key=compare_func)
        if len(tiles1) != len(tiles2):
            return False
        for i in range(len(tiles1)):
            if tiles1[i][0]!=tiles2[i][0] or tiles1[i][1]!=tiles2[i][1]:
                return False
        return True
        

    @staticmethod
    def calculate_score(hand,joker_color=6):
        '''该函数计算一只手的得分
        这段代码定义了一个名为calculate_score的静态方法，它接受两个参数:hand和joker_color。
        它根据特定条件计算一副牌的得分。该函数遍历手上的每一组平铺图，检查平铺图的长度是否大于2。
        如果是，则遍历集合中的每个贴片，并将贴片的第二个元素添加到score变量，除非贴片的第一个元素等于joker_color。
        如果手里有一个set的长度小于或等于2，则得分设置为0并返回。
        最后，该函数返回计算出的得分。
        '''
        score = 0
        for set in hand:
            if len(set) > 2:
                for tile in set:
                    if tile[0] != joker_color: #小丑不得分
                        score += tile[1] #score是所有瓷砖的总和
            else:  # 如果任何一个集合不超过两个，则解决方案不得分
                score = 0
                return score
        return score

    @staticmethod
    def copy_list_and_delete_tiles(to_remove, tiles):
        '''此函数以to_remove作为输入,并从瓦片中删除内容
            主要用于从手上用过的瓷砖。
            这段代码定义了一个名为copy_list_and_delete_tiles的静态方法，它接受两个形参:to_remove和tiles。
            这个方法的目的是根据to_remove中的值从一个tiles列表中删除元素。
            如果to_remove为None，该方法简单地返回原始瓷砖列表。如果to_remove是一个元组，它会从列表中删除特定的贴片。
            如果to_remove是一个瓦片列表(元组或列表)，它将从列表中删除所有这些瓦片。
            然后，该方法返回修改后的瓦片列表。该函数还包括一些中文文档说明其用途。
            '''
        if to_remove is None:  # 如果不需要移除任何东西，返回瓷砖
            return tiles
        else:
            templist = tiles.copy()  # 复制瓷砖
            if type(to_remove) is tuple:  # 如果我们只移除一块瓷砖
                templist.remove(to_remove)
                return templist
            else:  # 如果to_remove是要删除的瓷砖列表
                for tile in to_remove:
                    if type(tile) is tuple:
                        templist.remove(tile)
                    else:
                        for tupletile in tile:
                            templist.remove(tupletile)
                return templist
