import pygame as pg
import os
import pieces as p
import tkinter
from tkinter import PhotoImage, messagebox
from game import Game, PROMOTION_PIECES
from board import Board, BOARD_SIZE


GAME_NAME = "Prönchen's Chess Game"
WINDOW_ICON = 'icon.png'
WIDTH, HEIGHT = 888, 888  # should be a multiple of BOARD_SIZE
SQ_SIZE = WIDTH // BOARD_SIZE
FPS = 120
WHITE_SQ_COLOR = '#f0d9b5'
DARK_SQ_COLOR = '#b58863'
MOVE_SQ_COLOR = '#d0d46c'
CHECK_COLOR = '#e6725b'
IMG_DIR = 'assets'
IMG_DIR_PIECES = IMG_DIR + '/piece_set_std'  # piece images
IMG_DIR_ICONS = IMG_DIR + '/promotion_icons'  # icons for promotion window


class Application:
    def __init__(self):
        self.game = Game()
        self.curr_position = self.game.get_position()
        self.game_pieces = self._load_pieces()
        self.screen = None
        self.clock = None
        self._init_screen()

    def run(self):
        # Initialize game
        running = True
        drag = None
        showed_message = False

        # main-loop
        while running:
            self.clock.tick(FPS)
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    running = False
                    break

                elif event.type == pg.MOUSEBUTTONDOWN and not drag:
                    from_pos = self._get_rc_num(pg.mouse.get_pos())
                    if from_pos in self.curr_position:
                        piece = self.curr_position[from_pos]
                        drag = self.game_pieces[piece.__repr__()]
                        del self.curr_position[from_pos]

                elif event.type == pg.MOUSEBUTTONUP and drag:
                    to_pos = self._get_rc_num(pg.mouse.get_pos())

                    # PLEASE DO NOT MOVE PIECES OUT OF THE WINDOW!
                    if to_pos[0] >= BOARD_SIZE or to_pos[0] < 0 or to_pos[1] >= BOARD_SIZE or to_pos[1] < 0:
                        self.curr_position[from_pos] = piece
                        drag = None
                        continue

                    self.game.move(piece, from_pos, to_pos)
                    self.curr_position = self.game.get_position()
                    drag = None

            self._draw_board()

            if self.game.last_move_from and self.game.last_move_to is not None:
                pg.draw.rect(self.screen, MOVE_SQ_COLOR, (
                    *self._get_coordinate(self.game.last_move_from), SQ_SIZE, SQ_SIZE))
                pg.draw.rect(self.screen, MOVE_SQ_COLOR, (
                    *self._get_coordinate(self.game.last_move_to), SQ_SIZE, SQ_SIZE))

            if self.game.is_check():
                pg.draw.rect(self.screen, CHECK_COLOR, (
                    *self._get_coordinate(self.game.get_active_king_pos()), SQ_SIZE, SQ_SIZE))

            self._draw_pieces()

            if drag:
                rect = drag.get_rect(center=pg.mouse.get_pos())
                self.screen.blit(drag, rect)

            pg.display.flip()

            if self.game.is_checkmate and not showed_message:
                showed_message = True
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showinfo("Checkmate!", "{} was checkmated".format(self.game.current_player.value))

            if self.game.stalemate and not showed_message:
                showed_message = True
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showinfo("Draw!", "Stalemate!")

            if self.game.threefold_rep and not showed_message:
                showed_message = True
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showinfo("Draw!", "Threefold Repetition!")

            if self.game.fifty_moves and not showed_message:
                showed_message = True
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showinfo("Draw!", "50-Move Rule!")

            if self.game.promotion:
                self._build_promotion_window()
                self.curr_position = self.game.get_position()
                self._draw_board()

    def _get_coordinate(self, rc):
        return rc[1] * SQ_SIZE, rc[0] * SQ_SIZE

    def _get_rc_num(self, xy):
        return xy[1] // SQ_SIZE, xy[0] // SQ_SIZE

    def _init_screen(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.display.set_caption(GAME_NAME)
        pg.display.set_icon(pg.image.load(os.path.join(IMG_DIR, WINDOW_ICON)))

    def _draw_board(self):
        for rc, square in Board.SQUARES.items():
            color = WHITE_SQ_COLOR if square else DARK_SQ_COLOR
            pg.draw.rect(self.screen, color, (*self._get_coordinate(rc), SQ_SIZE, SQ_SIZE))

    def _load_pieces(self):
        images = {}
        for dict in p.PIECE_REPR.values():
            for repr in dict.values():
                images[repr] = pg.transform.scale(
                    pg.image.load(os.path.join(IMG_DIR_PIECES, repr + '.png')), (SQ_SIZE, SQ_SIZE)
                )
        return images

    def _draw_pieces(self):
        for rc, piece in self.curr_position.items():
            self.screen.blit(self.game_pieces[piece.__repr__()], self._get_coordinate(rc))

    def _promote(self, id, window, color):
        self.game.promote(PROMOTION_PIECES[id].__name__, self.game.last_move_to, color)
        window.destroy()

    def _build_promotion_window(self):
        root = tkinter.Tk()
        root.title('Promote to...')
        root.geometry("430x120")
        root.config(bg=DARK_SQ_COLOR)
        root.eval('tk::PlaceWindow . center')

        icons = []
        promoting_color = p.Color.WHITE if self.game.current_player == p.Color.BLACK else p.Color.BLACK
        pieces = p.PIECE_REPR[promoting_color]
        for key in pieces:
            if key in PROMOTION_PIECES:
                icons.append(PhotoImage(file=os.path.join(IMG_DIR_ICONS, pieces[key] + '_small.png')))

        for i in range(len(icons)):
            tkinter.Button(
                root, image=icons[i],
                bd=0, bg=WHITE_SQ_COLOR, activebackground=MOVE_SQ_COLOR,
                command=lambda i=i: self._promote(i, root, promoting_color)
            ).place(x=20 + i*100, y=15)

        root.mainloop()


if __name__ == '__main__':
    Application().run()
