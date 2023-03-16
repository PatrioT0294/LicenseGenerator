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
needed_licenses_counted = []
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
        }
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
        "counted": {}
    },
    "custom": {
        "uncounted": {},
        "counted": {}
    }
}
custom_licenses = {
        "uncounted": [],
        "counted": {}
    }
def get_custom_licenses_info():
    global custom_licenses
    custom_licenses = {
        "uncounted": [],
        "counted": {}
    }
    current_frame = 0
    for i in counted_custom_license_frame.winfo_children():
        count = 0
        name = ''
        state = False
        error = False
        for j in i.winfo_children():
            if type(j) == Checkbutton:
                if counted_custom_vars[current_frame].get() == True:
                    state = True
            if j.winfo_name() == '!entry2':
                name = j.get().replace(" ", "")
            if j.winfo_name() == '!entry':
                if re.match(r"\d+", j.get()):
                    count = j.get()
                else:
                    error = True
        if error == True and state == True:
            messagebox.showinfo('Ошибка', 'Введено некорректное количество лицензий')
            break
        if name == '' and state == True:
            messagebox.showinfo('Ошибка', 'Введите название лицензий во всех отмеченных полях')
            break
        elif error == False and state == True:
            if name not in custom_licenses["counted"]:
                custom_licenses["counted"][name] = 0
                custom_licenses["counted"][name] = count
        current_frame += 1

    state = False
    current_frame = 0

    for i in uncounted_custom_license_frame.winfo_children():
        for j in i.winfo_children():
            if type(j) == Checkbutton:
                if uncounted_custom_vars[current_frame].get() == True:
                    state = True
            if type(j) == Entry:
                license_name = j.get()
        if license_name not in custom_licenses and state == True:
            if license_name == '':
                messagebox.showinfo('Ошибка', 'Введите название лицензий во всех отмеченных полях')
            else:
                custom_licenses["uncounted"].append(license_name)
        current_frame += 1
        state = False
    return custom_licenses

def clicked(device_type):
    """ Обработка нажатия кнопки """
    custom_licenses = get_custom_licenses_info()
    if vdh.get() == '' or sku.get() == '':
        messagebox.showinfo('Ошибка', 'Заполните VDH и SKU и отметьте нужные лицензии!')
    else:
        if needed_licenses == [] and custom_licenses["uncounted"] == [] and custom_licenses["counted"] == {}:
            messagebox.showinfo('Ошибка', 'Заполните VDH и SKU и отметьте нужные лицензии!')
        else:
            generate_licenses(device_type)


def generate_licenses(device_type):
    """ Подключение по telnet и генерация лицензий """
    try:
        print('Подключение к Nexus с root правами... ', end='')
        tn = telnet_connection()
        time.sleep(2)
        log_in = tn.read_very_eager().decode('utf-8')
        if re.search('Linux#', log_in):
            print('Done')
            creating_final_license_files(tn, device_type)
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
                creating_final_license_files(tn, device_type)
            elif re.search('Login incorrect', log_in):
                print('Получить root права не удалось. Попробуйте вручную')
    except TimeoutError:
        messagebox.showinfo('Ошибка', 'Проблема с подключением к Nexus')


