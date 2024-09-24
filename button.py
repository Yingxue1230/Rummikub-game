import pygame
from pygame.locals import *

class Button:

    def __init__(self,text,rect):
        '''This code defines a class method called __init__. 
        It takes in two parameters, text and rect. 
        The method assigns the values of text and rect to the instance variables self.text and self.rect, respectively.
        It also sets the instance variables self.enable and self.show to True.'''
        self.text = text
        self.rect = rect
        self.enable = True
        self.show = True
    
    def handle_event(self,event):
        '''这段代码定义了一个接受事件参数的函数handle_event。
        它检查是否设置了enable标志，如果没有，则返回。
        然后，检查事件类型是否为MOUSEBUTTONUP事件，
        以及鼠标位置是否在self.rect定义的矩形内。
        如果两个条件都为真，就调用perform_mouse_up函数。'''
        if not self.enable:
            return
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                self.perform_mouse_up()

    def perform_mouse_up(self):
        '''这段代码定义了一个名为perform_mouse_up的函数，
        它什么都不做(它的函数体是空的)。
        它接受一个参数self，在面向对象编程中，
        这个参数通常用于引用方法所属类的实例。'''
        pass

    def refresh(self,screen):
        '''这段代码定义了一个refresh方法，它接受一个screen参数。
        它首先检查self.show是真实的。如果没有，则立即返回。
        然后，它使用pygame.mouse.get_pos()取得鼠标的当前位置。
        它使用pygame.font.SysFont()创建了一个大小为12的font对象。
        接下来，检查鼠标是否在self.rect定义的矩形内。
        如果是，就使用pygame.draw.rect()在屏幕上绘制一个浅灰色的矩形。否则，它将绘制一个白色矩形。
        然后，它渲染存储在self中的文本。
        使用font对象的文本，颜色设置为黑色。
        它计算矩形的中心位置，并在该位置将渲染的文本块移到屏幕上。'''
        if not self.show:
            return
        mouse_pos = pygame.mouse.get_pos()
        font = pygame.font.SysFont(None, 12)
        
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, pygame.Color("lightgray"), self.rect)
        else:
            pygame.draw.rect(screen, pygame.Color("white"),self.rect)
    
        text = font.render(self.text, True, pygame.Color("black"))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)