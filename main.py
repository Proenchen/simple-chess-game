import pygame as pg
import os
import pieces
import tkinter
from tkinter import messagebox
from game import Game
from board import Board, BOARD_SIZE

GAME_NAME = "Julians Schachspiel"
WINDOW_ICON = 'icon.png'
WIDTH, HEIGHT = 888, 888  # should be a multiple of BOARD_SIZE
SQ_SIZE = WIDTH // BOARD_SIZE
FPS = 60
WHITE_SQ_COLOR = '#f0d9b5'
DARK_SQ_COLOR = '#b58863'
MOVE_SQ_COLOR = '#d0d46c'
CHECK_COLOR = '#e6725b'
IMG_DIR = 'assets'


def get_coordinate(rc):
    return rc[1] * SQ_SIZE, rc[0] * SQ_SIZE


def get_rc_num(xy):
    return xy[1] // SQ_SIZE, xy[0] // SQ_SIZE


def draw_board(screen):
    for rc, square in Board.SQUARES.items():
        color = WHITE_SQ_COLOR if square else DARK_SQ_COLOR
        pg.draw.rect(screen, color, (*get_coordinate(rc), SQ_SIZE, SQ_SIZE))


def load_pieces():
    images = {}
    for dict in pieces.PIECE_REPR.values():
        for repr in dict.values():
            images[repr] = pg.transform.scale(
                pg.image.load(os.path.join(IMG_DIR, repr + '.png')), (SQ_SIZE, SQ_SIZE)
            )
    return images


def draw_pieces(p, screen, pieces):
    for rc, piece in p.items():
        screen.blit(pieces[piece.__repr__()], get_coordinate(rc))


def main():

    # Initialize pygame
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    pg.display.set_caption(GAME_NAME)
    pg.display.set_icon(pg.image.load(os.path.join(IMG_DIR, WINDOW_ICON)))

    # Initialize game
    game_pieces = load_pieces()
    game = Game()
    curr_position = game.get_position()
    running = True
    drag = None
    showed_message = False

    # main-loop
    while running:
        clock.tick(FPS)
        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN and not drag:
                from_pos = get_rc_num(pg.mouse.get_pos())
                if from_pos in curr_position:
                    piece = curr_position[from_pos]
                    drag = game_pieces[piece.__repr__()]
                    del curr_position[from_pos]

            elif event.type == pg.MOUSEBUTTONUP and drag:
                to_pos = get_rc_num(pg.mouse.get_pos())

                # PLEASE DO NOT MOVE PIECES OUT OF THE WINDOW!
                if to_pos[0] >= BOARD_SIZE or to_pos[0] < 0 or to_pos[1] >= BOARD_SIZE or to_pos[1] < 0:
                    curr_position[from_pos] = piece
                    drag = None
                    continue

                game.move(piece, from_pos, to_pos)
                curr_position = game.get_position()
                drag = None

        draw_board(screen)

        if game.last_move_from and game.last_move_to is not None:
            pg.draw.rect(screen, MOVE_SQ_COLOR, (*get_coordinate(game.last_move_from), SQ_SIZE, SQ_SIZE))
            pg.draw.rect(screen, MOVE_SQ_COLOR, (*get_coordinate(game.last_move_to), SQ_SIZE, SQ_SIZE))

        if game.is_check():
            pg.draw.rect(screen, CHECK_COLOR, (*get_coordinate(game.get_active_king_pos()), SQ_SIZE, SQ_SIZE))

        draw_pieces(curr_position, screen, game_pieces)

        if drag:
            rect = drag.get_rect(center=pg.mouse.get_pos())
            screen.blit(drag, rect)

        pg.display.flip()

        if game.is_checkmate and not showed_message:
            showed_message = True
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showinfo("Checkmate!", "{} was checkmated".format(game.current_player.value))

        if game.stalemate and not showed_message:
            showed_message = True
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showinfo("Draw!", "Stalemate!")


if __name__ == "__main__":
    main()
