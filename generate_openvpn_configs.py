import glob
import random
import re
import subprocess


def run(command):
    subprocess.run(command, shell=True, check=True, capture_output=True)


multiple_nopass = 'certificati/file configurazione separati/senza password'
multiple_pass = 'certificati/file configurazione separati/con password'
single_nopass = 'certificati/file configurazione singoli/senza password'
single_pass = 'certificati/file configurazione singoli/con password'
run(f'mkdir -p "{multiple_nopass}"')
run(f'mkdir -p "{multiple_pass}"')
run(f'mkdir -p "{single_nopass}"')
run(f'mkdir -p "{single_pass}"')
passwords = []
original_file = glob.glob('*.ovpn')[0]

single_lines = [line.rstrip() for line in open(original_file).readlines() if not re.match(r'(ca|cert|key|tls-auth) ', line)]
single_lines.append('key-direction 1')

for i in range(1, 100):
    client = f'client{i:02}'
    run(f'mkdir "{multiple_nopass}/{client}"')
    run(f'cp "{original_file}" "{multiple_nopass}/{client}"')
    run(f'cp pki/ca.crt "{multiple_nopass}/{client}"')
    run(f'cp ta.key "{multiple_nopass}/{client}"')
    run(f'cp pki/private/{client}.key "{multiple_nopass}/{client}"')
    run(f'cp pki/issued/{client}.crt "{multiple_nopass}/{client}"')
    run(f'sed -i "s/client01.crt/{client}.crt/g;s/client01.key/{client}.key/g" "{multiple_nopass}/{client}/{original_file}"')

    run(f'cp -a "{multiple_nopass}/{client}" "{multiple_pass}/{client}"')
    password = ''.join([random.choice('QWERTYUPASDFGHJKLZXCVBNMqwertyuipasdfghjkzxcvbnm23456789') for j in range(12)])
    passwords.append(password)
    run(f'openssl rsa -in "{multiple_nopass}/{client}/{client}.key" -out "{multiple_pass}/{client}/{client}.key" -des3 -passout pass:"{password}"')

    run(f'mkdir "{single_nopass}/{client}"')
    with open(f'{single_nopass}/{client}/{original_file}', 'w') as file:
        file.write(f'#certificato: {client}\n\n')
        file.write('\n'.join(single_lines))

        file.write('\n\n<ca>\n')
        file.write(open('pki/ca.crt').read())
        file.write('</ca>\n')

        file.write('\n<cert>\n')
        file.write(open(f'{multiple_nopass}/{client}/{client}.crt').read())
        file.write('</cert>\n')

        file.write('\n<key>\n')
        file.write(open(f'{multiple_nopass}/{client}/{client}.key').read())
        file.write('</key>\n')

        file.write('\n<tls-auth>\n')
        file.write(open('ta.key').read())
        file.write('</tls-auth>\n')

    run(f'mkdir "{single_pass}/{client}"')
    with open(f'{single_pass}/{client}/{original_file}', 'w') as file:
        file.write(f'#certificato: {client}\n\n')
        file.write('\n'.join(single_lines))

        file.write('\n\n<ca>\n')
        file.write(open('pki/ca.crt').read())
        file.write('</ca>\n')

        file.write('\n<cert>\n')
        file.write(open(f'{multiple_pass}/{client}/{client}.crt').read())
        file.write('</cert>\n')

        file.write('\n<key>\n')
        file.write(open(f'{multiple_pass}/{client}/{client}.key').read())
        file.write('</key>\n')

        file.write('\n<tls-auth>\n')
        file.write(open('ta.key').read())
        file.write('</tls-auth>\n')
with open(f'{multiple_pass}/../../passwords.txt', 'w') as file:
    file.writelines([f'client{i:02}: {p}\n' for i, p in enumerate(passwords, 1)])
