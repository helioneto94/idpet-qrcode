from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
import os
import zipfile

app = Flask(__name__)

# DEFINIR URL http://idpet.ong.br/?id=1000
# DEFINIR URL https://idpet.ong.br/t/código

#urlFixa = "http://idpet.ong.br/?id="
urlFixa = "https://idpet.ong.br/t/"

# INTERVALO DE INICIO E FIM; VARIAVEL PARA CÓDIGO UNICO (inicializando todas com zero)
inicio = fim = codigoUnico = 0

# CRIAR VALIDAÇÃO SE VAI HAVER LOOPING (DEFINIR LIMITE MAXIMO DE CODIGOS DE UMA VEZ?)
gerarSoUmCodigo = False

# Pasta onde os arquivos são armazenados
DOWNLOAD_FOLDER = './downloads'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

#Função para limpar a pasta antes de gerar novos QR Codes.
#Remove todos os arquivos dentro da pasta especificada.
#Se a pasta não existir, cria ela. 
#Parametro (str): caminho da pasta, no caso 'downloads' (./downloads)
def limpar_pasta(pasta):
    try:
        # Verifica se a pasta existe, e cria caso não exista
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"Pasta '{pasta}' não existia, foi criada.")
            return  # Não há arquivos para apagar

        # Lista todos os itens da pasta
        for item in os.listdir(pasta):
            caminho_item = os.path.join(pasta, item)

            # Remove apenas arquivos
            if os.path.isfile(caminho_item):
                os.remove(caminho_item)
                print(f"Arquivo removido: {caminho_item}")
            else:
                print(f"Ignorado (não é arquivo): {caminho_item}")

        print(f"Todos os arquivos da pasta '{pasta}' foram removidos.")
    except Exception as e:
        print(f"Ocorreu um erro ao limpar a pasta: {e}")

# Função que gera o QR code e armazena na pasta downloads
def gerarQrCode(id):

    id = str(id)
    url = urlFixa + id

    doCaption = 1
    fontFile = 'static/fonts/arial.ttf'
    fontName = 'arial.ttf'
    qrName = "id-"+ id
    boxPixels = 5 #padrão 10
    imageExt = '.png'

    qrLabel = f'TAG {id}'

    # cria a instancia do qrcode
    qr = qrcode.QRCode()

    # Adiciona os dados ao qrcode
    qr.box_size = int(boxPixels)
    qr.add_data(url)
    qr.make(fit=False)

    # depois que tira o while, a fontHeightMax nao é mais usada
    fontHeightMax = qr.border * qr.box_size - 35

    # cria uma imagem a partir da instacia do qrcode
    img = qr.make_image()


    # Are we adding a caption?
    if doCaption:
        draw = ImageDraw.Draw(img)
        QRwidth, QRheight = img.size
        print(f'-------QRwidth ={QRwidth} QRheight (vertical) ={QRheight}-------')

        fontSize = 15 #starting font size antes era 20
        captionX = 0 #HORIZONTAL
        captionY = 0 #VERTICAL
        
        # depois que tira o while, a img_fraction nao é mais usada
        img_fraction = 0.90 # portion of image width you want text width to be, I've had good luck with .90

        try:
             # Garantir que qrLabel seja string
            qrLabel = str(qrLabel)
            font = ImageFont.truetype(fontFile, fontSize)
            
            # ESSE WHILE NEM É USADO
            # while captionX < img_fraction * QRwidth and captionY < fontHeightMax:
            #     fontSize += 1
            #     font = ImageFont.truetype(fontFile, fontSize)
            #     # Obtém as dimensões do texto
            #     captionX, captionY = font.getbbox(qrLabel)[2], font.getbbox(qrLabel)[3]
            #     print(f'------- antes X (horizontal) ={captionX} Y (vertical) ={captionY}-------')

            print(f'-------antes X (horizontal) ={captionX} Y (vertical) ={captionY}-------')
            captionX = int(QRwidth - font.getbbox(qrLabel)[2]) / 2 #Center the label
            print(f'-------meio X (horizontal) ={captionX} Y (vertical) ={captionY}-------')
            # print('Posição X (horizontal): ' + str(captionX))

            # captionX = 18
            # captionY = captionY + 285 #para boxPixels 10
            captionY = captionY + 145



            #adiciona +20 pixels para baixo para compensar o aumento do qrcode quando o numero é maior que 99
            if (int(id) > 99): 
                captionY = captionY + 20

            print(f'-------depois X (horizontal) ={captionX} Y (vertical) ={captionY}-------') #auxiliar para ajustar a posição da legenda
            draw.text((captionX, captionY), qrLabel, font=font)


            # Redimensionar a imagem
            img = img.convert("RGB")
            new_size = (185, 185)  # Define as novas dimensões (largura, altura)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f'-------QRwidth ={QRwidth} QRheight (vertical) ={QRheight}-------')

            # Save it somewhere, change the extension as needed:
            img.save(DOWNLOAD_FOLDER + "/" + str(qrName) + imageExt)
            print('******* QR Code Salvo com sucesso como:  ' + str(qrName) + imageExt + ' *******')

        except OSError as e:
            print(f"!!!!!!!!!!!!!! Erro ao carregar a fonte: {e} !!!!!!!!!!!!!!")

