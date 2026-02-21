import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 30)

# --- Player ---
player_pos = [WIDTH // 2, HEIGHT // 5]
player_speed = 5
player_health = 100

# --- Lists ---
bullets = []
zombies = []

# --- Zombie spawn timer ---
spawn_timer = 0


def spawn_zombie():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return [random.randint(0, WIDTH), 0]
    if side == "bottom":
        return [random.randint(0, WIDTH), HEIGHT]
    if side == "left":
        return [0, random.randint(0, HEIGHT)]
    if side == "right":
        return [WIDTH, random.randint(0, HEIGHT)]


running = True
game_over = False

while running:
    clock.tick(60)
    screen.fill((20, 20, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = pygame.mouse.get_pos()
            dx = mx - player_pos[0]
            dy = my - player_pos[1]
            angle = math.atan2(dy, dx)
            bullets.append([
                player_pos[0],
                player_pos[1],
                math.cos(angle) * 10,
                math.sin(angle) * 10
            ])

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

    # --- Spawn zombies ---
    if not game_over:
        spawn_timer += 1
        if spawn_timer > 60:
            zombies.append(spawn_zombie())
            spawn_timer = 0

    # --- Update bullets ---
    for bullet in bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

        if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
            bullets.remove(bullet)

    # --- Update zombies ---
    for zombie in zombies[:]:
        dx = player_pos[0] - zombie[0]
        dy = player_pos[1] - zombie[1]
        dist = math.hypot(dx, dy)

        if dist != 0:
            zombie[0] += dx / dist * 1.5
            zombie[1] += dy / dist * 1.5

        # Zombie hits player
        if dist < 20:
            player_health -= 0.5
            if player_health <= 0:
                game_over = True

        # Bullet hits zombie
        for bullet in bullets[:]:
            if math.hypot(bullet[0] - zombie[0], bullet[1] - zombie[1]) < 15:
                if zombie in zombies:
                    zombies.remove(zombie)
                if bullet in bullets:
                    bullets.remove(bullet)

    # --- Draw player ---
    pygame.draw.circle(screen, (50, 200, 255), player_pos, 15)

    # --- Draw bullets ---
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 5)

    # --- Draw zombies ---
    for zombie in zombies:
        pygame.draw.circle(screen, (0, 200, 0), (int(zombie[0]), int(zombie[1])), 15)

    # --- Health bar ---
    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 255, 0), (20, 20, 2 * player_health, 20))

    if game_over:
        text = font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()