import socket
import threading
import sys


def receive(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            # 현재 입력 줄 지우고 새 메시지 출력 후 다시 프롬프트 출력
            sys.stdout.write('\r' + ' ' * 80 + '\r')  # 현재 줄 지우기
            print(msg)
            print("💬 메시지 입력: ", end="", flush=True)
        except:
            print("❌ 서버 연결이 끊어졌습니다.")
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.233', 12345))  # 서버 IP 주소 및 포트

    # 닉네임 받기
    server_prompt = sock.recv(1024).decode()
    nickname = input(server_prompt)
    sock.sendall(nickname.encode())

    # 메시지 수신용 쓰레드
    threading.Thread(target=receive, args=(sock,), daemon=True).start()

    # 메시지 입력 및 전송 루프
    while True:
        try:
            msg = input("💬 메시지 입력: ")
            if msg.strip() == "":
                continue
            sock.sendall(msg.encode())
        except KeyboardInterrupt:
            print("\n👋 클라이언트를 종료합니다.")
            sock.close()
            break


if __name__ == "__main__":
    main()
