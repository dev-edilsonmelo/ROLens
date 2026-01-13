import sys
import json
import struct
from ctypes import *
from ctypes.wintypes import *

# Constantes do Windows API
PROCESS_ALL_ACCESS = 0x1F0FFF
TH32CS_SNAPPROCESS = 0x00000002

# Estruturas do Windows
class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('cntUsage', DWORD),
        ('th32ProcessID', DWORD),
        ('th32DefaultHeapID', POINTER(ULONG)),
        ('th32ModuleID', DWORD),
        ('cntThreads', DWORD),
        ('th32ParentProcessID', DWORD),
        ('pcPriClassBase', LONG),
        ('dwFlags', DWORD),
        ('szExeFile', c_char * 260)
    ]

class MODULEENTRY32(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('th32ModuleID', DWORD),
        ('th32ProcessID', DWORD),
        ('GlblcntUsage', DWORD),
        ('ProccntUsage', DWORD),
        ('modBaseAddr', POINTER(BYTE)),
        ('modBaseSize', DWORD),
        ('hModule', HMODULE),
        ('szModule', c_char * 256),
        ('szExePath', c_char * 260)
    ]

# Funções do Windows API
kernel32 = windll.kernel32
CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
Process32First = kernel32.Process32First
Process32Next = kernel32.Process32Next
Module32First = kernel32.Module32First
Module32Next = kernel32.Module32Next
OpenProcess = kernel32.OpenProcess
ReadProcessMemory = kernel32.ReadProcessMemory
CloseHandle = kernel32.CloseHandle

def list_processes():
    """Lista todos os processos Ragexe.exe"""
    processes = []
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

    if snapshot == -1:
        return processes

    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)

    if Process32First(snapshot, byref(pe32)):
        while True:
            exe_name = pe32.szExeFile.decode('utf-8', errors='ignore')
            if exe_name.lower() == 'ragexe.exe':
                processes.append({
                    'pid': pe32.th32ProcessID,
                    'name': exe_name
                })

            if not Process32Next(snapshot, byref(pe32)):
                break

    CloseHandle(snapshot)
    return processes

def get_module_base(pid, module_name):
    """Obtém o endereço base de um módulo"""
    TH32CS_SNAPMODULE = 0x00000008
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)

    if snapshot == -1:
        return 0

    me32 = MODULEENTRY32()
    me32.dwSize = sizeof(MODULEENTRY32)

    base_addr = 0
    if Module32First(snapshot, byref(me32)):
        while True:
            mod_name = me32.szModule.decode('utf-8', errors='ignore')
            if mod_name.lower() == module_name.lower():
                base_addr = cast(me32.modBaseAddr, c_void_p).value
                break

            if not Module32Next(snapshot, byref(me32)):
                break

    CloseHandle(snapshot)
    return base_addr

def read_int32(handle, address):
    """Lê um valor int32 da memória"""
    buffer = c_int32()
    bytes_read = c_size_t()

    if ReadProcessMemory(handle, c_void_p(address), byref(buffer), sizeof(buffer), byref(bytes_read)):
        return buffer.value
    return 0

def read_byte(handle, address):
    """Lê um byte da memória"""
    buffer = c_byte()
    bytes_read = c_size_t()

    if ReadProcessMemory(handle, c_void_p(address), byref(buffer), sizeof(buffer), byref(bytes_read)):
        return buffer.value
    return 0

def read_string(handle, address, length=24):
    """Lê uma string da memória"""
    buffer = create_string_buffer(length)
    bytes_read = c_size_t()

    if ReadProcessMemory(handle, c_void_p(address), buffer, length, byref(bytes_read)):
        try:
            return buffer.value.decode('utf-8', errors='ignore').rstrip('\x00')
        except:
            return ""
    return ""

def read_game_data(pid):
    """Lê os dados do jogo"""
    # Offsets
    offsets = {
        'xpBase': 0x106B6D0,
        'xpJob': 0x106B6E8,
        'hp': 0x106F28C,
        'sp': 0x106F294,
        'nvBase': 0x106B6F0,
        'nvJob': 0x106B6F8,
        'hpMax': 0x106F290,
        'spMax': 0x106F298,
        'name': 0x1071CD8
    }

    # Abre o processo
    handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not handle:
        return {'error': 'Failed to open process'}

    # Obtém o endereço base do módulo
    base_address = get_module_base(pid, 'Ragexe.exe')
    if not base_address:
        CloseHandle(handle)
        return {'error': 'Failed to get base address'}

    # Lê os dados
    data = {
        'xpBase': read_int32(handle, base_address + offsets['xpBase']),
        'xpJob': read_int32(handle, base_address + offsets['xpJob']),
        'hp': read_int32(handle, base_address + offsets['hp']),
        'sp': read_int32(handle, base_address + offsets['sp']),
        'nvBase': read_byte(handle, base_address + offsets['nvBase']),
        'nvJob': read_byte(handle, base_address + offsets['nvJob']),
        'hpMax': read_int32(handle, base_address + offsets['hpMax']),
        'spMax': read_int32(handle, base_address + offsets['spMax']),
        'nome': read_string(handle, base_address + offsets['name'], 24),
        'baseAddress': hex(base_address)
    }

    CloseHandle(handle)
    return data

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Missing command'}))
        return

    command = sys.argv[1]

    if command == 'list':
        processes = list_processes()
        print(json.dumps(processes))

    elif command == 'read':
        if len(sys.argv) < 3:
            print(json.dumps({'error': 'Missing PID'}))
            return

        try:
            pid = int(sys.argv[2])
            data = read_game_data(pid)
            print(json.dumps(data))
        except ValueError:
            print(json.dumps({'error': 'Invalid PID'}))

    else:
        print(json.dumps({'error': 'Unknown command'}))

if __name__ == '__main__':
    main()
