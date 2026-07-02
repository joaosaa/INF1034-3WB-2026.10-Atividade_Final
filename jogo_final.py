import pygame, sys

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Deepstrand")

tempo_ultimo_dano = 0

pygame.mixer.music.load("sounds/TRILHA SONORA/Soundtrack.mp3")
pygame.mixer.music.set_volume(0.090)
pygame.mixer.music.play(-1)


pygame.mixer.set_num_channels(16)

som_passos = pygame.mixer.Sound("sounds/PASSOS NA PEDRA/PASSO.mpeg")
som_pulo = pygame.mixer.Sound("sounds/PULO/jump.mp3")
som_moeda = pygame.mixer.Sound("sounds/COLETAR MOEDA/Picked Coin Echo.wav")
som_aterrissagem = pygame.mixer.Sound("sounds/ATERRISSAGEM (LANDING AFTER JUMP)/ATERRISSAGEM.mpeg")
som_siri = pygame.mixer.Sound("siri.mp3")
som_lagosta = pygame.mixer.Sound("lagosta.mp3")

som_passos.set_volume(0.4)

# canal 1 é só dos passos, canal 2 é só do som de matar inimigo.
# assim um som nunca corta o outro.
canal_passos = pygame.mixer.Channel(1)
canal_inimigos = pygame.mixer.Channel(2)

def tocar_som_do_inimigo(tipo):
    if tipo == "caranguejo":
        canal_inimigos.play(som_siri)
    elif tipo == "lagosta":
        canal_inimigos.play(som_lagosta)

def atualizar_sistema_sonoro(jogador_movendo):
    if jogador_movendo:
        if not canal_passos.get_busy():
            canal_passos.play(som_passos, loops=-1)
    else:
        canal_passos.stop()

# SISTEMA DE HUD, PONTUAÇÃO E REGRAS (LUIGI)
pygame.font.init()
fonte_hud = pygame.font.SysFont("courier", 35, bold=True)
fonte_telas = pygame.font.SysFont("courier", 90, bold=True)

pontuacao = 0
coracoes = 3
vida_atual = 100
vida_maxima = 100

estado_jogo = "MENU"

# VARIÁVEIS DO MENU, NOME DO JOGADOR E RANKING (LUIGI)
nome_jogador = ""
pontuacao_salva = False
arquivo_ranking = "ranking.txt"

opcoes_menu = ["Jogar", "Sair"]
menu_selecionado = 0

boss_morto = False
tempo_queda = 0

# IMAGEM BOLHA (LUIGI)
img_bolha = pygame.image.load("coracao bolha.png")
img_bolha = pygame.transform.scale(img_bolha, (30, 30))
img_bolha.set_colorkey((255, 255, 255))

# IMAGEM DE FUNDO DO MENU (LUIGI)
img_fundo_menu = pygame.image.load("tela_inicial.png")
img_fundo_menu = pygame.transform.scale(img_fundo_menu, (1280, 720))

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# FUNÇÕES DO RANKING: ORDENAR, CARREGAR E SALVAR A PONTUAÇÃO (LUIGI)
def ordenar_ranking(lista):
    for i in range(len(lista)):
        for j in range(len(lista) - 1 - i):
            if lista[j][1] < lista[j + 1][1]:
                temporario = lista[j]
                lista[j] = lista[j + 1]
                lista[j + 1] = temporario
    return lista

def carregar_ranking():
    lista = []
    try:
        arquivo = open(arquivo_ranking, "r")
        linhas = arquivo.readlines()
        arquivo.close()
        for linha in linhas:
            partes = linha.strip().split(",")
            if len(partes) == 2:
                lista.append((partes[0], int(partes[1])))
    except FileNotFoundError:
        lista = []
    lista = ordenar_ranking(lista)
    return lista[:5]

def salvar_pontuacao(nome, pontos):
    lista = carregar_ranking()
    lista.append((nome, pontos))
    lista = ordenar_ranking(lista)
    lista = lista[:5]
    arquivo = open(arquivo_ranking, "w")
    for item in lista:
        arquivo.write(item[0] + "," + str(item[1]) + "\n")
    arquivo.close()

