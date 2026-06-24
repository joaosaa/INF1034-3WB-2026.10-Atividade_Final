import pygame, sys

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("sounds/TRILHA SONORA/Soundtrack.mp3")
pygame.mixer.music.set_volume(0.090)
pygame.mixer.music.play(-1)

som_passos = pygame.mixer.Sound("sounds/PASSOS NA PEDRA/PASSO.mpeg")
som_pulo = pygame.mixer.Sound("sounds/PULO/jump.mp3")
som_moeda = pygame.mixer.Sound("sounds/COLETAR MOEDA/Picked Coin Echo.wav")
som_aterrissagem = pygame.mixer.Sound("sounds/ATERRISSAGEM (LANDING AFTER JUMP)/ATERRISSAGEM.mpeg")

som_passos.set_volume(0.4)
canal_passos = pygame.mixer.Channel(1)

def atualizar_sistema_sonoro(jogador_movendo):
    if jogador_movendo:
        if not canal_passos.get_busy():
            canal_passos.play(som_passos, loops=-1)
    else:
        canal_passos.stop()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

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

mapa = [
    "                                                             ",
    "                                                             ",
    "                                                             ",
    "                                                             ",
    "                                                             ",
    "                          PPP                                ",
    "                PP     PP                 PPP        PPP     ",
    "                                   PP                        ",
    "CCCCCCCCCC  CCC   CCCCCCCCCCCCCCC       CCCCCCCCCCCCCCCCCCCC",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD  DDD   DDDDDDDDDDDDDDD       DDDDDDDDDDDDDDDDDDDD",
]

largura_mapa = max(len(linha) for linha in mapa)
mapa = [linha.ljust(largura_mapa) for linha in mapa]

collider_list = []
for i in range(len(mapa)):
    for j in range(len(mapa[i])):
        if mapa[i][j] == "C" or mapa[i][j] == "P":
            collider_list.append(pygame.Rect(j * TILE, i * TILE + 32, TILE, TILE - 32))
        elif mapa[i][j] == "D":
            collider_list.append(pygame.Rect(j * TILE, i * TILE, TILE, TILE))

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

    #colisão horizontal
    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
    for bloco in collider_list:
        if collider_personagem.colliderect(bloco):
            if virado_direita:
                personagem_x = bloco.left - personagem_parado.get_width()
            else:
                personagem_x = bloco.right
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

    camera_x = max(0, personagem_x - 200)
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
                if estava_no_ar:
                    som_aterrissagem.play()
            else:
                char1_y = bloco.bottom
                velocidadechar1_y = 0
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
            encostando = pygame.Rect(collider_personagem.x, collider_personagem.y, collider_personagem.width, collider_personagem.height + 4)

    if teclas[pygame.K_SPACE] and no_chao:
        velocidadechar1_y = forca_pulo
        som_pulo.play()

    atualizar_sistema_sonoro(movendo and no_chao)

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

    screen.fill((3, 18, 15))

    for i, camada in enumerate(camadas):
        deslocamento = int(camera_x * velocidades[i]) % 1280
        screen.blit(camada, (-deslocamento, 0))
        screen.blit(camada, (1280 - deslocamento, 0))

    coluna_inicial = int(camera_x // TILE)
    colunas_finais = 1280 // TILE + 2

    for col_tela in range(colunas_finais):
        col_mapa = (coluna_inicial + col_tela) % largura_mapa
        x = (coluna_inicial + col_tela) * TILE - int(camera_x)
        for i, linha in enumerate(mapa):
            cel = linha[col_mapa]
            y = i * TILE
            if cel == 'C':
                screen.blit(t_topo, (x, y))
            elif cel == 'D':
                screen.blit(t_fill, (x, y))
            elif cel == 'P':
                screen.blit(t_topo, (x, y))

    screen.blit(imagem_atual, (char1_x + deslocamento_x_pulo, char1_y + deslocamento_y_pulo))

    pygame.display.update()