def get_root():
    """ Получение root прав """
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
    all_licenses_in_bootflash = True
    global licenses_not_in_bootflash
    licenses_not_in_bootflash = []
    id = 0
    """ Создание файлов предопределённых лицензий """
    for license in needed_licenses:
        if license in licenses[device_type]["uncounted"]:
            license_name = licenses[device_type]["uncounted"][license]
            file_name = f'{vdh.get().replace("VDH=", "")}_{license_name}.lic'
            file_id = ('0' + str(id))[-2:]
            current_license = f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {license_name} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>202203161532072{file_id}</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN=9F924AA63160'
            tn.write(b"printf '" + current_license.encode('ascii') + b"' > /bootflash/" + file_name.encode('ascii') + b"\n")
        id += 1

    """ Создание файлов counted лицензий """
    for license in custom_licenses["uncounted"]:
        file_id = ('0' + str(id))[-2:]
        file_name = f'{vdh.get().replace("VDH=", "")}_{license}.lic'
        current_license = f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {license} cisco 1.0 permanent uncounted \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>202203161532072{file_id}</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN=9F924AA63160'
        tn.write(b"printf '" + current_license.encode('ascii') + b"' > /bootflash/" + file_name.encode('ascii') + b"\n")
        id += 1

    """ Создание файлов uncounted лицензий """
    for license in custom_licenses["counted"].items():
        count = license[1]
        file_id = ('0' + str(id))[-2:]
        file_name = f'{vdh.get().replace("VDH=", "")}_{license[0]}.lic'
        current_license = f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {license[0]} cisco 1.0 permanent {count} \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>202203161532072{file_id}</LicFileID><LicLineID>1</LicLineID> \\\n    <PAK></PAK>" SIGN=9F924AA63160'
        tn.write(b"printf '" + current_license.encode('ascii') + b"' > /bootflash/" + file_name.encode('ascii') + b"\n")
        id += 1

    tn.write(b'cd /bootflash/\n')
    tn.write(b'ls -l\n')
    time.sleep(1)
    bootflash_licenses = re.findall(r'\S+.lic', tn.read_very_eager().decode('utf-8'))
    for license in needed_licenses:
        if license in licenses[device_type]["uncounted"]:
            license_name = licenses[device_type]["uncounted"][license]
            file_name = f'{vdh.get().replace("VDH=", "")}_{license_name}.lic'
            if file_name not in bootflash_licenses:
                all_licenses_in_bootflash = False
                licenses_not_in_bootflash.append(file_name)

    for license in custom_licenses["uncounted"]:
        file_name = f'{vdh.get().replace("VDH=", "")}_{license}.lic'
        if file_name not in bootflash_licenses:
            all_licenses_in_bootflash = False
            licenses_not_in_bootflash.append(file_name)

    for license in custom_licenses["counted"].items():
        file_name = f'{vdh.get().replace("VDH=", "")}_{license[0]}.lic'
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

def creating_final_license_files(tn, device_type):
    license_creation = create_license_files(tn, device_type)
    if license_creation:
        messagebox.showinfo('Ошибка', 'Не удалось создать все необходимые файлы лицензий в bootflash\nПопробуйте запустить заново')
        print('Следующие файлы лицензий не удалось создать:',
              '\n'.join(str(lic) for lic in licenses_not_in_bootflash), sep='\n')
    else:
        line1 = f"printf '{vdh.get().replace('VDH=', '')}"
        line2 = "' > serialno"
        tn.write(b'cp /bootflash/usr/bin/gdb /usr/bin/gdb\n')
        time.sleep(1)
        tn.write(b'cd /isan/etc/\n')
        time.sleep(1)
        tn.write(line1.encode('ascii') + b'\\x00\\x00' + line2.encode('ascii') + b'\n')

        id = 0
        for license in needed_licenses:
            license_name = licenses[device_type]["uncounted"][license]
            count = 'uncounted'
            file_id = ('0' + str(id))[-2:]
            get_license_sign(tn, license_name, count, file_id)
            id += 1
        for license in custom_licenses["uncounted"]:
            license_name = license
            count = 'uncounted'
            file_id = ('0' + str(id))[-2:]
            get_license_sign(tn, license_name, count, file_id)
            id += 1

        for license in custom_licenses["counted"].items():
            license_name = license[0]
            count = license[1]
            file_id = ('0' + str(id))[-2:]
            get_license_sign(tn, license_name, count, file_id)
            id += 1

        print(f'Лицензии успешно сгенерированы и находятся по следующему пути:\n{current_directory}')
        messagebox.showinfo('', f'Лицензии успешно сгенерированы и находятся по следующему пути:\n{current_directory}')

