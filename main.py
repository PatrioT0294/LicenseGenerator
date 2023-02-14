import re
import time
import tkinter
from tkinter import *
from tkinter import ttk
import telnetlib
from tkinter import messagebox
import os

user = 'alex'
password = 'cisco123'
current_directory = os.getcwd()
needed_licenses = []
licenses = {
    "enh": "ENHANCED_LAYER2_PKG",
    "ent": "ENTERPRISE_PKG",
    "fc": "FC_FEATURES_PKG",
    "fcoe": "FCOE_NPV_PKG",
    "fm": "FM_SERVER_PKG",
    "lan_base": "LAN_BASE_SERVICES_PKG",
    "lan_ent": "LAN_ENTERPRISE_SERVICES_PKG",
    "ntwrk": "NETWORK_SERVICES_PKG",
    "vmfex": "VMFEX_FEATURE_PKG",
    "custom": ""
}


def clicked():
    """ Обработка нажатия кнопки """
    if 'custom' in needed_licenses and custom_license_entry.get() != '':
        licenses['custom'] = custom_license_entry.get()
    if (vdh.get() or sku.get()) == '' or needed_licenses == []:
        messagebox.showinfo('Ошибка', 'Заполните VDH и SKU и отметьте нужные лицензии!')
    else:
        generate_licenses()


def generate_licenses():
    """ Подключение по telnet и генерация лицензий """
    line1 = f"printf '{vdh.get().replace('VDH=', '')}"
    line2 = "' > serialno"
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
    """ Получение root прав"""
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
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[license]}.lic'
        current_license = f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {licenses[license]} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>20220316153207275</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN=9F924AA63160'
        tn.write(b"printf '" + current_license.encode('ascii') + b"' > /bootflash/" + file_name.encode('ascii') + b"\n")
    tn.write(b'cd /bootflash/\n')
    tn.write(b'ls -l\n')
    time.sleep(1)
    bootflash_licenses = re.findall(r'\S+.lic', tn.read_very_eager().decode('utf-8'))
    for license in needed_licenses:
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[license]}.lic'
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
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[license]}.lic'
        print(f'Получение подписи для {file_name}... ', end='')
        tn.write(b'gdb liccheck\n')
        time.sleep(1)
        tn.write(b'break *0x0805D4E7\n')
        time.sleep(1)
        tn.write(b"r -v /bootflash/" + file_name.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b'info registers\n')
        time.sleep(3)
        edx = re.search(r'edx\s+(0x\S+)', tn.read_until(b'ebx').decode('utf-8'))[1]
        tn.write(b'x/g  ' + edx.encode('ascii') + b'\n')
        time.sleep(2)
        reverse_sign = re.search(r'(0x00\S+)', tn.read_very_eager().decode('utf-8').replace("\t", "\n"))[1][
                       -12:]
        time.sleep(1)
        tn.write(b'quit\n')
        time.sleep(1)
        tn.write(b'y\n')
        split_by_two = re.findall(r'..', reverse_sign)
        sign = ''
        for couple in reversed(split_by_two):
            sign += str(couple).upper()
        f = open(file_name, 'w')
        f.write(
            f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {licenses[license]} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>20220316153207275</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN={sign}')
        print('Done')
        print(f'Удаление {file_name} из bootflash...', end='')
        tn.write(b'rm /bootflash/' + file_name.encode('ascii') + b'\n')
        print(f'Done')

def update_needed_licenses(license):
    if license in needed_licenses:
        needed_licenses.remove(license)
    elif license not in needed_licenses:
        needed_licenses.append(license)
    return needed_licenses


if __name__ == "__main__":
    """ Основная функция, вывод на экран """
    window = Tk()
    window.title("License Generator")
    window.geometry("300x330")

    frame = ttk.Frame(padding=[0, 0])
    frame.grid(column=0, row=12, padx=5)

    vdh_frame = ttk.Frame(padding=[0, 0])  # borderwidth=1, relief=SOLID,
    vdh_frame.grid(column=0, row=0, sticky='w', padx=5)

    sku_frame = ttk.Frame(padding=[0, 0])
    sku_frame.grid(column=0, row=1, sticky='w', padx=5)

    licenses_frame = ttk.Frame(padding=[0, 0])
    licenses_frame.grid(column=0, row=2, sticky='w', padx=5)

    mds_licenses_frame = ttk.Frame(padding=[0, 0])
    mds_licenses_frame.grid(column=1, row=2, sticky='w', padx=5)

    vdh = Entry(vdh_frame, width=30)
    vdh.grid(column=0, row=0, sticky='w')

    sku = Entry(sku_frame, width=30)
    sku.grid(column=0, row=0, sticky='w')

    vdh_lbl = Label(vdh_frame, text='VDH')
    vdh_lbl.grid(column=1, row=0, sticky='w')

    sku_lbl = Label(sku_frame, text='SKU')
    sku_lbl.grid(column=1, row=0, sticky='w')

    for lic in licenses:
        if lic != 'custom':
            var = tkinter.BooleanVar()
            cb = Checkbutton(licenses_frame, text=licenses[lic], state=ACTIVE, variable=var, onvalue=True,
                             offvalue=False,
                             command=lambda lic=lic: update_needed_licenses(lic))
            cb.grid(sticky="w")

    custom_license_entry = Entry(frame, width=20)

    custom_lic = tkinter.BooleanVar()
    custom_lic_checkbutton = Checkbutton(frame, text=custom_license_entry.grid(column=1, row=0, sticky='w'),
                                         state=ACTIVE, variable=custom_lic,
                                         command=lambda: update_needed_licenses('custom'))
    custom_lic_checkbutton.grid(column=0, row=0, sticky='w')

    custom_license_lbl = Label(frame, text='Custom license')
    custom_license_lbl.grid(column=2, row=0, sticky='w')

    btn = Button(window, text="Generate", command=clicked, width=20)
    btn.grid(column=0, row=13)

    window.mainloop()
