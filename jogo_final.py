import pygame, sys

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

TILE = 64
tileset = pygame.image.load('CaveG.png').convert()
tileset.set_colorkey((0, 0, 0))

def get_tile(cow, row):
    tile = pygame.Surface((TILE, TILE))
    tile.blit(tileset, (0 , 0), (cow * TILE, row * TILE, TILE, TILE))
    tile.set_colorkey((0, 0, 0))
    return tile

t_chao = get_tile(8, 0)
t_chao2 = get_tile(8, 1)

MAPA = [
    "                      ",
    "                      ",
    "                      ",
    "                      ",
    "                      ",
    "                      ",
    "                      ",
    "CCCCCCCCCCCCCCCCCCCCCC",
    "VVVVVVVVVVVVVVVVVVVVVV",
]

camadas = []
velocidades = [0.05, 0.15, 0.25, 0.4]
for i in range(4, 0, -1):
    img = pygame.image.load(f'Background/ParallaxCave{i}.png').convert()
    img = pygame.transform.scale(img, (1280, 720))
    img.set_colorkey((0, 0, 0))
    camadas.append(img)

camera_x = 0.0

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    clock.tick(60)

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_d]: camera_x += 5
    if teclas[pygame.K_a]: camera_x -= 5

    screen.fill((3, 18, 15))
    for i, camada in enumerate(camadas):
        deslocamento = int(camera_x * velocidades[i]) % 1280
        screen.blit(camada, (-deslocamento, 0))
        screen.blit(camada, (1280 - deslocamento, 0))

    for i, linha in enumerate(MAPA):
        for j, cel in enumerate(linha):
            x = j * TILE - int(camera_x)
            y = i * TILE
            if cel == 'C':
                screen.blit(t_chao, (x, y))
            elif cel == 'V':
                 screen.blit(t_chao2, (x, y))   
    pygame.display.update()