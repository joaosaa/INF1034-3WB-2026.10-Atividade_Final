import pygame, sys

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

#spritesheet
spritesheet_andar = pygame.image.load('Characters/spritesheet_andar.png').convert_alpha()
LARGURA_TOTAL = spritesheet_andar.get_width()
FRAME_H = spritesheet_andar.get_height()
ESCALA = 0.9

NUM_FRAMES = 7
frame_w_fixo = LARGURA_TOTAL // NUM_FRAMES

frames_andar = []
for i in range(NUM_FRAMES):
    x_inicio = i * frame_w_fixo
    frame = pygame.Surface((frame_w_fixo, FRAME_H), pygame.SRCALPHA)
    frame.blit(spritesheet_andar, (0, 0), (x_inicio, 0, frame_w_fixo, FRAME_H))
    frame = pygame.transform.scale(frame, (int(frame_w_fixo * ESCALA), int(FRAME_H * ESCALA)))
    frames_andar.append(frame)

personagem_parado = frames_andar[0]

#spritesheet de pulo
spritesheet_pular = pygame.image.load('Characters/spritesheet_pular.png').convert_alpha()
LARGURA_TOTAL_PULAR = spritesheet_pular.get_width()
FRAME_H_PULAR = spritesheet_pular.get_height()
ESCALA_PULAR = 0.40

NUM_FRAMES_PULAR = 7
frame_w_fixo_pular = LARGURA_TOTAL_PULAR // NUM_FRAMES_PULAR

frames_pular = []
for i in range(NUM_FRAMES_PULAR):
    x_inicio = i * frame_w_fixo_pular
    frame = pygame.Surface((frame_w_fixo_pular, FRAME_H_PULAR), pygame.SRCALPHA)
    frame.blit(spritesheet_pular, (0, 0), (x_inicio, 0, frame_w_fixo_pular, FRAME_H_PULAR))
    frame = pygame.transform.scale(frame, (int(frame_w_fixo_pular * ESCALA_PULAR), int(FRAME_H_PULAR * ESCALA_PULAR)))
    frames_pular.append(frame)

frame_atual = 0
contador_frames = 0
INTERVALO_FRAME = 9

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

MAPA = [
    "                                                             ",
    "                                                             ",
    "                                                             ",
    "                                                             ",
    "                                                             ",
    "                          PPP                                ",
    "                PP     PP                PPP         PPP     ",
    "                                                             ",
    "CCCCCCCCCC  CCC   CCCCCCCCCCCCCCC       CCCCCCCCCCCCCCCCCCCC",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
]

LARGURA_MAPA = max(len(linha) for linha in MAPA)
MAPA = [linha.ljust(LARGURA_MAPA) for linha in MAPA]

FOLGA_TOPO_TILE = 28  # o desenho do t_topo so comeca 28px dentro da celula de 64px

collider_list = []
for i in range(len(MAPA)):
    for j in range(len(MAPA[i])):
        if MAPA[i][j] == "C" or MAPA[i][j] == "P":
            collider_list.append(pygame.Rect(j * TILE, i * TILE + FOLGA_TOPO_TILE, TILE, TILE - FOLGA_TOPO_TILE))
        elif MAPA[i][j] == "D":
            collider_list.append(pygame.Rect(j * TILE, i * TILE, TILE, TILE))

