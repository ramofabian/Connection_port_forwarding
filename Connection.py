import sshtunnel
from paramiko import SSHClient
import paramiko
import logging
import time
import threading

REMOTE_SERVER_IP="########"
REMOTE_SERVER_PORT=22
REMOTE_SERVER_USER="########"
REMOTE_SERVER_PASSWORD="########"

PRIVATE_SERVER_IP="="########""
PRIVATE_SERVER_PORT=22
PRIVATE_SERVER_USER="########"
PRIVATE_SERVER_PASSWORD="########"

NOKIA_DEVICE_IP="########"
NOKIA_DEVICE_PORT=22
NOKIA_DEVICE_USER="########"
NOKIA_DEVICE_PASSWORD="########"

COMP_LOOPBACK_IP = "########"
COMP_PORT = 2224
COMMANDS_file = "Commands.cfg"

Equipos = {"########", "########", "########"}


class ssh_port_forwarding():

    def __init__(self, REMOTE_SERVER_1_IP, REMOTE_SERVER_1_USERNAME, REMOTE_SERVER_1_PASSWORD, REMOTE_SERVER_1_PORT,
                 REMOTE_SERVER_2_IP, REMOTE_SERVER_2_USERNAME, REMOTE_SERVER_2_PASSWORD, REMOTE_SERVER_2_PORT,
                 END_ROUTER_IP, END_ROUTER_USER, END_ROUTER_PASSWORD, END_ROUTER_PORT, LOCAL_IP, LOCAL_PORT,
                 COMMAND_FILE, LOG_FILE):

        self.REMOTE_SERVER_1_IP = REMOTE_SERVER_1_IP
        self.REMOTE_SERVER_1_USERNAME = REMOTE_SERVER_1_USERNAME
        self.REMOTE_SERVER_1_PASSWORD = REMOTE_SERVER_1_PASSWORD
        self.REMOTE_SERVER_1_PORT = REMOTE_SERVER_1_PORT

        self.REMOTE_SERVER_2_IP = REMOTE_SERVER_2_IP
        self.REMOTE_SERVER_2_USERNAME = REMOTE_SERVER_2_USERNAME
        self.REMOTE_SERVER_2_PASSWORD = REMOTE_SERVER_2_PASSWORD
        self.REMOTE_SERVER_2_PORT = REMOTE_SERVER_2_PORT

        self.END_ROUTER_IP = END_ROUTER_IP
        self.END_ROUTER_USER = END_ROUTER_USER
        self.END_ROUTER_PASSWORD = END_ROUTER_PASSWORD
        self.END_ROUTER_PORT = END_ROUTER_PORT

        self.LOCAL_IP = LOCAL_IP
        self.LOCAL_PORT = LOCAL_PORT
        self.COMMAND_FILE = COMMAND_FILE
        self.LOG_FILE = LOG_FILE

    def run(self):
        try:
            with sshtunnel.open_tunnel(
                ssh_address_or_host = (self.REMOTE_SERVER_1_IP, self.REMOTE_SERVER_1_PORT),
                ssh_username = self.REMOTE_SERVER_1_USERNAME,
                ssh_password = self.REMOTE_SERVER_1_PASSWORD,
                remote_bind_address=(self.REMOTE_SERVER_2_IP, self.REMOTE_SERVER_2_PORT),
                local_bind_address=(self.LOCAL_IP, self.LOCAL_PORT),
                block_on_close=False
            ) as tunnel1:
                print('Connection to tunnel1 ('+self.REMOTE_SERVER_1_IP+':'+str(self.REMOTE_SERVER_2_PORT)+') OK...')
                with sshtunnel.open_tunnel(
                    ssh_address_or_host = ('localhost', tunnel1.local_bind_port),
                    remote_bind_address = (self.END_ROUTER_IP, self.END_ROUTER_PORT),
                    ssh_username = self.REMOTE_SERVER_2_USERNAME,
                    ssh_password = self.REMOTE_SERVER_2_PASSWORD,
                    block_on_close = False
                ) as tunnel2:
                    print('Connection to tunnel2 ('+self.REMOTE_SERVER_2_IP+':'+str(self.REMOTE_SERVER_2_PORT)+') OK...')
                    try:
                        with SSHClient() as ssh:
                            ssh.load_system_host_keys()
                            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            ssh.connect(
                                'localhost',
                                port = tunnel2.local_bind_port,
                                username = self.END_ROUTER_USER,
                                password = self.END_ROUTER_PASSWORD,
                                timeout=10,
                                #look_for_keys=False,
                                #allow_agent=False
                            )
                            print('Connection established: '+self.END_ROUTER_IP + ' OK...')
                            channel = ssh.invoke_shell()
                            config_file=open(self.COMMAND_FILE, "r")
                            log_file=open(self.LOG_FILE, "a+")
                            for line in config_file:
                                channel.send(line + '\n')
                                resp_beauty=''
                                while resp_beauty.endswith('# ') is False:
                                    time.sleep(1)
                                    resp = channel.recv(9000000000)
                                    resp_beauty+=str(resp, 'utf-8')
                                print(resp_beauty)
                                for lines in resp_beauty:
                                    if lines.endswith("\n") is not True:
                                        log_file.write(lines)
                            config_file.close()
                            log_file.close()
                            channel.close()
                            print("Channel closed!!")
                            ssh.close()
                            print("Connection closed!!")
                    except Exception as error_1:
                        print("Can't connect to %s" % self.END_ROUTER_IP)
                        print("port=%s, username=%s, password=%s" % (self.END_ROUTER_PORT, self.END_ROUTER_USER, self.END_ROUTER_PASSWORD))
                        print("Thread exit!\n")
                        print(error_1 + " Execption 1")

        except Exception as error:
            print("Can't connect to %s" % self.END_ROUTER_IP)
            print("port=%s, username=%s, password=%s" % (self.END_ROUTER_PORT, self.END_ROUTER_USER, self.END_ROUTER_PASSWORD))
            print("Thread exit!\n")
            print(error+" Execption 0")
            return