def get_license_sign(tn, license_name, count, file_id):
    file_name = f'{vdh.get().replace("VDH=", "")}_{license_name}.lic'
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
    reverse_sign = re.search(r'(0x00\S+)', tn.read_very_eager().decode('utf-8').replace("\t", "\n"))[1][-12:]
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
        f'SERVER this_host ANY\nVENDOR cisco\nINCREMENT {license_name} cisco 1.0 permanent {count} \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku.get()}</SKU> \\\n    HOSTID=VDH={vdh.get().replace("VDH=", "")} \\\n    NOTICE="<LicFileID>202203161532072{file_id}</LicFileID>1</LicLineID> \\\n    <PAK></PAK>" SIGN={sign}')
    print('Done')
    print(f'Удаление {file_name} из bootflash...', end='')
    tn.write(b'rm /bootflash/' + file_name.encode('ascii') + b'\n')
    time.sleep(1)
    print(f'Done')

def get_counted_license_information(mds_counted_licenses_frame):
    """ Получение имени counted лицензии и количества, внесение данных в основной словарь """
    found_count = True
    for i in mds_counted_licenses_frame.winfo_children():                           # Проход по основному фрейму
        if found_count == False:
            messagebox.showinfo('Ошибка', 'В поле количества лицензий введено неправильное значение')
            break
        else:
            for j in i.winfo_children():
                if type(j) == Entry:
                    count = j.get()
                elif type(j) == Checkbutton:
                    name = j.cget("text")
                    if name in needed_licenses_counted:
                        if name not in licenses['mds']['counted']:
                            licenses['mds']['counted'][name] = {'name': '', 'count': ''}
                        if count != '' and re.search(r'\d+', count):
                                licenses['mds']['counted'][name]["count"] = count
                        else:
                            found_count = False
                            break
                    else:
                        continue
    return licenses

def update_needed_licenses(license, device_type_temp, license_type):
    global device_type
    device_type = device_type_temp
    if license_type == 'uncounted':
        if license in needed_licenses:
            needed_licenses.remove(license)
        elif license not in needed_licenses:
            needed_licenses.append(license)
    elif license_type == 'counted':
            if license in needed_licenses_counted:
                needed_licenses_counted.remove(license)
            elif license not in needed_licenses_counted:
                needed_licenses_counted.append(license)
    if needed_licenses == [] and needed_licenses_counted == []:
        current_switch_type = 'all'
    else:
        for license_list in [needed_licenses, needed_licenses_counted]:
            for lic in license_list:
                if lic in licenses["nexus"]["uncounted"]:
                    current_switch_type = 'nexus'
                    break
                elif lic in licenses["mds"]["uncounted"]:
                    current_switch_type = 'mds'
                    break
                else:
                    current_switch_type = 'all'
    if current_switch_type == 'mds':
        for widget in nexus_frame.winfo_children():
            widget.destroy()
        nexus_checkbutton(current_switch_type)
    elif current_switch_type == 'nexus':
        for widget in mds_frame.winfo_children():
            widget.destroy()
        mds_checkbutton(current_switch_type)
    else:
        for widget in nexus_frame.winfo_children():
            widget.destroy()
        nexus_checkbutton(current_switch_type)
        for widget in mds_frame.winfo_children():
            widget.destroy()
        mds_checkbutton(current_switch_type)
    return needed_licenses
    return needed_licenses_counted
    return device_type

def nexus_checkbutton(current_switch_type):
    """ Отрисовка Nexus checkbutton """
    global custom_license_entry
    if current_switch_type == 'mds':
        blocked = DISABLED
    else:
        blocked = ACTIVE
    for lic in licenses["nexus"]["uncounted"]:
        if lic != 'custom':
            var = tkinter.BooleanVar()
            cb = Checkbutton(nexus_frame, text=licenses["nexus"]["uncounted"][lic], state=blocked, variable=var,
                             onvalue=True,
                             offvalue=False,
                             command=lambda lic=lic: update_needed_licenses(lic, 'nexus', 'uncounted'))
            cb.pack(anchor="w")

