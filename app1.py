from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
import os

# Inicializa o Flask
app = Flask(__name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Cria o diretório de uploads, se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se o arquivo de imagem tem a extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função que gera o crachá
def gerar_cracha(nome, campus, matricula, rg, modalidade, foto_path, x_offset, y_offset, c):
    # Desenhando a foto primeiro, centralizada
    foto_x = x_offset + 60  # Posição X centralizada
    c.drawImage(foto_path, foto_x, y_offset + 250, width=85, height=113)  # Foto 3x4, centralizada sobre os campos

    # Desenhando a palavra "ATLETA" abaixo da foto
    c.setFont("Helvetica-Bold", 20)
    c.drawString(x_offset + 50, y_offset + 220, "ATLETA")  # Ajustando a posição de "ATLETA" abaixo da foto

    c.setFont("Helvetica-Bold", 12)

    # Função para desenhar os campos com bordas arredondadas
    def draw_field(label, text, y_position):
        c.setFillColorRGB(1, 1, 1)  # Cor de fundo branca
        c.roundRect(x_offset + 50, y_position, 200, 20, 5, fill=1)  # Retângulo com bordas arredondadas
        c.setFillColorRGB(0, 0, 0)  # Cor do texto (preto)
        c.drawString(x_offset + 60, y_position + 4, f"{text.upper()}")  # Texto em maiúsculas

    # Função para centralizar o nome dos campos
    def draw_centered_text(label, y_position):
        # Calculando a largura do texto e centralizando
        text_width = c.stringWidth(label, "Helvetica-Bold", 12)
        x_position = x_offset + (200 - text_width) / 2  # Centralizando com base na largura do campo
        c.drawString(x_position, y_position, label)

    # Posicionamento dos campos (Ajustando a posição dos campos abaixo de "ATLETA")
    draw_centered_text("CAMPUS", y_offset + 190)
    draw_field("", campus, y_offset + 170)

    draw_centered_text("NOME", y_offset + 150)
    draw_field("", nome, y_offset + 130)

    draw_centered_text("RG", y_offset + 110)
    draw_field("", rg, y_offset + 90)

    draw_centered_text("MATRÍCULA", y_offset + 70)
    draw_field("", matricula, y_offset + 50)

    draw_centered_text("MODALIDADE", y_offset + 30)
    draw_field("", modalidade, y_offset + 10)

# Função que gera o PDF com os crachás
def gerar_pdf_com_crachas(alunos):
    nome_arquivo = "crachas.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=letter)
    
    largura, altura = letter
    # Definindo o espaçamento para dois crachás (1 por coluna)
    largura_crachas = largura / 2  # Cada crachá ocupará metade da largura da folha
    
    # Ajuste da posição para os dois crachás
    x_offset = 50  # Deslocamento X para o primeiro crachá
    y_offset = altura - 400  # Deslocamento Y para o primeiro crachá, garantindo que não fique cortado

    # Gerar os dois crachás
    for i, aluno in enumerate(alunos[:2]):  # Limitando para 2 alunos
        nome, campus, matricula, rg, modalidade, foto_path = aluno
        
        # Ajustar as posições X e Y dependendo do índice (esquerda ou direita)
        x = i * largura_crachas + x_offset  # Colocando o primeiro crachá à esquerda e o segundo à direita
        y = altura - 400  # Mantendo o Y fixo para a linha superior
        
        gerar_cracha(nome, campus, matricula, rg, modalidade, foto_path, x, y, c)
    
    c.save()  # Salva o arquivo PDF
    return nome_arquivo

# Rota para exibir o formulário de cadastro de alunos
@app.route('/', methods=['GET', 'POST'])
def cadastrar_alunos():
    if request.method == 'POST':
        alunos = []
        
        for i in range(2):  # Limitar para 2 alunos
            nome = request.form[f'nome_{i+1}']
            campus = request.form[f'campus_{i+1}']
            matricula = request.form[f'matricula_{i+1}']
            modalidade = request.form[f'modalidade_{i+1}']
            rg = request.form[f'rg_{i+1}']
            
            foto = request.files[f'foto_{i+1}']
            if foto and allowed_file(foto.filename):
                foto_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(foto.filename))
                foto.save(foto_path)
            else:
                foto_path = ''
            
            alunos.append((nome, campus, matricula, rg, modalidade, foto_path))
        
        # Gerar o PDF com os crachás
        nome_arquivo = gerar_pdf_com_crachas(alunos)
        
        # Enviar o arquivo PDF gerado para o usuário fazer o download
        return send_file(nome_arquivo, as_attachment=True)

    return render_template('index1.html')  # Renderiza o template 'index1.html'

# Executar o app
if __name__ == "__main__":
    app.run(debug=True)
