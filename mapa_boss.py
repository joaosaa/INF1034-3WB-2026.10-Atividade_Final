import pygame, sys

# TRILHA SONORA DO BOSS (LUIGI)
pygame.mixer.music.load("sounds\TRILHA SONORA\FINAL BOSS\Final Boss.mp3")
pygame.mixer.music.set_volume(0.090)
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

#spritesheet (mergulhador com tridente)
spritesheet_andar = pygame.image.load('Characters/spritesheet_andando_tridente.png').convert_alpha()
escala = 0.35

# frame 0 = parado (idle), frames 1 a 5 = ciclo de andar
# cortados pelo bounding box real de cada um (contorno, não fatia fixa)
frame_parado_bbox = (68, 364, 162, 557)
frames_andar_bbox = [
    (434, 737, 162, 556),
    (777, 1099, 163, 557),
    (1151, 1470, 163, 554),
    (1535, 1833, 165, 557),
    (1858, 2166, 164, 557),
]

def cortar_frame(x_inicio, x_fim, y_inicio, y_fim):
    frame_w = x_fim - x_inicio + 1
    frame_h_frame = y_fim - y_inicio + 1
    frame = pygame.Surface((frame_w, frame_h_frame), pygame.SRCALPHA)
    frame.blit(spritesheet_andar, (0, 0), (x_inicio, y_inicio, frame_w, frame_h_frame))
    return pygame.transform.scale(frame, (int(frame_w * escala), int(frame_h_frame * escala)))

personagem_parado = cortar_frame(*frame_parado_bbox)
frames_andar = [cortar_frame(*bbox) for bbox in frames_andar_bbox]

# ATAQUE COM O TRIDENTE: botão esquerdo do mouse dispara a animação uma vez,
# e no ápice do golpe (tridente esticado) checa se acertou o boss
escala_atacar = 0.6
spritesheet_atacar = pygame.image.load('Characters/spritesheet_batendo_tridente.png').convert_alpha()
frames_atacar_bbox = [
    (38, 182, 257, 498),
    (265, 441, 242, 497),
    (537, 826, 283, 497),
    (827, 1072, 283, 497),
    (1166, 1425, 301, 497),
    (1867, 2165, 314, 499),
]

frames_atacar = []
# pontinhos residuais de frames vizinhos (fragmentos de 1-9px) que sobraram
# no corte por contorno - limpa antes de escalar
limpeza_por_frame = {
    1: [(75, 73, 1, 1)],
    2: [(286, 17, 5, 7)],
}
for indice_frame, (x_inicio, x_fim, y_inicio, y_fim) in enumerate(frames_atacar_bbox):
    frame_w = x_fim - x_inicio + 1
    frame_h_frame = y_fim - y_inicio + 1
    frame = pygame.Surface((frame_w, frame_h_frame), pygame.SRCALPHA)
    frame.blit(spritesheet_atacar, (0, 0), (x_inicio, y_inicio, frame_w, frame_h_frame))
    for (lx, ly, lw, lh) in limpeza_por_frame.get(indice_frame, []):
        frame.fill((0, 0, 0, 0), pygame.Rect(lx, ly, lw, lh))
    frame = pygame.transform.scale(frame, (int(frame_w * escala_atacar), int(frame_h_frame * escala_atacar)))
    frames_atacar.append(frame)

atacando = False
atk_frame_atual = 0
atk_contador_frames = 0
atk_intervalo_frame = 4

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

LARGURA_ARENA = len(mapa[0]) * TILE  

collider_list = []
for i, linha in enumerate(mapa):
    for j, cel in enumerate(linha):
        if cel == 'C' or cel == 'P':
            collider_list.append(pygame.Rect(j * TILE, i * TILE + 32, TILE, TILE - 32))
        elif cel == 'D':
            collider_list.append(pygame.Rect(j * TILE, i * TILE, TILE, TILE))

# paredes laterais invisíveis
collider_list.append(pygame.Rect(-10, 0, 10, 720))           
collider_list.append(pygame.Rect(LARGURA_ARENA, 0, 10, 720)) 

#personagem
personagem_x = 100.0
char1_y = (9 * TILE + 32) - personagem_parado.get_height()
velocidadechar1_y = 0
gravidade = 0.8
forca_pulo = -15
no_chao = True
virado_direita = True

# POSIÇÃO INICIAL DO JOGADOR NA ARENA, PRA RESPAWNAR AQUI SE MORRER (LUIGI)
ARENA_PERSONAGEM_X = 100.0
ARENA_PERSONAGEM_Y = (9 * TILE + 32) - personagem_parado.get_height()

# BOSS: animado (spritesheet), 4x maior e centralizado na arena, com hitbox
# de colisão pra tomar/dar dano depois (LUIGI)
CHAO_ARENA = 9 * TILE + 32
boss_frames = [pygame.transform.scale(f, (f.get_width() * 4, f.get_height() * 4)) for f in frames_boss]
boss_largura = boss_frames[0].get_width()
boss_altura = boss_frames[0].get_height()
boss_x = LARGURA_ARENA // 2 - boss_largura // 2
boss_y = CHAO_ARENA - boss_altura
boss_contador_frames = 0
boss_intervalo_frame = 12

