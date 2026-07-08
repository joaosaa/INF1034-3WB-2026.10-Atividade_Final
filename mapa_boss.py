import pygame, sys
import math

# TRILHA SONORA DO BOSS (LUIGI)
pygame.mixer.music.load("sounds\TRILHA SONORA\FINAL BOSS\Final Boss.mp3")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

#spritesheet (mergulhador com tridente)
spritesheet_andar = pygame.image.load('Characters/spritesheet_andando_tridente.png').convert_alpha()
escala = 0.35

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
ataque_acertou_boss = False
DANO_ATAQUE_TRIDENTE = 5
FRAMES_ATIVOS_ATAQUE = [2, 3, 4, 5]

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
    "                    ",
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
forca_pulo = -18
no_chao = True
virado_direita = True

# POSIÇÃO INICIAL DO JOGADOR NA ARENA, PRA RESPAWNAR AQUI SE MORRER (LUIGI)
ARENA_PERSONAGEM_X = 100.0
ARENA_PERSONAGEM_Y = (9 * TILE + 32) - personagem_parado.get_height()

CHAO_ARENA = 9 * TILE + 32
boss_frames = [pygame.transform.scale(f, (int(f.get_width() * 0.9), int(f.get_height() * 0.9))) for f in frames_boss]

CENTRO_BOSS_X = LARGURA_ARENA // 2
DISTANCIA_LADO = 400          
DURACAO_PREPARO_MS = 400    
DURACAO_INVESTIDA_MS = 850   
INTERVALO_PARADO_MS = 2000    
VIDA_FASE_2_BOSS = 50
DURACAO_PREPARO_FASE_2_MS = 300
DURACAO_INVESTIDA_FASE_2_MS = 620
INTERVALO_PARADO_FASE_2_MS = 1200

# QUEDA DE ENTRADA: o boss fica fora do mapa por um tempo e depois cai do céu
TEMPO_ATE_QUEDA_BOSS_MS = 5000
DURACAO_QUEDA_BOSS_MS = 600
ALTURA_QUEDA_BOSS = 750
PONTO_QUEDA_FIXO = 350  # deslocamento do centro da arena; positivo = mais pra direita
tempo_inicio_mapa = pygame.time.get_ticks()

# Hitbox mais baixa: assim o boss acerta quem esta no chao,
# mas nao pega o jogador quando ele esta em cima da plataforma.
HITBOX_BOSS_LARGURA = 240
HITBOX_BOSS_ALTURA = 120
hitbox_boss_y = CHAO_ARENA - HITBOX_BOSS_ALTURA

