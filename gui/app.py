from tkinter import *
from tkinter import ttk
from game.board import Board
import random
import threading
import queue

current_n = 3
current_k = 3
board = Board(current_n, current_k)
buttons = []

game_id = 0
ai_queue = queue.Queue()

def is_human_turn():
    if board.player == 1:
        return combo_x.get() == "Human"
    else:
        return combo_o.get() == "Human"

def next_turn(row, column):
    if not is_human_turn():
        return

    if not board.is_terminal() and board.grid[row][column] == 0:
        board.play((row, column))
        render()
        window.after(100, trigger_ai)

def trigger_ai():
    if board.is_terminal() or is_human_turn():
        return

    t = threading.Thread(target=ai_worker, args=(board.copy(), game_id))
    t.start()

def ai_worker(board_copy, current_game_id):
    moves = board_copy.legal_moves()
    best_move = random.choice(moves) if moves else None

    ai_queue.put((best_move, current_game_id))


def poll_ai():
    try:
        move, thread_game_id = ai_queue.get_nowait()

        if thread_game_id == game_id and move is not None:
            board.play(move)
            render()
            window.after(350, trigger_ai)
    except queue.Empty:
        pass

    window.after(50, poll_ai)



def render():
    MARK = {1: "X", 2: "O", 0: ""}

    for row in range(board.n):
        for column in range(board.n):
            val = board.grid[row][column]

            buttons[row][column]['text'] = MARK.get(val, "")

            buttons[row][column].config(bg="#F0F0F0")

            if hasattr(board, 'win_line') and board.win_line:
                for r, c in board.win_line:
                    buttons[r][c].config(bg="lightgreen")

            elif board.is_full() and board.winner_ is None:
                buttons[row][column].config(bg="lightyellow")

    if board.winner_:
        winner_mark = MARK.get(board.winner_, str(board.winner_))
        label.config(text=f"{winner_mark} wins!")
    elif board.is_full():
        label.config(text="Tie!")
    else:
        player_mark = MARK.get(board.player, str(board.player))
        label.config(text=f"{player_mark}'s turn")


def new_game():

    global board, current_n, current_k, game_id

    game_id += 1

    try:
        current_n = int(n_var.get())
        current_k = int(k_var.get())
        # Đảm bảo k không được lớn hơn n
        if current_k > current_n:
            current_k = current_n
    except ValueError:
        current_n, current_k = 3, 3

    board = Board(current_n, current_k)

    build_grid(current_n)
    render()

    window.after(350, trigger_ai)


def build_grid(n):
    global buttons

    for w in frame.winfo_children():
        w.destroy()

    buttons = [[None for _ in range(n)] for _ in range(n)]

    font_size = max(10, 40 - 2 * n)

    for row in range(n):
        for column in range(n):
            btn = Button(frame, text="", font=('consolas', font_size), width=5, height=2,
                         command=lambda r=row, c=column: next_turn(r, c))

            btn.grid(row=row, column=column)
            buttons[row][column] = btn

# ================= KỞI TẠO GIAO DIỆN ================= #
window = Tk()
window.title("Tic-Tac-Toe")

label = Label(text="Game Start", font=('consolas', 40))
label.pack(side="top", pady=10)

control_frame = Frame(window)
control_frame.pack(side="top", pady=5)

Label(control_frame, text="Size (n):", font=('consolas', 12)).grid(row=0, column=0, padx=5)
n_var = StringVar(value="3")
Spinbox(control_frame, from_=3, to=20, textvariable=n_var, width=5, font=('consolas', 12)).grid(row=0, column=1, padx=5)

Label(control_frame, text="Win (k):", font=('consolas', 12)).grid(row=0, column=2, padx=5)
k_var = StringVar(value="3")
Spinbox(control_frame, from_=3, to=20, textvariable=k_var, width=5, font=('consolas', 12)).grid(row=0, column=3, padx=5)

AGENT_LIST = ["Human", "Random"] 

Label(control_frame, text="Player X:", font=('consolas', 12)).grid(row=1, column=0, padx=5, pady=5)
combo_x = ttk.Combobox(control_frame, values=AGENT_LIST, state="readonly", width=10, font=('consolas', 12))
combo_x.set("Human")
combo_x.grid(row=1, column=1, padx=5, pady=5)

Label(control_frame, text="Player O:", font=('consolas', 12)).grid(row=1, column=2, padx=5, pady=5)
combo_o = ttk.Combobox(control_frame, values=AGENT_LIST, state="readonly", width=10, font=('consolas', 12))
combo_o.set("Human")
combo_o.grid(row=1, column=3, padx=5, pady=5)

reset_button = Button(control_frame, text="Ván mới", font=('consolas', 14), command=new_game)
reset_button.grid(row=2, column=0, columnspan=4, pady=10)

frame = Frame(window)
frame.pack()

build_grid(current_n)
new_game()

poll_ai()  

window.mainloop()

