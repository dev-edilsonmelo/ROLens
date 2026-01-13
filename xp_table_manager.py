import json
import os
import urllib.request
from typing import Dict, Optional
from filelock import FileLock

class XPTableManager:
    """Gerencia a tabela de XP necessária por nível com suporte a múltiplos processos"""
    
    GITHUB_XP_TABLE_URL = "https://raw.githubusercontent.com/dev-edilsonmelo/ROLens/main/xp_table.json"

    def __init__(self, filename='xp_table.json', auto_download=True):
        self.filename = filename
        self.lock_filename = filename + '.lock'
        self.lock = FileLock(self.lock_filename, timeout=5)
        # Agora armazena dict com 'xp' e 'confirmed'
        self.base_table: Dict[str, Dict] = {}
        
        # Se não existe e auto_download está ativo, tenta baixar do GitHub
        if auto_download and not os.path.exists(self.filename):
            print("xp_table.json não encontrado. Baixando do GitHub...")
            if self.download_from_github():
                print("✓ Tabela XP baixada com sucesso!")
            else:
                print("⚠ Não foi possível baixar. Criando tabela vazia...")
        
        self.load()

    def load(self):
        """Carrega a tabela de XP do arquivo JSON com lock"""
        if os.path.exists(self.filename):
            try:
                # Adquire lock antes de ler
                with self.lock:
                    with open(self.filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Converte formato antigo (int) para novo formato (dict)
                        self.base_table = self._convert_to_new_format(data.get('base', {}))
            except Exception as e:
                print(f"Erro ao carregar tabela de XP: {e}")
                self.base_table = {}
        else:
            self.base_table = {}

    def save(self):
        """Salva a tabela de XP no arquivo JSON com lock"""
        try:
            # Adquire lock antes de escrever
            with self.lock:
                # Re-lê o arquivo para pegar atualizações de outros processos
                if os.path.exists(self.filename):
                    with open(self.filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        existing_base = self._convert_to_new_format(data.get('base', {}))

                        # Merge: mantém o maior valor de XP para cada nível
                        # IMPORTANTE: preserva flag confirmed se qualquer versão estiver confirmada
                        for level, entry in existing_base.items():
                            if level not in self.base_table:
                                self.base_table[level] = entry
                            else:
                                # Se XP do arquivo é maior, atualiza XP
                                if entry['xp'] > self.base_table[level]['xp']:
                                    self.base_table[level]['xp'] = entry['xp']
                                # Preserva confirmed se qualquer versão estiver confirmada
                                if entry.get('confirmed', False) or self.base_table[level].get('confirmed', False):
                                    self.base_table[level]['confirmed'] = True

                # Salva dados mesclados
                data = {
                    'base': self.base_table
                }
                with open(self.filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar tabela de XP: {e}")

    def _convert_to_new_format(self, table: Dict) -> Dict:
        """Converte formato antigo (int) para novo formato (dict com xp e confirmed)"""
        converted = {}
        for level, value in table.items():
            if isinstance(value, dict):
                # Já está no novo formato
                converted[level] = value
            else:
                # Formato antigo (apenas int), converte
                converted[level] = {'xp': value, 'confirmed': False}
        return converted

    def update_base_xp(self, level: int, current_xp: int, confirmed: bool = False):
        """
        Atualiza a XP máxima vista para um nível base.
        Sempre pega o maior valor de XP visto para aquele nível.
        confirmed=True indica que este é o valor total do nível (após level up)
        """
        level_key = str(level)

        # Se não existe ou o novo valor é maior, atualiza
        if level_key not in self.base_table or current_xp > self.base_table[level_key]['xp']:
            self.base_table[level_key] = {'xp': current_xp, 'confirmed': confirmed}
            self.save()
            return True
        # Se já existe mas agora está confirmado, atualiza a flag
        elif confirmed and not self.base_table[level_key].get('confirmed', False):
            self.base_table[level_key]['confirmed'] = True
            self.save()
            return True
        return False

    def get_base_xp_required(self, level: int) -> Optional[int]:
        """Retorna a XP necessária para um nível base"""
        entry = self.base_table.get(str(level))
        return entry['xp'] if entry else None

    def get_base_progress(self, current_level: int, current_xp: int, temp_estimate: Optional[int] = None) -> Dict:
        """
        Calcula o progresso do nível atual base
        Prioridade: temp_estimate (manual %) > confirmed
        Retorna: {
            'xp_required': int ou None,
            'xp_remaining': int ou None,
            'percentage': float ou None,
            'confirmed': bool,
            'manual_estimate': bool
        }
        """
        # Busca dados do nível ATUAL, não do próximo
        entry = self.base_table.get(str(current_level))
        
        # Prioridade 1: Estimativa manual (runtime)
        if temp_estimate is not None:
            xp_remaining = temp_estimate - current_xp
            percentage = (current_xp / temp_estimate * 100) if temp_estimate > 0 else 0
            return {
                'xp_required': temp_estimate,
                'xp_remaining': max(0, xp_remaining),
                'percentage': min(100, percentage),
                'confirmed': False,
                'manual_estimate': True
            }
        
        # Prioridade 2: Dados confirmados (ignora observados não confirmados)
        if entry is not None:
            confirmed = entry.get('confirmed', False)
            
            # Apenas usa se estiver confirmado
            if confirmed:
                xp_required = entry['xp']
                xp_remaining = xp_required - current_xp
                percentage = (current_xp / xp_required * 100) if xp_required > 0 else 0

                return {
                    'xp_required': xp_required,
                    'xp_remaining': max(0, xp_remaining),
                    'percentage': min(100, percentage),
                    'confirmed': True,
                    'manual_estimate': False
                }
        
        # Nenhum dado disponível
        return {
            'xp_required': None,
            'xp_remaining': None,
            'percentage': None,
            'confirmed': False,
            'manual_estimate': False
        }

    def get_job_progress(self, current_level: int, current_xp: int, temp_estimate: Optional[int] = None) -> Dict:
        """
        Calcula o progresso do nível atual job
        Prioridade: temp_estimate (manual %)
        Retorna: {
            'xp_required': int ou None,
            'xp_remaining': int ou None,
            'percentage': float ou None,
            'confirmed': bool,
            'manual_estimate': bool
        }
        """
        # Prioridade 1: Estimativa manual (runtime)
        if temp_estimate is not None:
            xp_remaining = temp_estimate - current_xp
            percentage = (current_xp / temp_estimate * 100) if temp_estimate > 0 else 0
            return {
                'xp_required': temp_estimate,
                'xp_remaining': max(0, xp_remaining),
                'percentage': min(100, percentage),
                'confirmed': False,
                'manual_estimate': True
            }
        
        # Nenhum dado disponível
        return {
            'xp_required': None,
            'xp_remaining': None,
            'percentage': None,
            'confirmed': False,
            'manual_estimate': False
        }

    def download_from_github(self) -> bool:
        """Baixa a tabela XP do GitHub"""
        try:
            print(f"Baixando de: {self.GITHUB_XP_TABLE_URL}")
            
            # Baixa o arquivo
            with urllib.request.urlopen(self.GITHUB_XP_TABLE_URL, timeout=10) as response:
                data = response.read().decode('utf-8')
                github_table = json.loads(data)
            
            # Valida estrutura básica
            if 'base' not in github_table:
                print("Erro: Formato inválido do arquivo do GitHub")
                return False
            
            # Se já existe arquivo local, faz merge
            if os.path.exists(self.filename):
                with self.lock:
                    with open(self.filename, 'r', encoding='utf-8') as f:
                        local_table = json.load(f)
                    
                    # Merge: prioriza dados confirmados e maiores valores
                    github_base = self._convert_to_new_format(github_table.get('base', {}))
                    local_base = self._convert_to_new_format(local_table.get('base', {}))
                    
                    for level, github_entry in github_base.items():
                        if level not in local_base:
                            local_base[level] = github_entry
                        else:
                            # Mantém o maior XP
                            if github_entry['xp'] > local_base[level]['xp']:
                                local_base[level]['xp'] = github_entry['xp']
                            # Preserva confirmed se qualquer versão estiver confirmada
                            if github_entry.get('confirmed', False) or local_base[level].get('confirmed', False):
                                local_base[level]['confirmed'] = True
                    
                    # Salva merged
                    merged_table = {'base': local_base}
                    with open(self.filename, 'w', encoding='utf-8') as f:
                        json.dump(merged_table, f, indent=2, ensure_ascii=False)
            else:
                # Não existe local, salva direto do GitHub
                with self.lock:
                    with open(self.filename, 'w', encoding='utf-8') as f:
                        json.dump(github_table, f, indent=2, ensure_ascii=False)
            
            return True
            
        except urllib.error.URLError as e:
            print(f"Erro de rede ao baixar tabela: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON do GitHub: {e}")
            return False
        except Exception as e:
            print(f"Erro ao baixar tabela do GitHub: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas sobre a tabela"""
        return {
            'base_levels_known': len(self.base_table),
            'base_levels': sorted([int(k) for k in self.base_table.keys()])
        }
