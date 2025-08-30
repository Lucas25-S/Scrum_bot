import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, session, send_file
import os
import datetime
import tempfile

app = Flask(__name__)
app.secret_key = os.urandom(24)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não está configurada.")
    print("Visite https://aistudio.google.com/ para obter sua chave.")
    exit()

genai.configure(api_key=api_key)

# --- Prompts e Mensagens de Introdução ---
PROMPTS = {
    "scrum_master": """
    Você é um Scrum Master assistente. Sua função é guiar a equipe em um projeto ágil.
    Lembre o time sobre a Daily Scrum, pergunte sobre impedimentos ("O que te impede?") e
    sugira melhorias no processo de forma profissional e encorajadora.
    """,
    "user_story_generator": """
    Você é um gerador de User Stories. Sua tarefa é transformar uma descrição de funcionalidade
    em uma User Story no formato 'Como [persona], quero [funcionalidade], para [benefício]'.
    Para cada história, sugira 2-3 critérios de aceitação detalhados. Se a descrição for
    muito curta, peça mais informações.
    """,
    "backlog_prioritizer": """
    Você é um especialista em priorização de backlog. Receberá uma lista de funcionalidades
    com seus critérios de priorização (ex.: valor de negócio, esforço, risco).
    Ajude a organizar o backlog aplicando a técnica MoSCoW (Must, Should, Could, Won't).
    Peça os dados se não forem fornecidos.
    """,
    "sprint_planning": """
    Você é um assistente de Sprint Planning. Sua função é ajudar o time a estimar histórias de usuário
    em pontos (como no Planning Poker). Peça à equipe para listar suas user stories e,
    para cada uma, sugira uma estimativa de pontos (ex: 1, 2, 3, 5, 8, 13). Explique brevemente o
    raciocínio por trás da sua sugestão.
    """,
    "impediment_detector": """
    Você é um detector de impedimentos. Receberá um relato de uma Daily Stand-up.
    Identifique padrões de problemas recorrentes, gargalos ou dependências problemáticas.
    Sua resposta deve listar os impedimentos detectados e sugerir o próximo passo para o Scrum Master.
    """,
    "retrospective_facilitator": """
    Você é um facilitador de retrospectivas. Ajude o time a processar feedbacks de uma sprint.
    Organize os pontos em categorias claras (Start, Stop, Continue) e, para cada categoria,
    sugira 1 a 2 planos de ação concretos e acionáveis.
    """,
    "virtual_po": """
    Você é um Product Owner (PO) virtual. Sua função é simular a interação com uma equipe de desenvolvimento.
    Seja exigente, peça por mais detalhes nos requisitos, esclareça dúvidas e valide as entregas com a equipe.
    Mantenha um tom profissional, mas direto, focado no valor do produto.
    """,
    "kanban_generator": """
    Você é um gerador de quadro Kanban. Sua tarefa é pegar uma lista de tarefas e organizá-las
    automaticamente em um quadro Kanban. Use as colunas 'A Fazer' (To Do), 'Em Progresso' (In Progress) e
    'Feito' (Done). Para cada tarefa, atribua uma coluna e explique por que a categorizou assim.
    """
}

INTRO_MESSAGES = {
    "menu": """Olá! Sou um chatbot para Métodos Ágeis. Por favor, escolha uma opção para começar:
1. Chatbot Scrum Master
2. Gerador de User Stories
3. Priorizador de Backlog
4. Assistente de Sprint Planning
5. Detector de Impedimentos
6. Facilitador de Retrospectivas
7. Simulação de Cliente Virtual (PO)
8. Gerador de Kanban
    """,
    "scrum_master": "Ótimo! Modo Scrum Master ativado. Diga-me como posso ajudar a sua equipe hoje.",
    "user_story_generator": "Excelente! Modo Gerador de User Stories ativado. Descreva a funcionalidade que você quer que eu transforme em uma User Story.",
    "backlog_prioritizer": "Certo. Modo Priorizador de Backlog ativado. Liste as funcionalidades com seus critérios de priorização.",
    "sprint_planning": "Pronto para o planejamento? Modo Sprint Planning ativado. Liste as user stories para que eu sugira estimativas de pontos.",
    "impediment_detector": "Modo Detector de Impedimentos ativado. Por favor, envie o registro de uma Daily Stand-up para que eu identifique os problemas.",
    "retrospective_facilitator": "Modo Retrospectiva ativado. Envie os feedbacks da sprint. Eu os organizarei em 'Start', 'Stop', 'Continue'.",
    "virtual_po": "Simulação de Cliente ativada. Pode me chamar de PO. Me diga o que sua equipe precisa para começar.",
    "kanban_generator": "Modo Gerador de Kanban ativado. Envie a lista de tarefas, e eu as organizarei em um quadro."
}

def get_response_from_model(user_message, selected_prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=selected_prompt)
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        print(f"Erro na API: {e}")
        return "Desculpe, a IA está offline ou encontrou um erro. Tente novamente mais tarde."

@app.route("/")
def home():
    session['mode'] = "menu"
    # Cria arquivo temporário para histórico se não existir
    if "history_file" not in session:
        temp = tempfile.NamedTemporaryFile(delete=False, mode="a+", encoding="utf-8", suffix=".txt")
        session["history_file"] = temp.name
        temp.close()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["mensagem"].strip()
    
    # Salva a mensagem do usuário no histórico
    history_file = session.get("history_file")
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"Você: {user_message}\n")

    if session.get('mode') == "menu":
        try:
            choice = int(user_message)
            if 1 <= choice <= 8:
                modes = list(PROMPTS.keys())
                selected_mode = modes[choice - 1]
                session['mode'] = selected_mode
                bot_response = INTRO_MESSAGES.get(selected_mode, "Modo desconhecido.")
            else:
                bot_response = "Opção inválida. Por favor, escolha um número de 1 a 8."
        except ValueError:
            bot_response = "Opção inválida. Por favor, digite o número da sua escolha."
    else:
        selected_mode = session.get('mode')
        prompt = PROMPTS.get(selected_mode)

        if user_message.lower() == "menu":
            session['mode'] = "menu"
            bot_response = INTRO_MESSAGES["menu"]
        elif not prompt:
            bot_response = "Erro: modo de IA não reconhecido. Digite 'menu' para voltar."
        else:
            bot_response = get_response_from_model(user_message, prompt)
    
    # Salva a resposta do bot no histórico
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"Scrum Master IA: {bot_response}\n")
    
    return jsonify({"resposta": bot_response})

@app.route("/save_chat")
def save_chat():
    history_file = session.get("history_file")
    if not history_file or not os.path.exists(history_file):
        return "Nenhuma conversa encontrada.", 404
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"conversa_chatbot_{now}.txt"
    return send_file(history_file, as_attachment=True, download_name=file_name)

if __name__ == "__main__":
    app.run(debug=True, port=5500)