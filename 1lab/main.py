import copy

WHITE = "white"
BLACK = "black"

letters = "abcdefgh"


def to_pos(s):
    if len(s) != 2 or s[0] not in letters or not s[1].isdigit():
        raise ValueError
    return (8 - int(s[1]), letters.index(s[0]))


def to_notation(pos):
    return letters[pos[1]] + str(8 - pos[0])


class Piece:
    symbol = "?"

    def __init__(self, color):
        self.color = color
        self.has_moved = False

    def get_attacks(self, board, pos):
        return self.get_moves(board, pos)

    def name(self):
        return "Фигура"



class Guard(Piece):
    symbol = "G"
    def name(self): return "Страж"

    def get_moves(self, board, pos):
        moves=[]
        x,y=pos
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            for step in [1,2]:
                t=(x+dx*step,y+dy*step)
                if board.in_bounds(t):
                    if board.is_empty(t) or board.is_enemy(t,self.color):
                        moves.append(t)
                    else:
                        break
        return moves


class Jumper(Piece):
    symbol = "J"
    def name(self): return "Прыгун"

    def get_moves(self, board, pos):
        moves=[]
        x,y=pos
        for dx,dy in [(2,0),(-2,0),(0,2),(0,-2)]:
            t=(x+dx,y+dy)
            if board.in_bounds(t) and not board.is_friend(t,self.color):
                moves.append(t)
        return moves


class DiagonalGuard(Piece):
    symbol = "D"
    def name(self): return "Диагональный страж"

    def get_moves(self, board, pos):
        moves=[]
        x,y=pos
        for dx,dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            for step in [1,2]:
                t=(x+dx*step,y+dy*step)
                if board.in_bounds(t):
                    if board.is_empty(t) or board.is_enemy(t,self.color):
                        moves.append(t)
                    else:
                        break
        return moves



class Pawn(Piece):
    symbol = "P"
    def name(self): return "Пешка"

    def get_moves(self, board, pos):
        moves=[]
        x,y=pos
        d=-1 if self.color==WHITE else 1

        one=(x+d,y)
        if board.is_empty(one):
            moves.append(one)

            two=(x+2*d,y)
            if not self.has_moved and board.is_empty(two):
                moves.append(two)

        for dy in [-1,1]:
            t=(x+d,y+dy)
            if board.is_enemy(t,self.color):
                moves.append(t)

        return moves

    def get_attacks(self, board, pos):
        x,y=pos
        d=-1 if self.color==WHITE else 1
        return [(x+d,y-1),(x+d,y+1)]


class Rook(Piece):
    symbol="R"
    def name(self): return "Ладья"
    def get_moves(self,b,p): return b.linear(p,self.color,[(1,0),(-1,0),(0,1),(0,-1)])


class Bishop(Piece):
    symbol="B"
    def name(self): return "Слон"
    def get_moves(self,b,p): return b.linear(p,self.color,[(1,1),(1,-1),(-1,1),(-1,-1)])


class Queen(Piece):
    symbol="Q"
    def name(self): return "Ферзь"
    def get_moves(self,b,p): return b.linear(p,self.color,
        [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)])


class Knight(Piece):
    symbol="N"
    def name(self): return "Конь"
    def get_moves(self,b,p):
        moves=[]
        x,y=p
        for dx,dy in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            t=(x+dx,y+dy)
            if b.in_bounds(t) and not b.is_friend(t,self.color):
                moves.append(t)
        return moves


class King(Piece):
    symbol="K"
    def name(self): return "Король"
    def get_moves(self,b,p):
        moves=[]
        x,y=p
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx==dy==0: continue
                t=(x+dx,y+dy)
                if b.in_bounds(t) and not b.is_friend(t,self.color):
                    moves.append(t)
        return moves



