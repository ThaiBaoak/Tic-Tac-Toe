from tkinter import *
from tkinter import ttk
from game.board import Board
from agents.mcts_agent import MCTSAgent
from agents.alphabeta import AlphaBetaAgent
from agents.backtracking import BacktrackingAgent
import random
import threading
import queue

current_n = 3
current_k = 3
board = Board(current_n, current_k)

game_id = 0
ai_queue = queue.Queue()

def is_human_turn():
    if board.player == 1:
        return combo_x.get() == "Human"
    else:
        return combo_o.get() == "Human"

def current_agent():
    if board.player == 1:
        return combo_x.get()
    return combo_o.get()

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

    try:
        iterations = max(1, int(iterations_var.get()))
    except ValueError:
        iterations = 500
        iterations_var.set("500")

    t = threading.Thread(
        target=ai_worker,
        args=(board.copy(), game_id, current_agent(), iterations),
        daemon=True
    )
    t.start()

def ai_worker(board_copy, current_game_id, agent_name, iterations):
    if agent_name == "MCTS":
        best_move = MCTSAgent(iterations=iterations).choose_move(board_copy)
    elif agent_name == "AlphaBeta":
        best_move = AlphaBetaAgent().choose_move(board_copy)
    elif agent_name == "Backtracking":
        best_move = BacktrackingAgent().choose_move(board_copy)
    else:
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



def board_geometry():
    # Ô vuông, tự co theo kích thước canvas hiện tại để luôn thấy toàn bàn
    width = max(canvas.winfo_width(), 1)
    height = max(canvas.winfo_height(), 1)
    cell = max(min(width, height) // board.n, 1)
    offset_x = (width - cell * board.n) // 2
    offset_y = (height - cell * board.n) // 2
    return cell, offset_x, offset_y

def on_canvas_click(event):
    cell, offset_x, offset_y = board_geometry()
    column = (event.x - offset_x) // cell
    row = (event.y - offset_y) // cell
    if 0 <= row < board.n and 0 <= column < board.n:
        next_turn(row, column)

def render():
    MARK = {1: "X", 2: "O", 0: ""}

    canvas.delete("all")
    cell, offset_x, offset_y = board_geometry()
    font_size = max(int(cell * 0.45), 6)
    win_cells = set(board.win_line) if board.win_line else set()
    tied = board.is_full() and board.winner_ is None

    for row in range(board.n):
        for column in range(board.n):
            x1 = offset_x + column * cell
            y1 = offset_y + row * cell

            if (row, column) in win_cells:
                color = "lightgreen"
            elif tied:
                color = "lightyellow"
            else:
                color = "#F0F0F0"

            canvas.create_rectangle(x1, y1, x1 + cell, y1 + cell,
                                    fill=color, outline="#808080")

            mark = MARK.get(board.grid[row][column], "")
            if mark:
                canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=mark,
                                   font=('consolas', font_size, 'bold'))

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

    render()

    window.after(350, trigger_ai)

# ================= KỞI TẠO GIAO DIỆN ================= #
window = Tk()
window.title("Tic-Tac-Toe")

# Cửa sổ luôn nằm gọn trong màn hình và căn giữa; bàn cờ co giãn theo cửa sổ
screen_w = window.winfo_screenwidth()
screen_h = window.winfo_screenheight()
win_w = min(900, screen_w - 80)
win_h = min(950, screen_h - 120)
window.geometry(f"{win_w}x{win_h}+{(screen_w - win_w) // 2}+{max((screen_h - win_h) // 2 - 20, 0)}")
window.minsize(640, 480)

label = Label(text="Game Start", font=('consolas', 24))
label.pack(side="top", pady=5)

control_frame = Frame(window)
control_frame.pack(side="top", pady=5)

Label(control_frame, text="Size (n):", font=('consolas', 12)).grid(row=0, column=0, padx=5)
n_var = StringVar(value="3")
Spinbox(control_frame, from_=3, to=20, textvariable=n_var, width=5, font=('consolas', 12)).grid(row=0, column=1, padx=5)

Label(control_frame, text="Win (k):", font=('consolas', 12)).grid(row=0, column=2, padx=5)
k_var = StringVar(value="3")
Spinbox(control_frame, from_=3, to=20, textvariable=k_var, width=5, font=('consolas', 12)).grid(row=0, column=3, padx=5)

Label(control_frame, text="MCTS iterations:", font=('consolas', 12)).grid(row=0, column=4, padx=5)
iterations_var = StringVar(value="500")
Spinbox(control_frame, from_=1, to=100000, increment=100, textvariable=iterations_var,
        width=7, font=('consolas', 12)).grid(row=0, column=5, padx=5)

AGENT_LIST = ["Human", "Random", "MCTS","AlphaBeta", "Backtracking"] 

Label(control_frame, text="Player X:", font=('consolas', 12)).grid(row=1, column=0, padx=5, pady=5)
combo_x = ttk.Combobox(control_frame, values=AGENT_LIST, state="readonly", width=10, font=('consolas', 12))
combo_x.set("Human")
combo_x.grid(row=1, column=1, padx=5, pady=5)

Label(control_frame, text="Player O:", font=('consolas', 12)).grid(row=1, column=2, padx=5, pady=5)
combo_o = ttk.Combobox(control_frame, values=AGENT_LIST, state="readonly", width=10, font=('consolas', 12))
combo_o.set("Human")
combo_o.grid(row=1, column=3, padx=5, pady=5)

reset_button = Button(control_frame, text="Ván mới", font=('consolas', 14), command=new_game)
reset_button.grid(row=2, column=0, columnspan=6, pady=10)

canvas = Canvas(window, highlightthickness=0)
canvas.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))
canvas.bind("<Button-1>", on_canvas_click)
canvas.bind("<Configure>", lambda event: render())

new_game()

poll_ai()  

window.mainloop()