boss = {
    "x": boss_x,
    "y": boss_y,
    "frames": boss_frames,
    "frame_atual": 0,
    "imagem": boss_frames[0],
    "hitbox": pygame.Rect(boss_x + int(boss_largura * 0.15), boss_y + int(boss_altura * 0.1), int(boss_largura * 0.7), int(boss_altura * 0.85)),
    "vivo": True
}
vida_boss_maxima = 100
vida_boss = vida_boss_maxima

print("DEBUG: boss_largura =", boss_largura, "boss_altura =", boss_altura)
print("DEBUG: boss_x =", boss_x, "boss_y =", boss_y)
print("DEBUG: LARGURA_ARENA =", LARGURA_ARENA)

#fade
fade_alpha = 255
fade_surface = pygame.Surface((1280, 720))
fade_surface.fill((0, 0, 0))

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not atacando:
                atacando = True
                atk_frame_atual = 0
                atk_contador_frames = 0

    clock.tick(60)
    dt = clock.get_time()

    teclas = pygame.key.get_pressed()
    movendo = False

    if not atacando and teclas[pygame.K_d]:
        personagem_x += 300 * dt / 1000
        virado_direita = True
        movendo = True

    if not atacando and teclas[pygame.K_a]:
        personagem_x -= 300 * dt / 1000
        virado_direita = False
        movendo = True

    personagem_x = max(0, personagem_x)
    personagem_x = min(personagem_x, LARGURA_ARENA - personagem_parado.get_width())

    # MORREU NA LUTA: reinicia só a batalha, sem voltar pro mapa inteiro (LUIGI)
    if vida_atual <= 0:
        coracoes -= 1
        vida_atual = vida_maxima
        if coracoes <= 0:
            coracoes = 3
            vida_atual = vida_maxima
            vida_boss = vida_boss_maxima
            boss["vivo"] = True
            personagem_x = ARENA_PERSONAGEM_X
            char1_y = ARENA_PERSONAGEM_Y
            velocidadechar1_y = 0

    #colisão horizontal
    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
    for bloco in collider_list:
        if collider_personagem.colliderect(bloco):
            if virado_direita:
                personagem_x = bloco.left - personagem_parado.get_width()
            else:
                personagem_x = bloco.right
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

    # ANIMAÇÃO DO BOSS (LUIGI)
    if boss["vivo"]:
        boss_contador_frames += 1
        if boss_contador_frames >= boss_intervalo_frame:
            boss_contador_frames = 0
            boss["frame_atual"] = (boss["frame_atual"] + 1) % len(boss["frames"])
            boss["imagem"] = boss["frames"][boss["frame_atual"]]

    # COLISÃO DO JOGADOR COM O BOSS: por enquanto só tira vida ao encostar (LUIGI)
    if boss["vivo"] and collider_personagem.colliderect(boss["hitbox"]):
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - tempo_ultimo_dano > 1000:
            vida_atual -= 25
            tempo_ultimo_dano = tempo_atual

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
    pes_y = int(char1_y) + personagem_parado.get_height()
    if atacando:
        atk_contador_frames += 1
        if atk_contador_frames >= atk_intervalo_frame:
            atk_contador_frames = 0
            atk_frame_atual += 1
            if atk_frame_atual >= len(frames_atacar):
                atacando = False
                atk_frame_atual = 0
        imagem_atual = frames_atacar[atk_frame_atual] if atacando else personagem_parado
        pos_y_desenho = pes_y - imagem_atual.get_height()
    elif not no_chao:
        imagem_atual = frames_pular[3]
        deslocamento_x_pulo = -20
        # pulo ainda usa ancoragem pelo topo (esse spritesheet não foi cortado
        # pelo contorno igual os outros, então usa o esquema antigo)
        pos_y_desenho = int(char1_y) - 60
    elif movendo and no_chao:
        contador_frames += 1
        if contador_frames >= intervalo_frame:
            contador_frames = 0
            frame_atual = (frame_atual + 1) % len(frames_andar)
        imagem_atual = frames_andar[frame_atual]
        pos_y_desenho = pes_y - imagem_atual.get_height()
    else:
        frame_atual = 0
        contador_frames = 0
        imagem_atual = personagem_parado
        pos_y_desenho = pes_y - imagem_atual.get_height()

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

    screen.blit(imagem_atual, (int(personagem_x) + deslocamento_x_pulo, pos_y_desenho))

    if boss["vivo"]:
        screen.blit(boss["imagem"], (boss["x"], boss["y"]))

    # CORAÇÕES E BARRA DE VIDA DO JOGADOR, IGUAL AO MAPA PRINCIPAL (LUIGI)
    for i in range(coracoes):
        screen.blit(img_bolha, (20 + (i * 35), 20))

    pygame.draw.rect(screen, (255, 215, 0), (18, 68, 204, 24), 3)
    pygame.draw.rect(screen, (0, 105, 148), (20, 70, vida_atual * 2, 20))

    # BARRA DE VIDA DO BOSS (LUIGI)
    largura_barra_boss = 400
    pygame.draw.rect(screen, (255, 215, 0), (1280 // 2 - largura_barra_boss // 2 - 3, 17, largura_barra_boss + 6, 24), 3)
    pygame.draw.rect(screen, (148, 0, 0), (1280 // 2 - largura_barra_boss // 2, 20, int(largura_barra_boss * vida_boss / vida_boss_maxima), 18))

    # fade de entrada
    if fade_alpha > 0:
        fade_alpha = max(0, fade_alpha - 3)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

    pygame.display.update()