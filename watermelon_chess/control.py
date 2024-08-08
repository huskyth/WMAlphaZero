import pygame
import urllib
from pygame.locals import *

from MCTS import control_by_net_work
from watermelon_chess.common import *

# difficulty of the game
DEEPEST_LEVEL = 3


def inRect(x, y, rect, game):
    if rect[0][0] < x < rect[0][0] + rect[1] \
            and rect[0][1] < y < rect[0][1] + rect[2] \
            and rect in game.enableButton:
        return True
    else:
        return False


def chosenButton(x, y, game):
    if inRect(x, y, LOCALGAME_RECT, game):
        return 'localGame'
    elif inRect(x, y, NETWORKGAME_RECT, game):
        return 'networkGame'
    elif inRect(x, y, MENU_QUIT_RECT, game):
        return 'quit'
    elif inRect(x, y, BACK_RECT, game):
        return 'back'
    elif inRect(x, y, REPLAY_RECT, game):
        return 'replay'
    elif inRect(x, y, CONFIRM_RECT, game):
        return 'confirm'
    elif inRect(x, y, CANCEL_RECT, game):
        return 'cancel'
    else:
        return None


def chosenChessman(x, y, gameMap):
    x, y = x / (SCREEN_WIDTH + 0.0), y / (SCREEN_HEIGHT + 0.0)
    for point in range(21):
        if abs(x - gameMap[point][0]) < 0.05 and abs(y - gameMap[point][1]) < 0.05:
            return point
    return None


def getScore(pointStatus, distance):
    score = 0
    scoreLevel = [1, 2, 4, 6]
    black = [x for x in distance if x == BLACK]
    # if chessman was eaten, sub 8 score for each one
    score -= 8 * (6 - len(black))
    for chessman, color in enumerate(pointStatus):
        advantg = 0
        disadvtg = 0
        neighboors = getNeighboors(chessman, distance)
        for eachNeighboor in neighboors:
            # computer use black chessman as default
            if pointStatus[eachNeighboor] == BLACK and color == WHITE:
                advantg += 1
                score += scoreLevel[advantg - 1]
            elif pointStatus[eachNeighboor] == WHITE and color == BLACK:
                disadvtg += 1
                score -= scoreLevel[disadvtg - 1]
            else:
                pass
            # unnecessary
            '''
            elif color == WHITE:
                if pointStatus[eachNeighboor] == BLACK:
                    score += 2
                elif pointStatus[eachNeighboor] == WHITE:
                    score -= 2
            '''
    return score


def computerMove(pointStatus, distance, level):
    move = []
    maxScore = -48
    bestMove = None
    # for convenient, set color = computer color (black) when enter the
    # function firstly
    if level % 2 == 1:
        selfColor = BLACK
        opponentColor = WHITE
    else:
        selfColor = WHITE
        opponentColor = WHITE
    # In the deepest level, the best move is itself, replace it with None
    if level > DEEPEST_LEVEL:
        score = getScore(pointStatus, distance)
        return [], score
    else:
        for chessman, color in enumerate(pointStatus):
            if color == selfColor:
                for neighboorChessman in getNeighboors(chessman, distance):
                    if pointStatus[neighboorChessman] == 0:
                        move.append((chessman, neighboorChessman))
        if not move:
            return [], -49
        bakPointStatus = copy.deepcopy(pointStatus)
        for eachMove in move:
            pointStatus[eachMove[1]] = selfColor
            pointStatus[eachMove[0]] = 0
            pointStatus = shiftOutChessman(pointStatus, distance)
            # newMove is useless, just for return the best move in the first
            # level
            newMove, score = computerMove(pointStatus, distance, level + 1)
            if score > maxScore:
                maxScore = score
                bestMove = eachMove
            # revoke the change
            pointStatus = copy.deepcopy(bakPointStatus)
        return bestMove, maxScore


def checkWinner(game):
    game.chessBoard.blackNum = 0
    game.chessBoard.whiteNum = 0
    for color in game.pointStatus:
        if color == BLACK:
            game.chessBoard.blackNum += 1
        elif color == WHITE:
            game.chessBoard.whiteNum += 1
    if game.chessBoard.blackNum != game.chessBoard.whiteNum:
        game.status = 'query'
        game.over = True
        if game.chessBoard.blackNum < game.chessBoard.whiteNum:
            winner = WHITE
        else:
            winner = BLACK
        if game.playerColor == winner:
            game = setQuery(game, 'play', 'menu', 'You win!')
        else:
            game = setQuery(game, 'play', 'menu', 'You lose~')
    return game


