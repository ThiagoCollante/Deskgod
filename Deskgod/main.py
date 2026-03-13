import pygame
import sys
import os
import ctypes
import random
import math
from ctypes import wintypes

# --- Global Configuration ---
FPS = 60
TRANSPARENT_KEY = (1, 1, 1) 

# Weather Types
WEATHER_CLOUDY = "cloudy"
WEATHER_RAIN = "rain"
WEATHER_STORM = "storm"

def get_next_weather(current_weather):
    if current_weather == WEATHER_CLOUDY:
        return random.choice([WEATHER_CLOUDY, WEATHER_RAIN])
    elif current_weather == WEATHER_RAIN:
        return random.choice([WEATHER_CLOUDY, WEATHER_RAIN, WEATHER_STORM])
    elif current_weather == WEATHER_STORM:
        return random.choice([WEATHER_RAIN, WEATHER_STORM])
    return WEATHER_CLOUDY

def get_dynamic_floor():
    rect = wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0) 
    return rect.bottom

class Person:
    def __init__(self, name, sprite, screen_w, start_x):
        self.name = name
        self.screen_w = screen_w
        self.taskbar_y = get_dynamic_floor() 
        
        # Using standard scale to prevent black edge blending
        TARGET_HEIGHT = 50
        scale_ratio = TARGET_HEIGHT / sprite.get_height()
        new_width = max(1, int(sprite.get_width() * scale_ratio))
        self.base_sprite = pygame.transform.scale(sprite, (new_width, TARGET_HEIGHT))
        
        self.x = start_x
        self.vx = 0
        self.state = "idle" 
        self.state_timer = random.randint(60, 180)
        
        self.facing_left = False
        self.walk_speed = random.uniform(0.5, 1.5)

    def update(self, current_floor):
        self.taskbar_y = current_floor

        self.state_timer -= 1
        if self.state_timer <= 0:
            if self.state == "idle":
                self.state = "walk"
                self.vx = random.choice([-self.walk_speed, self.walk_speed])
                self.state_timer = random.randint(90, 300) 
            else:
                self.state = "idle"
                self.vx = 0
                self.state_timer = random.randint(60, 240) 

        if self.state == "walk":
            self.x += self.vx
            self.facing_left = self.vx < 0
            
            if self.x < 30:
                self.x = 30
                self.vx *= -1
                self.facing_left = False
            elif self.x > self.screen_w - 30:
                self.x = self.screen_w - 30
                self.vx *= -1
                self.facing_left = True

    def draw(self, surface):
        img = pygame.transform.flip(self.base_sprite, self.facing_left, False)
        
        angle = 0
        if self.state == "walk":
            time_ms = pygame.time.get_ticks()
            angle = math.sin(time_ms * 0.01) * 10 
            
        img = pygame.transform.rotate(img, angle)
        
        rect = img.get_rect()
        rect.midbottom = (self.x, self.taskbar_y)
        
        surface.blit(img, rect)

class Splash:
    def __init__(self, x, y, weather_type):
        self.particles = []
        num_particles = random.randint(3, 5) if weather_type == WEATHER_STORM else random.randint(1, 3)
        
        for _ in range(num_particles):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, -5) 
            self.particles.append([x, y, vx, vy])
            
        self.life = random.randint(8, 15) 
        self.color = (180, 190, 200) if weather_type == WEATHER_STORM else (130, 150, 180)

    def update(self):
        self.life -= 1
        for p in self.particles:
            p[0] += p[2]  
            p[1] += p[3]  
            p[3] += 0.5   
        return self.life > 0 

    def draw(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, self.color, (int(p[0]), int(p[1])), 1)

