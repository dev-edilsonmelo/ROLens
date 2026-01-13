#!/usr/bin/env python3
"""
Script para gerar executável autocontido do ROLens
Usa PyInstaller para criar um .exe standalone
"""

import PyInstaller.__main__
import os
import sys

def build_executable():
    """Gera executável do ROLens"""
    
    # Caminho base do projeto
    base_path = os.path.dirname(os.path.abspath(__file__))
    xp_table_path = os.path.join(base_path, 'xp_table.json')
    manifest_path = os.path.join(base_path, 'ROLens.manifest')
    
    # Argumentos do PyInstaller
    args = [
        'gui.py',  # Script principal
        '--name=ROLens',  # Nome do executável
        '--onefile',  # Um único arquivo
        '--windowed',  # Sem console (GUI)
        '--icon=NONE',  # Sem ícone por enquanto
        '--clean',  # Limpa cache
        '--noconfirm',  # Não pede confirmação
        '--uac-admin',  # Força execução como administrador (UAC)
        
        # Adiciona manifesto UAC para forçar execução como admin
        f'--manifest={manifest_path}' if os.path.exists(manifest_path) else '',
        
        # NÃO incluir xp_table.json - será criado externamente para permitir atualizações
        
        # Hidden imports necessários
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=qrcode',
        '--hidden-import=matplotlib',
        '--hidden-import=filelock',
        
        # Coleta todos os módulos do projeto
        '--collect-all=customtkinter',
        
        # Otimizações
        '--optimize=2',
        
        # Diretório de saída
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
    ]
    
    # Remove argumentos vazios
    args = [arg for arg in args if arg]
    
    print("=" * 60)
    print("ROLens - Gerando Executável Autocontido")
    print("=" * 60)
    print()
    
    print("ℹ xp_table.json será criado automaticamente na pasta do executável")
    print("  Isso permite que o arquivo seja atualizado durante o uso")
    
    if os.path.exists(manifest_path):
        print("✓ Manifesto UAC encontrado - executável pedirá privilégios de admin")
    else:
        print("⚠ Manifesto UAC não encontrado")
    
    print()
    print("Isso pode levar alguns minutos...")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        
        print()
        print("=" * 60)
        print("✓ Executável gerado com sucesso!")
        print("=" * 60)
        print()
        print(f"Localização: {os.path.join(base_path, 'dist', 'ROLens.exe')}")
        print()
        print("O executável é autocontido e pode ser distribuído")
        print("sem necessidade de instalação de Python ou dependências.")
        print()
        print("NOTA: O arquivo xp_table.json será criado automaticamente")
        print("na mesma pasta do executável na primeira execução.")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Erro ao gerar executável!")
        print("=" * 60)
        print()
        print(f"Erro: {e}")
        print()
        sys.exit(1)

if __name__ == '__main__':
    build_executable()
