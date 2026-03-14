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

# --- Fallback Generators ---
def create_fallback_icon(name):
    surf = pygame.Surface((28, 28), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 200, 200), (14, 14), 14)
    pygame.draw.circle(surf, (50, 50, 50), (14, 14), 14, 2)
    font = pygame.font.SysFont(None, 18, bold=True)
    text = font.render(name[0].upper(), True, (0, 0, 0))
    surf.blit(text, text.get_rect(center=(14, 14)))
    return surf

# --- Updated: Pause Menu Class ---
class PauseMenu:
    def __init__(self, screen_w, screen_h, assets):
        self.screen_w = screen_w
        self.screen_h = screen_h
        # use technique background of pause menu the pausemenu.png image
        self.menu_sprite = assets['pausemenu']
        
        # Determine center based on loaded/generated image size
        self.rect = self.menu_sprite.get_rect()
        self.rect.center = (screen_w // 2, screen_h // 2)
        
        # font_title removed as requested to remove paused text
        self.font_opt = pygame.font.SysFont("Courier New", 32, bold=True)
        
        self.options = [
            "Placeholder 1", 
            "Placeholder 2", 
            "Placeholder 3", 
            "Quit Game"
        ]

    def handle_click(self, mouse_pos):
        # Adjusted Y starting position as text moved up, adjusted for new bigger image size
        start_y = self.rect.y + 100 # Moved up from 180 since title is gone
        
        for i, opt in enumerate(self.options):
            # invisible rectangle hitbox updated for new size/position
            opt_rect = pygame.Rect(self.rect.x, start_y + (i * 70), self.rect.width, 50)
            if opt_rect.collidepoint(mouse_pos):
                return opt
        return None

    def draw(self, surface):
        # use technique to make the background behind the menu darker
        # Full-screen dimming overlay (alpha=180 technique)
        full_screen_dim = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        pygame.draw.rect(full_screen_dim, (10, 10, 15, 180), full_screen_dim.get_rect())
        surface.blit(full_screen_dim, (0, 0))
        
        # 1. Draw Pause Menu Background (Loaded PNG image)
        # image bigger technique handled via asset loading/fallback generation
        surface.blit(self.menu_sprite, self.rect.topleft)
        
        # --- REQUEST REMOVE BORDER ---
        # The gray border is removed by commenting out this line: technique
        # pygame.draw.rect(surface, (100, 100, 120, 255), self.rect, 6, border_radius=30)
        
        # 2. Draw Title
        # --- REQUEST REMOVE PAUSED TEXT ---
        # Paused text blit removed technique
        # title_surf = self.font_title.render("PAUSED", True, (255, 255, 255))
        # surface.blit(title_surf, title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 90)))
        
        # 3. Draw Interactive Text Options
        mx, my = pygame.mouse.get_pos()
        start_y = self.rect.y + 100 # Position shifted up due to removed title technique
        
        for i, opt in enumerate(self.options):
            # invisible rectangle hitbox, slightly larger spacing for bigger menu
            opt_rect = pygame.Rect(self.rect.x, start_y + (i * 70), self.rect.width, 50)
            is_hovered = opt_rect.collidepoint((mx, my))
            
            # Hover color logic
            if opt == "Quit Game":
                color = (255, 100, 100) if is_hovered else (200, 60, 60)
            else:
                color = (255, 215, 0) if is_hovered else (200, 200, 200) # Gold if hovered, else gray
                
            text_surf = self.font_opt.render(opt, True, color)
            surface.blit(text_surf, text_surf.get_rect(center=opt_rect.center))

# --- Radial Menu Class ---
class RadialMenu:
    def __init__(self, assets):
        self.radius = 75
        self.active_npc = None
        self.icons = {
            "move": assets['move'],
            "inventory": assets['inventory'],
            "build": assets['build'],
            "exit": assets['exit']
        }
        
        self.wedges = [
            ("move", -math.pi, -3*math.pi/4),
            ("inventory", -3*math.pi/4, -math.pi/2),
            ("build", -math.pi/2, -math.pi/4),
            ("exit", -math.pi/4, 0)
        ]

    def open_for(self, npc):
        self.active_npc = npc
        npc.menu_open = True

    def close(self):
        if self.active_npc:
            self.active_npc.menu_open = False
            self.active_npc = None

    def get_center(self):
        if not self.active_npc: 
            return (0, 0)
        return (self.active_npc.x, self.active_npc.taskbar_y - 25)

    def handle_click(self, mouse_pos):
        if not self.active_npc:
            return False
            
        cx, cy = self.get_center()
        mx, my = mouse_pos
        dx = mx - cx
        dy = my - cy
        dist = math.hypot(dx, dy)
        
        if dist <= self.radius:
            angle = math.atan2(dy, dx)
            if angle == math.pi: 
                angle = -math.pi
                
            for name, start_ang, end_ang in self.wedges:
                if start_ang <= angle <= end_ang:
                    if name == "exit":
                        self.close()
                    else:
                        print(f"Clicked {name} - Feature not yet implemented!")
                    return True 
        return False

    def draw(self, surface):
        if not self.active_npc:
            return
            
        cx, cy = self.get_center()
        mx, my = pygame.mouse.get_pos()
        dx = mx - cx
        dy = my - cy
        dist = math.hypot(dx, dy)
        
        hovered_name = None
        if dist <= self.radius:
            angle = math.atan2(dy, dx)
            if angle == math.pi: 
                angle = -math.pi
            for name, start_ang, end_ang in self.wedges:
                if start_ang <= angle <= end_ang:
                    hovered_name = name
                    break

        temp_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        for name, start_ang, end_ang in self.wedges:
            mid_ang = (start_ang + end_ang) / 2
            icon_dist = self.radius * 0.65
            ix = self.radius + math.cos(mid_ang) * icon_dist
            iy = self.radius + math.sin(mid_ang) * icon_dist
            
            icon_img = self.icons[name]
            
            if name == hovered_name:
                new_w = int(icon_img.get_width() * 1.5)
                new_h = int(icon_img.get_height() * 1.5)
                icon_img = pygame.transform.scale(icon_img, (new_w, new_h))
                
            icon_rect = icon_img.get_rect(center=(ix, iy))
            temp_surf.blit(icon_img, icon_rect)

        surface.blit(temp_surf, (cx - self.radius, cy - self.radius))

class Person:
    def __init__(self, name, sprite, screen_w, start_x):
        self.name = name
        self.screen_w = screen_w
        self.taskbar_y = get_dynamic_floor() 
        
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
        
        self.menu_open = False
        self.rect = self.base_sprite.get_rect(midbottom=(self.x, self.taskbar_y))

    def update(self, current_floor):
        self.taskbar_y = current_floor
        self.rect.midbottom = (self.x, self.taskbar_y)

        if self.menu_open:
            return

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
        if self.state == "walk" and not self.menu_open:
            time_ms = pygame.time.get_ticks()
            angle = math.sin(time_ms * 0.01) * 10 
            
        img = pygame.transform.rotate(img, angle)
        
        draw_rect = img.get_rect()
        draw_rect.midbottom = (self.x, self.taskbar_y)
        
        surface.blit(img, draw_rect)

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
        self.pop_timer = 0
        
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

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and self.weather == WEATHER_CLOUDY and self.pop_timer == 0:
            self.set_weather(WEATHER_RAIN) 
            self.pop_timer = 105  
            return True
        return False

    def respawn(self, existing_clouds, global_weather, start_offscreen=True):
        self.scale = random.uniform(0.3, 0.5)
        self.speed = random.uniform(0.8, 1.2)
        self.weather = global_weather
        self.is_transitioning = False 
        self.pop_timer = 0
        
        base_sprite = self.sprites[self.weather]
        new_w = max(1, int(base_sprite.get_width() * self.scale))
        new_h = max(1, int(base_sprite.get_height() * self.scale))
        self.image = pygame.transform.scale(base_sprite, (new_w, new_h))
        
        test_rect = self.image.get_rect()

        for _ in range(20):
            min_y = max(10, int(self.screen_h * 0.01))
            max_y = max(min_y + 10, int(self.screen_h * 0.12))
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
        
        if self.pop_timer > 0:
            self.pop_timer -= 1
            if self.pop_timer == 0:
                self.respawn(existing_clouds, global_weather, start_offscreen=True)
                
        elif self.rect.x > self.screen_w:
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
            temp_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            if self.old_image: temp_surf.blit(self.old_image, (0, 0))
            if self.new_image: temp_surf.blit(self.new_image, (0, 0))
            img_to_draw = temp_surf
        else:
            img_to_draw = self.image

        draw_rect = self.rect.copy()

        if self.pop_timer > 0:
            if self.pop_timer > 90:
                t = (105 - self.pop_timer) / 15.0
                scale = 1.0 + math.sin(t * math.pi / 2.0) * 0.4 
                alpha = 255
            elif self.pop_timer > 30:
                scale = 1.4
                alpha = 255
            else:
                t = (30 - self.pop_timer) / 30.0
                scale = 1.4 * (1.0 - t)
                scale = max(0.01, scale) 
                alpha = int(255 * (1.0 - t))

            new_w = max(1, int(draw_rect.width * scale))
            new_h = max(1, int(draw_rect.height * scale))
            
            img_to_draw = pygame.transform.scale(img_to_draw, (new_w, new_h))
            
            if alpha < 255:
                img_to_draw = img_to_draw.copy()
                img_to_draw.set_alpha(alpha)
            
            draw_rect = img_to_draw.get_rect(center=self.rect.center)

        surface.blit(img_to_draw, draw_rect)

def setup_transparent_fullscreen():
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1) - 1 

    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
    
    hwnd = pygame.display.get_wm_info()['window']
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    LWA_COLORKEY = 1
    
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, screen_w, screen_h, 0x0001 | 0x0040)
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
    
    colorref = TRANSPARENT_KEY[0] | (TRANSPARENT_KEY[1] << 8) | (TRANSPARENT_KEY[2] << 16)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, colorref, 0, LWA_COLORKEY)
    
    return screen, screen_w, screen_h