#spritesheet
spritesheet_andar = pygame.image.load('Characters/spritesheet_andar.png').convert_alpha()
largura_total = spritesheet_andar.get_width()
frame_h = spritesheet_andar.get_height()
escala = 0.64

num_frames = 7
frame_w_fixo = largura_total // num_frames

frames_andar = []
for i in range(num_frames):
    x_inicio = i * frame_w_fixo
    frame = pygame.Surface((frame_w_fixo, frame_h), pygame.SRCALPHA)
    frame.blit(spritesheet_andar, (0, 0), (x_inicio, 0, frame_w_fixo, frame_h))
    frame = pygame.transform.scale(frame, (int(frame_w_fixo * escala), int(frame_h * escala)))
    frames_andar.append(frame)

personagem_parado = frames_andar[0]

#spritesheet de pulo
spritesheet_pular = pygame.image.load('Characters/spritesheet_pular.png').convert_alpha()
largura_pular = spritesheet_pular.get_width()
frame_h_pular = spritesheet_pular.get_height()
escala_pular = 0.40

num_frames_pular = 7
frame_w_fixo_pular = largura_pular // num_frames_pular

frames_pular = []
for i in range(num_frames_pular):
    x_inicio = i * frame_w_fixo_pular
    frame = pygame.Surface((frame_w_fixo_pular, frame_h_pular), pygame.SRCALPHA)
    frame.blit(spritesheet_pular, (0, 0), (x_inicio, 0, frame_w_fixo_pular, frame_h_pular))
    frame = pygame.transform.scale(frame, (int(frame_w_fixo_pular * escala_pular), int(frame_h_pular * escala_pular)))
    frames_pular.append(frame)

frame_atual = 0
contador_frames = 0
intervalo_frame = 9

# spritesheet caranguejo
spritesheet_caranguejo = pygame.image.load('Characters/caranguejo.png').convert_alpha()
largura_caranguejo = spritesheet_caranguejo.get_width()
altura_caranguejo = spritesheet_caranguejo.get_height()
num_frames_caranguejo = 7
frame_w_caranguejo = largura_caranguejo // num_frames_caranguejo

frames_caranguejo = []
for i in range(num_frames_caranguejo):
    frame = pygame.Surface((frame_w_caranguejo, altura_caranguejo), pygame.SRCALPHA)
    frame.blit(spritesheet_caranguejo, (0, 0), (i * frame_w_caranguejo, 0, frame_w_caranguejo, altura_caranguejo))
    frame = pygame.transform.scale(frame, (int(frame_w_caranguejo * 0.35), int(altura_caranguejo * 0.35)))
    frames_caranguejo.append(frame)

# spritesheet lagosta
spritesheet_lagosta = pygame.image.load('Characters/lagosta.png').convert_alpha()
largura_lagosta = spritesheet_lagosta.get_width()
altura_lagosta = spritesheet_lagosta.get_height()
num_frames_lagosta = 7
frame_w_lagosta = largura_lagosta // num_frames_lagosta
frames_lagosta = []
for i in range(num_frames_lagosta):
    x_inicio = i * frame_w_lagosta
    frame = pygame.Surface((frame_w_lagosta, altura_lagosta), pygame.SRCALPHA)
    frame.blit(spritesheet_lagosta, (0, 0), (x_inicio, 0, frame_w_lagosta, altura_lagosta))
    frame = pygame.transform.scale(frame, (int(frame_w_lagosta * 0.45), int(altura_lagosta * 0.45)))
    frames_lagosta.append(frame)

# spritesheet boss
spritesheet_boss = pygame.image.load('Characters/boss_final.png').convert_alpha()
largura_boss = spritesheet_boss.get_width()
altura_boss = spritesheet_boss.get_height()
num_frames_boss = 5
frame_w_boss = largura_boss // num_frames_boss
espaco = 10 
frames_boss = []
for i in range(num_frames_boss):
    x_inicio = i * frame_w_boss
    frame = pygame.Surface((frame_w_boss - espaco, altura_boss),  pygame.SRCALPHA)
    frame.blit(spritesheet_boss, (0, 0), (x_inicio, 0, frame_w_boss - espaco, altura_boss))
    frame = pygame.transform.scale(frame, (int(frame.get_width() * 1), int(frame.get_height() * 1)))
    frames_boss.append(frame)

