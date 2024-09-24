from termcolor import colored

class Console:

    def __init__(self):
        pass

    def text_gui(self, query, *answers):
        '''这个函数允许我们提出一个带有一些答案的查询，并处理输入
        这段代码定义了一个名为text_gui的函数，它接受一个查询和可变数量的答案作为输入。
        它创建了一个循环，向用户提示查询，接受用户输入，并检查输入是否与提供的任何答案匹配。
        如果找到有效的答案，则返回它。否则，系统会提示用户再试一次。'''
        while True:
            print(query)
            inp = input()
            answer = inp.lower() if inp.lower() in [str(answer) for answer in answers] else None
            if answer is not None:
                return answer
            else:
                print('Try again, that input was not valid')

    def board_pretty_print(self, board):
        '''这个函数在终端上打印彩色的电路板
        这段代码定义了一个名为board_pretty_print的函数，用于在终端上打印彩色电路板。
        它迭代board参数，并构建每组tiles的字符串表示。然后，该函数打印出棋盘的最终字符串表示。'''
        if len(board) == 0:
            pass
        else:
            printstring = ''
            for set in board:
                setstring = ''
                for tile in set:
                    setstring += f'{self.print_colored_tile(tile)}'
                printstring += f'[{setstring}] '
            print(printstring)

    def solution_pretty_print(self, solution):
        '''这个函数在终端中以彩色打印解决方案
        这段代码定义了一个名为solution_pretty_print的方法，它接受两个参数:self和solution。
        该方法在终端中以彩色格式打印解决方案。
        它遍历解字典中的集合，并连接集合中每个瓷砖的字符串表示。
        最后，打印拼接后的字符串。'''
        printstring = ''
        for set in solution['sets']:
            setstring = ''
            for tile in set:
                setstring += f'{self.print_colored_tile(tile)}'
            printstring += f'[{setstring}] '
        print(printstring)

    def print_colored_tile(self, tile):
        '''这个函数为单个瓷砖创建一个有色字符串
         这段代码定义了一个函数print_colored_tile，它接受一个tile形参。
         它创建了一个字典colordict，将数字映射到颜色。
         该函数返回一个字符串，该字符串被方括号括起来，并使用colordict字典根据tile[0]的值着色。
         颜色是使用colored函数应用的。 '''
        colordict = {1: 'grey', 2: 'red', 3: 'yellow', 4: 'blue', 5: 'magenta',6: 'magenta'}
        return f'[{colored(tile[1], colordict[tile[0]])}]'

    def rack_pretty_print(self, rack):
        '''该函数在终端上打印彩色机架
        这段代码定义了一个名为rack_pretty_print的函数，它接受一个rack形参。
        它遍历rack中的元素，对它们进行排序，并检查第一个字符是否小于6。
        如果是，则调用一个名为print_colored_tile的方法，并将结果连接到一个字符串。
        如果第一个字符不小于6，它会在print_colored_tile的结果中添加一些额外的文本。
        最后，它会打印出字符串及其首部。'''
        printstring = ''
        for i in sorted(rack):
            if int(i[0]) < 6:
                printstring += ' ' + self.print_colored_tile(i)
            else:
                printstring += ' jokers: ' + self.print_colored_tile(i)
        print('These tiles are on your rack:')
        print(printstring)