def setQuery(game, lastStatus, nextStatus, msg):
    game.lastStatus = lastStatus
    game.nextStatus = nextStatus
    game.enableButton = [CONFIRM_RECT, CANCEL_RECT]
    game.msg = msg
    return game


def post(roomID, action, name, url, pointStatus=None):
    parameters = {'roomID': roomID, 'action': action,
                  'name': name, 'pointStatus': pointStatus}
    postData = urllib.urlencode(parameters)
    req = urllib2.Request(url, postData)
    req.add_header('Content-Type', "application/x-www-form-urlencoded")
    response = urllib2.urlopen(req)
    jsonData = response.read()
    return json.loads(jsonData)


def initNetworkGame(game):
    response = post('', 'enter', '', game.url)
    if response['playerNum'] == '1':
        game.name = response['player1']
        game.playerColor = WHITE
        game.opponentColor = BLACK
    else:
        game.name = response['player2']
        game.playerColor = BLACK
        game.opponentColor = WHITE
    game.roomID = response['roomID']
    post(game.roomID, 'pre', game.name, game.url)
    return game


def sendData(game):
    response = post(game.roomID, 'play', game.name,
                    game.url, json.dumps(game.pointStatus))


def getData(game):
    response = post(game.roomID, 'query', game.name, game.url)
    return response


def resetRoom(game):
    response = post(game.roomID, 'leave', game.name, game.url)


# set a time interval


def clock(game):
    if time.time() - game.time > 0.8:
        return True
    else:
        return False


def checkOpponent(game):
    newPointStatus = game.pointStatus
    if clock(game):
        response = getData(game)
        print
        response
        game.msg = time.ctime() + "waiting for you opponent's movement"
        game.time = time.time()
        game.turn = response['turn']
        try:
            newPointStatus = json.loads(response['pointStatus'])
        except:
            pass
        if not response['turn']:
            game.status = 'query'
            game = setQuery(game, 'play', 'menu',
                            'Your opponent ran away~ return pls')
            game.enableButton = [CONFIRM_RECT]
    return game, newPointStatus


def playControl(event, game, network, wm_game):
    color = game.strColor(game.playerColor)
    chessman = None
    button = None
    if event.type == MOUSEBUTTONDOWN:
        x, y = pygame.mouse.get_pos()
        button = chosenButton(x, y, game)
        chessman = chosenChessman(x, y, game.gameMap)

    if button:
        if button == 'replay':
            game.status = 'query'
            game = setQuery(game, 'play', 'play', 'Reset the game?')
        elif button == 'back':
            game.status = 'query'
            game = setQuery(game, 'play', 'menu', 'Back to menu?')
        else:
            pass
    else:
        if game.turn == 'none':
            if clock(game):
                response = getData(game)
                game.msg = 'preparing' + time.ctime()
                game.time = time.time()  # reset the clock after connection
                if response['preOK']:
                    game.turn = response['turn']
                    if game.name == response['player1']:
                        game.opponent = response['player2']
                    else:
                        game.opponent = response['player1']
                    game.msg = 'turn:' + game.turn
        elif game.turn == game.name:
            game.msg = "it's your turn to move with " + color
            if chessman != None:
                if not game.chessmanInHand:
                    if game.pointStatus[chessman] == game.playerColor:
                        game.chosenChessmanColor = game.pointStatus[chessman]
                        game.pointStatus[chessman] = 0
                        game.chessmanInHand = True
                        game.chosenChessman = chessman
                        game.msg = 'Chessman was chose'
                else:
                    if game.pointStatus[chessman] == 0 and \
                            game.distance[game.chosenChessman][chessman] == 1:
                        game.pointStatus[chessman] = game.chosenChessmanColor
                        game.msg = 'Chessman was moved'
                        bakPointStatus = copy.deepcopy(game.pointStatus)
                        game.pointStatus = shiftOutChessman(
                            bakPointStatus, game.distance)
                        game = checkWinner(game)
                        if game.isOnline:
                            game.turn = game.opponent
                            sendData(game)
                            game.time = time.time()
                        else:
                            game.turn = 'computer'
                    else:
                        game.pointStatus[
                            game.chosenChessman] = game.chosenChessmanColor
                        game.msg = 'not a valid choice'
                    game.chessmanInHand = False
            if game.isOnline:
                game, newPointStatus = checkOpponent(game)

        elif game.turn == 'computer':
            if event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                button = chosenButton(x, y, game)
                chessman = chosenChessman(x, y, game.gameMap)
                if button == 'replay':
                    game.status = 'query'
                    game = setQuery(game, 'play', 'play', 'Reset the game?')
                elif button == 'back':
                    game.status = 'query'
                    game = setQuery(game, 'play', 'menu', 'Back to menu?')
                else:
                    pass
            bakPointStatus = copy.deepcopy(game.pointStatus)
            # move, score = computerMove(bakPointStatus, game.distance, 1)
            move, score = control_by_net_work(network, bakPointStatus, wm_game)
            if game.pointStatus[move[0]] == 0:
                print()
            assert game.pointStatus[move[0]] != 0
            assert game.pointStatus[move[1]] == 0
            game.pointStatus[move[1]] = game.opponentColor
            game.pointStatus[move[0]] = 0
            game.turn = game.name
            bakPointStatus = copy.deepcopy(game.pointStatus)
            game.pointStatus = shiftOutChessman(bakPointStatus, game.distance)
            game = checkWinner(game)

        elif game.turn == game.opponent:
            if event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                button = chosenButton((x, y), game)
                chessman = chosenChessman((x, y), game.gameMap)
                if button == 'replay':
                    game.status = 'query'
                    game = setQuery(game, 'play', 'play', 'Reset the game?')
                elif button == 'back':
                    game.status = 'query'
                    game = setQuery(game, 'play', 'menu', 'Back to menu?')
                else:
                    pass
            game, newPointStatus = checkOpponent(game)
            if game.turn == game.name:
                game.pointStatus = newPointStatus
            bakPointStatus = copy.deepcopy(game.pointStatus)
            game.pointStatus = shiftOutChessman(bakPointStatus, game.distance)
            game = checkWinner(game)
        else:
            pass
    return game


