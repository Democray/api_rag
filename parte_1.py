from flask import Flask, request, jsonify
import chromadb
from openai import OpenAI
import parte_1  # Importa a preparação dos dados
import parte_2  # Importa a lógica de consulta ao ChromaDB

app = Flask(__name__)

# Inicializando ChromaDB
chroma_client = chromadb.PersistentClient(path="db")
collection = chroma_client.get_or_create_collection(name="artigo")

# Configuração da API Key do OpenAI
client = OpenAI(api_key="SUA_CHAVE_OPENAI_AQUI")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"mensagem": "API está rodando!"})


@app.route("/api/pergunta", methods=["POST"])
def obter_resposta():
    """Recebe uma pergunta e retorna a resposta baseada no banco de dados."""
    data = request.json
    if not data or "pergunta" not in data:
        return jsonify({"erro": "Nenhuma pergunta foi fornecida."}), 400

    questao = data["pergunta"]

    # Busca no banco de dados ChromaDB
    results = collection.query(query_texts=questao, n_results=2)

    if not results or not results["documents"] or not results["documents"][0]:
        return jsonify({"resposta": "Desculpe, mas não consigo ajudar."})

    conteudo = results["documents"][0][0] + results["documents"][0][1]

    prompt = f"""
    Você é um especialista em finanças, matemática e mercado financeiro.
    Use o seguinte contexto para responder à questão, sem adicionar informações externas:
    
    {conteudo}
    
    Se não houver informações suficientes, responda: "Desculpe, mas não consigo ajudar."
    """

    # Fazendo a requisição para a API da OpenAI
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": questao},
        ],
    )

    resposta = completion.choices[0].message.content
    return jsonify({"resposta": resposta})


if __name__ == "__main__":
    app.run(debug=True)
