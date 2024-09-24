import itertools
import numpy as np
import random
from collections import defaultdict


class SetGenerator:

    def __init__(self, numbers=15, colors=5, jokers=2, combi_len=3, tile_sets=2, minimal_startscore=30):
        '''这段代码为类定义了一个初始化方法。
        它设置了几个属性，如numbers、colors、jokers、combi_len、tile_sets和minimal_startscore。
        它还根据给定的属性生成一个贴片列表，并计算贴片的总数。
        '''
        self.numbers = numbers
        self.colors = colors
        self.jokers = jokers
        self.combi_len = combi_len
        self.tile_sets = tile_sets
        self.tiles = self.generate_tiles()
        self.tilecount = (colors * numbers) + jokers
        self.minimal_startscore = minimal_startscore

    def generate_tiles(self):
        '''
        这段代码为一个游戏生成一个方块列表。
        它创建不同颜色和数字的瓷砖，也包括小丑瓷砖。
        在返回之前，这些方块会被随机打乱。
        '''
        tiles = []
        for tileset in range(1, self.tile_sets + 1):
            for color in range(1, self.colors + 1):
                for tilenumber in range(1, self.numbers + 1):
                    tiles.append((color, tilenumber))
        for joker in range(1, self.jokers + 1):
            tiles.append((self.colors+1, joker))
        random.shuffle(tiles)
        return tiles

