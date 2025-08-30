# Chatbot Scrum Master com IA  

Este projeto é um assistente de IA para equipes ágeis, capaz de atuar como um Scrum Master e automatizar tarefas como a criação de User Stories, priorização de backlog e facilitação de retrospectivas.  

---

## ✨ Funcionalidades  

O chatbot oferece um menu com as seguintes ferramentas:  

- **Scrum Master:** Guia a equipe, pergunta sobre impedimentos e sugere melhorias.  
- **Gerador de User Stories:** Transforma descrições em histórias de usuário com critérios de aceitação.  
- **Priorizador de Backlog:** Organiza funcionalidades usando a técnica MoSCoW.  
- **Sprint Planning:** Ajuda a estimar pontos para histórias de usuário.  
- **Detector de Impedimentos:** Identifica gargalos em relatórios de Daily Stand-ups.  
- **Retrospectiva:** Ajuda a categorizar feedbacks e sugerir planos de ação.  
- **Cliente Virtual (PO):** Simula um Product Owner para treinar a equipe em negociação.  
- **Gerador de Kanban:** Organiza tarefas em um quadro Kanban.  

---

## 🛠 Tecnologias  

- **Python:** Linguagem principal do projeto.  
- **Flask:** Framework web que atua como o servidor da aplicação.  
- **Google Gemini API:** O motor de inteligência artificial do chatbot.  
- **HTML, CSS, JavaScript:** Tecnologias para a interface do usuário.  

---

## 🚀 Como Usar  

### 1. Instalação  

Abra o terminal na pasta do projeto e instale as dependências:  

```bash
pip install Flask google-generativeai
```
### 2. Configuração

Obtenha sua chave de API no Google AI Studio e configure-a como uma variável de ambiente:

No Windows:

```bash
set GOOGLE_API_KEY=SUA_CHAVE_AQUI
```

No Mac/Linux:

```bash
export GOOGLE_API_KEY="SUA_CHAVE_AQUI"
```

## 3. Execução

Inicie o servidor Flask e acesse o chatbot no navegador:

```bash
python scrum_bot.py
```
Abra http://127.0.0.1:5500 para começar a interagir com o bot.
