import pygame
from control import eventControl
from watermelon_chess.common import *
from watermelon_chess.game import Game


class UI:

    def __init__(self, name):
        pygame.init()
        self.playerName = name
        self.game = Game()
        self.setScreen()
        pygame.display.set_caption('西瓜棋')
        pygame.mouse.set_visible(False)

        self.temp_move = []

        self.background = pygame.image.load(BACKGROUND).convert()
        self.mouse_cursor = pygame.image.load(BLACKTILE).convert_alpha()
        self.blackTile = pygame.image.load(BLACKTILE).convert_alpha()
        self.whiteTile = pygame.image.load(WHITETILE).convert_alpha()
        self.hand = pygame.image.load(HAND).convert_alpha()
        self.menuImage = pygame.image.load(MENU).convert()
        self.startImage = pygame.image.load(START).convert_alpha()
        self.replayImage = pygame.image.load(REPLAY).convert_alpha()
        self.backImage = pygame.image.load(BACK).convert_alpha()
        self.localGameImage = pygame.image.load(LOCALGAME).convert_alpha()

        self.networkGameImage = pygame.image.load(
            NETWORKGAME).convert_alpha()
        self.quitImage = pygame.image.load(QUIT).convert_alpha()
        self.msgFont = pygame.font.Font(FONT, 20)
        self.queryFont = pygame.font.Font(FONT, 30)
        self.queryBkgImage = pygame.image.load(QUERY_BKG).convert()
        self.confirmImage = pygame.image.load(CONFIRM).convert_alpha()
        self.cancelImage = pygame.image.load(CANCEL).convert_alpha()
        self.displayMenu()

    def eventManagement(self):
        while True:
            if self.game.status == 'quit':
                return
            else:
                for event in pygame.event.get():
                    self.game = eventControl(event, self.game)
                    if self.game.status == 'menu':
                        self.displayMenu()
                    elif self.game.status == 'play':
                        self.displayPlay()
                    elif self.game.status == 'query':
                        self.displayQuery()
                    elif self.game.status == 'over':
                        self.displayGameOver()

    def displayMenu(self):
        self.setScreen()
        self.screen.blit(self.menuImage, (0, 0))
        self.screen.blit(self.localGameImage, LOCALGAME_RECT[0])
        self.screen.blit(self.networkGameImage, NETWORKGAME_RECT[0])
        self.screen.blit(self.quitImage, MENU_QUIT_RECT[0])
        self.blitMouse()
        pygame.display.update()

    def displayPlay(self):
        self.setScreen()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.backImage, BACK_RECT[0])
        self.screen.blit(self.replayImage, REPLAY_RECT[0])
        self.text_surface = self.msgFont.render(
            self.game.msg, True, (102, 204, 255), (255, 255, 255))

        color = self.game.strColor(self.game.playerColor)
        sideText = ['your name:' + str(self.game.name),
                    'your color:' + color,
                    'turn:' + str(self.game.turn),
                    'room:' + str(self.game.roomID),
                    "'q' to quit",
                    "'f' to fullscreen",
                    ]
        sideY = 5
        for text in sideText:
            self.sideSurface = self.msgFont.render(
                text, True, (102, 204, 255), (255, 255, 255))
            self.screen.blit(self.sideSurface, (430, sideY))
            sideY += 25
        self.screen.blit(self.text_surface, (10, 500))
        self.blitChessmen()
        self.blitMouse()
        pygame.display.update()

    def displayQuery(self):
        self.setScreen()
        self.screen.blit(self.queryBkgImage, (0, 0))
        self.text_surface = self.queryFont.render(
            self.game.msg, True, (102, 204, 255), (255, 255, 255))
        self.screen.blit(self.text_surface, (160, 200))
        self.screen.blit(self.confirmImage, CONFIRM_RECT[0])
        self.screen.blit(self.cancelImage, CANCEL_RECT[0])
        self.blitMouse()
        pygame.display.update()

    def setScreen(self):
        if self.game.fullScreenModChanged:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), self.game.fullScreenMod, 32)
            self.game.fullScreenModChanged = False

    def blitChessmen(self):
        for index, point in enumerate(self.game.pointStatus):
            if point != 0:
                (x, y) = self.fixXY(index)
                if point == BLACK:
                    self.screen.blit(self.blackTile, (x, y))
                elif point == WHITE:
                    self.screen.blit(self.whiteTile, (x, y))
                else:
                    self.game.msg = 'pointPos error'
        if self.game.chessmanInHand:
            if self.game.chosenChessmanColor == BLACK:
                self.screen.blit(self.blackTile, (self.handX, self.handY))
            else:
                self.screen.blit(self.whiteTile, (self.handX, self.handY))

    def blitMouse(self):
        self.handX, self.handY = pygame.mouse.get_pos()
        self.handX -= self.mouse_cursor.get_width() / 2
        self.handY -= self.mouse_cursor.get_height() / 2
        self.screen.blit(self.hand, (self.handX, self.handY))

    def fixXY(self, target):
        return fix_xy(target)


def main():
    name = 'player1'
    ui = UI(name)
    ui.eventManagement()


if __name__ == '__main__':
    main()
