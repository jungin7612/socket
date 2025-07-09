import socket
import threading

clients = {}  # conn: nickname
votes = {}    # nickname: vote
voting = False

vote_options = {
    "1": "✅ 갈게요",
    "2": "❌ 안 갈게요"
}

def handle_client(conn, addr):
    global voting

    print(f"📥 연결됨: {addr}")
    
    try:
        conn.sendall("NICKNAME: ".encode())
        nickname = conn.recv(1024).decode().strip()

        if not nickname:
            conn.sendall("❌ 닉네임이 올바르지 않습니다. 연결 종료.\n".encode())
            conn.close()
            return

        welcome = f"✅ {nickname} 님이 입장하셨습니다!"
        print(welcome)
        broadcast(welcome.encode(), None)
        clients[conn] = nickname

        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            text = msg.decode().strip()

            # ✅ 투표 중이면 투표 처리
            if voting and text in vote_options:
                if nickname not in votes:
                    votes[nickname] = text
                    conn.sendall("📥 투표 완료!\n".encode())
                else:
                    conn.sendall("⚠️ 이미 투표하셨습니다.\n".encode())
                continue

            # ✅ 투표 시작 명령
            if text == "/vote":
                start_vote()
                continue

            # ✅ 투표 종료 명령
            if text == "/endvote":
                end_vote()
                continue

            # ✅ 일반 채팅
            formatted = f"[{nickname}] {text}"
            print(formatted)
            broadcast(formatted.encode(), conn)

    except Exception as e:
        print(f"⚠️ 오류 발생 ({addr}): {e}")

    finally:
        if conn in clients:
            goodbye = f"❌ {clients[conn]} 님이 퇴장하셨습니다."
            print(goodbye)
            broadcast(goodbye.encode(), conn)
            del clients[conn]
        conn.close()

def broadcast(msg, sender_conn):
    for c in clients:
        if c != sender_conn:
            try:
                c.sendall(msg)
            except:
                pass

def start_vote():
    global voting, votes
    voting = True
    votes = {}

    prompt = (
        "\n🗳 [투표 시작] 뒷풀이 참석 여부!\n"
        "1. ✅ 갈게요\n"
        "2. ❌ 안 갈게요\n"
        "💬 숫자를 입력해주세요 (1 또는 2):\n"
    )
    print("📢 투표 시작")
    broadcast(prompt.encode(), None)


def end_vote():
    global voting
    voting = False
    count = {"1": 0, "2": 0}
    for vote in votes.values():
        if vote in count:
            count[vote] += 1
    total = sum(count.values())

    result = (
        "\n[ Afterparty Voting Result ]\n\n"
        "┌────────────┬────────────┐\n"
        "│   Option   │ Vote Count │\n"
        "├────────────┼────────────┤\n"
        f"│ Going      │     {count['1']}      │\n"
        f"│ Not Going  │     {count['2']}      │\n"
        "└────────────┴────────────┘\n"
        f"\nTotal {total} people voted.\n"
    )

    print(result)
    broadcast(result.encode(), None)
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 12345))
    server.listen(30)
    print("🌐 채팅 서버 실행 중 (포트 12345)...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    main()