#background
camadas = []
velocidades = [0.05, 0.15, 0.25, 0.4]
for i in range(4, 0, -1):
    img = pygame.image.load(f'Background/ParallaxCave{i}.png').convert()
    img = pygame.transform.scale(img, (1280, 720))
    img.set_colorkey((0, 0, 0))
    camadas.append(img)

#tileset
TILE = 64
tileset_raw = pygame.image.load('cave16.png').convert_alpha()

def get_tile(col, lin):
    tile = pygame.Surface((16, 16), pygame.SRCALPHA)
    tile.blit(tileset_raw, (0, 0), (col * 16, lin * 16, 16, 16))
    return pygame.transform.scale(tile, (TILE, TILE))

t_topo = get_tile(1, 0)
t_fill = get_tile(1, 4)

# MOEDA
moeda_raw = pygame.image.load('moeda.png').convert_alpha()
t_moeda = pygame.transform.scale(moeda_raw, (TILE, TILE))

mapa = [
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                          PPP                                 ",
    "                PP     PP              M  PPP        PPP      ",
    " M         M                M      PP              M          ",
    "CCCCCCCCCCCCCC   CCCCCCCCCCCCCCC       CCCCCCCCCCCCCCCCCCCCCCC",
    "DDDDDDDDDDDDDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDDDDDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDDDDDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDDDDDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDDDDD",
]

largura_mapa = max(len(linha) for linha in mapa)
mapa = [linha.ljust(largura_mapa) for linha in mapa]
largura_mapa_px = largura_mapa * TILE

moedas_coletadas = set()

def criar_inimigo(tipo, x, y, inicio, fim):

    if tipo == "caranguejo":
        return {
            "x": x,
            "y": y,
            "tipo": tipo,
            "inicio": inicio,
            "fim": fim,
            "vel": 2,
            "dir": 1,
            "imagem": frames_caranguejo[0],
            "frames": frames_caranguejo,
            "frame_atual": 0,
            "contador": 0,
            "hitbox": pygame.Rect(0,0,75,30),
            "offset_y": 130,
            "vivo": True
        }


    if tipo == "lagosta":
        return {
            "x": x,
            "y": y,
            "tipo": tipo,
            "inicio": inicio,
            "fim": fim,
            "vel": 2,
            "dir": -1,
            "imagem": frames_lagosta[0],
            "frames": frames_lagosta,
            "frame_atual": 0,
            "contador": 0,
            "hitbox": pygame.Rect(0,0,108,25),
            "offset_y": 0,
            "vivo": True
        }
    if tipo == "boss":

        return {
            "x": x,
            "y": y,
            "inicio": x,
            "fim": x,
            "vel": 0,
            "dir": 1,
            "imagem": frames_boss[0],
            "frames": frames_boss,
            "frame_atual": 0,
            "contador": 0,
            "hitbox": pygame.Rect(0,0,180,100),
            "offset_y": 0,
            "vivo": True
        }

#inimigos
inimigos = [
    criar_inimigo("caranguejo",750,377,750,890),
    criar_inimigo("caranguejo",1140,377,1140,1500),
    criar_inimigo("caranguejo",1650,185,1650,1790),
    criar_inimigo("caranguejo",2850,377,2850,3050),
    criar_inimigo("caranguejo", 3100, 377, 3100, 3350),
    criar_inimigo("caranguejo", 3800, 377, 3800, 4000),
    criar_inimigo("boss", 300, 300, 300, 200)
    ]

#movimentação do personagem
personagem_x = 200
camera_x = 0.0
char1_y = 407
velocidadechar1_y = 0
gravidade = 0.8
forca_pulo = -15
no_chao = True
estava_no_ar = False
virado_direita = True

