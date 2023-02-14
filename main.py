import re
import time
from tkinter import *
from tkinter import ttk
import telnetlib
from tkinter import messagebox
import os

text = ''
user = 'alex'
password = 'cisco123'
a = ''
current_directory = os.getcwd()
licenses = {
    "enh": {"name": "ENHANCED_LAYER2_PKG", "state": 0},
    "ent": {"name": "ENTERPRISE_PKG", "state": 0},
    "fc": {"name": "FC_FEATURES_PKG", "state": 0},
    "fcoe": {"name": "FCOE_NPV_PKG", "state": 0},
    "fm": {"name": "FM_SERVER_PKG", "state": 0},
    "lan_base": {"name": "LAN_BASE_SERVICES_PKG", "state": 0},
    "lan_ent": {"name": "LAN_ENTERPRISE_SERVICES_PKG", "state": 0},
    "ntwrk": {"name": "NETWORK_SERVICES_PKG", "state": 0},
    "vmfex": {"name": "VMFEX_FEATURE_PKG", "state": 0},
    "custom" : {}
}
selected_dict = {}
needed_licenses = []
license_test = []


serial_number = 'FOX1828GX44'


def clicked():
    if 'custom' in needed_licenses and custom_license_entry.get() != '':
        licenses['custom']['name'] = custom_license_entry.get()
    if (vdh.get() or sku.get()) == '' or needed_licenses == []:
        messagebox.showinfo('Ошибка', 'Заполните VDH и SKU и отметьте нужные лицензии!')
    else:
        generate_licenses()

def generate_licenses():
    """ Подключение по telnet и генерация лицензий """
    line1 = f"printf '{vdh.get().replace('VDH=', '')}"
    line2 = "' > serialno"
    sign = ''
    try:
        print('Подключение к Nexus с root правами... ', end='')
        tn = telnet_connection()
        time.sleep(2)
        log_in = tn.read_very_eager().decode('utf-8')
        if re.search('Linux#', log_in):
            # print('Подлючение по telnet прошло успешно')
            print('Done')
            creating_finaly_licens_files(tn, line1, line2)
        else:
            print('Fail\nПолучение root прав... ', end='')
            tn.close()
            get_root()
            print('Done')
            print('Повторное подключение по telnet... ', end='')
            tn = telnet_connection()
            time.sleep(2)
            log_in = tn.read_very_eager().decode('utf-8')
            if re.search('Linux#', log_in):
                print('Done')
                creating_finaly_licens_files(tn, line1, line2)
            elif re.search('Login incorrect', log_in):
                print('Получить root права не удалось. Попробуйте вручную')
    except TimeoutError:
        messagebox.showinfo('Ошибка', 'Проблема с подключением к Nexus')

def get_root():
    tn_root = telnetlib.Telnet('172.25.80.171', timeout=10)
    tn_root.read_until(b"login: ")
    tn_root.write(b"admin\n")
    tn_root.read_until(b"Password: ")
    tn_root.write(b"cisco123\n")
    time.sleep(1)
    tn_root.write(b"cd bootflash:\ndelete xxx\n\ncd bootflash:\nmkdir xxx\ncd xxx\n")
    time.sleep(1)
    tn_root.write(b"echo 'echo \"alex:x:0:0::/var/home/admin:/bin/bash\" >> /etc/passwd' > runme\n")
    time.sleep(1)
    tn_root.write(b"echo \"echo 'alex:$1$53bQkv6o$64CA4b9BcYZDdQlBBRIm70:15838:0:99999:7:::'>> /etc/shadow\" >> runme\n")
    tn_root.write(b"cd bootflash:\ncd xxx\nmkdir $(bash$IFS\"$a\"\ncd bootflash:///xxx/$(bash$IFS\"$a\"\nmkdir bootflash\n")
    time.sleep(1)
    tn_root.write(b"cd bootflash:///xxx/$(bash$IFS\"$a\"\ncd bootflash\nmkdir xxx\ncd bootflash:\ncd xxx\n")
    time.sleep(1)
    tn_root.write(b"cd bootflash:///xxx/$(bash$IFS\"$a\"\ncd bootflash\ncd xxx\necho pwn3d > runme).lic\n\n")
    time.sleep(1)
    tn_root.write(b"cd bootflash:\n")
    tn_root.write(b"cd xxx\n")
    tn_root.write(b"install license $(bash$IFS\"$a\"/bootflash/xxx/runme).lic\n")
    time.sleep(1)
    tn_root.close()

