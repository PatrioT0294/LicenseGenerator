import re
import time
import tkinter
from tkinter import *
from tkinter import ttk
import telnetlib
from tkinter import messagebox
import os
import random



user = 'alex'
password = 'cisco123'
current_directory = os.getcwd()
licenses_for_generate = {}
needed_licenses = []
current_switch_type = 'all'
device_type = ''
new = 'INCREMENT {license_name} cisco 1.0 permanent {count} \\\n    VENDOR_STRING=<LIC_SOURCE>MDS_SWIFT</LIC_SOURCE><SKU>{sku_string}</SKU> \\\n    HOSTID=VDH={vdh_string} \\\n    NOTICE="<LicFileID>{license_id}</LicFileID><LicLineID>{file_id}</LicLineID> \\\n    <PAK></PAK>" SIGN={sign}'
old = 'INCREMENT {license_name} cisco 1.0 permanent {count} VENDOR_STRING=MDS \\\n        HOSTID=VDH={vdh_string} \\\n        NOTICE=<LicFileID>{license_id}</LicFileID><LicLineID>{file_id}</LicLineID><PAK>{sku_string}{vdh_string}AMS15160167</PAK> \\\n        SIGN={sign}'
sku_string = ''
vdh_string = ''
final_license_list = []
licenses = {
    "nexus": {
        "uncounted": {
            "ENHANCED_LAYER2_PKG": "ENHANCED_L2",
            "ENTERPRISE_PKG": "ENTERPRISE",
            "FC_FEATURES_PKG": "FC_FEATURES",
            "FCOE_NPV_PKG": "FCOE_NPV",
            "FM_SERVER_PKG": "FM_SERVER",
            "LAN_BASE_SERVICES_PKG": "LAN_BASE",
            "LAN_ENTERPRISE_SERVICES_PKG": "LAN_ENT",
            "NETWORK_SERVICES_PKG": "NETWORK",
            "VMFEX_FEATURE_PKG": "VMFEX",
            "24P_LIC_PKG": "24P_LIC_PKG",
            "24P_UPG_PKG": "24P_UPG_PKG"
        }
    },
    "mds": {
        "uncounted": {
            # "ENTERPRISE_PKG": "ENT_PKG",
            "SAN_TELEMETRY_PKG": "TELEMETRY",
            "SAN_ANALYTICS_PKG": "ANALYTICS",
            "MAINFRAME_PKG": "MAINFRAME",
            "DMM_FOR_SSM_PKG": "DMM_FOR_SSM"
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
def get_license_info():
    # Составление итогового списка нужных лицензий
    global custom_licenses
    global licenses_for_generate
    custom_licenses = {
        "uncounted": [],
        "counted": {}
    }
    current_frame = 0
    stop = False
    file_id = 1
    for license in needed_licenses:
        license_id = ''
        for id_i in range(0, 17):
            license_id += str(random.randint(0, 9))
        licenses_for_generate[file_id] = {}
        licenses_for_generate[file_id]["name"] = license
        licenses_for_generate[file_id]["count"] = "uncounted"
        licenses_for_generate[file_id]["license_id"] = license_id
        file_id += 1
    for i in counted_custom_license_frame.winfo_children():
        license_id = ''
        for id_i in range(0, 17):
            license_id += str(random.randint(0, 9))
        count = 'uncounted'
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
            stop = True
            messagebox.showinfo('Ошибка', 'Введено некорректное количество лицензий')
            break
        elif name == '' and state == True:
            stop = True
            messagebox.showinfo('Ошибка', 'Введите название лицензий во всех отмеченных полях')
            break
        elif error == False and state == True:
            if name not in custom_licenses["counted"]:
                custom_licenses["counted"][name] = 0
                custom_licenses["counted"][name] = count
            licenses_for_generate[file_id] = {}
            licenses_for_generate[file_id]["name"] = name
            licenses_for_generate[file_id]["count"] = count
            licenses_for_generate[file_id]["license_id"] = license_id
            file_id += 1
        current_frame += 1

    state = False
    current_frame = 0
    for i in uncounted_custom_license_frame.winfo_children():
        license_id = ''
        for id_i in range(0, 17):
            license_id += str(random.randint(0, 9))
        for j in i.winfo_children():
            if type(j) == Checkbutton:
                if uncounted_custom_vars[current_frame].get() == True:
                    state = True
            if type(j) == Entry:
                license_name = j.get()
        if license_name not in custom_licenses and state == True:
            if license_name == '':
                stop = True
                messagebox.showinfo('Ошибка', 'Введите название лицензий во всех отмеченных полях')
                break
            else:
                custom_licenses["uncounted"].append(license_name)
                licenses_for_generate[file_id] = {}
                licenses_for_generate[file_id]["name"] = license_name
                licenses_for_generate[file_id]["count"] = 'uncounted'
                licenses_for_generate[file_id]["license_id"] = license_id
                file_id += 1
        current_frame += 1
        state = False
    return [custom_licenses, stop, licenses_for_generate]

def clicked(device_type):
    """ Обработка нажатия кнопки """
    global current_license
    global sku_string
    global vdh_string
    global licenses_for_generate
    sku_string = sku.get()
    vdh_string = vdh.get().replace("VDH=", "")
    if format.get() == 'new':
        current_license = new
    else:
        current_license = old
    custom_licenses_info = get_license_info()
    # custom_licenses = custom_licenses_info[0]
    error = custom_licenses_info[1]
    licenses_for_generate = custom_licenses_info[2]
    if error == False:
        if vdh.get() == '' or sku.get() == '':
            messagebox.showinfo('Ошибка', 'Заполните VDH и SKU и отметьте нужные лицензии!')
        else:
            if licenses_for_generate == {}:
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
            print('Failed\nПолучение root прав... ', end='')
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
    created_licenses_list = []
    all_licenses_in_bootflash = True
    global licenses_not_in_bootflash
    licenses_not_in_bootflash = []
    id = 0

    """ Создание файлов в bootflash """
    for license in licenses_for_generate.items():
        if needed_licenses == []:
            name_for_file = license[1]["name"]
        else:
            if license[1]["name"] in licenses[device_type]["uncounted"]:
                name_for_file = licenses[device_type]["uncounted"][license[1]["name"]]
            else:
                name_for_file = license[1]["name"]
        license_name = license[1]["name"]
        if license[1]["count"] == '0':
            count = 'uncounted'
        else:
            count = license[1]["count"]
        license_id = license[1]["license_id"]
        file_id = ('0' + str(license[0]))[-2:]
        filename = f'{vdh.get().replace("VDH=", "")}_{name_for_file}_{file_id}.lic'
        sign = '9F924AA63160'
        license_string = 'SERVER this_host ANY\nVENDOR cisco\n' + current_license.format(license_name=license_name, count=count, sku_string=sku_string,
                                                      vdh_string=vdh_string, license_id=license_id, file_id=license[0], sign=sign)
        tn.write(b"printf '" + license_string.encode('ascii') + b"' > /bootflash/" + filename.encode('ascii') + b"\n")
        created_licenses_list.append(filename)
        id += 1
    tn.write(b'cd /bootflash/\n')
    tn.write(b'ls -l\n')
    time.sleep(1)

    ''' Проверяем, что в bootflash создались все лицензии'''
    for license in licenses_for_generate.items():
        if needed_licenses == []:
            name_for_file = license[1]["name"]
        else:
            if license[1]["name"] in licenses[device_type]["uncounted"]:
                name_for_file = licenses[device_type]["uncounted"][license[1]["name"]]
            else:
                name_for_file = license[1]["name"]
        file_id = ('0' + str(license[0]))[-2:]
        filename = f'{vdh.get().replace("VDH=", "")}_{name_for_file}_{file_id}.lic'
        if filename not in created_licenses_list:
            all_licenses_in_bootflash = False
            licenses_not_in_bootflash.append(license[1]["name"])
    if all_licenses_in_bootflash == True:
        print('Done')
    else:
        return licenses_not_in_bootflash

def telnet_connection():
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
        for license in licenses_for_generate.items():
            if needed_licenses == []:
                name_for_file = license[1]["name"]
            else:
                if license[1]["name"] in licenses[device_type]["uncounted"]:
                    name_for_file = licenses[device_type]["uncounted"][license[1]["name"]]
                else:
                    name_for_file = license[1]["name"]
            file_id = ('0' + str(license[0]))[-2:]
            filename = f'{vdh.get().replace("VDH=", "")}_{name_for_file}_{file_id}.lic'
            license_name = license[1]["name"]
            license[1]["sign"] = get_license_sign(tn, license_name, filename)
            print('Done')
            print(f'Удаление {filename} из bootflash...', end='')
            tn.write(b'rm /bootflash/' + filename.encode('ascii') + b'\n')
            time.sleep(1)
            print(f'Done')
        summary_file = f"{vdh_string}.lic"
        f = open(summary_file, 'w')
        f.write('SERVER this_host ANY\nVENDOR cisco\n')
        for license in licenses_for_generate.items():
            license_name = license[1]["name"]
            count = license[1]["count"]
            license_id = license[1]["license_id"]
            sign = license[1]["sign"]
            f.write(current_license.format(license_name=license_name, count=count, sku_string=sku_string, vdh_string=vdh_string, license_id=license_id, file_id=license[0], sign=sign) + '\n')
        print(f'Лицензии успешно сгенерированы и находятся по следующему пути:\n{current_directory}')
        messagebox.showinfo('', f'Лицензии успешно сгенерированы и находятся по следующему пути:\n{current_directory}')

def get_license_sign(tn, license_name, file_name):
    print(f'Получение подписи для {license_name}... ', end='')
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
    return sign

def update_needed_licenses(license, device_type_temp):
    global device_type
    device_type = device_type_temp
    if license in needed_licenses:
        needed_licenses.remove(license)
    elif license not in needed_licenses:
        needed_licenses.append(license)
    if needed_licenses == []:
        current_switch_type = 'all'
    else:
        for license_list in needed_licenses:
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
    return device_type

def nexus_checkbutton(current_switch_type):
    """ Отрисовка Nexus checkbutton """
    global custom_license_entry
    if current_switch_type == 'mds':
        blocked = DISABLED
    else:
        blocked = ACTIVE
    for lic in licenses["nexus"]["uncounted"].items():
        var = tkinter.BooleanVar()
        cb = Checkbutton(nexus_frame, text=lic[0], state=blocked, variable=var,
                         onvalue=True,
                         offvalue=False,
                         command=lambda lic=lic[0]: update_needed_licenses(lic, 'nexus'))
        cb.pack(anchor="w")

def mds_checkbutton(current_switch_type):
    """ Отрисовка MDS checkbutton """
    if current_switch_type == 'nexus':
        blocked = DISABLED
    else:
        blocked = ACTIVE
    for mds_lic in licenses["mds"]["uncounted"].items():
        var = tkinter.BooleanVar()
        mds_cb = Checkbutton(mds_frame, text=mds_lic[0], state=blocked, variable=var, onvalue=True,
                         offvalue=False,
                         command=lambda mds_lic=mds_lic[0]: update_needed_licenses(mds_lic, 'mds'))
        mds_cb.pack(anchor="w")

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
    window.title("License Generator 2.0")
    window.geometry("450x540")

    """ Фрейм выбора формата лицензии"""
    first_frame = ttk.Frame(padding=[0, 0])
    first_frame.pack(anchor='w', padx=0)

    vdh_sku_frame = ttk.Frame(first_frame, padding=[0, 0])
    vdh_sku_frame.pack(anchor='w', side=LEFT, padx=0)

    format_frame = ttk.LabelFrame(first_frame, text='Format', padding=[0, 0])
    format_frame.pack(anchor='nw', side=RIGHT, padx=0)

    vdh_frame = ttk.LabelFrame(vdh_sku_frame, text='VDH', padding=[0, 0])  # borderwidth=1, relief=SOLID,
    vdh_frame.pack(anchor='w', padx=10)

    vdh = Entry(vdh_frame, width=33)
    vdh.pack(anchor='w')

    sku_frame = ttk.LabelFrame(vdh_sku_frame, text='SKU', padding=[0, 0])
    sku_frame.pack(anchor='w', padx=10)

    sku = Entry(sku_frame, width=33)
    sku.pack(anchor='w')

    new_format = "new"
    old_format = "old"

    format = StringVar(value=new_format)

    new_format = Radiobutton(format_frame, text='New format', value=new_format, variable=format)
    new_format.pack(anchor='n', padx=1)

    old_format = Radiobutton(format_frame, text='Old format', value=old_format, variable=format)
    old_format.pack(anchor='n', padx=1)

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