def menuControl(event, game):
    if event.type == MOUSEBUTTONDOWN:
        x, y = pygame.mouse.get_pos()
        button = chosenButton(x, y, game)
        if button == 'localGame':
            game.resetGame()
            game.status = 'play'
            game.isOnline = False
            game.name = 'local'
            game.turn = game.name
            game.opponentColor = BLACK
            game.enableButton = [BACK_RECT, REPLAY_RECT]
        elif button == 'networkGame':
            game.resetGame()
            game.status = 'play'
            game.isOnline = True
            # pdb.set_trace()
            game = initNetworkGame(game)
            game.msg = time.ctime() + '  enter room: ' + game.roomID + \
                       ' get name: ' + game.name
            game.time = time.time()
            game.enableButton = [BACK_RECT, REPLAY_RECT]

        elif button == 'quit':
            game.status = 'query'
            game = setQuery(game, 'menu', 'quit', 'Quit the game?')
        else:
            pass
    return game


def queryControl(event, game):
    if event.type == MOUSEBUTTONDOWN:
        x, y = pygame.mouse.get_pos()
        button = chosenButton(x, y, game)
        if button == 'confirm':
            game.resetGame()
            game.status = game.nextStatus
            if game.nextStatus == 'play':
                game.enableButton = [BACK_RECT, REPLAY_RECT]
                if game.over:
                    game.resetGame()
            else:
                if game.nextStatus == 'menu':
                    game.enableButton = [LOCALGAME_RECT,
                                         NETWORKGAME_RECT, MENU_QUIT_RECT]
                # if menu or quit
                if game.isOnline:
                    resetRoom(game)
        elif button == 'cancel':
            game.status = game.lastStatus
        else:
            pass

    return game


def eventControl(event, game, network, wm_game):
    if event.type == QUIT:
        game.lastStatus = game.status
        game.status = 'query'
        game = setQuery(game, game.lastStatus, 'quit', 'Quit the game?')

    elif event.type == KEYDOWN:
        if event.key == K_q:
            # pdb.set_trace()
            game.lastStatus = game.status
            game.status = 'query'
            game = setQuery(game, game.lastStatus, 'quit', 'Quit the game?')
        elif event.key == K_f:
            if game.fullScreenMod == 0:
                game.fullScreenMod = FULLSCREEN
            else:
                game.fullScreenMod = 0
            game.fullScreenModChanged = True

    else:
        if game.status == 'menu':
            game = menuControl(event, game)
        elif game.status == 'play':
            game = playControl(event, game, network, wm_game)
        elif game.status == 'query':
            game = queryControl(event, game)
        else:
            pass

    return game


