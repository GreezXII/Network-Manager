import os
import re
import wmi
import sys
import winreg
from pyuac import main_requires_admin
from tkinter import *
from tkinter import ttk
from time import sleep


def ShowPopUp(title, message, error=False, time=3):
    
    def Show():
        alpha = 0.0
        while alpha <= 1.0:
            root.attributes('-alpha', alpha)
            alpha += 0.03
            sleep(0.001)
            root.update()

        sleep(time)

        while alpha >= 0:
            root.attributes('-alpha', alpha)
            alpha -= 0.03
            sleep(0.001)
            root.update()

        root.destroy()

    
    root = Tk()
    # Size and possition
    width = 420
    height = 80
    padding_x = 10
    padding_y = 50
    x = root.winfo_screenwidth() - width - padding_x
    y = root.winfo_screenheight() - height - padding_y
    root.geometry(f"{width}x{height}+{x}+{y}")
    # Layout
    root.resizable(0, 0)
    root.overrideredirect(True)
    root["bg"] = 'white'
    line = Frame(root, width=5, height=height, background="#3086EB")
    line.pack(side=LEFT)
    canvas = Canvas(root, width=62, height=42, highlightbackground="white", background='white')
    canvas.pack(side=LEFT)
    if (error):
        image_name = "error.png"
    else:
        image_name = "notification.png"
    image_path = os.path.join(os.getcwd(), image_name)
    image = PhotoImage(file=image_path)
    canvas.create_image(35, 23, image=image)

    header = Label(text=title, background="white", font="Arial 13 bold")
    message = Label(text=message, foreground="#424244", background="white", font="Arial 11")
    header.place(relx=.18, rely=.17)
    message.place(relx=.18, rely=.5)
    
    # Logic
    root.after(0, Show)
    root.mainloop()

def GetAdapterSettings():
    windowsVersion = sys.getwindowsversion()[0]
    if windowsVersion == 10:
        adapterNamePattern = ".*Ethernet.*"
    elif windowsVersion == 6:
        adapterNamePattern = ".*Подключение по локальной сети.*"

    c = wmi.WMI()
    for nic in c.Win32_NetworkAdapter(PhysicalAdapter=True):
        if re.match(adapterNamePattern, nic.NetConnectionID):
            return c.Win32_NetworkAdapterConfiguration(InterfaceIndex=nic.InterfaceIndex)[0]
    
    ShowPopUp("Ошибка", "Не найден сетевой интерфейс.", erroe=True)

def GetCurrentIP():
    adapter_settings = GetAdapterSettings()
    return adapter_settings.IPAddress[0]

def EnableProxy():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings", access=winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)

def DisableProxy():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings", access=winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

@main_requires_admin(return_output=False)
def EnableStaticIP(nicSettings, ip, gateway, dns):
    nicSettings.EnableStatic([ip], ["255.255.252.0"])
    nicSettings.SetGateways(DefaultIPGateway=[gateway])
    nicSettings.SetDNSServerSearchOrder(dns)
    nicSettings.SetDNSDomain("oao-pes.local")
    ip = GetCurrentIP()
    ShowPopUp("Режим работы: NAT", f"IP Адрес: {ip}")

@main_requires_admin(return_output=False)
def EnableDHCP(nicSettings):
    nicSettings.EnableDHCP()
    nicSettings.SetDNSServerSearchOrder()
    ip = GetCurrentIP()
    ShowPopUp(f"Режим работы: DHCP", f"IP Адрес: {ip}")

def NAT(ip, gw):
    DisableProxy()
    dns = ["192.168.100.253", "4.4.4.4"]
    nicSettings = GetAdapterSettings()
    EnableStaticIP(nicSettings, ip, gw, dns)

def DHCP():
    EnableProxy()
    nicSettings = GetAdapterSettings()
    EnableDHCP(nicSettings)


def Main():
    if (len(sys.argv) > 1): 
        cmd = sys.argv[1].lower()

        if (cmd == "-nat101"):
            ip = "192.168.101.230"
            gw = "192.168.101.254"
            NAT(ip, gw)

        elif (cmd == '-nat99'):
            ip = "192.168.99.230"
            gw = "192.168.99.254"
            NAT(ip, gw)

        elif (cmd == '-dhcp'):
            DHCP()
        
        elif (cmd =='-?'):
            ShowPopUp("Возможные параметры", "-nat101 -nat99 -dhcp", time=6)

        else:
            ShowPopUp("Ошибка", "Неправильный параметр. Вывод параметров -?", error=True)
    
    else:
        ShowPopUp("Ошибка", "Не указан параметр. Вывод параметров -?", error=True)
        

if __name__ == "__main__":
    Main()