class Raindrop:
    def __init__(self, x, y, weather_type):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.personal_wind_variance = random.uniform(-0.5, 0.5)
        self.weather_type = weather_type
        
        if weather_type == WEATHER_STORM:
            self.speed_y = random.uniform(15, 25)
            self.color = (180, 190, 200) 
            self.length = random.randint(15, 25)
        else:
            self.speed_y = random.uniform(8, 15)
            self.color = (130, 150, 180)
            self.length = random.randint(8, 15)

    def update(self, global_wind):
        self.speed_x = global_wind + self.personal_wind_variance
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, surface):
        end_pos = (int(self.x + self.speed_x), int(self.y + self.length))
        pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), end_pos, 2)

class Cloud:
    def __init__(self, screen_w, screen_h, sprites, current_weather, existing_clouds=None):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.sprites = sprites
        self.image = None
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.speed = 0.0
        self.scale = 1.0
        
        self.weather = current_weather
        self.is_transitioning = False
        self.old_image = None
        self.new_image = None
        self.transition_alpha = 0
        
        self.respawn(existing_clouds or [], current_weather, start_offscreen=False)

    def set_weather(self, target_weather):
        if self.weather == target_weather or self.is_transitioning:
            return
            
        self.is_transitioning = True
        self.transition_alpha = 0
        self.old_image = self.image.copy()
        
        base_sprite = self.sprites[target_weather]
        new_w = max(1, int(base_sprite.get_width() * self.scale))
        new_h = max(1, int(base_sprite.get_height() * self.scale))
        self.new_image = pygame.transform.scale(base_sprite, (new_w, new_h))
        self.weather = target_weather

    def respawn(self, existing_clouds, global_weather, start_offscreen=True):
        self.scale = random.uniform(0.3, 0.5)
        self.speed = random.uniform(0.8, 1.2)
        self.weather = global_weather
        self.is_transitioning = False 
        
        base_sprite = self.sprites[self.weather]
        new_w = max(1, int(base_sprite.get_width() * self.scale))
        new_h = max(1, int(base_sprite.get_height() * self.scale))
        self.image = pygame.transform.scale(base_sprite, (new_w, new_h))
        
        test_rect = self.image.get_rect()

        for _ in range(20):
            min_y = max(50, int(self.screen_h * 0.05))
            max_y = max(min_y + 10, int(self.screen_h * 0.25))
            test_rect.y = random.randint(min_y, max_y)
            
            if start_offscreen:
                test_rect.x = -test_rect.width - random.randint(50, 300)
            else:
                test_rect.x = random.randint(50, self.screen_w - 50)
                
            overlap = False
            for other in existing_clouds:
                if other is not self and other.rect.width > 0:
                    if test_rect.colliderect(other.rect.inflate(20, 20)):
                        overlap = True
                        break
            if not overlap:
                break
                
        self.rect = test_rect

    def update(self, existing_clouds, global_weather):
        self.rect.x += self.speed
        if self.rect.x > self.screen_w:
            self.respawn(existing_clouds, global_weather, start_offscreen=True)
            
        if self.is_transitioning:
            self.transition_alpha += 3 
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.image = self.new_image
                self.is_transitioning = False
            else:
                self.new_image.set_alpha(self.transition_alpha)

    def draw(self, surface):
        if self.is_transitioning:
            surface.blit(self.old_image, self.rect)
            surface.blit(self.new_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

def setup_transparent_fullscreen():
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    # Subtract exactly 1 pixel so Windows doesn't hide the taskbar
    screen_h = ctypes.windll.user32.GetSystemMetrics(1) - 1 

    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
    
    hwnd = pygame.display.get_wm_info()['window']
    GWL_EXSTYLE = -20
    # Removed WS_EX_TOOLWINDOW so the icon shows up on the taskbar
    WS_EX_LAYERED = 0x00080000
    LWA_COLORKEY = 1
    
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, screen_w, screen_h, 0x0001 | 0x0040)
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
    
    colorref = TRANSPARENT_KEY[0] | (TRANSPARENT_KEY[1] << 8) | (TRANSPARENT_KEY[2] << 16)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, colorref, 0, LWA_COLORKEY)
    
    return screen, screen_w, screen_h

