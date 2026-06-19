import pygame, sys

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# ---------- parallax ----------
camadas = []
velocidades = [0.05, 0.15, 0.25, 0.4]
for i in range(4, 0, -1):
    img = pygame.image.load(f'Background/ParallaxCave{i}.png').convert()
    img = pygame.transform.scale(img, (1280, 720))
    img.set_colorkey((0, 0, 0))
    camadas.append(img)

# ---------- tileset ----------
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

# ---------- mapa ----------
# C = topo chao, D = fill chao, P = plataforma (topo)
MAPA = [
    "                                                            ",
    "                                                            ",
    "                                                            ",
    "                                                            ",
    "                          PPP                               ",
    "                                                             ",
    "                                       PPP                  ",
    "              PPP                                    PPP    ",
    "                                                             ",
    "CCCCCCCCC          CCCCCCCCCCCCC          CCCCCCCCCCCCCCCCCC",
    "DDDDDDDDD          DDDDDDDDDDDDD          DDDDDDDDDDDDDDDDDD",
    "DDDDDDDDD          DDDDDDDDDDDDD          DDDDDDDDDDDDDDDDDD",
    "DDDDDDDDD          DDDDDDDDDDDDD          DDDDDDDDDDDDDDDDDD",
    "DDDDDDDDD          DDDDDDDDDDDDD          DDDDDDDDDDDDDDDDDD",
]

LARGURA_MAPA = len(MAPA[0])  # numero de colunas do padrao, que se repete

camera_x = 0.0

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    clock.tick(60)

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_d]: camera_x += 5
    if teclas[pygame.K_a]: camera_x = max(0, camera_x - 5)

    screen.fill((3, 18, 15))

    for i, camada in enumerate(camadas):
        deslocamento = int(camera_x * velocidades[i]) % 1280
        screen.blit(camada, (-deslocamento, 0))
        screen.blit(camada, (1280 - deslocamento, 0))

    # primeira coluna visivel na tela (em unidades de tile)
    coluna_inicial = int(camera_x // TILE)
    colunas_visiveis = 1280 // TILE + 2  # +2 de margem pra nao cortar nas bordas

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

    pygame.display.update()