#movimentação do personagem
ALTURA_COLISAO = 189  # altura real do personagem visivel (sem a folga vazia abaixo dos pes)
LARGURA_COLISAO = 60  # largura real do corpo (sem a folga vazia nas laterais)
DESLOCAMENTO_X_COLISAO = 31  # onde o corpo realmente comeca dentro do recorte
personagem_x = 200 
camera_x = 0.0
char1_y = 323
velocidadechar1_y = 0
gravidade = 0.8
forca_pulo = -15
no_chao = True
virado_direita = True

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    clock.tick(60)
    dt = clock.get_time()

    teclas = pygame.key.get_pressed()
    movendo = False
    if teclas[pygame.K_d]:
        personagem_x += 300 * dt / 1000 
        virado_direita = True
        movendo = True

    if teclas[pygame.K_a]:
        personagem_x -= 300 * dt / 1000
        virado_direita = False
        movendo = True

    personagem_x = max(0, personagem_x) 

    camera_x = max(0, personagem_x - 200)
    char1_x = personagem_x - camera_x  

    # COLISAO HORIZONTAL (primeiro, igual no Mario)
    collider_personagem = pygame.Rect(int(personagem_x + DESLOCAMENTO_X_COLISAO), int(char1_y), LARGURA_COLISAO, ALTURA_COLISAO)
    for bloco in collider_list:
        if collider_personagem.colliderect(bloco):
            if virado_direita:
                personagem_x = bloco.left - DESLOCAMENTO_X_COLISAO - LARGURA_COLISAO
            else:
                personagem_x = bloco.right - DESLOCAMENTO_X_COLISAO
            collider_personagem = pygame.Rect(int(personagem_x + DESLOCAMENTO_X_COLISAO), int(char1_y), LARGURA_COLISAO, ALTURA_COLISAO)

    camera_x = max(0, personagem_x - 200)
    char1_x = personagem_x - camera_x

    velocidadechar1_y += gravidade
    char1_y += velocidadechar1_y

    # COLISAO VERTICAL (depois)
    no_chao = False
    collider_personagem = pygame.Rect(int(personagem_x + DESLOCAMENTO_X_COLISAO), int(char1_y), LARGURA_COLISAO, ALTURA_COLISAO)
    caixa_checagem = collider_personagem.inflate(0, 4)  # um pouco maior, pra contar "encostando" como colisao
    for bloco in collider_list:
        if caixa_checagem.colliderect(bloco):
            if velocidadechar1_y >= 0:
                char1_y = bloco.top - ALTURA_COLISAO
                velocidadechar1_y = 0
                no_chao = True
            elif velocidadechar1_y < 0:
                char1_y = bloco.bottom
                velocidadechar1_y = 0
            collider_personagem = pygame.Rect(int(personagem_x + DESLOCAMENTO_X_COLISAO), int(char1_y), LARGURA_COLISAO, ALTURA_COLISAO)
            caixa_checagem = collider_personagem.inflate(0, 4)

    if teclas[pygame.K_SPACE] and no_chao:
        velocidadechar1_y = forca_pulo

    # animacao do personagem
    deslocamento_y_pulo = 0
    if not no_chao:
        imagem_atual = frames_pular[3]   # frame fixo enquanto no ar
        deslocamento_y_pulo = -11
    elif movendo and no_chao:
        contador_frames += 1
        if contador_frames >= INTERVALO_FRAME:
            contador_frames = 0
            frame_atual = (frame_atual + 1) % len(frames_andar)
        imagem_atual = frames_andar[frame_atual]
    else:
        frame_atual = 0
        contador_frames = 0
        imagem_atual = personagem_parado

    if not virado_direita:
        imagem_atual = pygame.transform.flip(imagem_atual, True, False)

    screen.fill((3, 18, 15))

    for i, camada in enumerate(camadas):
        deslocamento = int(camera_x * velocidades[i]) % 1280
        screen.blit(camada, (-deslocamento, 0))
        screen.blit(camada, (1280 - deslocamento, 0))

    coluna_inicial = int(camera_x // TILE)
    colunas_finais = 1280 // TILE + 2

    for col_tela in range(colunas_finais):
        col_mapa = (coluna_inicial + col_tela) % LARGURA_MAPA
        x = (coluna_inicial + col_tela) * TILE - int(camera_x)
        for i, linha in enumerate(MAPA):
            cel = linha[col_mapa]
            y = i * TILE
            if cel == 'C':
                screen.blit(t_topo, (x, y))
            elif cel == 'D':
                screen.blit(t_fill, (x, y))
            elif cel == 'P':
                screen.blit(t_topo, (x, y))

    screen.blit(imagem_atual, (char1_x, char1_y + deslocamento_y_pulo))

    pygame.display.update()