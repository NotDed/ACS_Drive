import subprocess
from time import sleep

print('Launching server @tcp://localhost:1111 \n')
subprocess.Popen('py server.py 1111 waitActions', creationflags=subprocess.CREATE_NEW_CONSOLE)
sleep(1)

print('Launching server @tcp://localhost:2222 \n')
subprocess.Popen('py server.py 2222 attach tcp://localhost:1111', creationflags=subprocess.CREATE_NEW_CONSOLE)
sleep(1)

print('Launching server @tcp://localhost:3333 \n')
subprocess.Popen('py server.py 3333 attach tcp://localhost:1111', creationflags=subprocess.CREATE_NEW_CONSOLE)
sleep(1)

print('Launching server @tcp://localhost:4444 \n')
subprocess.Popen('py server.py 4444 attach tcp://localhost:1111', creationflags=subprocess.CREATE_NEW_CONSOLE)
sleep(1)

print('Launching server @tcp://localhost:5555 \n')
subprocess.Popen('py server.py 5555 attach tcp://localhost:1111', creationflags=subprocess.CREATE_NEW_CONSOLE)
sleep(1)

print('Launching ringWalker @tcp://localhost:6666')
print()
subprocess.call('py server.py 6666 walk tcp://localhost:1111')
print()