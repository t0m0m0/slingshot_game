import pygame
import math
import sys
import os
import random  # Added missing import for random module

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slingshot Physics Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)

# Physics parameters
GRAVITY = 0.3  # さらに重力を弱く
FRICTION = 0.97  # 摩擦をさらに減らす
ELASTICITY = 0.9  # 弾性をさらに高める

# Game states
AIMING = 0
PROJECTILE_IN_MOTION = 1
LEVEL_COMPLETE = 2
GAME_OVER = 3
WAITING_FOR_NEXT_SHOT = 4  # 新しいゲーム状態を追加

class Projectile:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = RED
        self.vel_x = 0
        self.vel_y = 0
        self.launched = False
        self.stopped = False
        self.trail = []  # For visual trail effect
        self.max_trail_length = 20
    
    def update(self):
        if self.launched and not self.stopped:
            # Store position for trail
            if len(self.trail) >= self.max_trail_length:
                self.trail.pop(0)
            self.trail.append((self.x, self.y))
            
            # Apply gravity
            self.vel_y += GRAVITY
            
            # Apply air resistance
            self.vel_x *= FRICTION
            self.vel_y *= FRICTION
            
            # Update position
            self.x += self.vel_x
            self.y += self.vel_y
            
            # Check if projectile has almost stopped
            if abs(self.vel_x) < 0.1 and abs(self.vel_y) < 0.1 and self.y > HEIGHT - self.radius - 10:
                self.stopped = True
            
            # Handle screen boundaries
            if self.x - self.radius < 0:
                self.x = self.radius
                self.vel_x *= -ELASTICITY
            elif self.x + self.radius > WIDTH:
                self.x = WIDTH - self.radius
                self.vel_x *= -ELASTICITY
                
            if self.y - self.radius < 0:
                self.y = self.radius
                self.vel_y *= -ELASTICITY
            elif self.y + self.radius > HEIGHT - 20:  # Ground level
                self.y = HEIGHT - 20 - self.radius
                self.vel_y *= -ELASTICITY * 0.8  # Less bounce on ground
                self.vel_x *= 0.9  # More friction on ground
    
    def draw(self, screen):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_radius = int(self.radius * (i / len(self.trail)) * 0.8)
            trail_surface = pygame.Surface((trail_radius*2, trail_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*self.color, alpha), (trail_radius, trail_radius), trail_radius)
            screen.blit(trail_surface, (trail_x - trail_radius, trail_y - trail_radius))
        
        # Draw projectile
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw a highlight for 3D effect
        highlight_radius = self.radius // 2
        pygame.draw.circle(screen, (255, 150, 150), (int(self.x - self.radius//3), int(self.y - self.radius//3)), highlight_radius)

class Target:
    def __init__(self, x, y, width=40, height=60):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = GREEN
        self.hit = False
        self.hit_animation = 0
    
    def check_collision(self, projectile):
        if self.hit:
            return False
            
        # Simple collision detection (circle vs rectangle)
        test_x = max(self.x, min(projectile.x, self.x + self.width))
        test_y = max(self.y, min(projectile.y, self.y + self.height))
        
        distance = math.sqrt((test_x - projectile.x)**2 + (test_y - projectile.y)**2)
        
        if distance < projectile.radius:
            self.hit = True
            return True
        return False
    
    def update(self):
        if self.hit:
            self.hit_animation += 1
    
    def draw(self, screen):
        if not self.hit:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Draw face
            eye_size = 5
            pygame.draw.circle(screen, BLACK, (int(self.x + self.width//3), int(self.y + self.height//3)), eye_size)
            pygame.draw.circle(screen, BLACK, (int(self.x + 2*self.width//3), int(self.y + self.height//3)), eye_size)
            pygame.draw.arc(screen, BLACK, (self.x + self.width//4, self.y + self.height//2, self.width//2, self.height//3), 0, math.pi, 2)
        else:
            # Hit animation
            if self.hit_animation < 20:
                # Falling animation
                fall_y = self.y + self.hit_animation * 2
                pygame.draw.rect(screen, self.color, (self.x, fall_y, self.width, self.height))
                # Sad face
                eye_size = 5
                pygame.draw.circle(screen, BLACK, (int(self.x + self.width//3), int(fall_y + self.height//3)), eye_size)
                pygame.draw.circle(screen, BLACK, (int(self.x + 2*self.width//3), int(fall_y + self.height//3)), eye_size)
                pygame.draw.arc(screen, BLACK, (self.x + self.width//4, fall_y + 2*self.height//3, self.width//2, self.height//3), math.pi, 2*math.pi, 2)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = BROWN
    
    def check_collision(self, projectile):
        # Simple collision detection (circle vs rectangle)
        test_x = max(self.x, min(projectile.x, self.x + self.width))
        test_y = max(self.y, min(projectile.y, self.y + self.height))
        
        distance = math.sqrt((test_x - projectile.x)**2 + (test_y - projectile.y)**2)
        
        if distance < projectile.radius:
            # Calculate collision response
            if abs(projectile.x - (self.x + self.width/2)) > abs(projectile.y - (self.y + self.height/2)):
                # Horizontal collision
                projectile.vel_x *= -ELASTICITY
                if projectile.x < self.x + self.width/2:
                    projectile.x = self.x - projectile.radius
                else:
                    projectile.x = self.x + self.width + projectile.radius
            else:
                # Vertical collision
                projectile.vel_y *= -ELASTICITY
                if projectile.y < self.y + self.height/2:
                    projectile.y = self.y - projectile.radius
                else:
                    projectile.y = self.y + self.height + projectile.radius
            return True
        return False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add wood texture effect
        for i in range(0, self.width, 10):
            pygame.draw.line(screen, (100, 50, 0), (self.x + i, self.y), (self.x + i, self.y + self.height), 1)

class Slingshot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 80
        self.band_color = (139, 69, 19)  # Brown
        self.base_color = (160, 82, 45)  # Sienna
    
    def draw(self, screen, projectile=None):
        # Draw slingshot base
        pygame.draw.rect(screen, self.base_color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        pygame.draw.circle(screen, self.base_color, (self.x, self.y - self.height//2), self.width//2)
        
        # Draw slingshot band (behind projectile)
        if projectile and not projectile.launched:
            pygame.draw.line(screen, self.band_color, (self.x - self.width//2, self.y - self.height//2), 
                            (projectile.x, projectile.y), 5)
            pygame.draw.line(screen, self.band_color, (self.x + self.width//2, self.y - self.height//2), 
                            (projectile.x, projectile.y), 5)

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.targets = []
        self.obstacles = []
        self.projectile_count = 5  # 弾の数を増やす (3→5)
        self.projectiles_used = 0
        
        # Set up level based on level number
        self.setup_level()
    
    def setup_level(self):
        if self.level_number == 1:
            # Level 1: Simple targets - ターゲットをさらに近づける
            self.targets = [
                Target(400, HEIGHT - 80),
                Target(450, HEIGHT - 80),
                Target(500, HEIGHT - 80)
            ]
        elif self.level_number == 2:
            # Level 2: Targets with obstacles - 配置を調整
            self.targets = [
                Target(450, HEIGHT - 80),
                Target(550, HEIGHT - 80)
            ]
            self.obstacles = [
                Obstacle(400, HEIGHT - 150, 20, 130),
                Obstacle(500, HEIGHT - 100, 100, 20)
            ]
        elif self.level_number == 3:
            # Level 3: More complex arrangement - 配置を調整
            self.targets = [
                Target(400, HEIGHT - 200),
                Target(500, HEIGHT - 300),
                Target(600, HEIGHT - 80)
            ]
            self.obstacles = [
                Obstacle(450, HEIGHT - 150, 20, 130),
                Obstacle(550, HEIGHT - 250, 100, 20),
                Obstacle(650, HEIGHT - 150, 20, 130)
            ]
    
    def is_complete(self):
        return all(target.hit for target in self.targets)
    
    def draw(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        for target in self.targets:
            target.draw(screen)

def draw_background(screen):
    # Sky gradient
    for y in range(HEIGHT):
        # Calculate color based on y position
        sky_color = (
            135 - int(y / HEIGHT * 50),
            206 - int(y / HEIGHT * 50),
            235 - int(y / HEIGHT * 100)
        )
        pygame.draw.line(screen, sky_color, (0, y), (WIDTH, y))
    
    # Ground
    ground_rect = pygame.Rect(0, HEIGHT - 20, WIDTH, 20)
    pygame.draw.rect(screen, (100, 80, 0), ground_rect)
    
    # Add some grass
    for i in range(0, WIDTH, 5):
        grass_height = random.randint(3, 7)
        pygame.draw.line(screen, (50, 150, 50), (i, HEIGHT - 20), (i, HEIGHT - 20 - grass_height), 2)
    
    # Add some clouds
    cloud_positions = [(100, 50), (300, 80), (500, 40), (700, 70)]
    for x, y in cloud_positions:
        draw_cloud(screen, x, y)

def draw_cloud(screen, x, y):
    cloud_color = (250, 250, 250)
    pygame.draw.circle(screen, cloud_color, (x, y), 20)
    pygame.draw.circle(screen, cloud_color, (x + 15, y - 10), 15)
    pygame.draw.circle(screen, cloud_color, (x + 30, y), 20)
    pygame.draw.circle(screen, cloud_color, (x + 15, y + 10), 15)

def draw_ui(screen, level, projectile_count, game_state):
    # Draw level info
    font = pygame.font.SysFont('Arial', 24)
    level_text = font.render(f"Level: {level.level_number}", True, BLACK)
    screen.blit(level_text, (20, 20))
    
    # Draw projectile count
    projectile_text = font.render(f"Projectiles: {projectile_count}", True, BLACK)
    screen.blit(projectile_text, (20, 50))
    
    # Draw instructions
    if game_state == AIMING:
        instruction_text = font.render("Drag to aim and release to fire", True, BLACK)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 20))
    elif game_state == WAITING_FOR_NEXT_SHOT:
        instruction_text = font.render("Next shot coming...", True, BLACK)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 20))
    
    # Draw restart instruction
    restart_text = font.render("Press 'R' to restart game", True, BLACK)
    screen.blit(restart_text, (WIDTH - restart_text.get_width() - 20, 20))
    
    # Draw game state messages
    if game_state == LEVEL_COMPLETE:
        message_text = font.render("Level Complete! Click to continue", True, GREEN)
        screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT//2))
    elif game_state == GAME_OVER:
        message_text = font.render("Game Over! Click to restart", True, RED)
        screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT//2))

def main():
    clock = pygame.time.Clock()
    
    # Initialize game objects
    slingshot = Slingshot(100, HEIGHT - 100)
    current_level = Level(1)
    projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
    projectile_count = current_level.projectile_count
    
    game_state = AIMING
    dragging = False
    
    # Function to restart the game
    def restart_game():
        nonlocal current_level, projectile, projectile_count, game_state
        current_level = Level(1)
        projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
        projectile_count = current_level.projectile_count
        game_state = AIMING
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart game when 'R' is pressed
                    restart_game()
                elif event.key == pygame.K_SPACE and game_state == WAITING_FOR_NEXT_SHOT:  # スペースキーでも次の弾を発射可能に
                    projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
                    game_state = AIMING
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # タイマーをキャンセル
            
            if event.type == pygame.USEREVENT and game_state == WAITING_FOR_NEXT_SHOT:
                projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
                game_state = AIMING
                pygame.time.set_timer(pygame.USEREVENT, 0)  # タイマーをキャンセル
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == AIMING and not projectile.launched:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Check if clicked near the projectile
                    if math.sqrt((mouse_x - projectile.x)**2 + (mouse_y - projectile.y)**2) < 50:
                        dragging = True
                elif game_state == LEVEL_COMPLETE:
                    # Go to next level
                    current_level = Level(current_level.level_number + 1)
                    projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
                    projectile_count = current_level.projectile_count
                    game_state = AIMING
                elif game_state == GAME_OVER:
                    # Restart game
                    restart_game()
            
            if event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                # Launch projectile
                mouse_x, mouse_y = pygame.mouse.get_pos()
                power = min(30, math.sqrt((mouse_x - slingshot.x)**2 + (mouse_y - (slingshot.y - slingshot.height//2))**2) / 6)  # パワーをさらに増加
                angle = math.atan2((slingshot.y - slingshot.height//2) - mouse_y, slingshot.x - mouse_x)
                
                projectile.vel_x = math.cos(angle) * power
                projectile.vel_y = math.sin(angle) * power
                projectile.launched = True
                projectile_count -= 1
                game_state = PROJECTILE_IN_MOTION
        
        # Update game objects
        if game_state == AIMING and dragging and not projectile.launched:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Limit the drag distance
            max_drag = 150  # ドラッグ距離を増加
            dx = slingshot.x - mouse_x
            dy = (slingshot.y - slingshot.height//2) - mouse_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > max_drag:
                scale = max_drag / distance
                mouse_x = slingshot.x - dx * scale
                mouse_y = (slingshot.y - slingshot.height//2) - dy * scale
            
            projectile.x = mouse_x
            projectile.y = mouse_y
        elif game_state == PROJECTILE_IN_MOTION:
            projectile.update()
            
            # Check for collisions with obstacles
            for obstacle in current_level.obstacles:
                obstacle.check_collision(projectile)
            
            # Check for collisions with targets
            for target in current_level.targets:
                target.check_collision(projectile)
                target.update()
            
            # Check if level is complete
            if current_level.is_complete():
                game_state = LEVEL_COMPLETE
            
            # Check if projectile has stopped
            if projectile.stopped or projectile.x < 0 or projectile.x > WIDTH or projectile.y > HEIGHT:
                if projectile_count > 0:
                    # Reset for next shot - 3秒後に自動的に次の弾をセット
                    pygame.time.set_timer(pygame.USEREVENT, 1000)  # 1秒後にイベント発生
                    game_state = WAITING_FOR_NEXT_SHOT
                else:
                    # Check if all targets are hit
                    if not current_level.is_complete():
                        game_state = GAME_OVER
        
        # Draw everything
        draw_background(screen)
        
        # Draw slingshot
        slingshot.draw(screen, projectile if game_state == AIMING and not projectile.launched else None)
        
        # Draw level objects
        current_level.draw(screen)
        
        # Draw projectile
        projectile.draw(screen)
        
        # Draw UI
        draw_ui(screen, current_level, projectile_count, game_state)
        
        # Draw aiming line
        if game_state == AIMING and dragging and not projectile.launched:
            pygame.draw.line(screen, BLACK, (slingshot.x, slingshot.y - slingshot.height//2), 
                            (projectile.x, projectile.y), 2)
            
            # Draw projected trajectory (simple prediction)
            power = min(30, math.sqrt((projectile.x - slingshot.x)**2 + (projectile.y - (slingshot.y - slingshot.height//2))**2) / 6)
            angle = math.atan2((slingshot.y - slingshot.height//2) - projectile.y, slingshot.x - projectile.x)
            vel_x = math.cos(angle) * power
            vel_y = math.sin(angle) * power
            
            # Draw trajectory dots
            for t in range(1, 30):  # 予測軌道を長くする (20→30)
                # Simple physics prediction (not accounting for bounces)
                pred_x = projectile.x + vel_x * t
                pred_y = projectile.y + vel_y * t + 0.5 * GRAVITY * t * t
                
                # Stop if prediction goes off screen
                if pred_x < 0 or pred_x > WIDTH or pred_y < 0 or pred_y > HEIGHT:
                    break
                
                # Draw prediction dot
                alpha = 255 - t * 8  # 透明度の減少を緩やかに (10→8)
                if alpha > 0:
                    dot_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(dot_surface, (200, 200, 200, alpha), (3, 3), 3)
                    screen.blit(dot_surface, (pred_x - 3, pred_y - 3))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
