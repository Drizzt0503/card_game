def read_player2_control() -> bool:
    while True:
        choice = input("Player 2 控制方式（1=真人，2=AI）：").strip()
        if choice == "1":
            return False
        if choice == "2":
            return True
        print("請輸入 1 或 2。")