# FADE / TROCA DE MAPA
fade_alpha = 0
fadendo = False
fade_surface = pygame.Surface((1280, 720))
fade_surface.fill((0, 0, 0))

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # EVENTOS DO MENU, NOME DO JOGADOR E RANKING (LUIGI)
        if evento.type == pygame.KEYDOWN:

            if estado_jogo == "MENU":
                if evento.key == pygame.K_UP:
                    menu_selecionado = (menu_selecionado - 1) % len(opcoes_menu)
                elif evento.key == pygame.K_DOWN:
                    menu_selecionado = (menu_selecionado + 1) % len(opcoes_menu)
                elif evento.key == pygame.K_RETURN:
                    opcao = opcoes_menu[menu_selecionado]
                    if opcao == "Jogar":
                        nome_jogador = ""
                        estado_jogo = "NOME"
                    elif opcao == "Sair":
                        pygame.quit()
                        sys.exit()

            elif estado_jogo == "NOME":
                if evento.key == pygame.K_RETURN and len(nome_jogador) > 0:
                    pontuacao = 0
                    coracoes = 3
                    vida_atual = vida_maxima
                    personagem_x = 200
                    char1_y = 407
                    velocidadechar1_y = 0
                    boss_morto = False
                    pontuacao_salva = False
                    fade_alpha = 0
                    fadendo = False
                    tempo_ultimo_dano = pygame.time.get_ticks()
                    for inimigo in inimigos:
                        inimigo["x"] = inimigo["inicio"]
                        inimigo["dir"] = 1
                        inimigo["vivo"] = True
                    estado_jogo = "JOGANDO"
                elif evento.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                elif len(nome_jogador) < 12 and evento.unicode.isprintable():
                    nome_jogador += evento.unicode

            elif estado_jogo == "TELA_RANKING":
                if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                    menu_selecionado = 0
                    estado_jogo = "MENU"

            elif estado_jogo == "DERROTA" or estado_jogo == "VITORIA":
                if evento.key == pygame.K_RETURN:
                    estado_jogo = "TELA_RANKING"

    clock.tick(60)
    dt = clock.get_time()

    teclas = pygame.key.get_pressed()
    movendo = False

    # LÓGICA DE TEMPORIZADOR DE QUEDA (LUIGI)
    if estado_jogo == "TELA_QUEDA":
        if pygame.time.get_ticks() - tempo_queda > 2000:
            estado_jogo = "JOGANDO"
            personagem_x = 200
            char1_y = 407
            velocidadechar1_y = 0
            vida_atual = vida_maxima
            tempo_ultimo_dano = pygame.time.get_ticks()
            for inimigo in inimigos:
                inimigo["x"] = inimigo["inicio"]
                inimigo["dir"] = 1
                inimigo["vivo"] = True

    # LÓGICA DE DANO, QUEDA E FIM DE JOGO (LUIGI)
    if estado_jogo == "JOGANDO":

        if char1_y > 800:
            coracoes -= 1
            pontuacao -= 50
            vida_atual = vida_maxima
            if pontuacao < 0:
                pontuacao = 0
            if coracoes <= 0:
                estado_jogo = "DERROTA"
                pontuacao = 0
            else:
                estado_jogo = "TELA_QUEDA"
                tempo_queda = pygame.time.get_ticks()

        if vida_atual <= 0:
            coracoes -= 1
            pontuacao -= 50
            vida_atual = vida_maxima
            if pontuacao < 0:
                pontuacao = 0
            if coracoes <= 0:
                estado_jogo = "DERROTA"
                pontuacao = 0
            else:
                estado_jogo = "TELA_QUEDA"
                tempo_queda = pygame.time.get_ticks()

        if coracoes <= 0:
            estado_jogo = "DERROTA"
            pontuacao = 0

        # TROCA DE MAPA: ao chegar no limite, começa o fade em vez de ir direto pra vitória
        elif personagem_x >= largura_mapa_px * 3 - personagem_parado.get_width() and not fadendo:
            fadendo = True

        if not fadendo:
            if teclas[pygame.K_d]:
                personagem_x += 300 * dt / 1000
                virado_direita = True
                movendo = True

            if teclas[pygame.K_a]:
                personagem_x -= 300 * dt / 1000
                virado_direita = False
                movendo = True
        else:
            velocidadechar1_y = 0

    for inimigo in inimigos:
        inimigo["x"] += inimigo["vel"] * inimigo["dir"]
        if "frames" in inimigo:
            inimigo["contador"] += 1
            if inimigo["contador"] >= 8:
                inimigo["contador"] = 0
                inimigo["frame_atual"] += 1
                if inimigo["frame_atual"] >= len(inimigo["frames"]):
                    inimigo["frame_atual"] = 0
                inimigo["imagem"] = inimigo["frames"][inimigo["frame_atual"]]
        
        inimigo["hitbox"].x = inimigo["x"] + 2
        inimigo["hitbox"].y = inimigo["y"] + inimigo["offset_y"]

        if inimigo["x"] >= inimigo["fim"]:
            inimigo["dir"] = -1
        if inimigo["x"] <= inimigo["inicio"]:
            inimigo["dir"] = 1

    personagem_x = max(0, personagem_x)
    personagem_x = min(personagem_x, largura_mapa_px * 3 - personagem_parado.get_width())

    camera_x = max(0, personagem_x - 200)
    camera_x = min(camera_x, largura_mapa_px * 3 - 1280)
    char1_x = personagem_x - camera_x

    coluna_inicial = int(camera_x // TILE)
    colunas_finais = 1280 // TILE + 2

    collider_list = []
    for col_tela in range(colunas_finais):
        col_mapa = (coluna_inicial + col_tela) % largura_mapa
        for i, linha in enumerate(mapa):
            cel = linha[col_mapa]
            y = i * TILE
            if cel == 'C' or cel == 'P':
                collider_list.append(pygame.Rect((coluna_inicial + col_tela) * TILE, y + 32, TILE, TILE - 32))
            elif cel == 'D':
                collider_list.append(pygame.Rect((coluna_inicial + col_tela) * TILE, y, TILE, TILE))

    #colisão horizontal
    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
    for bloco in collider_list:
        if collider_personagem.colliderect(bloco):
            if virado_direita:
                personagem_x = bloco.left - personagem_parado.get_width()
            else:
                personagem_x = bloco.right
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

    # COLISÃO DO JOGADOR COM OS INIMIGOS: PISÃO MATA, TOQUE LATERAL TIRA VIDA (LUIGI)
    if estado_jogo == "JOGANDO":
        for inimigo in inimigos:
            if not inimigo["vivo"]:
                continue
            if collider_personagem.colliderect(inimigo["hitbox"]):
                if velocidadechar1_y > 0 and collider_personagem.bottom < inimigo["hitbox"].top + 8:
                    inimigo["vivo"] = False
                    tocar_som_do_inimigo(inimigo["tipo"])
                    pontuacao += 100
                    velocidadechar1_y = -10
                else:
                    if collider_personagem.centerx < inimigo["hitbox"].centerx:
                        personagem_x = inimigo["hitbox"].left - personagem_parado.get_width()
                    else:
                        personagem_x = inimigo["hitbox"].right
                    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
                    tempo_atual = pygame.time.get_ticks()
                    if tempo_atual - tempo_ultimo_dano > 1000:
                        vida_atual -= 25
                        tempo_ultimo_dano = tempo_atual
                        velocidadechar1_y = -5

    camera_x = max(0, personagem_x - 200)
    camera_x = min(camera_x, largura_mapa_px * 3 - 1280)
    char1_x = personagem_x - camera_x

    velocidadechar1_y += gravidade
    char1_y += velocidadechar1_y

    #colisão vertical
    estava_no_ar = not no_chao
    no_chao = False
    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
    encostando = pygame.Rect(collider_personagem.x, collider_personagem.y, collider_personagem.width, collider_personagem.height + 4)
    for bloco in collider_list:
        if encostando.colliderect(bloco):
            if velocidadechar1_y >= 0 and collider_personagem.top < bloco.top:
                char1_y = bloco.top - personagem_parado.get_height()
                velocidadechar1_y = 0
                no_chao = True
                if estava_no_ar and estado_jogo == "JOGANDO":
                    som_aterrissagem.play()
            else:
                char1_y = bloco.bottom
                velocidadechar1_y = 0
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
            encostando = pygame.Rect(collider_personagem.x, collider_personagem.y, collider_personagem.width, collider_personagem.height + 4)

    if estado_jogo == "JOGANDO" and teclas[pygame.K_SPACE] and no_chao and not fadendo:
        velocidadechar1_y = forca_pulo
        som_pulo.play()

    if estado_jogo != "JOGANDO" and estado_jogo != "TELA_QUEDA":
        canal_passos.stop()
    else:
        atualizar_sistema_sonoro(movendo and no_chao)

    # COLETA DE MOEDAS
    if estado_jogo == "JOGANDO":
        for col_tela in range(colunas_finais):
            col_mapa = (coluna_inicial + col_tela) % largura_mapa
            coluna_mundo = coluna_inicial + col_tela
            for i, linha in enumerate(mapa):
                cel = linha[col_mapa]
                if cel == 'M':
                    chave = (coluna_mundo, i)
                    if chave not in moedas_coletadas:
                        rect_moeda = pygame.Rect(coluna_mundo * TILE, i * TILE, TILE, TILE)
                        if collider_personagem.colliderect(rect_moeda):
                            moedas_coletadas.add(chave)
                            som_moeda.play()

    # animacao do personagem
    deslocamento_x_pulo = 0
    deslocamento_y_pulo = 0
    if not no_chao:
        imagem_atual = frames_pular[3]
        deslocamento_y_pulo = -63
        deslocamento_x_pulo = -18
    elif movendo and no_chao:
        contador_frames += 1
        if contador_frames >= intervalo_frame:
            contador_frames = 0
            frame_atual = (frame_atual + 1) % len(frames_andar)
        imagem_atual = frames_andar[frame_atual]
    else:
        frame_atual = 0
        contador_frames = 0
        imagem_atual = personagem_parado

    if not virado_direita:
        imagem_atual = pygame.transform.flip(imagem_atual, True, False)

    if (estado_jogo == "DERROTA" or estado_jogo == "VITORIA") and not pontuacao_salva:
        salvar_pontuacao(nome_jogador, pontuacao)
        pontuacao_salva = True

    screen.fill((3, 18, 15))

    estados_que_mostram_cenario = ["JOGANDO", "DERROTA", "VITORIA"]
    if estado_jogo in estados_que_mostram_cenario:
        for i, camada in enumerate(camadas):
            deslocamento = int(camera_x * velocidades[i]) % 1280
            screen.blit(camada, (-deslocamento, 0))
            screen.blit(camada, (1280 - deslocamento, 0))

        for col_tela in range(colunas_finais):
            col_mapa = (coluna_inicial + col_tela) % largura_mapa
            coluna_mundo = coluna_inicial + col_tela
            x = coluna_mundo * TILE - int(camera_x)
            for i, linha in enumerate(mapa):
                cel = linha[col_mapa]
                y = i * TILE
                if cel == 'C':
                    screen.blit(t_topo, (x, y))
                elif cel == 'D':
                    screen.blit(t_fill, (x, y))
                elif cel == 'P':
                    screen.blit(t_topo, (x, y))
                elif cel == 'M' and (coluna_mundo, i) not in moedas_coletadas:
                    screen.blit(t_moeda, (x, y + 20))

        for inimigo in inimigos:
            if inimigo["vivo"]:
                img = inimigo["imagem"]
                if inimigo["dir"] == 1:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (inimigo["x"] - camera_x, inimigo["y"]))

        screen.blit(imagem_atual, (char1_x + deslocamento_x_pulo, char1_y + deslocamento_y_pulo))

    # DESENHO DA INTERFACE (HUD), MENU, RANKING E TELAS FINAIS (LUIGI)
    if estado_jogo == "MENU":
        screen.blit(img_fundo_menu, (0, 0))

        pos_y_opcao = 420
        for indice in range(len(opcoes_menu)):
            opcao = opcoes_menu[indice]
            if indice == menu_selecionado:
                cor = (27, 28, 27)
                texto = "> " + opcao + " <"
            else:
                cor = (255, 255, 255)
                texto = opcao
            item_render = fonte_hud.render(texto, True, cor)
            screen.blit(item_render, (1280 // 2 - item_render.get_width() // 2, pos_y_opcao))
            pos_y_opcao += 60

        instrucao = fonte_hud.render("Setas para navegar - ENTER para confirmar", True, (255, 215, 0))
        screen.blit(instrucao, (1280 // 2 - instrucao.get_width() // 2, pos_y_opcao + 30))

    elif estado_jogo == "NOME":
        screen.blit(img_fundo_menu, (0, 0))

        titulo = fonte_hud.render("Digite seu nome e aperte ENTER", True, (255, 255, 255))
        screen.blit(titulo, (1280 // 2 - titulo.get_width() // 2, 280))

        texto_nome = fonte_telas.render(nome_jogador, True, (255, 215, 0))
        screen.blit(texto_nome, (1280 // 2 - texto_nome.get_width() // 2, 380))

    elif estado_jogo == "TELA_RANKING":
        titulo = fonte_hud.render("RANKING - TOP 5", True, (255, 215, 0))
        screen.blit(titulo, (1280 // 2 - titulo.get_width() // 2, 100))

        ranking = carregar_ranking()
        posicao_y = 200
        colocacao = 1
        for item in ranking:
            linha_texto = fonte_hud.render(str(colocacao) + ". " + item[0] + " - " + str(item[1]), True, (255, 255, 255))
            screen.blit(linha_texto, (1280 // 2 - linha_texto.get_width() // 2, posicao_y))
            posicao_y += 45
            colocacao += 1

        instrucao = fonte_hud.render("ENTER / ESC - Voltar ao Menu", True, (255, 255, 255))
        screen.blit(instrucao, (1280 // 2 - instrucao.get_width() // 2, posicao_y + 40))

    elif estado_jogo == "JOGANDO":
        for i in range(coracoes):
            screen.blit(img_bolha, (20 + (i * 35), 20))

        pygame.draw.rect(screen, (255, 215, 0), (18, 68, 204, 24), 3)
        pygame.draw.rect(screen, (0, 105, 148), (20, 70, vida_atual * 2, 20))

        texto_pontos = fonte_hud.render("Pontuação: " + str(pontuacao), True, (255, 215, 0))
        pos_x_pontos = 1280 - texto_pontos.get_width() - 30
        screen.blit(texto_pontos, (pos_x_pontos, 20))

    elif estado_jogo == "TELA_QUEDA":
        texto_afogou = fonte_telas.render("VOCÊ MORREU!", True, (255, 0, 0))
        screen.blit(texto_afogou, (1280 // 2 - texto_afogou.get_width() // 2, 720 // 2))

    elif estado_jogo == "DERROTA":
        texto_derrota = fonte_telas.render("GAME OVER", True, (255, 0, 0))
        screen.blit(texto_derrota, (1280 // 2 - texto_derrota.get_width() // 2, 720 // 2))

        texto_voltar = fonte_hud.render("ENTER - Ver Ranking", True, (255, 255, 255))
        screen.blit(texto_voltar, (1280 // 2 - texto_voltar.get_width() // 2, 720 // 2 + 80))

    elif estado_jogo == "VITORIA":
        texto_vitoria = fonte_telas.render("VOCÊ VENCEU!", True, (0, 255, 0))
        screen.blit(texto_vitoria, (1280 // 2 - texto_vitoria.get_width() // 2, 720 // 2))

        texto_bonus = fonte_hud.render("Pontuação Final: " + str(pontuacao), True, (255, 215, 0))
        screen.blit(texto_bonus, (1280 // 2 - texto_bonus.get_width() // 2, 720 // 2 + 80))

        texto_voltar = fonte_hud.render("ENTER - Ver Ranking", True, (255, 255, 255))
        screen.blit(texto_voltar, (1280 // 2 - texto_voltar.get_width() // 2, 720 // 2 + 130))

    # FADE / TROCA DE MAPA
    if fadendo:
        fade_alpha = min(255, fade_alpha + 3)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
        if fade_alpha >= 255:
            pygame.time.wait(500)
            canal_passos.stop()
            exec(open("mapa_boss.py").read())
            sys.exit()

    pygame.display.update()