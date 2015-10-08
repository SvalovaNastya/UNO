import struct


class SocketSender:
    @staticmethod
    def send_all(sock, message): # in bytes
        n = len(message)
        sock.sendall(struct.pack('I', n))
        sock.sendall(message)

    @staticmethod
    def _recv_while_not_full_buffer(sock, buffer):
        while True:
            ans = sock.recv(buffer)
            if len(ans) < buffer:
                buffer -= len(ans)
            else:
                return ans

    @staticmethod
    def recv_all(sock): # in bytes
        n = struct.unpack('I', SocketSender._recv_while_not_full_buffer(sock, 4))
        ans = SocketSender._recv_while_not_full_buffer(sock, n[0])
        return ans