# --- Generates Fallback PNG with UPDATED LARGER SIZE ---
def create_fallback_pause_menu_png():
    """Generates a dynamic 1000x700 surface to serve as the pausemenu.png sprite."""
    # use szeem to have made a semi transparent black background for the menu technique used in draw, image biggger technique
    # image bigger technique: Size increased to 1000x700
    surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
    
    # Procedural background details for the image itself
    pygame.draw.rect(surf, (30, 30, 40), surf.get_rect(), border_radius=30)
    # Inner border texture
    pygame.draw.rect(surf, (60, 60, 80), surf.get_rect().inflate(-20,-20), 4, border_radius=25)
    
    return surf

def load_assets():
    asset_dir = os.path.join(os.path.dirname(__file__), "assets")
    assets = {'sprites': {}}
    
    try:
        assets['sprites'][WEATHER_CLOUDY] = pygame.image.load(os.path.join(asset_dir, "cloudy.png")).convert_alpha()
        assets['sprites'][WEATHER_RAIN] = pygame.image.load(os.path.join(asset_dir, "rain.png")).convert_alpha()
        assets['sprites'][WEATHER_STORM] = pygame.image.load(os.path.join(asset_dir, "storm.png")).convert_alpha()
        
        assets['adam'] = pygame.image.load(os.path.join(asset_dir, "adam.png")).convert_alpha()
        assets['eve'] = pygame.image.load(os.path.join(asset_dir, "eve.png")).convert_alpha()
    except pygame.error as e:
        print(f"FAILED TO LOAD BASE ASSETS: {e}")
        pygame.quit()
        sys.exit()

    for icon_name in ["move", "inventory", "build", "exit"]:
        try:
            img = pygame.image.load(os.path.join(asset_dir, f"{icon_name}.png")).convert_alpha()
            assets[icon_name] = pygame.transform.scale(img, (28, 28))
        except pygame.error:
            assets[icon_name] = create_fallback_icon(icon_name)
            
    # --- Load Pause Menu PNG ---
    try:
        # use technique background of pause menu the pausemenu.png image
        assets['pausemenu'] = pygame.image.load(os.path.join(asset_dir, "pausemenu.png")).convert_alpha()
    except pygame.error:
        # Generate larger fallback
        assets['pausemenu'] = create_fallback_pause_menu_png()

    return assets