def mds_checkbutton(current_switch_type):
    """ Отрисовка MDS checkbutton """
    global mds_counted_licenses_frame
    if current_switch_type == 'nexus':
        blocked = DISABLED
    else:
        blocked = ACTIVE
    for mds_lic in licenses["mds"]["uncounted"]:
        if mds_lic != 'custom':
            var = tkinter.BooleanVar()
            mds_cb = Checkbutton(mds_frame, text=licenses["mds"]["uncounted"][mds_lic], state=blocked, variable=var, onvalue=True,
                             offvalue=False,
                             command=lambda mds_lic=mds_lic: update_needed_licenses(mds_lic, 'mds', 'uncounted'))
            mds_cb.pack(anchor="w")

    mds_counted_licenses_frame = ttk.Frame(mds_frame, padding=[0, 0])
    mds_counted_licenses_frame.pack(anchor="w", padx=1)

def create_custom_license_checkbutton():
    uncounted_custom_vars = []
    counted_custom_vars = []
    for i in range(0, 4):
        """ Создание Checkbutton для counted лицензий """
        custom_license_frame = ttk.Frame(counted_custom_license_frame, padding=[0, 0])
        custom_license_frame.pack(anchor="w", padx=1)
        count_entry = Entry(custom_license_frame, width=3)
        name_entry = Entry(custom_license_frame, width=25)
        state = tkinter.BooleanVar()
        counted_custom_vars.append(state)
        text = f'{count_entry.pack(anchor="w", side=RIGHT, padx=0)}{name_entry.pack(anchor="w", side=RIGHT, padx=0)}'
        custom_counted_lic_checkbutton = Checkbutton(custom_license_frame,
                                                     text=text.replace("None", ""), variable=counted_custom_vars[i])
        custom_counted_lic_checkbutton.pack(anchor='w', side=LEFT, padx=0)

        """ Создание Checkbutton для uncounted лицензий """
        custom_license_frame = ttk.Frame(uncounted_custom_license_frame, padding=[0, 0])
        custom_license_frame.pack(anchor="w", padx=1)
        name_entry = Entry(custom_license_frame, width=28)
        state = tkinter.BooleanVar()
        uncounted_custom_vars.append(state)
        custom_lic_checkbutton = Checkbutton(custom_license_frame,
                                             text=name_entry.pack(anchor='w', side=RIGHT, padx=0),
                                             variable=uncounted_custom_vars[i])
        custom_lic_checkbutton.pack(anchor='w', side=LEFT, padx=0)
    return (uncounted_custom_vars, counted_custom_vars)

if __name__ == "__main__":
    global nexus_frame
    """ Основная функция, вывод на экран """
    window = Tk()
    window.title("License Generator")
    window.geometry("450x540")

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

    custom_license_frame = ttk.LabelFrame(text='Custom', padding=[0, 0])
    custom_license_frame.pack(anchor='w', padx=5)

    nexus_frame = ttk.LabelFrame(licenses_frame, text='Nexus', padding=[0, 0])
    nexus_frame.pack(anchor='w', padx=5, side=LEFT)

    mds_frame = ttk.LabelFrame(licenses_frame, text='MDS', padding=[0, 0])
    mds_frame.pack(anchor='nw', padx=5, side=RIGHT)

    counted_custom_license_frame = ttk.LabelFrame(custom_license_frame, text='Counted', padding=[0, 0])
    counted_custom_license_frame.pack(anchor='e', padx=5, side=RIGHT)

    uncounted_custom_license_frame = ttk.LabelFrame(custom_license_frame, text='Uncounted', padding=[0, 0])
    uncounted_custom_license_frame.pack(anchor='w', padx=5, side=RIGHT,)

    custom_vars = create_custom_license_checkbutton()
    uncounted_custom_vars = custom_vars[0]
    counted_custom_vars = custom_vars[1]

    nexus_checkbutton(current_switch_type)
    mds_checkbutton(current_switch_type)

    bottom_frame = ttk.Frame(window)
    bottom_frame.pack()

    btn = Button(bottom_frame, text="Generate", command=lambda: clicked(device_type), width=20)
    btn.pack(anchor='s')

    window.mainloop()