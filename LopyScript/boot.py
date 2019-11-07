import socket
import sys
import time
import _thread
import json
from network import LoRa
from machine import SD
import os

sd = SD()
os.mount(sd, '/sd')

# List of GIDs of actively connected clients.
connected_client_gid_list = []
# Messages that needs to be sent to another LoPy.
broadcast_message_list = []
# Messages those needs to be synced with clients.
pending_data_packets_dict = {}

# Initial run to ensure connected_devices list.
try:
    fh = open('/sd/data/connected_devices.json', 'r')
    fh.close()
except:
    fh = open('/sd/data/connected_devices.json', 'w')
    fh.write('{}')
    fh.close()
# Initial run to ensure connected_devices list.
try:
    fh = open('/sd/data/messages', 'r')
    fh.close()
except:
    fh = open('/sd/data/messages', 'w')
    fh.write('[]')
    fh.close()


def update_connected_gid(gid):
    file = open('/sd/data/connected_devices.json', 'r')
    connected_gid_dict = json.loads(file.read().replace('\'', '"'))
    connected_gid_dict[gid] = 'True'
    file.close()
    file = open('/sd/data/connected_devices.json', 'w')
    file.write(str(connected_gid_dict))
    file.close()
    return True


def is_gid_connected(gid, fetch_data=True):
    file = open('/sd/data/connected_devices.json', 'r')
    data = file.read()
    connected_gid_dict = json.loads(data.replace('\'', '"'))
    for existing_gid in connected_gid_dict.keys():
        if existing_gid == gid:
            if fetch_data:
                data = get_gid_data(gid)
                return data
            else:
                return True
    return False


def get_gid_data(gid):
    try:
        file = open('/sd/data/' + str(gid), 'r')
        read_data = file.read()
        if read_data == 'None':
            read_data = '[]'
        data = json.loads(read_data.replace('\'', '"'))
        file.close()
        file = open('/sd/data/' + str(gid), 'w')
        file.write('[]')
        file.close()
        return str(data)
    except:
        file = open('/sd/data/' + str(gid), 'w')
        file.write('[]')
        file.close()
        return str([])


def update_data_for_gid(gid, message):
    try:
        file = open('/sd/data/' + str(gid), 'r')
        read_data = file.read()
        if read_data == 'None':
            read_data = [message]
        else:
            read_data = json.loads(read_data.replace('\'', '"'))
            read_data.append(message)
        file.close()
        file = open('/sd/data/' + str(gid), 'w')
        file.write(str(read_data))
        file.close()
    except:
        file = open('/sd/data/' + str(gid), 'w')
        file.write(str([message]))
        file.close()

    try:
        file = open('/sd/data/messages', 'r')
        read_data = file.read() or '[]'
        data = json.loads(read_data)
        if not data:
            data = [message['timestamp']]
        else:
            data.append(message['timestamp'])
        file.close()
        file = open('/sd/data/messages', 'w')
        file.write(str(data))
        file.close()
        return True
    except:
        file = open('/sd/data/messages', 'w')
        file.write(str([message['timestamp']]))
        file.close()
        return True


def is_data_in_pending_list(timestamp):
    file = open('/sd/data/messages', 'r')
    read_data = file.read()
    data = json.loads(read_data)
    file.close()
    for message_timestamp in data:
        if timestamp == message_timestamp:
            return True
    return False


