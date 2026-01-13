#!/usr/bin/env python3
"""
ROLens - Interface Gráfica Moderna
Interface gráfica com CustomTkinter para monitoramento do Ragnarok Online
"""

import customtkinter as ctk
import threading
import time
from PIL import Image
import qrcode
from io import BytesIO
import memory_reader
from stats_calculator import StatsCalculator
import os
from datetime import datetime
import logging

# Configura logging em arquivo
try:
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rolens_debug.log')
    # Cria arquivo de log imediatamente
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"=== ROLens Debug Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
except:
    LOG_FILE = 'rolens_debug.log'

def log_debug(message):
    """Escreve mensagem de debug no arquivo de log"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
            f.flush()  # Força escrita imediata
    except Exception as e:
        # Tenta escrever em local alternativo
        try:
            with open('C:\\temp\\rolens_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except:
            pass

class ROLensGUI:
    """Interface gráfica moderna para o ROLens"""
    
    def __init__(self):
        log_debug("=== ROLensGUI.__init__ chamado ===")
        # Configurações do CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        log_debug("CustomTkinter configurado")
        
        # Janela principal
        self.root = ctk.CTk()
        self.root.title("ROLens - Ragnarok Online Lens")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        
        # Variáveis
        self.stats_calculator = StatsCalculator()
        self.selected_pid = None
        self.running = False
        self.update_thread = None
        
        # Criar interface
        self._create_welcome_screen()
        
    def _create_welcome_screen(self):
        """Cria tela de boas-vindas"""
        # Redimensiona para tamanho padrão
        self.root.geometry("385x506")
        self.root.minsize(385, 506)
        
        # Frame principal
        welcome_frame = ctk.CTkFrame(self.root)
        welcome_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título compacto
        title_label = ctk.CTkLabel(
            welcome_frame,
            text="ROLens",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00ffff"
        )
        title_label.pack(pady=(10, 3))
        
        subtitle_label = ctk.CTkLabel(
            welcome_frame,
            text="Monitor de Ragnarok Online",
            font=ctk.CTkFont(size=11)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Container de conteúdo (2 colunas)
        content_frame = ctk.CTkFrame(welcome_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Coluna esquerda - WhatsApp
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))
        
        community_label = ctk.CTkLabel(
            left_frame,
            text="💬 Comunidade WhatsApp",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#25D366"
        )
        community_label.pack(pady=(10, 5))
        
        community_text = ctk.CTkLabel(
            left_frame,
            text="Junte-se ao grupo do WhatsApp!\n\nTire dúvidas, compartilhe\nexperiências e receba\natualizações sobre o ROLens.",
            font=ctk.CTkFont(size=10),
            justify="center"
        )
        community_text.pack(pady=(0, 10))
        
        whatsapp_btn = ctk.CTkButton(
            left_frame,
            text="Entrar no Grupo",
            command=lambda: self._open_url("https://chat.whatsapp.com/E7M5Svybe2V1EcTR6S3rPm"),
            fg_color="#25D366",
            hover_color="#128C7E",
            height=40,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        whatsapp_btn.pack(pady=10, padx=10)
        
        # Coluna direita - PIX
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(3, 0))
        
        support_label = ctk.CTkLabel(
            right_frame,
            text="❤️ Apoie o Projeto",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ff6b6b"
        )
        support_label.pack(pady=(10, 5))
        
        support_text = ctk.CTkLabel(
            right_frame,
            text="Este projeto é gratuito\ne de código aberto!\n\nConsidere apoiar o\ndesenvolvimento via PIX.",
            font=ctk.CTkFont(size=10),
            justify="center"
        )
        support_text.pack(pady=(0, 5))
        
        # PIX
        pix_key_label = ctk.CTkLabel(
            right_frame,
            text="Chave PIX:\n+5567984085823",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#00ff00"
        )
        pix_key_label.pack(pady=5)
        
        # QR Code PIX
        pix_code = "00020101021126460014br.gov.bcb.pix0114+55679840858230206ROLens5204000053039865802BR5925EDILSON PEREIRA DE SOUZA 6008BRASILIA62100506ROLens63047F76"
        qr_image = self._generate_qr_image(pix_code, size=110)
        
        if qr_image:
            qr_label = ctk.CTkLabel(right_frame, image=qr_image, text="")
            qr_label.pack(pady=5)
        
        copy_btn = ctk.CTkButton(
            right_frame,
            text="Copiar Chave PIX",
            command=lambda: self._copy_to_clipboard("+5567984085823"),
            height=30,
            font=ctk.CTkFont(size=10)
        )
        copy_btn.pack(pady=5, padx=10)
        
        # Botão continuar
        continue_btn = ctk.CTkButton(
            welcome_frame,
            text="Continuar →",
            command=self._show_process_selection,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            fg_color="#1a7f64",
            hover_color="#2d9f7f"
        )
        continue_btn.pack(pady=10)
        
    def _generate_qr_image(self, data, size=200):
        """Gera imagem QR code"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((size, size))
            
            return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        except:
            return None
    
    def _copy_to_clipboard(self, text):
        """Copia texto para área de transferência"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        
    def _open_url(self, url):
        """Abre URL no navegador"""
        import webbrowser
        webbrowser.open(url)
        
    def _show_process_selection(self):
        """Mostra tela de seleção de processo"""
        # Limpa tela atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Mantém tamanho padrão
        self.root.geometry("385x506")
        self.root.minsize(385, 506)
            
        # Frame principal
        selection_frame = ctk.CTkFrame(self.root)
        selection_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título compacto
        title_label = ctk.CTkLabel(
            selection_frame,
            text="Selecione o Processo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ffff"
        )
        title_label.pack(pady=(5, 10))
        
        # Lista de processos
        processes = memory_reader.list_processes()
        
        if not processes:
            error_label = ctk.CTkLabel(
                selection_frame,
                text="❌ Nenhum processo encontrado!\n\nInicie o jogo e tente novamente.",
                font=ctk.CTkFont(size=11),
                text_color="red"
            )
            error_label.pack(pady=20)
            
            back_btn = ctk.CTkButton(
                selection_frame,
                text="← Voltar",
                command=self._create_welcome_screen,
                height=32,
                font=ctk.CTkFont(size=11)
            )
            back_btn.pack(pady=10)
            return
        
        # Lê nome do personagem de cada processo
        info_label = ctk.CTkLabel(
            selection_frame,
            text="Lendo informações...",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.pack(pady=3)
        self.root.update()
        
        for proc in processes:
            try:
                game_data = memory_reader.read_game_data(proc['pid'])
                if 'error' not in game_data and 'nome' in game_data and game_data['nome']:
                    proc['char_name'] = game_data['nome']
                    proc['level'] = f"Lv {game_data['nvBase']}/{game_data['nvJob']}"
                else:
                    proc['char_name'] = None
            except:
                proc['char_name'] = None
        
        info_label.destroy()
        
        # Frame para lista
        list_frame = ctk.CTkScrollableFrame(selection_frame, height=360)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Variável para processo selecionado
        selected_var = ctk.StringVar(value=str(processes[0]['pid']))
        
        for proc in processes:
            # Monta texto do radio button
            if proc.get('char_name'):
                text = f"👤 {proc['char_name']} ({proc['level']})"
            else:
                text = f"{proc['name']} (PID: {proc['pid']})"
            
            radio = ctk.CTkRadioButton(
                list_frame,
                text=text,
                variable=selected_var,
                value=str(proc['pid']),
                font=ctk.CTkFont(size=11)
            )
            radio.pack(pady=5, anchor="w")
        
        # Botões
        btn_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        btn_frame.pack(pady=5)
        
        back_btn = ctk.CTkButton(
            btn_frame,
            text="← Voltar",
            command=self._create_welcome_screen,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11)
        )
        back_btn.pack(side="left", padx=5)
        
        start_btn = ctk.CTkButton(
            btn_frame,
            text="Iniciar →",
            command=lambda: self._start_monitoring(int(selected_var.get())),
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
            width=150,
            fg_color="#1a7f64",
            hover_color="#2d9f7f"
        )
        start_btn.pack(side="left", padx=5)
        
    def _start_monitoring(self, pid):
        """Inicia monitoramento"""
        self.selected_pid = pid
        
        # Testa conexão
        initial_data = memory_reader.read_game_data(pid)
        if 'error' in initial_data:
            error_window = ctk.CTkToplevel(self.root)
            error_window.title("Erro")
            error_window.geometry("400x200")
            
            error_label = ctk.CTkLabel(
                error_window,
                text=f"Erro ao conectar: {initial_data['error']}\n\n"
                     "Execute este programa como Administrador!",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=40)
            
            ok_btn = ctk.CTkButton(
                error_window,
                text="OK",
                command=error_window.destroy
            )
            ok_btn.pack(pady=10)
            return
        
        # Inicializa stats
        log_debug(f"=== INICIANDO MONITORAMENTO ===")
        log_debug(f"PID selecionado: {pid}")
        log_debug(f"Dados iniciais: {initial_data}")
        
        self.stats_calculator.initialize(initial_data)
        log_debug("Stats calculator inicializado")
        
        # Cria interface de monitoramento
        self._create_monitoring_screen()
        log_debug("Tela de monitoramento criada")
        
        # Inicia loop de atualização usando after() do Tkinter (thread-safe)
        self.running = True
        log_debug("Iniciando loop de atualização...")
        self._schedule_update()
        log_debug("Loop de atualização agendado")
        
    def _create_monitoring_screen(self):
        """Cria tela de monitoramento"""
        # Limpa tela atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Redimensiona janela para modo compacto (23% menos largura, 25% mais altura)
        self.root.geometry("385x506")
        self.root.minsize(385, 506)
            
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Header com título e botões (2 linhas)
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=5, pady=3)
        
        # Linha 1: Título
        title_label = ctk.CTkLabel(
            header_frame,
            text="ROLens - Monitoramento",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(3, 2))
        
        # Linha 2: Botões de controle
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 3))
        
        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Reset (R)",
            command=self._reset_stats,
            width=60,
            height=22,
            font=ctk.CTkFont(size=9),
            fg_color="#1a4d2e",
            hover_color="#2d7a4f"
        )
        reset_btn.pack(side="left", padx=2)
        
        percentage_base_btn = ctk.CTkButton(
            btn_frame,
            text="% Base (P)",
            command=lambda: self._show_percentage_dialog('base'),
            width=60,
            height=22,
            font=ctk.CTkFont(size=9),
            fg_color="#1a3d5f",
            hover_color="#2d5f8f"
        )
        percentage_base_btn.pack(side="left", padx=2)
        
        percentage_job_btn = ctk.CTkButton(
            btn_frame,
            text="% Job (J)",
            command=lambda: self._show_percentage_dialog('job'),
            width=60,
            height=22,
            font=ctk.CTkFont(size=9),
            fg_color="#5f1a3d",
            hover_color="#8f2d5f"
        )
        percentage_job_btn.pack(side="left", padx=2)
        
        update_xp_btn = ctk.CTkButton(
            btn_frame,
            text="↻ XP",
            command=self._update_xp_table,
            width=45,
            height=22,
            font=ctk.CTkFont(size=9),
            fg_color="#1a5f7f",
            hover_color="#2d8faf"
        )
        update_xp_btn.pack(side="left", padx=2)
        
        # Container para stats (layout 2 colunas x 3 linhas)
        stats_container = ctk.CTkFrame(main_frame)
        stats_container.pack(fill="both", expand=True, padx=5, pady=3)
        
        # Grid 2x3 para cards de stats (igual ao terminal)
        self.stat_cards = {}
        
        # Linha 1: Personagem | Sessão
        self.stat_cards['personagem'] = self._create_stat_card(stats_container, "Personagem", 0, 0)
        self.stat_cards['sessao'] = self._create_stat_card(stats_container, "Sessão", 0, 1)
        
        # Linha 2: XP Base | XP Job
        self.stat_cards['base_xp'] = self._create_stat_card(stats_container, "XP Base", 1, 0)
        self.stat_cards['job_xp'] = self._create_stat_card(stats_container, "XP Job", 1, 1)
        
        # Linha 3: Combate | HP / SP
        self.stat_cards['combate'] = self._create_stat_card(stats_container, "Combate", 2, 0)
        self.stat_cards['hp_sp'] = self._create_stat_card(stats_container, "HP / SP", 2, 1)
        
        
    def _create_stat_card(self, parent, title, row, col):
        """Cria card de estatística com cores do terminal"""
        # Card normal (sem bordas especiais)
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Configura grid
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Título do card (ciano como terminal)
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ffff"
        )
        title_label.pack(pady=(2, 1))
        
        # Frame para conteúdo (permite múltiplos labels com cores)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=4, pady=1)
        
        return content_frame
        
    def _schedule_update(self):
        """Agenda próxima atualização (thread-safe)"""
        if self.running:
            log_debug("_schedule_update chamado")
            self._update_data()
            # Agenda próxima atualização em 1000ms (1 segundo)
            self.root.after(1000, self._schedule_update)
        else:
            log_debug("Loop parado (running=False)")
    
    def _update_data(self):
        """Atualiza dados do jogo (chamado pelo loop do Tkinter)"""
        try:
            log_debug(f"Tentando ler PID: {self.selected_pid}")
            # Lê dados do jogo
            game_data = memory_reader.read_game_data(self.selected_pid)
            
            log_debug(f"Dados recebidos: {game_data}")
            
            if 'error' not in game_data:
                log_debug("Sem erro, atualizando stats...")
                # Atualiza estatísticas
                self.stats_calculator.update(game_data)
                stats = self.stats_calculator.get_stats()
                
                log_debug("Stats obtidas, atualizando UI...")
                # Atualiza interface diretamente (já estamos na thread principal)
                self._update_ui(stats)
                log_debug("UI atualizada com sucesso!")
            else:
                log_debug(f"ERRO ao ler dados: {game_data['error']}")
        except Exception as e:
            log_debug(f"EXCEÇÃO ao atualizar dados: {e}")
            import traceback
            log_debug(traceback.format_exc())
            
    def _update_card_content(self, card_frame, lines):
        """Atualiza conteúdo de um card com linhas coloridas"""
        # Limpa conteúdo anterior
        for widget in card_frame.winfo_children():
            widget.destroy()
        
        # Adiciona cada linha com sua cor
        for text, color in lines:
            label = ctk.CTkLabel(
                card_frame,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color=color,
                anchor="w"
            )
            label.pack(anchor="w", pady=0)
    
    def _update_ui(self, stats):
        """Atualiza interface com novos dados"""
        try:
            current = stats.get('currentData', {})
            base_prog = stats.get('baseProgress', {})
            job_prog = stats.get('jobProgress', {})
            
            # Card Personagem
            nome = current.get('nome', 'Desconhecido')
            nvBase = current.get('nvBase', '?')
            nvJob = current.get('nvJob', '?')
            
            self._update_card_content(self.stat_cards['personagem'], [
                (f"Nome: {nome}", "#00ff00"),  # Verde
                (f"Lv Base: {nvBase}", "#ffff00"),  # Amarelo
                (f"Lv Job: {nvJob}", "#ffff00")  # Amarelo
            ])
            
            # Card Sessão
            tempo = stats.get('sessionTimeFormatted', '00:00:00')
            monstros = stats.get('monstersKilled', 0)
            avg_base_xp = stats.get('avgBaseXPPerMob') or 0
            avg_job_xp = stats.get('avgJobXPPerMob') or 0
            
            self._update_card_content(self.stat_cards['sessao'], [
                (f"Tempo: {tempo}", "#00ffff"),  # Ciano
                (f"Monstros: {monstros}", "#ff0000"),  # Vermelho
                (f"Média Base XP: {avg_base_xp:,}", "#00ff00"),  # Verde
                (f"Média Job XP: {avg_job_xp:,}", "#00ff00")  # Verde
            ])
            
            # Card Base XP
            xp_base = current.get('xpBase') or 0
            falta_base = base_prog.get('xp_remaining') or 0
            perc_base = base_prog.get('percentage') or 0
            total_nv = base_prog.get('xp_required') or 0
            xp_h_base = stats.get('baseXPPerHour') or 0
            
            # Calcula tempo estimado para level up
            if xp_h_base > 0 and falta_base > 0:
                horas_restantes = falta_base / xp_h_base
                segundos_restantes = int(horas_restantes * 3600)
                h = segundos_restantes // 3600
                m = (segundos_restantes % 3600) // 60
                s = segundos_restantes % 60
                tempo_estimado = f"{h:02d}:{m:02d}:{s:02d}"
            else:
                tempo_estimado = "--:--:--"
            
            # Monta linha do XP atual com porcentagem
            if total_nv:
                atual_line = f"Atual: {xp_base:,} ({perc_base:.2f}%)"
            else:
                atual_line = f"Atual: {xp_base:,}"
            
            base_lines = [
                (atual_line, "#ffaa00"),  # Laranja
                (f"Falta: {falta_base:,}", "#00ff00"),  # Verde
                (f"Total Nv: {total_nv:,}", "#ffffff"),  # Branco
                (f"Tempo up: {tempo_estimado}", "#00ffff"),  # Ciano
                (f"XP/h: {xp_h_base:,}", "#00ff00")  # Verde
            ]
            
            self._update_card_content(self.stat_cards['base_xp'], base_lines)
            
            # Card Job XP
            xp_job = current.get('xpJob') or 0
            falta_job = job_prog.get('xp_remaining') or 0
            perc_job = job_prog.get('percentage') or 0
            xp_h_job = stats.get('jobXPPerHour') or 0
            
            # Calcula tempo estimado para level up Job
            if xp_h_job > 0 and falta_job > 0:
                horas_restantes_job = falta_job / xp_h_job
                segundos_restantes_job = int(horas_restantes_job * 3600)
                h_job = segundos_restantes_job // 3600
                m_job = (segundos_restantes_job % 3600) // 60
                s_job = segundos_restantes_job % 60
                tempo_estimado_job = f"{h_job:02d}:{m_job:02d}:{s_job:02d}"
            else:
                tempo_estimado_job = "--:--:--"
            
            # Monta linha do XP atual com porcentagem
            if job_prog.get('xp_required'):
                atual_job_line = f"Atual: {xp_job:,} ({perc_job:.2f}%)"
                job_lines = [
                    (atual_job_line, "#ffaa00"),  # Laranja
                    (f"Falta: {falta_job:,}", "#00ff00"),  # Verde
                    (f"Tempo up: {tempo_estimado_job}", "#00ffff"),  # Ciano
                    (f"XP/h: {xp_h_job:,}", "#00ff00")  # Verde
                ]
            else:
                job_lines = [
                    (f"Atual: {xp_job:,}", "#ffaa00"),  # Laranja
                    ("Coletando...", "#888888")  # Cinza
                ]
            
            self._update_card_content(self.stat_cards['job_xp'], job_lines)
            
            # Card Combate
            mobs = stats.get('monstersKilled') or 0
            dano_total = stats.get('totalDamageTaken') or 0
            dano_min = stats.get('damagePerMinute') or 0
            avg_base_xp = stats.get('avgBaseXPPerMob') or 0
            avg_job_xp = stats.get('avgJobXPPerMob') or 0
            
            self._update_card_content(self.stat_cards['combate'], [
                (f"Mobs: {mobs}", "#ff0000"),  # Vermelho
                (f"Dano Total: {dano_total:,}", "#ffffff"),  # Branco
                (f"Dano/min: {dano_min:,}", "#ffff00")  # Amarelo
            ])
            
            # Card HP / SP
            hp = current.get('hp') or 0
            hpMax = current.get('hpMax') or 1
            sp = current.get('sp') or 0
            spMax = current.get('spMax') or 1
            hp_perc = (hp / hpMax * 100) if hpMax > 0 else 0
            sp_perc = (sp / spMax * 100) if spMax > 0 else 0
            
            # Cor do HP baseada na porcentagem
            hp_color = "#00ff00" if hp_perc > 50 else "#ffff00" if hp_perc > 25 else "#ff0000"
            sp_color = "#00aaff"  # Azul para SP
            
            self._update_card_content(self.stat_cards['hp_sp'], [
                (f"HP: {hp} / {hpMax} ({hp_perc:.0f}%)", hp_color),
                (f"SP: {sp} / {spMax} ({sp_perc:.0f}%)", sp_color)
            ])
            
        except Exception as e:
            print(f"Erro ao atualizar UI: {e}")
            
    def _reset_stats(self):
        """Reseta estatísticas"""
        self.stats_calculator.reset()
    
    def _update_xp_table(self):
        """Atualiza tabela XP do GitHub"""
        # Cria janela de progresso
        progress_window = ctk.CTkToplevel(self.root)
        progress_window.title("Atualizando Tabela XP")
        progress_window.geometry("350x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        status_label = ctk.CTkLabel(
            progress_window,
            text="Baixando tabela XP do GitHub...",
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=30)
        
        progress_window.update()
        
        # Tenta baixar do GitHub
        success = self.stats_calculator.xp_table.download_from_github()
        
        if success:
            # Recarrega a tabela
            self.stats_calculator.xp_table.load()
            status_label.configure(
                text="✓ Tabela XP atualizada com sucesso!",
                text_color="#00ff00"
            )
        else:
            status_label.configure(
                text="❌ Erro ao baixar tabela XP.\nVerifique sua conexão com a internet.",
                text_color="#ff0000"
            )
        
        # Botão OK
        ok_btn = ctk.CTkButton(
            progress_window,
            text="OK",
            command=progress_window.destroy,
            width=100
        )
        ok_btn.pack(pady=10)
        
    def _show_percentage_dialog(self, xp_type='base'):
        """Mostra diálogo para inserir porcentagem"""
        dialog = ctk.CTkToplevel(self.root)
        title = "Inserir Porcentagem Base" if xp_type == 'base' else "Inserir Porcentagem Job"
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        label_text = "Digite a porcentagem atual do nível Base:" if xp_type == 'base' else "Digite a porcentagem atual do nível Job:"
        label = ctk.CTkLabel(
            dialog,
            text=label_text,
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=20)
        
        entry = ctk.CTkEntry(dialog, width=200, placeholder_text="Ex: 45.5")
        entry.pack(pady=10)
        
        def submit():
            try:
                percentage = float(entry.get())
                if 0 < percentage < 100:
                    if xp_type == 'base':
                        success = self.stats_calculator.set_base_xp_estimate_from_percentage(percentage)
                    else:
                        success = self.stats_calculator.set_job_xp_estimate_from_percentage(percentage)
                    
                    if success:
                        dialog.destroy()
                    else:
                        error_label.configure(text="Erro ao definir estimativa!")
                else:
                    error_label.configure(text="Porcentagem deve estar entre 0 e 100!")
            except ValueError:
                error_label.configure(text="Valor inválido!")
        
        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=5)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ok_btn = ctk.CTkButton(btn_frame, text="OK", command=submit, width=100)
        ok_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy, width=100)
        cancel_btn.pack(side="left", padx=5)
        
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()
        self.running = False

def main():
    """Função principal"""
    app = ROLensGUI()
    app.run()

if __name__ == '__main__':
    main()
