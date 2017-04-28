import subprocess as sp

ans = sp.Popen(['nslookup', '192.168.1.10'], stdout=sp.PIPE)

for line in ans.stdout:
    line = line.decode('utf-8')
    if 'name = ' in line:
        print(line.split(' ')[-1].strip('.\n'))