def create_license_files(tn):
    """ Создание и загрузка файлов лицензий на Nexus """
    print('Создание файлов лицензий в bootflash... ', end='')
    all_licenses_in_bootflash = True
    global licenses_not_in_bootflash
    licenses_not_in_bootflash = []
    for license in needed_licenses:
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[license]["name"]}.lic'
        current_license = f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {licenses[license]["name"]} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>20220316153207275</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN=9F924AA63160'
        tn.write(b"printf '" + current_license.encode('ascii') + b"' > /bootflash/" + file_name.encode('ascii') + b"\n")
    tn.write(b'cd /bootflash/\n')
    tn.write(b'ls -l\n')
    time.sleep(1)
    bootflash_licenses = re.findall(r'\S+.lic', tn.read_very_eager().decode('utf-8'))
    for license in needed_licenses:
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[license]["name"]}.lic'
        if file_name not in bootflash_licenses:
            all_licenses_in_bootflash = False
            licenses_not_in_bootflash.append(file_name)
    if all_licenses_in_bootflash == True:
        print('Done')
    else:
        return licenses_not_in_bootflash

def telnet_connection():
    # global tn
    tn = telnetlib.Telnet('172.25.80.171', timeout=10)
    tn.read_until(b"login: ")
    tn.write(user.encode('ascii') + b"\n")
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")
    return tn

def creating_finaly_licens_files(tn, line1, line2):
    license_creation = create_license_files(tn)
    if license_creation:
        messagebox.showinfo('Ошибка', 'Не удалось создать все необходимые файлы лицензий в bootflash\nПопробуйте запустить заново')
        print('Следующие файлы лицензий не удалось создать:',
              '\n'.join(str(lic) for lic in licenses_not_in_bootflash), sep='\n')
    else:
        get_license_sign(tn, line1, line2)
        messagebox.showinfo('', f'Лицензии успешно сгенерированы и находятся по следующему пути:\n{current_directory}')