boss = {
    "estado": "aguardando",   
    "lado": -1,               
    "lado_destino": 1,
    "x_origem": CENTRO_BOSS_X - DISTANCIA_LADO,
    "x_destino": CENTRO_BOSS_X + DISTANCIA_LADO,
    "inicio_fase": 0,
    "proxima_acao": pygame.time.get_ticks() + INTERVALO_PARADO_MS,
    "frame_atual": 0,
    "deslocamento_x": -DISTANCIA_LADO,
    "posicao_atual": -DISTANCIA_LADO,
    "deslocamento_pouso": -DISTANCIA_LADO,
    "imagem": boss_frames[0],
    "hitbox": pygame.Rect(CENTRO_BOSS_X - DISTANCIA_LADO - HITBOX_BOSS_LARGURA // 2, hitbox_boss_y, HITBOX_BOSS_LARGURA, HITBOX_BOSS_ALTURA),
    "vivo": True,
    "tempo_idle": 0,
    "offset_y": 0,
    "y_extra": -ALTURA_QUEDA_BOSS
}
vida_boss_maxima = 100
vida_boss = vida_boss_maxima
DANO_INVESTIDA_BOSS = 25
COOLDOWN_DANO_BOSS_MS = 1000
tempo_ultimo_dano_boss = pygame.time.get_ticks()

#fade
fade_alpha = 255
fade_surface = pygame.Surface((1280, 720))
fade_surface.fill((0, 0, 0))

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if estado_jogo == "DERROTA" and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                canal_passos.stop()
                exec(open("jogo_final.py", encoding="utf-8").read())
                sys.exit()
        if estado_jogo == "VITORIA" and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if not pontuacao_salva:
                    salvar_pontuacao(nome_jogador, pontuacao)
                    pontuacao_salva = True
                canal_passos.stop()
                exec(open("jogo_final.py", encoding="utf-8").read())
                sys.exit()
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if estado_jogo != "DERROTA" and not atacando:
                atacando = True
                atk_frame_atual = 0
                atk_contador_frames = 0
                ataque_acertou_boss = False

    clock.tick(60)
    dt = clock.get_time()

    teclas = pygame.key.get_pressed()
    movendo = False

    if estado_jogo != "DERROTA" and not atacando and teclas[pygame.K_d]:
        personagem_x += 300 * dt / 1000
        virado_direita = True
        movendo = True

    if estado_jogo != "DERROTA" and not atacando and teclas[pygame.K_a]:
        personagem_x -= 300 * dt / 1000
        virado_direita = False
        movendo = True

    personagem_x = max(0, personagem_x)
    personagem_x = min(personagem_x, LARGURA_ARENA - personagem_parado.get_width())

    if vida_atual <= 0:
        coracoes -= 1
        vida_atual = vida_maxima
        if coracoes <= 0:
            estado_jogo = "DERROTA"
            pontuacao = 0
            vida_atual = 0
            canal_passos.stop()
        else:
            personagem_x = ARENA_PERSONAGEM_X
            char1_y = ARENA_PERSONAGEM_Y
            velocidadechar1_y = 0
            tempo_ultimo_dano_boss = pygame.time.get_ticks()

    #colisão horizontal
    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())
    for bloco in collider_list:
        if collider_personagem.colliderect(bloco):
            if virado_direita:
                personagem_x = bloco.left - personagem_parado.get_width()
            else:
                personagem_x = bloco.right
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

    if boss["vivo"]:
        agora = pygame.time.get_ticks()
        if vida_boss <= VIDA_FASE_2_BOSS:
            duracao_preparo_atual = DURACAO_PREPARO_FASE_2_MS
            duracao_investida_atual = DURACAO_INVESTIDA_FASE_2_MS
            intervalo_parado_atual = INTERVALO_PARADO_FASE_2_MS
        else:
            duracao_preparo_atual = DURACAO_PREPARO_MS
            duracao_investida_atual = DURACAO_INVESTIDA_MS
            intervalo_parado_atual = INTERVALO_PARADO_MS

        if boss["estado"] == "aguardando":
            if agora - tempo_inicio_mapa >= TEMPO_ATE_QUEDA_BOSS_MS:
                boss["estado"] = "caindo"
                boss["inicio_fase"] = agora
                # ponto fixo de queda: perto da parede direita, com uma margem
                deslocamento_alvo = PONTO_QUEDA_FIXO
                boss["lado"] = -1 if deslocamento_alvo < 0 else 1
                boss["deslocamento_x"] = deslocamento_alvo
                boss["deslocamento_pouso"] = deslocamento_alvo
                boss["frame_atual"] = 0

        elif boss["estado"] == "caindo":
            progresso = (agora - boss["inicio_fase"]) / DURACAO_QUEDA_BOSS_MS
            if progresso >= 1:
                progresso = 1
                boss["estado"] = "parado"
                pygame.mixer.Sound("sounds\TRILHA SONORA\FINAL BOSS\queda_monstro.mp3").play()
                boss["proxima_acao"] = agora + intervalo_parado_atual
            boss["y_extra"] = -ALTURA_QUEDA_BOSS * (1 - progresso)
            boss["deslocamento_x"] = boss["deslocamento_pouso"]
            boss["posicao_atual"] = boss["deslocamento_pouso"]
            boss["frame_atual"] = 0

        elif boss["estado"] == "parado":
            boss["frame_atual"] = 0
            boss["deslocamento_x"] = boss["posicao_atual"]
            if agora >= boss["proxima_acao"]:
                boss["estado"] = "preparando"
                boss["lado_destino"] = boss["lado"] * -1
                boss["inicio_fase"] = agora

        elif boss["estado"] == "preparando":
            progresso = (agora - boss["inicio_fase"]) / duracao_preparo_atual
            if progresso >= 1:
                progresso = 1
                boss["estado"] = "investindo"
                boss["x_origem"] = boss["posicao_atual"]
                boss["x_destino"] = boss["lado_destino"] * DISTANCIA_LADO
                boss["inicio_fase"] = agora
            boss["frame_atual"] = min(3, int(progresso * 4))
            boss["deslocamento_x"] = boss["posicao_atual"]

        elif boss["estado"] == "investindo":
            progresso = (agora - boss["inicio_fase"]) / duracao_investida_atual
            if progresso >= 1:
                progresso = 1
                boss["lado"] = boss["lado_destino"]
                boss["posicao_atual"] = boss["x_destino"]
                boss["estado"] = "parado"
                boss["proxima_acao"] = agora + intervalo_parado_atual

            boss["deslocamento_x"] = boss["x_origem"] + (boss["x_destino"] - boss["x_origem"]) * progresso
            boss["frame_atual"] = 3

        boss["imagem"] = boss_frames[boss["frame_atual"]]
        if boss["estado"] in ("preparando", "investindo"):
            direcao_atual = boss["lado_destino"]
        else:
            direcao_atual = boss["lado"] * -1  # parado: encara pra dentro da arena
        if direcao_atual > 0:
            boss["imagem"] = pygame.transform.flip(boss["imagem"], True, False)

        boss["hitbox"].centerx = CENTRO_BOSS_X + int(boss["deslocamento_x"])
        if boss["estado"] == "parado":
         boss["tempo_idle"] += 0.12
         boss["offset_y"] = math.sin(boss["tempo_idle"]) * 6
        else:
         boss["offset_y"] = 0

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

    collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

    # ATAQUE DO TRIDENTE: durante os frames ativos, cria uma hitbox na frente do jogador.
    if boss["vivo"] and boss["estado"] not in ("aguardando", "caindo") and atacando and not ataque_acertou_boss and atk_frame_atual in FRAMES_ATIVOS_ATAQUE:
        alcance_tridente = 150
        altura_tridente = 80
        if virado_direita:
            hitbox_ataque = pygame.Rect(collider_personagem.right - 10, collider_personagem.centery - altura_tridente // 2, alcance_tridente, altura_tridente)
        else:
            hitbox_ataque = pygame.Rect(collider_personagem.left - alcance_tridente + 10, collider_personagem.centery - altura_tridente // 2, alcance_tridente, altura_tridente)

        if hitbox_ataque.colliderect(boss["hitbox"]):
            vida_boss -= DANO_ATAQUE_TRIDENTE
            ataque_acertou_boss = True
            if vida_boss <= 0:
                vida_boss = 0
                boss["vivo"] = False
                boss_morto = True
                estado_jogo = "VITORIA"
                canal_passos.stop()
                pontuacao += 500

    # COLISAO DO BOSS: encostar bloqueia o jogador; na investida tambem tira vida.
    if boss["vivo"] and boss["estado"] not in ("aguardando", "caindo") and collider_personagem.colliderect(boss["hitbox"]):
        x_antes_do_empurrao = personagem_x

        if collider_personagem.centerx < boss["hitbox"].centerx:
            personagem_x = boss["hitbox"].left - personagem_parado.get_width()
        else:
            personagem_x = boss["hitbox"].right

        personagem_x = max(0, min(personagem_x, LARGURA_ARENA - personagem_parado.get_width()))
        collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

        empurrou_para_dentro_do_bloco = False
        for bloco in collider_list:
            if collider_personagem.colliderect(bloco):
                empurrou_para_dentro_do_bloco = True

        if empurrou_para_dentro_do_bloco:
            personagem_x = x_antes_do_empurrao
            collider_personagem = pygame.Rect(int(personagem_x), int(char1_y), personagem_parado.get_width(), personagem_parado.get_height())

        if boss["estado"] == "investindo":
            agora = pygame.time.get_ticks()
            if agora - tempo_ultimo_dano_boss > COOLDOWN_DANO_BOSS_MS:
                vida_atual -= DANO_INVESTIDA_BOSS
                tempo_ultimo_dano_boss = agora
                velocidadechar1_y = -8

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

    if boss["vivo"]:
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

        boss_img = boss["imagem"]
        boss_pos_x = CENTRO_BOSS_X - boss_img.get_width() // 2 + int(boss["deslocamento_x"])
        boss_pos_y = CHAO_ARENA - boss_img.get_height() + boss["offset_y"] + boss.get("y_extra", 0)
        screen.blit(boss_img, (boss_pos_x, boss_pos_y))

        # CORAÇÕES E BARRA DE VIDA DO JOGADOR, IGUAL AO MAPA PRINCIPAL (LUIGI)
        for i in range(coracoes):
            screen.blit(img_bolha, (20 + (i * 35), 20))

        pygame.draw.rect(screen, (255, 215, 0), (18, 68, 204, 24), 3)
        pygame.draw.rect(screen, (0, 105, 148), (20, 70, vida_atual * 2, 20))

        # BARRA DE VIDA DO BOSS (LUIGI)
        largura_barra_boss = 400
        pygame.draw.rect(screen, (255, 215, 0), (1280 // 2 - largura_barra_boss // 2 - 3, 17, largura_barra_boss + 6, 24), 3)
        pygame.draw.rect(screen, (148, 0, 0), (1280 // 2 - largura_barra_boss // 2, 20, int(largura_barra_boss * vida_boss / vida_boss_maxima), 18))

    else:
        texto_vitoria = fonte_telas.render("VOCE VENCEU!", True, (0, 255, 0))
        texto_pontos = fonte_hud.render("Pontuacao Final: " + str(pontuacao), True, (255, 215, 0))
        texto_voltar = fonte_hud.render("ENTER - Continuar", True, (255, 255, 255))
        screen.blit(texto_vitoria, (1280 // 2 - texto_vitoria.get_width() // 2, 720 // 2 - 100))
        screen.blit(texto_pontos, (1280 // 2 - texto_pontos.get_width() // 2, 720 // 2 + 50))
        screen.blit(texto_voltar, (1280 // 2 - texto_voltar.get_width() // 2, 720 // 2 + 140))

    # fade de entrada
    if fade_alpha > 0:
        fade_alpha = max(0, fade_alpha - 3)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

    pygame.display.update()