# def gerarQrCode(id):

#     id = str(id)
#     url = urlFixa + id

#     fontFile = 'static/fonts/arial.ttf'
#     qrName = "id-" + id
#     boxPixels = 5  # Tamanho fixo do box
#     borderSize = 4  # Tamanho fixo da borda
#     imageExt = '.png'

#     qrLabel = "TESTE VARIOS " + id

#     # Cria a instância do QRCode
#     qr = qrcode.QRCode(
#         box_size=boxPixels,
#         border=borderSize,  # Borda fixa para garantir o tamanho constante
#     )

#     # Adiciona os dados ao QR Code
#     qr.add_data(url)
#     qr.make(fit=False)  # Garante que o tamanho do QR Code seja constante

#     # Cria a imagem do QR Code
#     qr_image = qr.make_image().convert("RGB")
#     QRwidth, QRheight = qr_image.size

#     # Configuração da fonte e cálculo do espaço para a legenda
#     fontSize = 15
#     try:
#         font = ImageFont.truetype(fontFile, fontSize)
#     except OSError as e:
#         print(f"Erro ao carregar a fonte: {e}")
#         return

#     # Calcula as dimensões do texto
#     draw = ImageDraw.Draw(qr_image)
#     text_bbox = draw.textbbox((0, 0), qrLabel, font=font)
#     text_width = text_bbox[2] - text_bbox[0]
#     text_height = text_bbox[3] - text_bbox[1]

#     # Cria uma nova imagem maior para incluir a legenda
#     padding = 10  # Espaço entre o QR Code e a legenda
#     total_height = QRheight + text_height + padding
#     img_with_label = Image.new("RGB", (QRwidth, total_height), "white")

#     # Adiciona o QR Code na nova imagem
#     img_with_label.paste(qr_image, (0, 0))

#     # Calcula a posição do texto e desenha na imagem final
#     captionX = (QRwidth - text_width) // 2  # Centraliza horizontalmente
#     captionY = QRheight + padding  # Posiciona logo abaixo do QR Code
#     draw = ImageDraw.Draw(img_with_label)
#     draw.text((captionX, captionY), qrLabel, font=font, fill="black")

#     # Salva a imagem
#     img_with_label.save(DOWNLOAD_FOLDER + "/" + str(qrName) + imageExt)
#     print('******* QR Code Salvo com sucesso como:  ' + str(qrName) + imageExt + ' *******')


# Variáveis que o frontend poderá acessar
data_store = {"inicio": str(inicio), "fim": str(fim), "urlFixa":urlFixa, "codigoUnico":codigoUnico, "gerarSoUmCodigo":str(gerarSoUmCodigo)}
    
