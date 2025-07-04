import socket

HOST = 'localhost'
PORT = 877

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            data = s.recv(2048)
            if not data:
                break

            decoded = data.decode()
            print(decoded, end="")  # avoids extra newline

            # Trigger input if the message includes a prompt
            if "your move" in decoded.lower() or "enter your player name" in decoded.lower():
                user_input = input()
                s.send(user_input.encode())

if __name__ == "__main__":
    start_client()
