import pygame, sys

pygame.init()
pygame.mixer.init()

#audio
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

#personagem
char1 = pygame.image.load('Characters/mainchar.png')
char1 = pygame.transform.scale(char1, (200, 200))

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

def get_tile(col, row):
    tile = pygame.Surface((16, 16), pygame.SRCALPHA)
    tile.blit(tileset_raw, (0, 0), (col * 16, row * 16, 16, 16))
    return pygame.transform.scale(tile, (TILE, TILE))

def tingir_azul(tile, fator=0.55):
    w, h = tile.get_size()
    resultado = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        for y in range(h):
            r, g, b, a = tile.get_at((x, y))
            if a == 0:
                continue
            lum = int((r * 0.3 + g * 0.59 + b * 0.11) * fator)
            resultado.set_at((x, y), (lum, lum, lum, a))
    return resultado

t_topo = tingir_azul(get_tile(1, 0))   # chao com musgo no topo
t_fill = tingir_azul(get_tile(1, 4))   # pedra solida

#mapa
MAPA = [
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                          PPP                                 ",
    "              PPP                     PPP            PPP      ",
    "                                                               ",
    "CCCCCCCCCC        CCCCCCCCCCCCCCC        CCCCCCCCCCCCCCCCCCCC",
    "DDDDDDDDDD        DDDDDDDDDDDDDDD        DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD        DDDDDDDDDDDDDDD        DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD        DDDDDDDDDDDDDDD        DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDD        DDDDDDDDDDDDDDD        DDDDDDDDDDDDDDDDDDDD",
]

LARGURA_MAPA = max(len(linha) for linha in MAPA)
MAPA = [linha.ljust(LARGURA_MAPA) for linha in MAPA]

#movimentação do personagem
camera_x = 0.0
char1_x = 50
char1_y = 380
velocidadechar1_x = 1.5
velocidadechar1_y = 0
gravidade = 0.8
forca_pulo = -15
no_chao = False
chao_y = 380

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    clock.tick(60)

    teclas = pygame.key.get_pressed()
    andando = False
    if teclas[pygame.K_d]:
        camera_x += 5
        char1_x += velocidadechar1_x
        andando = True

    if teclas[pygame.K_a]:
        camera_x = max(0, camera_x - 5)
        char1_x -= velocidadechar1_x
        andando = True

    velocidadechar1_y += gravidade
    char1_y += velocidadechar1_y

    estava_no_ar = not no_chao
    if char1_y >= chao_y:
        char1_y = chao_y
        velocidadechar1_y = 0
        no_chao = True
        if estava_no_ar:
            som_aterrissagem.play()
    else:
        no_chao = False

    if teclas[pygame.K_SPACE] and no_chao:
        velocidadechar1_y = forca_pulo
        som_pulo.play()

    atualizar_sistema_sonoro(andando and no_chao)

    screen.fill((3, 18, 15))

    for i, camada in enumerate(camadas):
        deslocamento = int(camera_x * velocidades[i]) % 1280
        screen.blit(camada, (-deslocamento, 0))
        screen.blit(camada, (1280 - deslocamento, 0))

    coluna_inicial = int(camera_x // TILE)
    colunas_visiveis = 1280 // TILE + 2

    for col_tela in range(colunas_visiveis):
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

    screen.blit(char1, (char1_x, char1_y))

    pygame.display.update()