#Função para checar os valroes das variáveis. Usado somente para testes
def checarVariaveis(data_store):
    print(data_store)

    inicio = int(data_store['inicio'])
    fim = int(data_store['fim'])
    codigoUnico = int(data_store['codigoUnico'])
    urlFixa = data_store['urlFixa']
    gerarSoUmCodigo = data_store['gerarSoUmCodigo']

    print(f'VAR inicio:  {inicio}')
    print(f'VAR fim:  {fim}')
    print(f'VAR codigoUnico:  {codigoUnico}')
    print(f'VAR urlFixa:  {urlFixa}')
    print(f'VAR gerarSoUmCodigo:  {gerarSoUmCodigo}')

#Request inicial da página
@app.route('/')
def index():
    return render_template('index.html')

#Request que retorna as variáveis para o frontend
@app.route('/get-data', methods=['GET'])
def get_data():
    # checarVariaveis(data_store)
    return jsonify(data_store)
    
#Request para geração de QR Code com base no pedido do usuário
@app.route('/gerar-qr', methods=['POST'])
def solicitarGeracao():    
    # Atualiza as variáveis com os dados enviados pelo frontend.
    global data_store

    # Recebe dados em JSON do frontend
    new_data = request.json 
    
    # Popula a data_store com as informçãoes recebidas no JSON (new_data) se elas existirem
    if 'inicio' in new_data:
        data_store['inicio'] = new_data['inicio']
    if 'fim' in new_data:
        data_store['fim'] = new_data['fim']
    if 'codigoUnico' in new_data:
        data_store['codigoUnico'] = new_data['codigoUnico']
    if 'gerarSoUmCodigo' in new_data:
        data_store['gerarSoUmCodigo'] = new_data['gerarSoUmCodigo']
    if 'urlFixa' in new_data:
        data_store['urlFixa'] = new_data['urlFixa']

    # Joga esses valores para variáveis auxiliares para facilitar o manuseio delas
    inicio = int(data_store['inicio'])
    fim = int(data_store['fim'])
    codigoUnico = int(data_store['codigoUnico'])
    urlFixa = data_store['urlFixa']

    # Primeiro limpa a pasta 'downloads' antes de gerar os novos qrcodes
    limpar_pasta(DOWNLOAD_FOLDER)

   # Pega a resposta do front-end, transforma em boolean e adiciona para variavel auxTrueFalse
    if data_store['gerarSoUmCodigo'] == 'true':
        auxTrueFalse = True
    else:
        auxTrueFalse = False

    if auxTrueFalse:
        idQr = codigoUnico
        urlQr = urlFixa + str(idQr)
        gerarQrCode(idQr)
        print(f'URL GERADA: {urlQr}')
    else:
        # CHECAR SE O INÍCIO É MAIOR QUE O FIM,E TROCAR ENTRE ELES
        if(inicio > fim):
            aux = fim
            fim = inicio
            inicio= aux

        # GERAR FUNÇÃO PARA LOOPING COM INTERVALO
        for idQr in range(inicio, fim+1):
            urlQr = urlFixa + str(idQr)
            # GERAR e SALVAR QRCODE
            gerarQrCode(idQr)
            print(f'URL GERADA: {urlQr}')
    
    return jsonify({"status": "sucesso", "data": data_store})

#Request que retorna qual o host para frontend para as funções serem disparadas para o endereço correto 
@app.route('/get-host', methods=['GET'])
def get_host():
    return jsonify({'host': request.host_url.strip('/')})

#Request de download de arquivo único
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Enviar o arquivo solicitado
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

#Request de criação e envio de download de arquivo .zip    
@app.route('/download-zip', methods=['POST'])
def download_zip():
    try:
        # Lista de arquivos que o cliente quer incluir no ZIP
        files_to_zip = request.json.get('files', [])

        if not files_to_zip:
            return jsonify({'error': 'Nenhum arquivo selecionado para zipar.'}), 400

        # Cria um buffer em memória para armazenar o ZIP
        zip_buffer = BytesIO()

        # Cria o arquivo ZIP
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in files_to_zip:
                file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_name)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=file_name)
                else:
                    return jsonify({'error': f'O arquivo {file_name} não existe.'}), 400

        zip_buffer.seek(0)

        # Retorna o arquivo ZIP para download
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name='arquivos.zip',
            mimetype='application/zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')