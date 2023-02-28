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
current_switch_type = 'all'
device_type = ''
licenses = {
    "nexus": {
        "uncounted": {
            "enh": "ENHANCED_LAYER2_PKG",
            "ent": "ENTERPRISE_PKG",
            "fc": "FC_FEATURES_PKG",
            "fcoe": "FCOE_NPV_PKG",
            "fm": "FM_SERVER_PKG",
            "lan_base": "LAN_BASE_SERVICES_PKG",
            "lan_ent": "LAN_ENTERPRISE_SERVICES_PKG",
            "ntwrk": "NETWORK_SERVICES_PKG",
            "vmfex": "VMFEX_FEATURE_PKG",
            "lic_pkg_24": "24P_LIC_PKG",
            "lic_upg_24": "24P_UPG_PKG",
            "custom": ""
        },
        "counted": {}
    },
    "mds": {
        "uncounted": {
            "mds_ent": "ENTERPRISE_PKG",
            "san": "SAN_TELEMETRY_PKG",
            "san_a": "SAN_ANALYTICS_PKG",
            "mainframe": "MAINFRAME_PKG",
            "dmm": "DMM_FOR_SSM_PKG",
            "custom": ""
        },
        "counted": {
            "port": "PORT_ACTIVATION_PKG"
        }
    }
}


def clicked(device_type):
    """ Обработка нажатия кнопки """
    print(f'vdh{vdh.get()}')
    print(f'sku{sku.get()}')
    print(f"OR: {(vdh.get() or sku.get()) == ''}")
    if 'custom' in needed_licenses and custom_license_entry.get() != '':
        print(device_type)
        licenses[device_type]['uncounted']['custom'] = custom_license_entry.get()
    if vdh.get() == '' or sku.get() == '' or needed_licenses == []:
        messagebox.showinfo('Ошибка', 'Заполните VDH и SKU и отметьте нужные лицензии!')
    else:
        generate_licenses(device_type)


def generate_licenses(device_type):
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
            creating_final_license_files(tn, line1, line2, device_type)
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
                creating_final_license_files(tn, line1, line2, device_type)
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


def create_license_files(tn, device_type):
    """ Создание и загрузка файлов лицензий на Nexus """
    print('Создание файлов лицензий в bootflash... ', end='')
    print(device_type)
    all_licenses_in_bootflash = True
    global licenses_not_in_bootflash
    licenses_not_in_bootflash = []
    for license in needed_licenses:
        if license in licenses[device_type]["uncounted"]:
            license_name = licenses[device_type]["uncounted"][license]
            file_name = f'{vdh.get().replace("VDH=", "")}_{license_name}.lic'
            print(file_name)
            current_license = f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {license_name} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>20220316153207275</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN=9F924AA63160'
            tn.write(b"printf '" + current_license.encode('ascii') + b"' > /bootflash/" + file_name.encode('ascii') + b"\n")
    tn.write(b'cd /bootflash/\n')
    tn.write(b'ls -l\n')
    time.sleep(1)
    bootflash_licenses = re.findall(r'\S+.lic', tn.read_very_eager().decode('utf-8'))
    print(f'licenses {bootflash_licenses}')
    for license in needed_licenses:
        if license in licenses[device_type]["uncounted"]:
            license_name = licenses[device_type]["uncounted"][license]
            file_name = f'{vdh.get().replace("VDH=", "")}_{license_name}.lic'
            print(file_name)
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

def creating_final_license_files(tn, line1, line2, device_type):
    license_creation = create_license_files(tn, device_type)
    print('testttt')
    if license_creation:
        messagebox.showinfo('Ошибка', 'Не удалось создать все необходимые файлы лицензий в bootflash\nПопробуйте запустить заново')
        print('Следующие файлы лицензий не удалось создать:',
              '\n'.join(str(lic) for lic in licenses_not_in_bootflash), sep='\n')
    else:
        get_license_sign(tn, line1, line2, device_type)
        messagebox.showinfo('', f'Лицензии успешно сгенерированы и находятся по следующему пути:\n{current_directory}')

def get_license_sign(tn, line1, line2, device_type):
    tn.write(b'cp /bootflash/usr/bin/gdb /usr/bin/gdb\n')
    time.sleep(1)
    tn.write(b'cd /isan/etc/\n')
    time.sleep(1)
    tn.write(line1.encode('ascii') + b'\\x00\\x00' + line2.encode('ascii') + b'\n')
    print(needed_licenses)
    print(f'device type - {device_type}')
    for license in needed_licenses:
        print('ЛИЦЕНЗИЯ', license)
        print(licenses[device_type])
        file_name = f'{vdh.get().replace("VDH=", "")}_{licenses[device_type]["uncounted"][license]}.lic'
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
            f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {licenses[device_type]["uncounted"][license]} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>20220316153207275</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN={sign}')
        print('Done')
        print(f'Удаление {file_name} из bootflash...', end='')
        tn.write(b'rm /bootflash/' + file_name.encode('ascii') + b'\n')
        time.sleep(1)
        print(f'Done')