class WebServer(object):
    """
    Class for describing simple HTTP server objects
    """

    def __init__(self, port=80):
        self.host = ''  # Default to any avialable network interface
        self.port = port
        self.content_dir = '/sd/data'  # Directory where webpage files are stored

    # @aaankitjn10: Define a new function to push the recieved message from other LoPy into a array.

    # @aaankitjn10: Define a new function that checks that if a message packet thus passed is for any client
    # that is connected to the LoPy. If yes, it'll push the message to the dictionary and wait for the client
    # to make a poll. If not, it'll push the data and broadcast the data.
    # TODO: Think about timestamp as well to avoid duplicate data. or maybe use fromGID in a message and
    # discard if a fromGID exists in the list of connected clients.

    def start(self):
        """
        Attempts to create and bind a socket to launch the server
        """

        # @aaankitjn10: Add a new method for letting LoPy broadcast the message in the queue.
        # Or you could simply broadcast the message when a new message it recieved. But could
        # cause conflicts when there are a lot of concurrent client requests.

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print("Starting server on {host}:{port}".format(
                host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))

        except Exception as e:
            self.shutdown()
            sys.exit(1)

        self._listen()  # Start listening for connections

    def shutdown(self):
        """
        Shuts down the server
        """
        try:
            s.socket.shutdown(socket.SHUT_RDWR)

        except Exception:
            pass  # Pass if socket is already closed

    def _generate_headers(self, response_code):
        """
        Generate HTTP response headers.
        Parameters:
            - response_code: HTTP response code to add to the header. 200 and 404 supported
        Returns:
            A formatted HTTP header for the given response_code
        """
        header = ''
        if response_code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif response_code == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        header += 'Date: now'
        header += 'Server: Simple-Python-Server\n'
        # Signal that connection will be closed after completing the request
        header += 'Connection: close\n\n'
        return header.encode()

    def _listen(self):
        """
        Listens on self.port for any incoming connections
        """
        self.socket.listen(5)
        lora = LoRa(mode=LoRa.LORA)
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        s.setblocking(False)
        _thread.start_new_thread(self._receive_from_lopy, (s,))

        while True:
            (client, address) = self.socket.accept()
            client.settimeout(60)
            _thread.start_new_thread(self._handle_client, (client, address, s))

    def _receive_from_lopy(self, s):
        while True:
            time.sleep(0.25)
            data = s.recv(1024).decode()
            if data:
                data = data.replace('\'', '"')
                data = json.loads(data)
                print(data)
                if is_data_in_pending_list(data['timestamp']):
                    print('recieved bounced back data')
                    continue
                else:
                    print('Recieved new data')
                    update_data_for_gid(data['toGID'], data)

    def _send_data_packet_to_user(self, conn, requesting_client_gid):
        response_data = self._generate_headers(200)
        response_data += is_gid_connected(requesting_client_gid).replace('\'', '"').encode()
        conn.send(response_data)
        conn.close()
        return True

    def _handle_client_request(self, message_data_packet, reciever_gid, lopy_socket):
        lopy_socket.send(str(message_data_packet).encode())
        update_data_for_gid(reciever_gid, message_data_packet)
        return True

    def _handle_client(self, client, address, lopy_socket):
        """
        Main loop for handling connecting clients and serving files from content_dir
        Parameters:
            - client: socket client from accept()
            - address: socket address from accept()
        """
        PACKET_SIZE = 1024
        while True:
            # Recieve data packet from client and decode
            data = client.recv(PACKET_SIZE).decode()

            if not data:
                break

            request_method = data.split(' ')[0]

            if request_method == "POST" or request_method == "OPTIONS":
                sender_gid = data[data.find(
                    'fromgid') + 9: data.find('fromgid') + 19]
                reciever_gid = data[data.find(
                    'togid') + 7: data.find('togid') + 17]
                self._handle_client_request(json.loads(
                    data[data.find('{'):]), reciever_gid, lopy_socket)
                return self._send_data_packet_to_user(client, sender_gid)

            if request_method == "GET" or request_method == "HEAD":
                sender_gid = data[data.find(
                    'clientgid') + 11: data.find('clientgid') + 21]
                update_connected_gid(sender_gid)
                return self._send_data_packet_to_user(client, sender_gid)
            else:
                client.send('yoyoy')
                client.close()


server = WebServer(80)
server.start()
print("Press Ctrl+C to shut down server.")