def load_assets():
    asset_dir = os.path.join(os.path.dirname(__file__), "assets")
    assets = {'sprites': {}}
    
    try:
        assets['sprites'][WEATHER_CLOUDY] = pygame.image.load(os.path.join(asset_dir, "cloudy.png")).convert_alpha()
        assets['sprites'][WEATHER_RAIN] = pygame.image.load(os.path.join(asset_dir, "rain.png")).convert_alpha()
        assets['sprites'][WEATHER_STORM] = pygame.image.load(os.path.join(asset_dir, "storm.png")).convert_alpha()
        
        assets['adam'] = pygame.image.load(os.path.join(asset_dir, "adam.png")).convert_alpha()
        assets['eve'] = pygame.image.load(os.path.join(asset_dir, "eve.png")).convert_alpha()
        
        return assets
    except pygame.error as e:
        print(f"FAILED TO LOAD ASSETS: {e}")
        print("Ensure 'assets' folder contains: cloudy.png, rain.png, storm.png, adam.png, and eve.png")
        pygame.quit()
        sys.exit()

def main():
    pygame.init()
    
    screen, screen_w, screen_h = setup_transparent_fullscreen()
    clock = pygame.time.Clock()
    
    assets = load_assets()
    sprites = assets['sprites']
    
    adam = Person("Adam", assets['adam'], screen_w, screen_w // 3)
    eve = Person("Eve", assets['eve'], screen_w, (screen_w // 3) * 2)
    characters = [adam, eve]
    
    current_weather = WEATHER_CLOUDY
    weather_timer = 0
    WEATHER_CHANGE_TIME = FPS * 15 
    
    current_wind = 0.0
    target_wind = 0.0
    
    clouds = []
    for _ in range(6):
        clouds.append(Cloud(screen_w, screen_h, sprites, current_weather, clouds))
        
    raindrops = []
    splashes = []

    running = True
    while running:
        current_floor = get_dynamic_floor()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- Wind Logic ---
        if random.random() < 0.02: 
            if current_weather == WEATHER_STORM:
                target_wind = random.uniform(-10.0, 10.0)
            elif current_weather == WEATHER_RAIN:
                target_wind = random.uniform(-3.0, 3.0)
            else:
                target_wind = 0.0
        current_wind += (target_wind - current_wind) * 0.02

        # --- Weather Logic ---
        weather_timer += 1
        if weather_timer >= WEATHER_CHANGE_TIME:
            weather_timer = 0
            current_weather = get_next_weather(current_weather)
            for cloud in clouds:
                cloud.set_weather(current_weather)

        # --- Cloud & Rain Logic ---
        for cloud in clouds:
            cloud.update(clouds, current_weather)
            
            if cloud.weather in [WEATHER_RAIN, WEATHER_STORM]:
                spawn_chance = 0.4 if cloud.weather == WEATHER_STORM else 0.1
                if random.random() < spawn_chance:
                    drop_x = random.randint(cloud.rect.left + 10, cloud.rect.right - 10)
                    drop_y = cloud.rect.bottom - 10
                    raindrops.append(Raindrop(drop_x, drop_y, cloud.weather))

        # --- Update Raindrops & Splashes ---
        for drop in reversed(raindrops):
            drop.update(current_wind)
            
            if drop.y + drop.length >= current_floor:
                splashes.append(Splash(drop.x + drop.speed_x, current_floor, drop.weather_type))
                raindrops.remove(drop)
            elif drop.x < 0 or drop.x > screen_w:
                raindrops.remove(drop)

        for splash in reversed(splashes):
            if not splash.update():
                splashes.remove(splash)

        # --- Update Characters ---
        for char in characters:
            char.update(current_floor)

        # --- Render Logic ---
        screen.fill(TRANSPARENT_KEY)
        
        for drop in raindrops:
            drop.draw(screen)
        for splash in splashes:
            splash.draw(screen)
        for cloud in clouds:
            cloud.draw(screen)
        for char in characters:
            char.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()