def main():
    start = time.time()
    print('Time started')
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    for router in Equipos:
        NOKIA_DEVICE_IP = router
        OUTPUT_FILE = "OUTPUT_" + NOKIA_DEVICE_IP + ".txt"
        print("Device:"+ NOKIA_DEVICE_IP)
        connection = ssh_port_forwarding(
        REMOTE_SERVER_1_IP = REMOTE_SERVER_IP,
        REMOTE_SERVER_1_PORT = REMOTE_SERVER_PORT,
        REMOTE_SERVER_1_USERNAME = REMOTE_SERVER_USER,
        REMOTE_SERVER_1_PASSWORD = REMOTE_SERVER_PASSWORD,

        REMOTE_SERVER_2_IP = PRIVATE_SERVER_IP,
        REMOTE_SERVER_2_PORT = PRIVATE_SERVER_PORT,
        REMOTE_SERVER_2_USERNAME = PRIVATE_SERVER_USER,
        REMOTE_SERVER_2_PASSWORD = PRIVATE_SERVER_PASSWORD,

        END_ROUTER_IP = NOKIA_DEVICE_IP,
        END_ROUTER_PORT = NOKIA_DEVICE_PORT,
        END_ROUTER_USER = NOKIA_DEVICE_USER,
        END_ROUTER_PASSWORD = NOKIA_DEVICE_PASSWORD,

        LOCAL_IP = COMP_LOOPBACK_IP,
        LOCAL_PORT = COMP_PORT,
        COMMAND_FILE = COMMANDS_file,
        LOG_FILE = OUTPUT_FILE
        )
        connection.run()
    print('FINISH!')
    end = time.time()
    print(end - start)
    #time.sleep(2)

if __name__ == "__main__":
    main()