def update_needed_licenses(license, device_type_temp):
    global device_type
    device_type = device_type_temp
    if license in needed_licenses:
        needed_licenses.remove(license)
    elif license not in needed_licenses:
        needed_licenses.append(license)
    print(needed_licenses)
    if needed_licenses == []:
        current_switch_type = 'all'
    else:
        for lic in needed_licenses:
            if lic in (licenses["nexus"]["uncounted"] or licenses["nexus"]["counted"]):
                current_switch_type = 'nexus'
            elif lic in licenses["mds"]["uncounted"] or lic in licenses["mds"]["counted"]:
                current_switch_type = 'mds'
            else:
                current_switch_type = 'all'
    # update_needed_licenses(license)
    if current_switch_type == 'mds':
        for lic in cb_list:
            lic.destroy()
        custom_lic_checkbutton.destroy()
        custom_license_entry.destroy()
        for widget in nexus_frame.winfo_children():
            widget.destroy()
        nexus_checkbutton(current_switch_type)
        print(f'frameee {current_switch_type}')
    elif current_switch_type == 'nexus':
        print('jajajaja')
        for lic in mds_cb_list:
            lic.destroy()
        for widget in mds_frame.winfo_children():
            widget.destroy()
        mds_checkbutton(current_switch_type)
    else:
        for lic in cb_list:
            lic.destroy()
        custom_lic_checkbutton.destroy()
        custom_license_entry.destroy()
        for widget in nexus_frame.winfo_children():
            widget.destroy()
        nexus_checkbutton(current_switch_type)

        for lic in mds_cb_list:
            lic.destroy()
        for widget in mds_frame.winfo_children():
            widget.destroy()
        mds_checkbutton(current_switch_type)
    return needed_licenses
    return device_type

# def state_change(current_switch_type):
#     if current_switch_type == 'mds':
#         cb.configure(state=DISABLED)

def nexus_checkbutton(current_switch_type):
    """ Отрисовка Nexus checkbutton """
    global custom_license_entry
    global cb_list
    global custom_lic_checkbutton
    global custom_license_entry
    cb_list = []
    if current_switch_type == 'mds':
        blocked = DISABLED
        blocked_entry = DISABLED
    else:
        blocked = ACTIVE
        blocked_entry = NORMAL
    for lic in licenses["nexus"]["uncounted"]:
        if lic != 'custom':
            var = tkinter.BooleanVar()
            cb = Checkbutton(nexus_frame, text=licenses["nexus"]["uncounted"][lic], state=blocked, variable=var,
                             onvalue=True,
                             offvalue=False,
                             command=lambda lic=lic: update_needed_licenses(lic, 'nexus'))
            cb_list.append(cb)
            cb.pack(anchor="w")

    custom_license_frame = ttk.Frame(nexus_frame, padding=[0, 0])
    custom_license_frame.pack(anchor="w", padx=1)

    custom_license_entry = Entry(custom_license_frame, width=28, state=blocked_entry)

    custom_lic = tkinter.BooleanVar()
    custom_lic_checkbutton = Checkbutton(custom_license_frame,
                                         text=custom_license_entry.pack(anchor='w', side=RIGHT, padx=0),
                                         state=blocked, variable=custom_lic,
                                         command=lambda: update_needed_licenses('custom', 'nexus'))
    custom_lic_checkbutton.pack(anchor='w', side=LEFT, padx=0)

def mds_checkbutton(current_switch_type):
    """ Отрисовка MDS checkbutton """
    # global custom_license_entry
    global mds_cb_list
    # global custom_lic_checkbutton
    # global custom_license_entry
    mds_cb_list = []
    if current_switch_type == 'nexus':
        blocked = DISABLED
    else:
        blocked = ACTIVE
    for mds_lic in licenses["mds"]["uncounted"]:
        if mds_lic != 'custom':
            var = tkinter.BooleanVar()
            mds_cb = Checkbutton(mds_frame, text=licenses["mds"]["uncounted"][mds_lic], state=blocked, variable=var, onvalue=True,
                             offvalue=False,
                             command=lambda mds_lic=mds_lic: update_needed_licenses(mds_lic, 'mds'))
            mds_cb.pack(anchor="w")

if __name__ == "__main__":
    global nexus_frame
    """ Основная функция, вывод на экран """
    window = Tk()
    window.title("License Generator")
    window.geometry("400x450")

    vdh_frame = ttk.LabelFrame(text='VDH', padding=[0, 0])  # borderwidth=1, relief=SOLID,
    vdh_frame.pack(anchor='w', padx=10)

    vdh = Entry(vdh_frame, width=33)
    vdh.pack(anchor='w')

    sku_frame = ttk.LabelFrame(text='SKU', padding=[0, 0])
    sku_frame.pack(anchor='w', padx=10)

    sku = Entry(sku_frame, width=33)
    sku.pack(anchor='w')

    licenses_frame = ttk.Frame(padding=[0, 0])
    licenses_frame.pack(anchor='w', padx=5)

    nexus_frame = ttk.LabelFrame(licenses_frame, text='Nexus', padding=[0, 0])
    nexus_frame.pack(anchor='w', padx=5, side=LEFT)

    mds_frame = ttk.LabelFrame(licenses_frame, text='MDS', padding=[0, 0])
    mds_frame.pack(anchor='nw', padx=5, side=RIGHT)

    nexus_checkbutton(current_switch_type)
    mds_checkbutton(current_switch_type)

    bottom_frame = ttk.Frame(window)
    bottom_frame.pack()

    onefile = tkinter.BooleanVar()
    onefile_checkbutton = Checkbutton(bottom_frame,
                                      text='Все лицензии в одном файле',
                                      variable=onefile)
    onefile_checkbutton.pack(anchor='n', padx=0)

    btn = Button(bottom_frame, text="Generate", command=lambda: clicked(device_type), width=20)
    btn.pack(anchor='s')

    window.mainloop()






