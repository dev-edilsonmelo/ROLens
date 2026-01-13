import time
from typing import Dict, Optional
from xp_table_manager import XPTableManager

class StatsCalculator:
    """Calcula estatísticas do jogo (XP/hora, dano/minuto, monstros mortos, etc)"""

    def __init__(self):
        self.start_time = time.time()
        self.last_update = time.time()

        # Dados
        self.initial_data: Optional[Dict] = None
        self.previous_data: Optional[Dict] = None
        self.current_data: Optional[Dict] = None

        # Estatísticas acumuladas
        self.monsters_killed = 0
        self.total_base_xp_gained = 0
        self.total_job_xp_gained = 0
        self.total_damage_taken = 0

        # Histórico
        self.xp_history = []
        self.damage_history = []
        self.max_history_size = 60

        # Gerenciador de tabela de XP
        self.xp_table = XPTableManager()
        
        # Estimativas temporárias (runtime) baseadas em % manual
        self.temp_base_xp_estimate = {}  # {level: xp_total}
        self.temp_job_xp_estimate = {}   # {level: xp_total}

    def initialize(self, game_data: Dict):
        """Inicializa com os primeiros dados do jogo"""
        self.initial_data = game_data.copy()
        self.previous_data = game_data.copy()
        self.current_data = game_data.copy()
        self.start_time = time.time()
        self.last_update = time.time()

    def update(self, game_data: Dict):
        """Atualiza as estatísticas com novos dados"""
        if not self.initial_data:
            self.initialize(game_data)
            return

        self.previous_data = self.current_data.copy()
        self.current_data = game_data.copy()
        self.last_update = time.time()

        # Detecta eventos
        self._detect_xp_gain()
        self._detect_damage_taken()

    def _detect_xp_gain(self):
        """Detecta ganho de XP e conta monstros mortos"""
        base_xp_diff = self.current_data['xpBase'] - self.previous_data['xpBase']
        job_xp_diff = self.current_data['xpJob'] - self.previous_data['xpJob']

        # Detecta evolução de nível (level up)
        base_level_up = self.current_data['nvBase'] > self.previous_data['nvBase']

        # Se evoluiu de nível, salva a XP ANTERIOR como confirmada (XP total do nível)
        if base_level_up:
            # Salva a XP do nível anterior (que estava em previous_data) como confirmada
            self.xp_table.update_base_xp(
                self.previous_data['nvBase'],
                self.previous_data['xpBase'],
                confirmed=True
            )
            # Limpa estimativa temporária do nível anterior
            if self.previous_data['nvBase'] in self.temp_base_xp_estimate:
                del self.temp_base_xp_estimate[self.previous_data['nvBase']]
            # Evolução detectada! XP zerou mas é normal
            base_xp_diff = 0
        else:
            # Atualiza a tabela de XP com o valor atual (não confirmado)
            if base_xp_diff != 0:
                self.xp_table.update_base_xp(
                    self.current_data['nvBase'],
                    self.current_data['xpBase'],
                    confirmed=False
                )

        # Conta apenas ganhos de XP positivos (ignora perdas/zeros)
        if base_xp_diff > 0:
            self.total_base_xp_gained += base_xp_diff
            self.monsters_killed += 1

            self.xp_history.append({
                'baseXP': base_xp_diff,
                'jobXP': job_xp_diff,
                'timestamp': time.time()
            })

            if len(self.xp_history) > self.max_history_size:
                self.xp_history.pop(0)

        if job_xp_diff > 0:
            self.total_job_xp_gained += job_xp_diff

    def _detect_damage_taken(self):
        """Detecta dano recebido"""
        hp_diff = self.previous_data['hp'] - self.current_data['hp']

        if hp_diff > 0:
            self.total_damage_taken += hp_diff

            self.damage_history.append({
                'damage': hp_diff,
                'timestamp': time.time()
            })

            if len(self.damage_history) > self.max_history_size:
                self.damage_history.pop(0)

    def get_stats(self) -> Dict:
        """Retorna todas as estatísticas calculadas"""
        session_time = time.time() - self.start_time
        hours_elapsed = session_time / 3600
        minutes_elapsed = session_time / 60

        # XP por hora
        base_xp_per_hour = int(self.total_base_xp_gained / hours_elapsed) if hours_elapsed > 0 else 0
        job_xp_per_hour = int(self.total_job_xp_gained / hours_elapsed) if hours_elapsed > 0 else 0

        # Dano por minuto
        damage_per_minute = int(self.total_damage_taken / minutes_elapsed) if minutes_elapsed > 0 else 0

        # Média de XP por monstro
        avg_base_xp_per_mob = int(self.total_base_xp_gained / self.monsters_killed) if self.monsters_killed > 0 else 0
        avg_job_xp_per_mob = int(self.total_job_xp_gained / self.monsters_killed) if self.monsters_killed > 0 else 0

        # Progresso de XP (usando a tabela + estimativas temporárias)
        base_progress = self.xp_table.get_base_progress(
            self.current_data['nvBase'],
            self.current_data['xpBase'],
            temp_estimate=self.temp_base_xp_estimate.get(self.current_data['nvBase'])
        )
        job_progress = self.xp_table.get_job_progress(
            self.current_data['nvJob'],
            self.current_data['xpJob'],
            temp_estimate=self.temp_job_xp_estimate.get(self.current_data['nvJob'])
        )

        return {
            'monstersKilled': self.monsters_killed,
            'totalBaseXPGained': self.total_base_xp_gained,
            'totalJobXPGained': self.total_job_xp_gained,
            'totalDamageTaken': self.total_damage_taken,
            'sessionTime': session_time,
            'sessionTimeFormatted': self._format_time(session_time),
            'baseXPPerHour': base_xp_per_hour,
            'jobXPPerHour': job_xp_per_hour,
            'damagePerMinute': damage_per_minute,
            'avgBaseXPPerMob': avg_base_xp_per_mob,
            'avgJobXPPerMob': avg_job_xp_per_mob,
            'currentData': self.current_data,
            'baseProgress': base_progress,
            'jobProgress': job_progress
        }

    def set_base_xp_estimate_from_percentage(self, percentage: float):
        """Define estimativa de XP total baseada na porcentagem atual do nível"""
        if not self.current_data or percentage <= 0 or percentage >= 100:
            return False
        
        current_level = self.current_data['nvBase']
        current_xp = self.current_data['xpBase']
        
        # Calcula XP total estimada: xp_atual / (porcentagem / 100)
        estimated_total_xp = int(current_xp / (percentage / 100))
        self.temp_base_xp_estimate[current_level] = estimated_total_xp
        return True
    
    def set_job_xp_estimate_from_percentage(self, percentage: float):
        """Define estimativa de XP total baseada na porcentagem atual do nível"""
        if not self.current_data or percentage <= 0 or percentage >= 100:
            return False
        
        current_level = self.current_data['nvJob']
        current_xp = self.current_data['xpJob']
        
        # Calcula XP total estimada: xp_atual / (porcentagem / 100)
        estimated_total_xp = int(current_xp / (percentage / 100))
        self.temp_job_xp_estimate[current_level] = estimated_total_xp
        return True

    def _format_time(self, seconds: float) -> str:
        """Formata tempo em HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def reset(self):
        """Reseta todas as estatísticas"""
        self.start_time = time.time()
        self.last_update = time.time()
        self.initial_data = None
        self.previous_data = None
        self.current_data = None
        self.monsters_killed = 0
        self.total_base_xp_gained = 0
        self.total_job_xp_gained = 0
        self.total_damage_taken = 0
        self.xp_history = []
        self.damage_history = []
        self.temp_base_xp_estimate = {}
        self.temp_job_xp_estimate = {}
