# ROLens - Ragnarok Online Lens

![ROLens](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**ROLens** é um monitor em tempo real para Ragnarok Online que rastreia XP, níveis, HP/SP, dano recebido e estatísticas de sessão.

## 🎯 Características

- 📊 **Monitoramento em Tempo Real**: XP Base/Job, HP/SP, níveis
- ⏱️ **Estatísticas de Sessão**: Tempo, monstros mortos, XP/hora, dano/minuto
- 📈 **Progresso de Level**: Porcentagem, XP faltante, tempo estimado para level up
- 🎨 **Interface Moderna**: GUI compacta com cores e organização clara
- 💾 **Tabela XP Automática**: Download e atualização automática do GitHub
- 🔄 **Multi-instância**: Suporta múltiplas janelas do jogo simultaneamente
- 🚀 **Executável Standalone**: Não requer Python instalado

## 📋 Requisitos

### Para Executar o Código Fonte
- Python 3.8 ou superior
- Windows (devido ao uso de APIs do Windows para leitura de memória)
- Privilégios de Administrador (necessário para ler memória de processos)

### Para Usar o Executável
- Windows
- Privilégios de Administrador
- **Nada mais!** O executável é autocontido.

## 🚀 Instalação e Uso

### Opção 1: Baixar Executável (Recomendado)

1. Baixe o arquivo `ROLens.exe` da [página de releases](https://github.com/dev-edilsonmelo/ROLens/releases)
2. Execute como Administrador (clique com botão direito → "Executar como administrador")
3. Pronto! A interface será aberta automaticamente

### Opção 2: Executar do Código Fonte

1. **Clone o repositório**:
```bash
git clone https://github.com/dev-edilsonmelo/ROLens.git
cd ROLens
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute como Administrador**:
```powershell
.\run_gui_admin.ps1
```

## 🔨 Gerar Executável

Se você quiser gerar seu próprio executável:

1. **Instale as dependências de build**:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

2. **Execute o script de build**:
```bash
python build_exe.py
```

3. **O executável será gerado em**:
```
dist/ROLens.exe
```

O processo de build pode levar alguns minutos. O executável final terá aproximadamente 80-100 MB.

## 📖 Como Usar

### 1. Tela Inicial
- **Comunidade WhatsApp**: Entre no grupo para suporte e atualizações
- **Apoie o Projeto**: Contribua via PIX se desejar
- Clique em **"Continuar →"** para prosseguir

### 2. Seleção de Processo
- O ROLens detecta automaticamente processos do Ragnarok Online
- Mostra o nome do personagem e nível (se disponível)
- Selecione o processo desejado e clique em **"Iniciar →"**

### 3. Monitoramento
A tela de monitoramento é dividida em 6 cards:

#### **Personagem**
- Nome do personagem
- Nível Base
- Nível Job

#### **Sessão**
- Tempo de sessão
- Monstros mortos
- Média de XP Base por mob
- Média de XP Job por mob

#### **XP Base**
- XP atual e porcentagem
- XP faltante para próximo nível
- Total de XP necessário
- **Tempo up**: Tempo estimado para level up
- XP/hora

#### **XP Job**
- XP atual e porcentagem
- XP faltante para próximo nível
- **Tempo up**: Tempo estimado para level up
- XP/hora

#### **Combate**
- Monstros mortos
- Dano total recebido
- Dano por minuto

#### **HP / SP**
- HP atual/máximo e porcentagem
- SP atual/máximo e porcentagem

### 4. Botões de Controle

- **Reset (R)**: Reseta todas as estatísticas da sessão
- **% Base (P)**: Define porcentagem manual do nível Base (útil quando não há dados)
- **% Job (J)**: Define porcentagem manual do nível Job
- **↻ XP**: Atualiza a tabela de XP do GitHub (baixa novos dados de níveis)

## 🗂️ Estrutura do Projeto

```
ROLens/
├── gui.py                    # Interface gráfica principal
├── memory_reader.py          # Leitura de memória do jogo
├── stats_calculator.py       # Cálculo de estatísticas
├── xp_table_manager.py       # Gerenciamento da tabela XP
├── build_exe.py              # Script para gerar executável
├── run_gui_admin.ps1         # Script PowerShell para executar como admin
├── requirements.txt          # Dependências Python
├── xp_table.json            # Tabela de XP (criada automaticamente)
└── README.md                # Este arquivo
```

## 🔧 Tabela de XP

A tabela de XP (`xp_table.json`) é gerenciada automaticamente:

- **Primeira execução**: Baixa automaticamente do GitHub
- **Durante o jogo**: Atualiza automaticamente conforme você sobe de nível
- **Atualização manual**: Use o botão **"↻ XP"** para baixar a versão mais recente

### Formato da Tabela
```json
{
  "base": {
    "67": {
      "xp": 1231702,
      "confirmed": false
    }
  }
}
```

- `confirmed: true` = Valor confirmado após level up
- `confirmed: false` = Valor observado mas não confirmado

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você encontrou um bug ou tem uma sugestão:

1. Abra uma [issue](https://github.com/dev-edilsonmelo/ROLens/issues)
2. Faça um fork do projeto
3. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
4. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
5. Push para a branch (`git push origin feature/MinhaFeature`)
6. Abra um Pull Request

## 💰 Apoie o Projeto

Este projeto é gratuito e de código aberto. Se você gostou e quer apoiar o desenvolvimento:

**PIX**: `+5567984085823`

## 📱 Comunidade

Entre no grupo do WhatsApp para:
- Tirar dúvidas
- Compartilhar experiências
- Receber atualizações sobre o ROLens

[Entrar no Grupo WhatsApp](https://chat.whatsapp.com/E7M5Svybe2V1EcTR6S3rPm)

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚠️ Aviso Legal

Este software é fornecido "como está", sem garantias de qualquer tipo. O uso é por sua conta e risco. O ROLens lê a memória do processo do jogo para fins de monitoramento, mas não modifica nenhum dado. Sempre verifique os termos de serviço do seu servidor de Ragnarok Online antes de usar ferramentas de terceiros.

## 🙏 Agradecimentos

- Comunidade Ragnarok Online
- Todos os contribuidores do projeto
- Usuários que reportam bugs e sugestões

---

**Desenvolvido com ❤️ por [Edilson Melo](https://github.com/dev-edilsonmelo)**
