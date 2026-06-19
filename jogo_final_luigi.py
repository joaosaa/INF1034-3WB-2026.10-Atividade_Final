import pygame, sys

pygame.init()

# Sounds(LUIGI)

pygame.mixer.init() 

# Trilha Sonora de fundo

pygame.mixer.music.load("sounds/TRILHA SONORA/Soundtrack.mp3") 
pygame.mixer.music.set_volume(0.090) 
pygame.mixer.music.play(-1) 

# SFX

som_passos = pygame.mixer.Sound("sounds/PASSOS NA PEDRA/PASSO.mpeg") 
som_pulo = pygame.mixer.Sound("sounds/PULO/jump.mp3") 
som_moeda = pygame.mixer.Sound("sounds/COLETAR MOEDA/Picked Coin Echo.wav") 
som_aterrissagem = pygame.mixer.Sound("sounds/ATERRISSAGEM (LANDING AFTER JUMP)/ATERRISSAGEM.mpeg") 

# Volume e canal

som_passos.set_volume(0.4) 
canal_passos = pygame.mixer.Channel(1) 

# Logica dos passos (som de passos toca enquanto o jogador estiver se movendo, e para quando ele parar)

def atualizar_sistema_sonoro(jogador_movendo): 
    if jogador_movendo: 
        if not canal_passos.get_busy(): 
            canal_passos.play(som_passos, loops=-1) 
    else: 
        canal_passos.stop() 




screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

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

    # ativação do som

    andando = teclas[pygame.K_d] or teclas[pygame.K_a] 
    atualizar_sistema_sonoro(andando) # atualiza o sistema sonoro com base no estado de movimento do jogador

    screen.fill((3, 18, 15))
    for i, camada in enumerate(camadas):
        deslocamento = int(camera_x * velocidades[i]) % 1280
        screen.blit(camada, (-deslocamento, 0))
        screen.blit(camada, (1280 - deslocamento, 0))














    pygame.display.update()