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
ORANGE = (255, 165, 0)  # 弾のトレイル用
YELLOW = (255, 255, 0)  # 効果用

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
        self.max_trail_length = 30  # トレイルを長くする
        self.collision_particles = []  # 衝突時のパーティクル
    
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
            if (abs(self.vel_x) < 0.5 and abs(self.vel_y) < 0.5 and self.y > HEIGHT - self.radius - 30) or \
               (abs(self.vel_x) < 0.2 and abs(self.vel_y) < 0.2):  # 停止判定を緩和
                self.stopped = True
                # 停止時にパーティクルを生成
                self.generate_collision_particles()
                print("Projectile stopped")  # デバッグ用
            
            # Handle screen boundaries
            if self.x - self.radius < 0:
                self.x = self.radius
                self.vel_x *= -ELASTICITY
                self.generate_collision_particles()
            elif self.x + self.radius > WIDTH:
                self.x = WIDTH - self.radius
                self.vel_x *= -ELASTICITY
                self.generate_collision_particles()
                
            if self.y - self.radius < 0:
                self.y = self.radius
                self.vel_y *= -ELASTICITY
                self.generate_collision_particles()
            elif self.y + self.radius > HEIGHT - 20:  # Ground level
                self.y = HEIGHT - 20 - self.radius
                self.vel_y *= -ELASTICITY * 0.8  # Less bounce on ground
                self.vel_x *= 0.9  # More friction on ground
                self.generate_collision_particles()
        
        # パーティクルの更新
        for i in range(len(self.collision_particles) - 1, -1, -1):
            particle = self.collision_particles[i]
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.collision_particles.pop(i)
            else:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.1  # パーティクルにも重力を適用
    
    def generate_collision_particles(self):
        # 衝突時のパーティクルを生成
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.collision_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'radius': random.uniform(2, 5),
                'color': (255, random.randint(100, 200), 0),  # オレンジ〜黄色
                'life': random.randint(10, 30)
            })
    
    def draw(self, screen):
        # Draw trail with gradient color
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_radius = int(self.radius * (i / len(self.trail)) * 0.8)
            
            # グラデーションカラーを計算（赤からオレンジへ）
            r = 255
            g = int(165 * (i / len(self.trail)))
            b = 0
            
            trail_surface = pygame.Surface((trail_radius*2, trail_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (r, g, b, alpha), (trail_radius, trail_radius), trail_radius)
            screen.blit(trail_surface, (trail_x - trail_radius, trail_y - trail_radius))
        
        # Draw projectile with glow effect
        glow_radius = self.radius * 1.5
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        for r in range(int(glow_radius), 0, -2):
            alpha = 100 if r > self.radius else 200
            pygame.draw.circle(glow_surface, (*self.color[:3], alpha), (glow_radius, glow_radius), r)
        screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
        
        # Draw projectile
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw a highlight for 3D effect
        highlight_radius = self.radius // 2
        pygame.draw.circle(screen, (255, 150, 150), (int(self.x - self.radius//3), int(self.y - self.radius//3)), highlight_radius)
        
        # パーティクルを描画
        for particle in self.collision_particles:
            alpha = int(255 * (particle['life'] / 30))
            particle_surface = pygame.Surface((particle['radius']*2, particle['radius']*2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'], alpha), 
                (particle['radius'], particle['radius']), 
                particle['radius']
            )
            screen.blit(particle_surface, (particle['x'] - particle['radius'], particle['y'] - particle['radius']))

class Target:
    def __init__(self, x, y, width=40, height=60):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = GREEN
        self.hit = False
        self.hit_animation = 0
        self.particles = []  # ヒット時のパーティクル
        self.rotation = 0  # 回転角度
        self.eyes_blink = 0  # 目のまばたき
        self.blink_timer = random.randint(50, 150)  # まばたきタイマー
    
    def check_collision(self, projectile):
        if self.hit:
            return False
            
        # Simple collision detection (circle vs rectangle)
        test_x = max(self.x, min(projectile.x, self.x + self.width))
        test_y = max(self.y, min(projectile.y, self.y + self.height))
        
        distance = math.sqrt((test_x - projectile.x)**2 + (test_y - projectile.y)**2)
        
        if distance < projectile.radius:
            self.hit = True
            # ヒット時にパーティクルを生成
            self.generate_hit_particles()
            return True
        return False
    
    def generate_hit_particles(self):
        # ヒット時のパーティクルを生成
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            self.particles.append({
                'x': self.x + self.width/2,
                'y': self.y + self.height/2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'radius': random.uniform(2, 6),
                'color': (0, random.randint(200, 255), 0),  # 緑色のパーティクル
                'life': random.randint(20, 40)
            })
    
    def update(self):
        if self.hit:
            self.hit_animation += 1
            self.rotation += 5  # ヒット時に回転
            
            # パーティクルの更新
            for i in range(len(self.particles) - 1, -1, -1):
                particle = self.particles[i]
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.particles.pop(i)
                else:
                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    particle['vy'] += 0.2  # 重力
        else:
            # まばたきの処理
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.eyes_blink = 10  # まばたき時間
                self.blink_timer = random.randint(100, 200)
            
            if self.eyes_blink > 0:
                self.eyes_blink -= 1
    
    def draw(self, screen):
        if not self.hit:
            # 通常の描画
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # 目の描画（まばたき対応）
            eye_size = 5
            if self.eyes_blink <= 0:
                # 通常の目
                pygame.draw.circle(screen, BLACK, (int(self.x + self.width//3), int(self.y + self.height//3)), eye_size)
                pygame.draw.circle(screen, BLACK, (int(self.x + 2*self.width//3), int(self.y + self.height//3)), eye_size)
                # 白目のハイライト
                pygame.draw.circle(screen, WHITE, (int(self.x + self.width//3) + 2, int(self.y + self.height//3) - 2), 2)
                pygame.draw.circle(screen, WHITE, (int(self.x + 2*self.width//3) + 2, int(self.y + self.height//3) - 2), 2)
            else:
                # まばたき中
                pygame.draw.line(screen, BLACK, 
                                (int(self.x + self.width//3) - eye_size, int(self.y + self.height//3)),
                                (int(self.x + self.width//3) + eye_size, int(self.y + self.height//3)), 2)
                pygame.draw.line(screen, BLACK, 
                                (int(self.x + 2*self.width//3) - eye_size, int(self.y + self.height//3)),
                                (int(self.x + 2*self.width//3) + eye_size, int(self.y + self.height//3)), 2)
            
            # 口の描画
            pygame.draw.arc(screen, BLACK, (self.x + self.width//4, self.y + self.height//2, self.width//2, self.height//3), 0, math.pi, 2)
        else:
            # ヒットアニメーション
            if self.hit_animation < 40:  # アニメーション時間を延長
                # 回転して落下するアニメーション
                fall_y = self.y + self.hit_animation * 2
                
                # 回転の中心点を計算
                center_x = self.x + self.width/2
                center_y = fall_y + self.height/2
                
                # 回転した矩形を描画するための準備
                target_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(target_surface, self.color, (5, 5, self.width, self.height))
                
                # 目（×印）
                pygame.draw.line(target_surface, BLACK, (self.width//3, self.height//3), (self.width//3 + 10, self.height//3 + 10), 2)
                pygame.draw.line(target_surface, BLACK, (self.width//3 + 10, self.height//3), (self.width//3, self.height//3 + 10), 2)
                
                pygame.draw.line(target_surface, BLACK, (2*self.width//3, self.height//3), (2*self.width//3 + 10, self.height//3 + 10), 2)
                pygame.draw.line(target_surface, BLACK, (2*self.width//3 + 10, self.height//3), (2*self.width//3, self.height//3 + 10), 2)
                
                # 悲しい口
                pygame.draw.arc(target_surface, BLACK, (self.width//4, 2*self.height//3, self.width//2, self.height//3), math.pi, 2*math.pi, 2)
                
                # 回転
                rotated_surface = pygame.transform.rotate(target_surface, self.rotation)
                rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))
                screen.blit(rotated_surface, rotated_rect.topleft)
            
            # パーティクルを描画
            for particle in self.particles:
                alpha = int(255 * (particle['life'] / 40))
                particle_surface = pygame.Surface((particle['radius']*2, particle['radius']*2), pygame.SRCALPHA)
                pygame.draw.circle(
                    particle_surface, 
                    (*particle['color'], alpha), 
                    (particle['radius'], particle['radius']), 
                    particle['radius']
                )
                screen.blit(particle_surface, (particle['x'] - particle['radius'], particle['y'] - particle['radius']))

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
        self.band_stretch = 0  # バンドの伸縮アニメーション用
    
    def draw(self, screen, projectile=None):
        # バンドの伸縮アニメーション
        self.band_stretch = math.sin(pygame.time.get_ticks() / 200) * 2
        
        # Draw slingshot base with wood texture
        base_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        pygame.draw.rect(screen, self.base_color, base_rect)
        
        # 木目テクスチャ
        for i in range(0, self.height, 5):
            wood_color = (
                min(255, self.base_color[0] + random.randint(-20, 20)),
                min(255, self.base_color[1] + random.randint(-20, 20)),
                min(255, self.base_color[2] + random.randint(-20, 20))
            )
            pygame.draw.line(
                screen, 
                wood_color, 
                (self.x - self.width//2, self.y - self.height//2 + i),
                (self.x + self.width//2, self.y - self.height//2 + i)
            )
        
        # 上部の丸みを帯びた部分
        pygame.draw.circle(screen, self.base_color, (self.x, self.y - self.height//2), self.width//2)
        
        # Draw slingshot band (behind projectile)
        if projectile and not projectile.launched:
            # バンドの描画（より自然な曲線）
            band_points1 = [
                (self.x - self.width//2, self.y - self.height//2),
                (self.x - self.width//4, self.y - self.height//4),
                (projectile.x, projectile.y)
            ]
            band_points2 = [
                (self.x + self.width//2, self.y - self.height//2),
                (self.x + self.width//4, self.y - self.height//4),
                (projectile.x, projectile.y)
            ]
            
            # バンドの影
            shadow_color = (100, 50, 0, 150)
            pygame.draw.lines(screen, shadow_color, False, band_points1, 6)
            pygame.draw.lines(screen, shadow_color, False, band_points2, 6)
            
            # バンド本体
            pygame.draw.lines(screen, self.band_color, False, band_points1, 5)
            pygame.draw.lines(screen, self.band_color, False, band_points2, 5)
        else:
            # 静止状態のバンド（少し揺れる）
            band_y_offset = self.band_stretch
            pygame.draw.line(
                screen, 
                self.band_color, 
                (self.x - self.width//2, self.y - self.height//2),
                (self.x + self.width//2, self.y - self.height//2 + band_y_offset), 
                5
            )
        
        # 装飾的な要素（金属部品など）
        metal_color = (200, 200, 200)
        pygame.draw.circle(screen, metal_color, (self.x, self.y - self.height//2), 5)
        pygame.draw.rect(screen, metal_color, (self.x - 5, self.y + self.height//3, 10, 5))

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
    # Sky gradient with time of day effect
    time_factor = (math.sin(pygame.time.get_ticks() / 50000) + 1) / 2  # 時間による変化（ゆっくり）
    
    for y in range(HEIGHT):
        # Calculate color based on y position with time factor
        sky_color = (
            int(135 - y / HEIGHT * 50 + time_factor * 20),
            int(206 - y / HEIGHT * 50 - time_factor * 30),
            int(235 - y / HEIGHT * 100 + time_factor * 20)
        )
        # 色の範囲を制限
        sky_color = tuple(max(0, min(255, c)) for c in sky_color)
        pygame.draw.line(screen, sky_color, (0, y), (WIDTH, y))
    
    # 太陽または月
    sun_radius = 40
    sun_x = WIDTH * (0.2 + time_factor * 0.6)  # 左から右へ移動
    sun_y = HEIGHT * (0.3 - time_factor * 0.2)  # 高さも少し変化
    
    # 太陽/月のグラデーション
    for r in range(sun_radius, 0, -1):
        sun_color = (
            int(255 - (sun_radius - r) * 2),
            int(255 - (sun_radius - r) * 5 - time_factor * 100),
            int(200 - time_factor * 150)
        )
        sun_color = tuple(max(0, min(255, c)) for c in sun_color)
        pygame.draw.circle(screen, sun_color, (int(sun_x), int(sun_y)), r)
    
    # 雲を描画（動かす）
    cloud_positions = [
        (100 + (pygame.time.get_ticks() / 100) % WIDTH, 50),
        (300 + (pygame.time.get_ticks() / 120) % WIDTH, 80),
        (500 + (pygame.time.get_ticks() / 80) % WIDTH, 40),
        (700 + (pygame.time.get_ticks() / 150) % WIDTH, 70)
    ]
    
    for x, y in cloud_positions:
        x = x % (WIDTH + 100) - 50  # 画面外から入ってくるように
        draw_cloud(screen, x, y)
    
    # 遠景の山
    mountain_color = (100, 100, 100)
    for i in range(3):
        mountain_height = HEIGHT * 0.3 * (i + 1) / 3
        for x in range(0, WIDTH, WIDTH//3):
            offset = (i * 100 + x) % 200
            points = [
                (x - 100, HEIGHT),
                (x + offset, HEIGHT - mountain_height),
                (x + 200, HEIGHT)
            ]
            pygame.draw.polygon(screen, mountain_color, points)
    
    # Ground with texture
    ground_rect = pygame.Rect(0, HEIGHT - 20, WIDTH, 20)
    pygame.draw.rect(screen, (100, 80, 0), ground_rect)
    
    # Add some grass (静的な草に戻す)
    for i in range(0, WIDTH, 5):
        grass_height = random.randint(3, 7)
        grass_color = (50, 150 + random.randint(-20, 20), 50)
        pygame.draw.line(
            screen, 
            grass_color, 
            (i, HEIGHT - 20), 
            (i, HEIGHT - 20 - grass_height), 
            2
        )

def draw_cloud(screen, x, y):
    cloud_color = (250, 250, 250, 200)  # 半透明の雲
    cloud_surface = pygame.Surface((100, 50), pygame.SRCALPHA)
    
    # より自然な雲の形
    pygame.draw.circle(cloud_surface, cloud_color, (20, 25), 20)
    pygame.draw.circle(cloud_surface, cloud_color, (40, 15), 15)
    pygame.draw.circle(cloud_surface, cloud_color, (60, 20), 20)
    pygame.draw.circle(cloud_surface, cloud_color, (80, 25), 15)
    pygame.draw.circle(cloud_surface, cloud_color, (30, 35), 15)
    pygame.draw.circle(cloud_surface, cloud_color, (50, 30), 20)
    pygame.draw.circle(cloud_surface, cloud_color, (70, 35), 15)
    
    # 雲の影を追加
    shadow_surface = pygame.Surface((100, 10), pygame.SRCALPHA)
    shadow_color = (100, 100, 100, 100)
    pygame.draw.ellipse(shadow_surface, shadow_color, (10, 0, 80, 10))
    
    # 画面に描画
    screen.blit(cloud_surface, (int(x - 50), int(y - 25)))
    screen.blit(shadow_surface, (int(x - 50), int(y + 20)))

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
    next_shot_timer = 0  # 次の弾のタイマーを追加
    
    # Function to restart the game
    def restart_game():
        nonlocal current_level, projectile, projectile_count, game_state
        current_level = Level(1)
        projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
        projectile_count = current_level.projectile_count
        game_state = AIMING
        print("Game restarted")  # デバッグ用
    
    # Function to set next projectile
    def set_next_projectile():
        nonlocal projectile, game_state
        projectile = Projectile(slingshot.x, slingshot.y - slingshot.height//2)
        game_state = AIMING
        print("New projectile set")  # デバッグ用
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}, Game state: {game_state}")  # デバッグ用
                if event.key == pygame.K_r:  # Restart game when 'R' is pressed
                    restart_game()
                elif event.key == pygame.K_SPACE:  # スペースキーはどの状態でも次の弾を準備
                    if game_state == WAITING_FOR_NEXT_SHOT or game_state == PROJECTILE_IN_MOTION:
                        if projectile_count > 0:
                            set_next_projectile()
                            print("Space pressed: New projectile set")  # デバッグ用
            
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
                print(f"Projectile state: stopped={projectile.stopped}, x={projectile.x}, y={projectile.y}")  # デバッグ用
                if projectile_count > 0:
                    # Reset for next shot - 次の弾への切り替えを開始
                    game_state = WAITING_FOR_NEXT_SHOT
                    next_shot_timer = pygame.time.get_ticks() + 1000  # 現在時刻 + 1000ミリ秒
                    print(f"Waiting for next shot, timer set to {next_shot_timer}")  # デバッグ用
                else:
                    # Check if all targets are hit
                    if not current_level.is_complete():
                        game_state = GAME_OVER
        elif game_state == WAITING_FOR_NEXT_SHOT:
            # 次の弾への切り替えタイマーをチェック
            current_time = pygame.time.get_ticks()
            if current_time >= next_shot_timer:
                set_next_projectile()
                print(f"Timer expired at {current_time}, new projectile set")  # デバッグ用
        
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