def main():
    pygame.init()
    
    screen, screen_w, screen_h = setup_transparent_fullscreen()
    clock = pygame.time.Clock()
    
    pygame.font.init()
    debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
    debug_mode = False
    game_paused = False 
    
    assets = load_assets()
    sprites = assets['sprites']
    
    # Initialize UI
    radial_menu = RadialMenu(assets)
    pause_menu = PauseMenu(screen_w, screen_h, assets)
    
    adam = Person("Adam", assets['adam'], screen_w, screen_w // 3)
    eve = Person("Eve", assets['eve'], screen_w, (screen_w // 3) * 2)
    characters = [adam, eve]
    
    current_weather = WEATHER_CLOUDY
    weather_timer = 0
    WEATHER_CHANGE_TIME = FPS * 15 
    
    water_depletion = 0 
    MAX_DEPLETION = FPS * 25 
    
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT: 
                        running = False
                    else:
                        game_paused = not game_paused 
                elif event.key == pygame.K_F4:
                    debug_mode = not debug_mode
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # PAUSE MENU CLICK LOGIC
                if game_paused:
                    action = pause_menu.handle_click(mouse_pos)
                    if action == "Quit Game":
                        running = False
                    elif action:
                        print(f"Pause Menu Clicked: {action}")
                    continue # Skip checking in-game objects if we are paused!
                
                # Priority 1: Did we click inside an open Radial Menu?
                if radial_menu.handle_click(mouse_pos):
                    continue
                
                # Priority 2: Did we click an NPC?
                clicked_npc = None
                for char in characters:
                    if char.rect.collidepoint(mouse_pos):
                        clicked_npc = char
                        break
                        
                if clicked_npc:
                    if radial_menu.active_npc != clicked_npc:
                        radial_menu.close()
                        radial_menu.open_for(clicked_npc)
                    continue
                
                # Priority 3: Did we click a Cloud?
                for cloud in clouds:
                    if cloud.handle_click(mouse_pos):
                        water_depletion += FPS * 5 
                        if water_depletion > MAX_DEPLETION:
                            water_depletion = MAX_DEPLETION
                        break

        # --- ONLY UPDATE THE WORLD IF UNPAUSED ---
        if not game_paused:
            if water_depletion > 0:
                water_depletion -= 0.5 

            if random.random() < 0.02: 
                if current_weather == WEATHER_STORM:
                    target_wind = random.uniform(-10.0, 10.0)
                elif current_weather == WEATHER_RAIN:
                    target_wind = random.uniform(-3.0, 3.0)
                else:
                    target_wind = 0.0
            current_wind += (target_wind - current_wind) * 0.02

            weather_timer += 1
            
            if current_weather in [WEATHER_RAIN, WEATHER_STORM]:
                effective_duration = max(0, WEATHER_CHANGE_TIME - water_depletion)
            else:
                effective_duration = WEATHER_CHANGE_TIME

            if weather_timer >= effective_duration:
                weather_timer = 0
                current_weather = get_next_weather(current_weather)
                
                if current_weather in [WEATHER_RAIN, WEATHER_STORM]:
                    if max(0, WEATHER_CHANGE_TIME - water_depletion) <= 0:
                        current_weather = WEATHER_CLOUDY 
                        
                for cloud in clouds:
                    cloud.set_weather(current_weather)

            for cloud in clouds:
                cloud.update(clouds, current_weather)
                
                is_shrinking = (0 < cloud.pop_timer <= 30)
                
                if cloud.weather in [WEATHER_RAIN, WEATHER_STORM] and not is_shrinking:
                    spawn_chance = 0.8 if cloud.pop_timer > 0 else (0.4 if cloud.weather == WEATHER_STORM else 0.1)
                    
                    if random.random() < spawn_chance:
                        visual_width_offset = int(cloud.rect.width * 0.2) if cloud.pop_timer > 0 else 0
                        drop_x = random.randint(cloud.rect.left - visual_width_offset, cloud.rect.right + visual_width_offset)
                        drop_y = cloud.rect.bottom - 10
                        raindrops.append(Raindrop(drop_x, drop_y, cloud.weather))

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
            
        if not game_paused:
            radial_menu.draw(screen)
            
        # --- Draw Pause Menu (Draws dynamically!) ---
        if game_paused:
            pause_menu.draw(screen)
            
        # --- Draw Debug Menu ---
        if debug_mode:
            debug_info = [
                f"=== DEBUG MODE ===",
                f"FPS: {clock.get_fps():.1f}",
                f"Game Paused: {game_paused}",
                f"Weather: {current_weather.upper()}",
                f"Wind Speed: {current_wind:.2f}",
                f"Water Depletion: {water_depletion / FPS:.1f}s / {MAX_DEPLETION / FPS:.1f}s",
                f"Weather Timer: {weather_timer / FPS:.1f}s / {WEATHER_CHANGE_TIME / FPS:.1f}s",
                f"Raindrops: {len(raindrops)} | Splashes: {len(splashes)}"
            ]
            y_offset = 10
            for info in debug_info:
                text_surf = debug_font.render(info, True, (0, 255, 0)) 
                bg_rect = text_surf.get_rect(topleft=(10, y_offset))
                pygame.draw.rect(screen, (0, 0, 0), bg_rect) 
                screen.blit(text_surf, (10, y_offset))
                y_offset += 22
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()