def get_license_sign(tn, line1, line2):
    tn.write(b'cp /bootflash/usr/bin/gdb /usr/bin/gdb\n')
    time.sleep(1)
    tn.write(b'cd /isan/etc/\n')
    time.sleep(1)
    tn.write(line1.encode('ascii') + b'\\x00\\x00' + line2.encode('ascii') + b'\n')
    for license in needed_licenses:
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[license]["name"]}.lic'
        print(f'Получение подписи для {file_name}... ', end='')
        # print('Переход в gdb liccheck')
        tn.write(b'gdb liccheck\n')
        time.sleep(1)
        # print('liccheck')
        tn.write(b'break *0x0805D4E7\n')
        time.sleep(1)
        # print('break')
        tn.write(b"r -v /bootflash/" + file_name.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b'info registers\n')
        # print('info registers')
        time.sleep(3)
        # print(tn.read_until(b'ebx'))
        edx = re.search(r'edx\s+(0x\S+)', tn.read_until(b'ebx').decode('utf-8'))[1]
        # print(edx)
        # edx = re.search(r'edx', tn.read_very_eager().decode('utf-8'))
        # print(f'edx {edx}')
        tn.write(b'x/g  ' + edx.encode('ascii') + b'\n')
        time.sleep(2)
        reverse_sign = re.search(r'(0x00\S+)', tn.read_very_eager().decode('utf-8').replace("\t", "\n"))[1][
                       -12:]
        time.sleep(1)
        tn.write(b'quit\n')
        time.sleep(1)
        tn.write(b'y\n')
        # print(reverse_sign)
        split_by_two = re.findall(r'..', reverse_sign)
        sign = ''
        for couple in reversed(split_by_two):
            sign += str(couple).upper()
        # print(sign)
        f = open(file_name, 'w')
        f.write(
            f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {licenses[license]["name"]} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>20220316153207275</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN={sign}')
        print('Done')
        print(f'Удаление {file_name} из bootflash...', end='')
        tn.write(b'rm /bootflash/' + file_name.encode('ascii') + b'\n')
        print(f'Done')

def update_needed_licenses(state, license):
    # print(license)
    if state.get() == 0 and license in needed_licenses:
        needed_licenses.remove(license)
    elif state.get() == 1 and license not in needed_licenses:
        needed_licenses.append(license)
    # print(needed_licenses)
    return needed_licenses
    updated_type_list = []
    for item in inventory['total']['items'].items():
        if item[1]['type'] in type_list:
            updated_type_list.append(item[1]['name'])
    combo['values'] = (sorted(updated_type_list))
    combo.current(0)

if __name__ == "__main__":

    window = Tk()
    window.title("License Generator")
    window.geometry("300x310")

    frame = ttk.Frame(padding=[0, 0])
    frame.grid(column=0, row=12, padx=9)

    vdh_frame = ttk.Frame(padding=[0, 0])  #borderwidth=1, relief=SOLID,
    vdh_frame.grid(column=0, row=0)

    sku_frame = ttk.Frame(padding=[0, 0])
    sku_frame.grid(column=0, row=1)

    vdh = Entry(vdh_frame, width=30)
    vdh.grid(column=0, row=0, sticky='w')

    sku = Entry(sku_frame, width=30)
    sku.grid(column=0, row=0, sticky='w')

    vdh_lbl = Label(vdh_frame, text='VDH')
    vdh_lbl.grid(column=1, row=0, sticky='w')

    sku_lbl = Label(sku_frame, text='SKU')
    sku_lbl.grid(column=1, row=0, sticky='w')

    enh = IntVar()
    enh.set(0)
    enh_checkbutton = ttk.Checkbutton(text="ENHANCED_LAYER2_PKG", state=ACTIVE, variable=enh, command=lambda: update_needed_licenses(enh, 'enh'))
    enh_checkbutton.grid(column=0, row=2, sticky='w', padx=9)

    ent = IntVar()
    ent.set(0)
    ent_checkbutton = ttk.Checkbutton(text="ENTERPRISE_PKG", state=ACTIVE, variable=ent,
                                      command=lambda: update_needed_licenses(ent, 'ent'))
    ent_checkbutton.grid(column=0, row=3, sticky='w', padx=9)

    fc = IntVar()
    fc.set(0)
    fc_checkbutton = ttk.Checkbutton(text="FC_FEATURES_PKG", state=ACTIVE, variable=fc,
                                      command=lambda: update_needed_licenses(fc, 'fc'))
    fc_checkbutton.grid(column=0, row=4, sticky='w', padx=9)

    fcoe = IntVar()
    fcoe.set(0)
    fcoe_checkbutton = ttk.Checkbutton(text="FCOE_NPV_PKG", state=ACTIVE, variable=fcoe,
                                     command=lambda: update_needed_licenses(fcoe, 'fcoe'))
    fcoe_checkbutton.grid(column=0, row=5, sticky='w', padx=9)

    fm = IntVar()
    fm.set(0)
    fm_checkbutton = ttk.Checkbutton(text="FM_SERVER_PKG", state=ACTIVE, variable=fm,
                                       command=lambda: update_needed_licenses(fm, 'fm'))
    fm_checkbutton.grid(column=0, row=6, sticky='w', padx=9)

    lan_base = IntVar()
    lan_base.set(0)
    lan_base_checkbutton = ttk.Checkbutton(text="LAN_BASE_SERVICES_PKG", state=ACTIVE, variable=lan_base,
                                           command=lambda: update_needed_licenses(lan_base, 'lan_base'))
    lan_base_checkbutton.grid(column=0, row=7, sticky='w', padx=9)

    lan_ent = IntVar()
    lan_ent.set(0)
    lan_ent_checkbutton = ttk.Checkbutton(text="LAN_ENTERPRISE_SERVICES_PKG", state=ACTIVE, variable=lan_ent,
                                           command=lambda: update_needed_licenses(lan_ent, 'lan_ent'))
    lan_ent_checkbutton.grid(column=0, row=8, sticky='w', padx=9)

    ntwrk = IntVar()
    ntwrk.set(0)
    ntwrk_checkbutton = ttk.Checkbutton(text="NETWORK_SERVICES_PKG", state=ACTIVE, variable=ntwrk,
                                          command=lambda: update_needed_licenses(ntwrk, 'ntwrk'))
    ntwrk_checkbutton.grid(column=0, row=9, sticky='w', padx=9)

    vmfex = IntVar()
    vmfex.set(0)
    vmfex_checkbutton = ttk.Checkbutton(text="VMFEX_FEATURE_PKG", state=ACTIVE, variable=vmfex,
                                        command=lambda: update_needed_licenses(vmfex, 'vmfex'))
    vmfex_checkbutton.grid(column=0, row=10, sticky='w', padx=9)

    custom_license_entry = Entry(frame, width=20)
    custom_license_entry.grid(column=1, row=0, sticky='w')

    custom_lic = IntVar()
    custom_lic.set(0)
    custom_lic_checkbutton = ttk.Checkbutton(frame, text="", state=ACTIVE, variable=custom_lic,
                                      command=lambda: update_needed_licenses(custom_lic, 'custom'))
    custom_lic_checkbutton.grid(column=0, row=0, sticky='w')

    custom_license_lbl = Label(frame, text='Custom license')
    custom_license_lbl.grid(column=2, row=0, sticky='w')

    btn = Button(window, text="Generate", command=clicked, width=20)
    btn.grid(column=0, row=13)

    window.mainloop()