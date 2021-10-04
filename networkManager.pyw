import re
import wmi
import sys
import winreg
from pyuac import main_requires_admin

class NetworkAdapterNotFound(Exception):
    pass


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
    
    raise NetworkAdapterNotFound 

def EnableProxy():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings", access=winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)

def DisableProxy():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings", access=winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

@main_requires_admin
def EnableStaticIP(nicSettings, ip, gateway, dns):
    nicSettings.EnableStatic([ip], ["255.255.252.0"])
    nicSettings.SetGateways(DefaultIPGateway=[gateway])
    nicSettings.SetDNSServerSearchOrder(dns)
    nicSettings.SetDNSDomain("oao-pes.local")

@main_requires_admin
def EnableDHCP(nicSettings):
    nicSettings.EnableDHCP()
    nicSettings.SetDNSServerSearchOrder()

def NAT():
    DisableProxy()
    ip = "192.168.101.230"
    gateway = "192.168.101.254"
    dns = ["192.168.100.253", "4.4.4.4"]
    nicSettings = GetAdapterSettings()
    EnableStaticIP(nicSettings, ip, gateway, dns)

def DHCP():
    EnableProxy()
    nicSettings = GetAdapterSettings()
    EnableDHCP(nicSettings)

DHCP()
