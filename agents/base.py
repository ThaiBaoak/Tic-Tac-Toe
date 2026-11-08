class Agent:
    """Giao diện chung của mọi agent.

    choose_move(board, time_limit=None) trả về (hàng, cột) hoặc None nếu ván đã kết thúc.
    Sau mỗi lần gọi, self.stats chứa thống kê (ví dụ {"nodes": ...}).
    """

    name = "Agent"

    def __init__(self):
        self.stats = {}

    def choose_move(self, board, time_limit=None):
        raise NotImplementedError
