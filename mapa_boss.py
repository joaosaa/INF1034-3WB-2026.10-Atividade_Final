import pygame, sys

# NÃO chamar pygame.init() de novo aqui: o processo já está com tudo
# inicializado desde o arquivo principal (mesmo exec). Reinicializar
# reabre o dispositivo de áudio e quebra os sons já carregados (LUIGI)

# TRILHA SONORA DO BOSS (LUIGI)
pygame.mixer.music.load("sounds\TRILHA SONORA\FINAL BOSS\Final Boss.mp3")
pygame.mixer.music.set_volume(1.5)
pygame.mixer.music.play(-1)

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

#arena
mapa = [
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "  PP            PP  ",
    "                    ",
    "CCCCCCCCCCCCCCCCCCCC",
    "DDDDDDDDDDDDDDDDDDDD",
    "DDDDDDDDDDDDDDDDDDDD",
]

LARGURA_ARENA = len(mapa[0]) * TILE  # 1280px

collider_list = []
for i, linha in enumerate(mapa):
    for j, cel in enumerate(linha):
        if cel == 'C' or cel == 'P':
            collider_list.append(pygame.Rect(j * TILE, i * TILE + 32, TILE, TILE - 32))
        elif cel == 'D':
            collider_list.append(pygame.Rect(j * TILE, i * TILE, TILE, TILE))

# paredes laterais invisíveis
collider_list.append(pygame.Rect(-10, 0, 10, 720))           # parede esquerda
collider_list.append(pygame.Rect(LARGURA_ARENA, 0, 10, 720)) # parede direita

#personagem
personagem_x = 100.0
char1_y = 400.0
velocidadechar1_y = 0
gravidade = 0.8
forca_pulo = -15
no_chao = True
virado_direita = True

#fade
fade_alpha = 255
fade_surface = pygame.Surface((1280, 720))
fade_surface.fill((0, 0, 0))

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
    personagem_x = min(personagem_x, LARGURA_ARENA - personagem_parado.get_width())

    #colisão horizontal
    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
    for bloco in collider_list:
        if collider_personagem.colliderect(bloco):
            if virado_direita:
                personagem_x = bloco.left - personagem_parado.get_width()
            else:
                personagem_x = bloco.right
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

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

    if teclas[pygame.K_SPACE] and no_chao:
        velocidadechar1_y = forca_pulo
        som_pulo.play()

    # SOM DE PASSOS, REAPROVEITANDO O SISTEMA JÁ CRIADO NO ARQUIVO PRINCIPAL (LUIGI)
    atualizar_sistema_sonoro(movendo and no_chao)

    # animação do personagem
    deslocamento_x_pulo = 0
    deslocamento_y_pulo = 0
    if not no_chao:
        imagem_atual = frames_pular[3]
        deslocamento_y_pulo = -60
        deslocamento_x_pulo = -20
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
        screen.blit(camada, (0, 0))

    for i, linha in enumerate(mapa):
        for j, cel in enumerate(linha):
            x = j * TILE
            y = i * TILE
            if cel == 'C':
                screen.blit(t_topo, (x, y))
            elif cel == 'D':
                screen.blit(t_fill, (x, y))
            elif cel == 'P':
                screen.blit(t_topo, (x, y))

    screen.blit(imagem_atual, (int(personagem_x) + deslocamento_x_pulo, int(char1_y) + deslocamento_y_pulo))

    # fade de entrada
    if fade_alpha > 0:
        fade_alpha = max(0, fade_alpha - 3)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

    pygame.display.update()