class Board:
    def __init__(self):
        self.grid=[[None]*8 for _ in range(8)]
        self.history=[]

    def in_bounds(self,pos): return 0<=pos[0]<8 and 0<=pos[1]<8
    def is_empty(self,pos): return self.in_bounds(pos) and self.grid[pos[0]][pos[1]] is None
    def is_enemy(self,pos,color):
        return self.in_bounds(pos) and self.grid[pos[0]][pos[1]] and self.grid[pos[0]][pos[1]].color!=color
    def is_friend(self,pos,color):
        return self.in_bounds(pos) and self.grid[pos[0]][pos[1]] and self.grid[pos[0]][pos[1]].color==color

    def linear(self,pos,color,dirs):
        moves=[]
        for dx,dy in dirs:
            x,y=pos
            while True:
                x+=dx; y+=dy
                if not self.in_bounds((x,y)): break
                if self.is_empty((x,y)):
                    moves.append((x,y))
                elif self.is_enemy((x,y),color):
                    moves.append((x,y)); break
                else: break
        return moves

    def move(self,s,e):
        piece=self.grid[s[0]][s[1]]
        captured=self.grid[e[0]][e[1]]

        if captured:
            print(f"{piece.name()} съел {captured.name()} на {to_notation(e)}")
        else:
            print(f"{piece.name()} пошла на {to_notation(e)}")

        self.grid[e[0]][e[1]]=piece
        self.grid[s[0]][s[1]]=None
        piece.has_moved=True

        if isinstance(piece,Pawn) and (e[0]==0 or e[0]==7):
            self.grid[e[0]][e[1]]=Queen(piece.color)
            print("Пешка превращена в ферзя")

        self.history.append((s,e,piece,captured))

    def undo(self):
        if not self.history:
            print("Ошибка: нет ходов для отката")
            return
        s,e,p,c=self.history.pop()
        self.grid[s[0]][s[1]]=p
        self.grid[e[0]][e[1]]=c



class Game:
    def __init__(self,mode):
        self.board=Board()
        self.turn=WHITE
        self.mode=mode
        self.setup()

    def setup(self):
        for i in range(8):
            self.board.grid[1][i]=Pawn(BLACK)
            self.board.grid[6][i]=Pawn(WHITE)

        if self.mode=="classic":
            order=[Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
        else:
            order=[Rook,Guard,Jumper,Queen,King,DiagonalGuard,Knight,Rook]

        for i,cls in enumerate(order):
            self.board.grid[0][i]=cls(BLACK)
            self.board.grid[7][i]=cls(WHITE)

    def print_board(self):
        print("\n   a b c d e f g h")
        for i,row in enumerate(self.board.grid):
            print(8-i," ",end="")
            for p in row:
                print("." if not p else (p.symbol if p.color==WHITE else p.symbol.lower()), end=" ")
            print()

    def угрозы(self,color):
        res=set()

        for x in range(8):
            for y in range(8):
                enemy = self.board.grid[x][y]

                if enemy and enemy.color != color:
                    attacks = enemy.get_attacks(self.board, (x, y))

                    for ax, ay in attacks:
                        if not self.board.in_bounds((ax, ay)):
                            continue

                        target = self.board.grid[ax][ay]

                        if target and target.color == color:
                            res.add(to_notation((ax, ay)))

        return res

    def король_под_шахом(self,color):
        for x in range(8):
            for y in range(8):
                p=self.board.grid[x][y]
                if p and p.color==color and isinstance(p,King):
                    return to_notation((x,y)) in self.угрозы(color)
        return False

    def ходы(self,sq):
        try:
            pos=to_pos(sq)
        except:
            print("Ошибка: неверная клетка")
            return

        p=self.board.grid[pos[0]][pos[1]]
        if not p:
            print("Ошибка: на этой клетке нет фигуры")
            return

        print(p.name())
        print("Ходы:",[to_notation(m) for m in p.get_moves(self.board,pos)])

    def play(self):
        while True:
            self.print_board()
            print("Ход:", "Белые" if self.turn==WHITE else "Чёрные")

            print("Команды:")
            print("  ход a2 a4")
            print("  ходы a2")
            print("  откат")

            th=self.угрозы(self.turn)
            if th:
                print("Под угрозой:",list(th))

            if self.король_под_шахом(self.turn):
                print("ШАХ!")

            cmd=input("> ").split()

            if not cmd:
                print("Ошибка: введите команду")
                continue

            if cmd[0]=="откат":
                self.board.undo()
                continue

            if cmd[0]=="ходы":
                if len(cmd)<2:
                    print("Ошибка: укажите клетку")
                    continue
                self.ходы(cmd[1])
                continue

            if cmd[0]=="ход":
                if len(cmd)<3:
                    print("Ошибка: формат хода (e2 e4)")
                    continue

                try:
                    s,e=to_pos(cmd[1]),to_pos(cmd[2])
                except:
                    print("Ошибка: неверный формат координат")
                    continue

                p=self.board.grid[s[0]][s[1]]

                if not p:
                    print("Ошибка: на клетке нет фигуры")
                    continue

                if p.color!=self.turn:
                    print("Ошибка: не твой ход")
                    continue

                if e not in p.get_moves(self.board,s):
                    print("Ошибка: недопустимый ход")
                    continue

                self.board.move(s,e)
                self.turn=BLACK if self.turn==WHITE else WHITE
            else:
                print("Ошибка: неизвестная команда")


if __name__=="__main__":
    print("1 — классика")
    print("2 — новые фигуры")
    mode="classic" if input("> ")=="1" else "custom"
    Game(mode).play()