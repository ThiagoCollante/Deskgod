import pygame
import sys
import os
import ctypes
import random
import math
from ctypes import wintypes

# ==========================================
# --- CONFIGURATION & TWEAKS ---
# ==========================================

# Rendering
FPS = 60
TRANSPARENT_KEY = (1, 1, 1) 

# Cursor Settings & Offsets
CURSOR_LERP_SPEED = 0.35
CURSOR_RADIAL_Y_OFFSET = 30       # Upward jump when locking to radial icons
CURSOR_SLOT_INWARD_OFFSET = 28    # Inward pull when hovering a backpack slot
CURSOR_GRABBING_Y_OFFSET = 25     # Downward visual shift to cover the human while holding

# Interaction Thresholds
DRAG_HOLD_DELAY_MS = 150          # Milliseconds required to hold before grabbing vs tapping
DRAG_DROP_THRESHOLD = 5           # Pixels of movement allowed to still count as a "click"

# UI / Menu Settings
BACKPACK_SCALE = 0.7              # Multiplier to scale the backpack while preserving proportions
RADIAL_MENU_RADIUS = 75
INV_COLS = 4
INV_ROWS = 4
INV_SLOT_SIZE = 32                # Backpack slot size
INV_PADDING_X = 9
INV_PADDING_Y = 10
INV_OFFSET_X = 1
INV_OFFSET_Y = -7
MAX_STACK_SIZE = 64               # Minecraft style max stacking

# Item Settings
ITEM_BASE_SIZE = 36               # Base dimension for items in the inventory
TOOL_BASE_SIZE = 50               # Bigger dimension for tools
ITEM_DRAG_SCALE = 1.5             # Multiplier for how much bigger the item gets when dragged

# Character Settings
CHARACTER_TARGET_HEIGHT = 50
WALK_SPEED_MIN = 0.5
WALK_SPEED_MAX = 1.5
GRAVITY = 0.8
IDLE_TIME_MIN = 60
IDLE_TIME_MAX = 240
WALK_TIME_MIN = 90
WALK_TIME_MAX = 300

# Weather & Environment Settings
WEATHER_CHANGE_TIME_SECONDS = 15
MAX_WATER_DEPLETION_SECONDS = 25
CLOUD_SPEED_MIN = 0.8
CLOUD_SPEED_MAX = 1.2
CLOUD_SCALE_MIN = 0.3
CLOUD_SCALE_MAX = 0.5
WIND_STORM_RANGE = 10.0
WIND_RAIN_RANGE = 3.0
BOULDER_HEIGHT_MIN = 80           # Boulders will always be bigger than the 50px humans
BOULDER_HEIGHT_MAX = 150
TREE_HEIGHT_MIN = 120
TREE_HEIGHT_MAX = 200

# ==========================================
# --- CORE LOGIC ---
# ==========================================

# Ctypes structure for global mouse tracking
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

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
def create_fallback_icon(name, font_path=None):
    surf = pygame.Surface((28, 28), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 200, 200), (14, 14), 14)
    pygame.draw.circle(surf, (50, 50, 50), (14, 14), 14, 2)
    
    try:
        if font_path:
            font = pygame.font.Font(font_path, 18)
        else:
            font = pygame.font.SysFont(None, 18, bold=True)
    except:
        font = pygame.font.SysFont(None, 18, bold=True)
        
    text = font.render(name[0].upper(), True, (0, 0, 0))
    surf.blit(text, text.get_rect(center=(14, 14)))
    return surf

def create_fallback_pause_menu_png():
    surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
    pygame.draw.rect(surf, (30, 30, 40), surf.get_rect(), border_radius=30)
    return surf

def create_fallback_basiccrafting_png():
    surf = pygame.Surface((200, 200), pygame.SRCALPHA)
    pygame.draw.rect(surf, (150, 100, 50, 255), surf.get_rect(), border_radius=10)
    pygame.draw.rect(surf, (100, 50, 20, 255), surf.get_rect(), 4, border_radius=10)
    return surf

def create_fallback_backpackslot_png():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(surf, (40, 40, 50, 200), surf.get_rect(), border_radius=3)
    pygame.draw.rect(surf, (20, 20, 30, 255), surf.get_rect(), 2, border_radius=3)
    return surf

def create_fallback_toolslot_png():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(surf, (40, 50, 60, 200), surf.get_rect(), border_radius=3)
    pygame.draw.rect(surf, (30, 40, 80, 255), surf.get_rect(), 2, border_radius=3)
    return surf

def create_fallback_backpack_png():
    surf = pygame.Surface((240, 260), pygame.SRCALPHA)
    pygame.draw.rect(surf, (139, 69, 19, 255), (0, 15, 240, 245), border_radius=20)
    pygame.draw.rect(surf, (80, 40, 10, 255), (0, 15, 240, 245), 4, border_radius=20)
    pygame.draw.rect(surf, (100, 50, 15, 255), (90, 0, 60, 20), border_radius=10)
    pygame.draw.rect(surf, (80, 40, 10, 255), (90, 0, 60, 20), 4, border_radius=10)
    
    start_x = 20
    start_y = 50
    for r in range(4):
        for c in range(4):
            px = start_x + c * (32 + 10)
            py = start_y + r * (32 + 10)
            if r == 0 and c < 2:
                pygame.draw.rect(surf, (0, 0, 255, 255), (px, py, 32, 32)) 
            else:
                pygame.draw.rect(surf, (255, 0, 0, 255), (px, py, 32, 32)) 
            
    return surf

def create_fallback_cursor_png():
    surf = pygame.Surface((12, 16), pygame.SRCALPHA)
    pts = [(0, 0), (0, 12), (3, 9), (6, 15), (8, 14), (5, 8), (10, 8)]
    pygame.draw.polygon(surf, (255, 255, 255), pts)
    pygame.draw.polygon(surf, (0, 0, 0), pts, 1)
    return surf

def create_fallback_selecting_png():
    surf = pygame.Surface((14, 14), pygame.SRCALPHA)
    pts = [(1, 1), (13, 1), (7, 13)]
    pygame.draw.polygon(surf, (255, 215, 0), pts)
    pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    return surf

def create_fallback_grabbing_png():
    surf = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 100, 0), (7, 7), 6)
    pygame.draw.circle(surf, (0, 0, 0), (7, 7), 6, 2)
    return surf

def create_fallback_pebble_png():
    surf = pygame.Surface((ITEM_BASE_SIZE, ITEM_BASE_SIZE), pygame.SRCALPHA)
    center = ITEM_BASE_SIZE // 2
    pygame.draw.circle(surf, (150, 150, 150), (center, center), center - 2)
    pygame.draw.circle(surf, (100, 100, 100), (center, center), center - 2, 2)
    pygame.draw.circle(surf, (200, 200, 200), (center - 4, center - 4), 3)
    return surf

def create_fallback_stick_png():
    surf = pygame.Surface((ITEM_BASE_SIZE, ITEM_BASE_SIZE), pygame.SRCALPHA)
    pygame.draw.line(surf, (139, 69, 19), (8, ITEM_BASE_SIZE - 8), (ITEM_BASE_SIZE - 8, 8), 4)
    pygame.draw.line(surf, (100, 50, 15), (8, ITEM_BASE_SIZE - 8), (ITEM_BASE_SIZE - 8, 8), 2)
    return surf

def create_fallback_vine_png():
    surf = pygame.Surface((ITEM_BASE_SIZE, ITEM_BASE_SIZE), pygame.SRCALPHA)
    pygame.draw.lines(surf, (34, 139, 34), False, [(12, 4), (24, 12), (12, 20), (24, 28), (12, 36)], 4)
    pygame.draw.lines(surf, (0, 100, 0), False, [(12, 4), (24, 12), (12, 20), (24, 28), (12, 36)], 2)
    return surf

def create_fallback_log_png():
    surf = pygame.Surface((ITEM_BASE_SIZE, ITEM_BASE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surf, (101, 67, 33), (8, 12, 20, 12))
    pygame.draw.rect(surf, (139, 69, 19), (8, 12, 20, 12), 2)
    pygame.draw.rect(surf, (205, 133, 63), (24, 12, 4, 12))
    return surf

def create_fallback_plank_png():
    surf = pygame.Surface((ITEM_BASE_SIZE, ITEM_BASE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surf, (205, 133, 63), (4, 10, 28, 16))
    pygame.draw.rect(surf, (139, 69, 19), (4, 10, 28, 16), 2)
    pygame.draw.line(surf, (160, 82, 45), (6, 14), (30, 14), 1)
    pygame.draw.line(surf, (160, 82, 45), (6, 22), (30, 22), 1)
    return surf

def create_fallback_boulder_png():
    surf = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (120, 120, 120), (5, 20, 90, 75))
    pygame.draw.ellipse(surf, (80, 80, 80), (5, 20, 90, 75), 4)
    pygame.draw.ellipse(surf, (140, 140, 140), (20, 30, 40, 25))
    return surf

def create_fallback_tree_png():
    surf = pygame.Surface((100, 180), pygame.SRCALPHA)
    pygame.draw.rect(surf, (101, 67, 33), (40, 100, 20, 80)) # Trunk
    pygame.draw.circle(surf, (34, 139, 34), (50, 60), 50)    # Leaves
    pygame.draw.circle(surf, (0, 100, 0), (50, 60), 50, 4)
    return surf

def create_fallback_basicpickaxe_png():
    surf = pygame.Surface((TOOL_BASE_SIZE, TOOL_BASE_SIZE), pygame.SRCALPHA)
    pygame.draw.line(surf, (139, 69, 19), (8, 42), (28, 22), 4)
    pts = [(12, 18), (34, 12), (40, 34), (28, 22)]
    pygame.draw.polygon(surf, (150, 150, 150), pts)
    pygame.draw.polygon(surf, (100, 100, 100), pts, 2)
    return surf

def create_fallback_basicaxe_png():
    surf = pygame.Surface((TOOL_BASE_SIZE, TOOL_BASE_SIZE), pygame.SRCALPHA)
    pygame.draw.line(surf, (139, 69, 19), (16, 42), (28, 22), 4)
    pts = [(12, 12), (28, 12), (28, 22), (16, 28), (12, 22)]
    pygame.draw.polygon(surf, (150, 150, 150), pts)
    pygame.draw.polygon(surf, (100, 100, 100), pts, 2)
    return surf

def create_fallback_movedot_png():
    surf = pygame.Surface((8, 8), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 200, 200, 150), (4, 4), 4)
    pygame.draw.circle(surf, (255, 255, 255, 255), (4, 4), 2)
    return surf

# --- Custom Cursor Class ---
class CustomCursor:
    def __init__(self, assets):
        self.cursor_img = assets['cursor']
        self.selecting_img = assets['selecting']
        self.grabbing_img = assets['grabbing']
        
        self.hover_ui_img = pygame.transform.rotate(self.selecting_img, -135)
        
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        self.x, self.y = pt.x, pt.y
        self.last_mouse_x = self.x
        self.facing_left = False
        
        self.cursor_state = "normal" 

    def update(self, characters, is_paused, radial_menu, inventory_menu, pause_menu, is_grabbing_human, is_grabbing_item, pending_move_command):
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        actual_mouse_x, actual_mouse_y = pt.x, pt.y
        actual_pos = (actual_mouse_x, actual_mouse_y)
        
        dx = actual_mouse_x - self.last_mouse_x
        if dx < 0:
            self.facing_left = True
        elif dx > 0:
            self.facing_left = False
        self.last_mouse_x = actual_mouse_x

        target_x = actual_mouse_x
        target_y = actual_mouse_y
        self.cursor_state = "normal"

        if pending_move_command:
            self.cursor_state = "locked"
            self.x += (target_x - self.x) * CURSOR_LERP_SPEED
            self.y += (target_y - self.y) * CURSOR_LERP_SPEED
            return

        if is_grabbing_human:
            self.cursor_state = "grabbing_human"
        elif is_grabbing_item:
            self.cursor_state = "grabbing_item"
            
        elif is_paused:
            if pause_menu.is_hovering(actual_pos):
                self.cursor_state = "hover_ui"
        else:
            hovered_icon_pos = radial_menu.get_hovered_icon_center(actual_pos)
            
            hovered_npc = None
            if not hovered_icon_pos:
                for char in characters:
                    if char.rect.collidepoint(actual_pos):
                        hovered_npc = char
                        break

            if hovered_icon_pos:
                target_x, target_y = hovered_icon_pos
                target_y -= CURSOR_RADIAL_Y_OFFSET
                self.cursor_state = "locked"
            elif hovered_npc:
                target_x = hovered_npc.rect.centerx
                target_y = hovered_npc.rect.top - 20
                self.cursor_state = "locked"
            else:
                hovered_slot = inventory_menu.get_hovered_slot(actual_pos)
                
                if hovered_slot:
                    self.cursor_state = "hover_slot"
                    target_x = actual_pos[0] + (self.hover_ui_img.get_width() // 2) - CURSOR_SLOT_INWARD_OFFSET
                    target_y = actual_pos[1] + (self.hover_ui_img.get_height() // 2) - CURSOR_SLOT_INWARD_OFFSET
                    
                elif inventory_menu.is_hovering(actual_pos):
                    self.cursor_state = "hover_ui"

        self.x += (target_x - self.x) * CURSOR_LERP_SPEED
        self.y += (target_y - self.y) * CURSOR_LERP_SPEED

    def draw(self, surface):
        img_to_draw = self.cursor_img
        
        if self.cursor_state == "locked":
            img_to_draw = self.selecting_img
        elif self.cursor_state in ("grabbing_human", "grabbing_item"):
            img_to_draw = self.grabbing_img
        elif self.cursor_state in ("hover_ui", "hover_slot"):
            img_to_draw = self.hover_ui_img
            
        if self.facing_left and self.cursor_state == "normal":
            img_to_draw = pygame.transform.flip(img_to_draw, True, False)
            
        draw_rect = img_to_draw.get_rect()
        
        if self.cursor_state == "grabbing_human":
            draw_rect.center = (self.x, self.y + CURSOR_GRABBING_Y_OFFSET)
        else:
            draw_rect.center = (self.x, self.y)
            
        surface.blit(img_to_draw, draw_rect)

# --- Environment Classes ---
class Boulder:
    def __init__(self, screen_w, base_sprite):
        self.x = random.randint(50, screen_w - 50)
        
        target_height = random.randint(BOULDER_HEIGHT_MIN, BOULDER_HEIGHT_MAX)
        scale_ratio = target_height / base_sprite.get_height()
        new_width = max(1, int(base_sprite.get_width() * scale_ratio))
        
        self.image = pygame.transform.scale(base_sprite, (new_width, target_height))
        
        if random.choice([True, False]):
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.y = get_dynamic_floor()
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def update(self, current_floor):
        self.y = current_floor
        self.rect.midbottom = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Tree:
    def __init__(self, screen_w, base_sprite):
        self.x = random.randint(50, screen_w - 50)
        
        target_height = random.randint(TREE_HEIGHT_MIN, TREE_HEIGHT_MAX)
        scale_ratio = target_height / base_sprite.get_height()
        new_width = max(1, int(base_sprite.get_width() * scale_ratio))
        
        self.image = pygame.transform.scale(base_sprite, (new_width, target_height))
        
        if random.choice([True, False]):
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.y = get_dynamic_floor()
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def update(self, current_floor):
        self.y = current_floor
        self.rect.midbottom = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# --- Dropped Item Physics Class ---
class DroppedItem:
    def __init__(self, item_id, item_type, sprite, count, x, y):
        self.id = item_id
        self.type = item_type
        self.sprite = sprite
        self.count = count
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.rect = self.sprite.get_rect(midbottom=(self.x, self.y))
        self.settled = False

    def update(self, current_floor):
        if not self.settled:
            self.vy += GRAVITY
            self.x += self.vx
            self.y += self.vy
            if self.y >= current_floor:
                self.y = current_floor
                self.vy = 0
                self.vx = 0
                self.settled = True
            self.rect.midbottom = (self.x, self.y)

    def draw(self, surface, item_font):
        surface.blit(self.sprite, self.rect)
        if self.count > 1:
            count_surf = item_font.render(str(self.count), True, (255, 255, 255))
            count_rect = count_surf.get_rect(bottomright=(self.rect.right, self.rect.bottom))
            for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                outline = item_font.render(str(self.count), True, (0,0,0))
                surface.blit(outline, count_rect.move(ox, oy))
            surface.blit(count_surf, count_rect)

class ItemGhost:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.vy = random.uniform(-2.0, -1.0)
        self.alpha = 255.0
        self.sprite = sprite.copy()

    def update(self):
        self.y += self.vy
        self.alpha -= 4  
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            temp = self.sprite.copy()
            temp.set_alpha(int(self.alpha))
            rect = temp.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(temp, rect)

# --- Dynamic Inventory Menu Class ---
class InventoryMenu:
    def __init__(self, assets, screen_w):
        self.screen_w = screen_w
        self.assets = assets
        self.bg_sprite = assets['backpack'].copy() 
        self.rect = self.bg_sprite.get_rect()
        self.active_npc = None
        self.mode = "inventory"
        
        self.slot_sprite = assets['backpackslot']
        self.tool_slot_sprite = assets['toolslot']
        
        self.slots = []         
        self.slot_sprites = []  
        self.slot_types = []    
        
        width, height = self.bg_sprite.get_size()
        px_array = pygame.PixelArray(self.bg_sprite)
        visited = set()
        
        for y in range(height):
            for x in range(width):
                if (x, y) not in visited:
                    color = self.bg_sprite.unmap_rgb(px_array[x, y])
                    is_red = (color.r == 255 and color.g == 0 and color.b == 0)
                    is_blue = (color.r == 0 and color.g == 0 and color.b == 255)
                    
                    if is_red or is_blue:
                        w = 0
                        while x + w < width:
                            c2 = self.bg_sprite.unmap_rgb(px_array[x + w, y])
                            if (is_red and c2.r == 255 and c2.g == 0 and c2.b == 0) or \
                               (is_blue and c2.r == 0 and c2.g == 0 and c2.b == 255):
                                w += 1
                            else:
                                break
                        h = 0
                        while y + h < height:
                            c3 = self.bg_sprite.unmap_rgb(px_array[x, y + h])
                            if (is_red and c3.r == 255 and c3.g == 0 and c3.b == 0) or \
                               (is_blue and c3.r == 0 and c3.g == 0 and c3.b == 255):
                                h += 1
                            else:
                                break
                                
                        slot_size = max(w, h)
                        new_slot = pygame.Rect(x, y, slot_size, slot_size)
                        
                        self.slots.append(new_slot)
                        
                        slot_type = "normal" if is_red else "tool"
                        self.slot_types.append(slot_type)
                        
                        sprite_to_use = self.slot_sprite if is_red else self.tool_slot_sprite
                        scaled_sprite = pygame.transform.scale(sprite_to_use, (slot_size, slot_size))
                        self.slot_sprites.append(scaled_sprite)
                        
                        for cy in range(y, y + h):
                            for cx in range(x, x + w):
                                visited.add((cx, cy))
                                px_array[cx, cy] = (0, 0, 0, 0)
                    else:
                        visited.add((x, y))
        
        px_array.close()
        
        combined = list(zip(self.slots, self.slot_types, self.slot_sprites))
        combined.sort(key=lambda item: (round(item[0].y / 10) * 10, item[0].x))
        if combined:
            self.slots, self.slot_types, self.slot_sprites = map(list, zip(*combined))
            
        self.num_base_slots = len(self.slots)

        # Setup Crafting UI components
        self.crafting_bg = assets['basiccrafting'].copy()
        
        # Ensure crafting background is bigger than the 3x3 slot grid
        CRAFT_SLOT_SIZE = 46  # Bigger than standard 32px slots
        CRAFT_PADDING = 5
        grid_w = 3 * CRAFT_SLOT_SIZE + 2 * CRAFT_PADDING
        grid_h = 3 * CRAFT_SLOT_SIZE + 2 * CRAFT_PADDING
        bg_w, bg_h = self.crafting_bg.get_size()
        
        if bg_w < grid_w + 30 or bg_h < grid_h + 30:
            new_w = max(bg_w, grid_w + 40)
            new_h = max(bg_h, grid_h + 40)
            self.crafting_bg = pygame.transform.scale(self.crafting_bg, (new_w, new_h))
            
        self.crafting_rect = self.crafting_bg.get_rect()
        
        # 9 slots for grid, 1 for output
        self.crafting_items = [None] * 10 
        self.crafting_slot_rects = []
        
        # Center the 3x3 grid perfectly inside the crafting background
        c_bg_w, c_bg_h = self.crafting_bg.get_size()
        start_x = (c_bg_w - grid_w) // 2
        start_y = (c_bg_h - grid_h) // 2
        
        for r in range(3):
            for c in range(3):
                rect = pygame.Rect(start_x + c * (CRAFT_SLOT_SIZE + CRAFT_PADDING), start_y + r * (CRAFT_SLOT_SIZE + CRAFT_PADDING), CRAFT_SLOT_SIZE, CRAFT_SLOT_SIZE)
                self.crafting_slot_rects.append(rect)
                
        # Setup lone Output Slot (Further Out on Top of Backpack)
        out_bg_size = CRAFT_SLOT_SIZE + 40
        self.crafting_out_bg = pygame.transform.scale(assets['basiccrafting'], (out_bg_size, out_bg_size))
        self.crafting_out_rect = self.crafting_out_bg.get_rect()
        
        out_c_x = (out_bg_size - CRAFT_SLOT_SIZE) // 2
        out_c_y = (out_bg_size - CRAFT_SLOT_SIZE) // 2
        self.crafting_out_slot_rect = pygame.Rect(out_c_x, out_c_y, CRAFT_SLOT_SIZE, CRAFT_SLOT_SIZE)

    def get_item(self, idx):
        if idx < self.num_base_slots:
            return self.active_npc.inventory[idx]
        else:
            return self.crafting_items[idx - self.num_base_slots]

    def set_item(self, idx, item):
        if idx < self.num_base_slots:
            self.active_npc.inventory[idx] = item
        else:
            self.crafting_items[idx - self.num_base_slots] = item

    def get_slot_type(self, idx):
        if idx == self.num_base_slots + 9:
            return "output"
        if idx < self.num_base_slots:
            return self.slot_types[idx]
        return "normal"

    def can_place_item(self, idx, item):
        st = self.get_slot_type(idx)
        if st == "output":
            return False
        return st == "normal" or item['type'] == "tool"

    def update_position(self):
        if not self.active_npc: return
        
        inv_w = self.rect.width
        craft_w = self.crafting_rect.width if self.mode == "crafting" else 0
        
        # Base width calculation for centering
        total_w = craft_w + inv_w if self.mode == "crafting" else inv_w
            
        start_x = self.active_npc.x - total_w // 2
        
        # Clamp horizontally to screen edges
        if start_x < 10:
            start_x = 10
        if start_x + total_w > self.screen_w - 10:
            start_x = self.screen_w - 10 - total_w
            
        y_pos = self.active_npc.y - 60
        
        if self.mode == "crafting":
            self.rect.bottomleft = (start_x + craft_w, y_pos)
            self.crafting_rect.midright = (self.rect.left, self.rect.centery)
            
            # Move the lone slot further out to the right, fully resting over the backpack
            self.crafting_out_rect.midleft = (self.rect.left + 25, self.rect.centery) 
        else:
            self.rect.bottomleft = (start_x, y_pos)

    def check_recipes(self):
        grid_ids = [[None] * 3 for _ in range(3)]
        total_items = 0
        log_count = 0
        for i in range(9):
            if self.crafting_items[i]:
                grid_ids[i // 3][i % 3] = self.crafting_items[i]['id']
                total_items += 1
                if self.crafting_items[i]['id'] == 'log':
                    log_count += 1
                    
        if total_items == 0:
            self.crafting_items[9] = None
            return
            
        is_plank = (total_items == 1 and log_count == 1)

        rows = [r for r in range(3) if any(grid_ids[r])]
        cols = [c for c in range(3) if any(grid_ids[r][c] for r in range(3))]
        
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)
        
        extracted = []
        for r in range(min_r, max_r + 1):
            row_data = []
            for c in range(min_c, max_c + 1):
                row_data.append(grid_ids[r][c])
            extracted.append(row_data)

        # -----------------
        # RECIPE PATTERNS
        # -----------------
        pickaxe_pattern = [
            ['pebble', 'pebble', 'pebble'],
            [None, 'vine', None],
            [None, 'stick', None]
        ]
        
        axe_left = [
            ['pebble', 'pebble'],
            ['pebble', 'vine'],
            [None, 'stick']
        ]
        
        axe_right = [
            ['pebble', 'pebble'],
            ['vine', 'pebble'],
            ['stick', None]
        ]

        def match(pattern):
            if len(extracted) != len(pattern): return False
            if len(extracted[0]) != len(pattern[0]): return False
            for r in range(len(extracted)):
                for c in range(len(extracted[0])):
                    if extracted[r][c] != pattern[r][c]:
                        return False
            return True

        if is_plank:
            self.crafting_items[9] = {
                'id': 'plank',
                'type': 'normal',
                'sprite': self.assets['plank'],
                'count': 4
            }
        elif match(pickaxe_pattern):
            self.crafting_items[9] = {
                'id': 'basicpickaxe',
                'type': 'tool',
                'sprite': self.assets['basicpickaxe'],
                'count': 1
            }
        elif match(axe_left) or match(axe_right):
            self.crafting_items[9] = {
                'id': 'basicaxe',
                'type': 'tool',
                'sprite': self.assets['basicaxe'],
                'count': 1
            }
        else:
            self.crafting_items[9] = None

    def consume_recipe(self):
        # Automatically consumes exactly 1 unit of everything in the grid
        for i in range(9):
            if self.crafting_items[i]:
                self.crafting_items[i]['count'] -= 1
                if self.crafting_items[i]['count'] <= 0:
                    self.crafting_items[i] = None

    def open_for(self, npc, mode="inventory"):
        drops = self.close() 
        self.active_npc = npc
        self.mode = mode
        npc.menu_open = True
        self.update_position()
        return drops

    def close(self):
        drops = []
        if self.active_npc:
            self.active_npc.menu_open = False
            self.active_npc = None
            
        # Prevent output item logic from throwing raw preview items, safely clear it
        self.crafting_items[9] = None
        
        # If any items are left in the crafting grid, pop them to the floor
        for i in range(9):
            if self.crafting_items[i] is not None:
                drops.append(self.crafting_items[i])
                self.crafting_items[i] = None
        return drops

    def handle_click(self, mouse_pos):
        if not self.active_npc:
            return False
        return True

    def get_hovered_slot_index(self, mouse_pos):
        if not self.active_npc:
            return None
        self.update_position()
            
        mx, my = mouse_pos
        
        if self.mode == "crafting":
            # Check output slot FIRST so it's clickable on top of overlaps
            absolute_out_rect = self.crafting_out_slot_rect.move(self.crafting_out_rect.x, self.crafting_out_rect.y)
            if absolute_out_rect.collidepoint(mx, my):
                return self.num_base_slots + 9
                
        for i, slot_rect in enumerate(self.slots):
            absolute_rect = slot_rect.move(self.rect.x, self.rect.y)
            if absolute_rect.collidepoint(mx, my):
                return i
                
        if self.mode == "crafting":
            for i, slot_rect in enumerate(self.crafting_slot_rects):
                absolute_rect = slot_rect.move(self.crafting_rect.x, self.crafting_rect.y)
                if absolute_rect.collidepoint(mx, my):
                    return self.num_base_slots + i
        return None

    def get_hovered_slot(self, mouse_pos):
        idx = self.get_hovered_slot_index(mouse_pos)
        if idx is not None:
            if idx < self.num_base_slots:
                return self.slots[idx].move(self.rect.x, self.rect.y)
            elif idx < self.num_base_slots + 9:
                c_idx = idx - self.num_base_slots
                return self.crafting_slot_rects[c_idx].move(self.crafting_rect.x, self.crafting_rect.y)
            else:
                return self.crafting_out_slot_rect.move(self.crafting_out_rect.x, self.crafting_out_rect.y)
        return None

    def is_hovering(self, mouse_pos):
        if not self.active_npc:
            return False
            
        self.update_position()
        if self.mode == "crafting":
            if self.crafting_out_rect.collidepoint(mouse_pos): return True
            if self.crafting_rect.collidepoint(mouse_pos): return True
        if self.rect.collidepoint(mouse_pos): return True
        return False

    def draw_item(self, surface, item, center, item_font):
        item_rect = item['sprite'].get_rect(center=center)
        surface.blit(item['sprite'], item_rect)
        if item['count'] > 1:
            count_surf = item_font.render(str(item['count']), True, (255, 255, 255))
            count_rect = count_surf.get_rect(bottomright=(item_rect.right + 2, item_rect.bottom + 2))
            for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                outline = item_font.render(str(item['count']), True, (0,0,0))
                surface.blit(outline, count_rect.move(ox, oy))
            surface.blit(count_surf, count_rect)

    def draw(self, surface, mouse_pos, item_font):
        if not self.active_npc:
            return
        self.update_position()
        mx, my = mouse_pos
        
        surface.blit(self.bg_sprite, self.rect.topleft)
        for idx, slot_rect in enumerate(self.slots):
            absolute_rect = slot_rect.move(self.rect.x, self.rect.y)
            is_hovered = absolute_rect.collidepoint((mx, my))
            base_slot_surf = self.slot_sprites[idx].copy()
            if is_hovered:
                highlight = pygame.Surface(absolute_rect.size, pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 50)) 
                base_slot_surf.blit(highlight, (0, 0))
            surface.blit(base_slot_surf, absolute_rect.topleft)
            
            item = self.active_npc.inventory[idx]
            if item:
                self.draw_item(surface, item, absolute_rect.center, item_font)

        if self.mode == "crafting":
            # Draw back panels
            surface.blit(self.crafting_out_bg, self.crafting_out_rect.topleft)
            surface.blit(self.crafting_bg, self.crafting_rect.topleft)
            
            # Draw 3x3 slots
            for idx, slot_rect in enumerate(self.crafting_slot_rects):
                absolute_rect = slot_rect.move(self.crafting_rect.x, self.crafting_rect.y)
                is_hovered = absolute_rect.collidepoint((mx, my))
                
                craft_slot_surf = pygame.transform.scale(self.slot_sprite, (slot_rect.width, slot_rect.height))
                if is_hovered:
                    highlight = pygame.Surface(absolute_rect.size, pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 50)) 
                    craft_slot_surf.blit(highlight, (0, 0))
                surface.blit(craft_slot_surf, absolute_rect.topleft)
                
                item = self.crafting_items[idx]
                if item:
                    self.draw_item(surface, item, absolute_rect.center, item_font)

            # Draw Output Slot completely last to ensure visual overlap priority
            absolute_out_rect = self.crafting_out_slot_rect.move(self.crafting_out_rect.x, self.crafting_out_rect.y)
            is_out_hovered = absolute_out_rect.collidepoint((mx, my))
            out_slot_surf = pygame.transform.scale(self.slot_sprite, (absolute_out_rect.width, absolute_out_rect.height))
            
            if is_out_hovered:
                highlight = pygame.Surface(absolute_out_rect.size, pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 50)) 
                out_slot_surf.blit(highlight, (0, 0))
            surface.blit(out_slot_surf, absolute_out_rect.topleft)
            
            out_item = self.crafting_items[9]
            if out_item:
                self.draw_item(surface, out_item, absolute_out_rect.center, item_font)

# --- Pause Menu Class ---
class PauseMenu:
    def __init__(self, screen_w, screen_h, assets):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.menu_sprite = assets['pausemenu']
        
        self.rect = self.menu_sprite.get_rect()
        self.rect.center = (screen_w // 2, screen_h // 2)
        
        font_path = assets.get('font_path')
        try:
            if font_path:
                self.font_opt = pygame.font.Font(font_path, 40)
            else:
                self.font_opt = pygame.font.SysFont("Courier New", 40, bold=True)
        except:
            self.font_opt = pygame.font.SysFont("Courier New", 40, bold=True)
        
        self.options = [
            "Placeholder 1", 
            "Placeholder 2", 
            "Placeholder 3", 
            "Quit Game"
        ]

    def is_hovering(self, mouse_pos):
        start_y = self.rect.bottom - 320 
        for i, opt in enumerate(self.options):
            opt_rect = pygame.Rect(self.rect.centerx - 200, start_y + (i * 45), 400, 40)
            if opt_rect.collidepoint(mouse_pos):
                return True
        return False

    def handle_click(self, mouse_pos):
        start_y = self.rect.bottom - 320 
        
        for i, opt in enumerate(self.options):
            opt_rect = pygame.Rect(self.rect.centerx - 200, start_y + (i * 45), 400, 40)
            if opt_rect.collidepoint(mouse_pos):
                return opt
        return None

    def draw(self, surface, mouse_pos):
        surface.blit(self.menu_sprite, self.rect.topleft)
        
        mx, my = mouse_pos
        start_y = self.rect.bottom - 320 
        
        for i, opt in enumerate(self.options):
            opt_rect = pygame.Rect(self.rect.centerx - 200, start_y + (i * 45), 400, 40)
            is_hovered = opt_rect.collidepoint((mx, my))
            
            if opt == "Quit Game":
                color = (255, 100, 100) if is_hovered else (200, 60, 60)
            else:
                color = (255, 215, 0) if is_hovered else (255, 255, 255) 
                
            text_surf = self.font_opt.render(opt, True, color)
            surface.blit(text_surf, text_surf.get_rect(center=opt_rect.center))

# --- Radial Menu Class ---
class RadialMenu:
    def __init__(self, assets):
        self.radius = RADIAL_MENU_RADIUS
        self.active_npc = None
        self.icons = {
            "move": assets['move'],
            "inventory": assets['inventory'],
            "build": assets['build'],
            "exit": assets['exit'],
            "crafting": assets['crafting'],
            "buildings": assets['buildings']
        }
        
        self.wedges_main = [
            ("move", -math.pi, -3*math.pi/4),
            ("inventory", -3*math.pi/4, -math.pi/2),
            ("build", -math.pi/2, -math.pi/4),
            ("exit", -math.pi/4, 0)
        ]
        
        self.wedges_build = [
            ("crafting", -math.pi, -2*math.pi/3),
            ("buildings", -2*math.pi/3, -math.pi/3),
            ("exit", -math.pi/3, 0)
        ]
        
        self.state = "main"
        self.wedges = self.wedges_main

    def set_state(self, state):
        self.state = state
        if state == "main":
            self.wedges = self.wedges_main
        elif state == "build":
            self.wedges = self.wedges_build

    def open_for(self, npc):
        self.active_npc = npc
        self.set_state("main")
        npc.menu_open = True

    def close(self):
        if self.active_npc:
            self.active_npc.menu_open = False
            self.active_npc = None

    def get_center(self):
        if not self.active_npc: 
            return (0, 0)
        return (self.active_npc.x, self.active_npc.y - 25)

    def get_hovered_icon_center(self, mouse_pos):
        if not self.active_npc:
            return None
            
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
                    mid_ang = (start_ang + end_ang) / 2
                    icon_dist = self.radius * 0.65
                    ix = cx + math.cos(mid_ang) * icon_dist
                    iy = cy + math.sin(mid_ang) * icon_dist
                    return (ix, iy)
        return None

    def handle_click(self, mouse_pos):
        if not self.active_npc:
            return None
            
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
                    return name
        return None

    def draw(self, surface, mouse_pos):
        if not self.active_npc:
            return
            
        cx, cy = self.get_center()
        mx, my = mouse_pos
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
    def __init__(self, name, sprite, screen_w, start_x, num_slots):
        self.name = name
        self.screen_w = screen_w
        self.taskbar_y = get_dynamic_floor() 
        
        scale_ratio = CHARACTER_TARGET_HEIGHT / sprite.get_height()
        new_width = max(1, int(sprite.get_width() * scale_ratio))
        self.base_sprite = pygame.transform.scale(sprite, (new_width, CHARACTER_TARGET_HEIGHT))
        
        self.x = start_x
        self.y = self.taskbar_y
        self.vy = 0
        
        self.vx = 0
        self.state = "idle" 
        self.state_timer = random.randint(IDLE_TIME_MIN, IDLE_TIME_MAX)
        self.facing_left = False
        self.walk_speed = random.uniform(WALK_SPEED_MIN, WALK_SPEED_MAX)
        
        self.menu_open = False
        self.is_dragged = False 
        self.rect = self.base_sprite.get_rect(midbottom=(self.x, self.y))
        
        self.anim_tick = 0
        self.angle = 0
        
        self.target_x = None
        self.target_boulder = None
        self.target_tree = None
        
        self.mining_yield = 0
        self.mining_duration = 0
        self.mining_timer = 0
        self.mining_ghost_ticks = []
        
        self.chopping_duration = 0
        self.chopping_timer = 0
        self.chopping_loot = []
        self.chopping_ghost_ticks = []
        
        self.inventory = [None] * num_slots

    def update(self, current_floor, dropped_items, boulders, trees, assets, inventory_menu, ghosts):
        if self.is_dragged:
            self.angle = math.sin(pygame.time.get_ticks() * 0.03) * 15
            return 
            
        if self.state in ["moving_to_mine", "mining"]:
            if self.target_boulder not in boulders:
                self.state = "idle"
                self.target_boulder = None
                self.target_x = None
                self.state_timer = 60
                self.vx = 0
                return
                
        if self.state in ["moving_to_chop", "chopping"]:
            if self.target_tree not in trees:
                self.state = "idle"
                self.target_tree = None
                self.target_x = None
                self.state_timer = 60
                self.vx = 0
                return
                
        if self.y < current_floor or self.state == "falling":
            self.state = "falling"
            self.vy += GRAVITY  
            self.y += self.vy
            self.angle += 20  
            
            if self.y >= current_floor:
                self.y = current_floor
                self.state = "idle"
                self.vy = 0
                self.angle = 0
                self.state_timer = 60 
                
            self.rect.midbottom = (self.x, self.y)
            return

        self.taskbar_y = current_floor
        self.y = current_floor
        self.rect.midbottom = (self.x, self.y)

        if self.menu_open:
            self.angle = 0 
            return

        if self.state == "moving_to_target" and self.target_x is not None:
            dx = self.target_x - self.x
            if abs(dx) <= self.walk_speed:
                self.x = self.target_x
                self.target_x = None
                self.state = "idle"
                self.vx = 0
                self.angle = 0
                self.state_timer = random.randint(IDLE_TIME_MIN, IDLE_TIME_MAX)
            else:
                self.vx = self.walk_speed if dx > 0 else -self.walk_speed
                self.x += self.vx
                self.facing_left = self.vx < 0
                self.anim_tick += 1
                self.angle = math.sin(self.anim_tick * 0.16) * 10
            self.rect.midbottom = (self.x, self.y)
            return
            
        if self.state == "moving_to_mine" and self.target_boulder is not None:
            dx = self.target_x - self.x
            if abs(dx) <= self.walk_speed + 40:
                self.state = "mining"
                self.vx = 0
                self.angle = 0
                self.facing_left = dx < 0
                self.mining_ghost_ticks = sorted([random.randint(10, self.mining_duration - 10) for _ in range(self.mining_yield)])
            else:
                self.vx = self.walk_speed if dx > 0 else -self.walk_speed
                self.x += self.vx
                self.facing_left = self.vx < 0
                self.anim_tick += 1
                self.angle = math.sin(self.anim_tick * 0.16) * 10
            self.rect.midbottom = (self.x, self.y)
            return
            
        if self.state == "moving_to_chop" and self.target_tree is not None:
            dx = self.target_x - self.x
            if abs(dx) <= self.walk_speed + 40:
                self.state = "chopping"
                self.vx = 0
                self.angle = 0
                self.facing_left = dx < 0
                
                logs = ['log'] * random.randint(2, 5)
                sticks = ['stick'] * random.randint(3, 7)
                vines = ['vine'] * random.randint(0, 3)
                self.chopping_loot = logs + sticks + vines
                random.shuffle(self.chopping_loot)
                
                self.chopping_duration = len(self.chopping_loot) * 30 
                self.chopping_timer = 0
                self.chopping_ghost_ticks = sorted([random.randint(10, self.chopping_duration - 10) for _ in self.chopping_loot])
            else:
                self.vx = self.walk_speed if dx > 0 else -self.walk_speed
                self.x += self.vx
                self.facing_left = self.vx < 0
                self.anim_tick += 1
                self.angle = math.sin(self.anim_tick * 0.16) * 10
            self.rect.midbottom = (self.x, self.y)
            return

        if self.state == "mining" and self.target_boulder is not None:
            self.mining_timer += 1
            self.anim_tick += 1
            
            while self.mining_ghost_ticks and self.mining_timer >= self.mining_ghost_ticks[0]:
                self.mining_ghost_ticks.pop(0)
                ghosts.append(ItemGhost(self.target_boulder.rect.centerx + random.randint(-15, 15), self.target_boulder.rect.centery - 10, assets['pebble']))
                
                added = False
                for idx, item in enumerate(self.inventory):
                    if inventory_menu.get_slot_type(idx) == "normal" and item and item['id'] == 'pebble' and item['count'] < MAX_STACK_SIZE:
                        item['count'] += 1
                        added = True
                        break
                if not added:
                    for idx, item in enumerate(self.inventory):
                        if inventory_menu.get_slot_type(idx) == "normal" and item is None:
                            self.inventory[idx] = {'id': 'pebble', 'type': 'normal', 'sprite': assets['pebble'], 'count': 1}
                            added = True
                            break
                if not added:
                    dropped_items.append(DroppedItem("pebble", "normal", assets['pebble'], 1, self.target_boulder.x, self.y))

            if self.mining_timer >= self.mining_duration:
                if self.target_boulder in boulders:
                    boulders.remove(self.target_boulder)
                
                self.state = "idle"
                self.target_boulder = None
                self.target_x = None
                self.state_timer = 60
            return

        if self.state == "chopping" and self.target_tree is not None:
            self.chopping_timer += 1
            self.anim_tick += 1
            
            while self.chopping_ghost_ticks and self.chopping_timer >= self.chopping_ghost_ticks[0]:
                self.chopping_ghost_ticks.pop(0)
                item_type_str = self.chopping_loot.pop(0)
                
                ghosts.append(ItemGhost(self.target_tree.rect.centerx + random.randint(-15, 15), self.target_tree.rect.centery - 10, assets[item_type_str]))
                
                added = False
                for idx, item in enumerate(self.inventory):
                    if inventory_menu.get_slot_type(idx) == "normal" and item and item['id'] == item_type_str and item['count'] < MAX_STACK_SIZE:
                        item['count'] += 1
                        added = True
                        break
                if not added:
                    for idx, item in enumerate(self.inventory):
                        if inventory_menu.get_slot_type(idx) == "normal" and item is None:
                            self.inventory[idx] = {'id': item_type_str, 'type': 'normal', 'sprite': assets[item_type_str], 'count': 1}
                            added = True
                            break
                if not added:
                    dropped_items.append(DroppedItem(item_type_str, "normal", assets[item_type_str], 1, self.target_tree.x, self.y))

            if self.chopping_timer >= self.chopping_duration:
                if self.target_tree in trees:
                    trees.remove(self.target_tree)
                
                self.state = "idle"
                self.target_tree = None
                self.target_x = None
                self.state_timer = 60
            return

        self.state_timer -= 1
        if self.state_timer <= 0:
            if self.state == "idle":
                self.state = "walk"
                self.vx = random.choice([-self.walk_speed, self.walk_speed])
                self.state_timer = random.randint(WALK_TIME_MIN, WALK_TIME_MAX) 
            else:
                self.state = "idle"
                self.vx = 0
                self.state_timer = random.randint(IDLE_TIME_MIN, IDLE_TIME_MAX) 

        if self.state == "walk":
            self.x += self.vx
            self.facing_left = self.vx < 0
            
            self.anim_tick += 1
            self.angle = math.sin(self.anim_tick * 0.16) * 10
            
            if self.x < 30:
                self.x = 30
                self.vx *= -1
                self.facing_left = False
            elif self.x > self.screen_w - 30:
                self.x = self.screen_w - 30
                self.vx *= -1
                self.facing_left = True
        else:
            self.angle = 0

    def draw(self, surface, assets):
        img = pygame.transform.flip(self.base_sprite, self.facing_left, False)
        img = pygame.transform.rotate(img, self.angle)
        draw_rect = img.get_rect()
        draw_rect.midbottom = (self.x, self.y) 
        surface.blit(img, draw_rect)
        
        if self.state == "mining" and self.target_boulder:
            pick_sprite = assets['basicpickaxe']
            swing_angle = math.sin(self.anim_tick * 0.3) * 45
            if self.facing_left:
                swing_angle = -swing_angle
                pick_sprite = pygame.transform.flip(pick_sprite, True, False)
            
            rotated_pick = pygame.transform.rotate(pick_sprite, swing_angle)
            offset_x = -20 if self.facing_left else 20
            pick_rect = rotated_pick.get_rect(center=(self.x + offset_x, self.y - 25))
            surface.blit(rotated_pick, pick_rect)

            bar_w = 40
            bar_h = 6
            bar_x = self.target_boulder.x - bar_w // 2
            bar_y = self.target_boulder.rect.centery - bar_h // 2
            
            progress = self.mining_timer / self.mining_duration
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, int(bar_w * progress), bar_h))
            pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1)

        if self.state == "chopping" and self.target_tree:
            axe_sprite = assets['basicaxe']
            swing_angle = math.sin(self.anim_tick * 0.3) * 45
            if self.facing_left:
                swing_angle = -swing_angle
                axe_sprite = pygame.transform.flip(axe_sprite, True, False)
            
            rotated_axe = pygame.transform.rotate(axe_sprite, swing_angle)
            offset_x = -20 if self.facing_left else 20
            axe_rect = rotated_axe.get_rect(center=(self.x + offset_x, self.y - 25))
            surface.blit(rotated_axe, axe_rect)

            bar_w = 40
            bar_h = 6
            bar_x = self.target_tree.x - bar_w // 2
            bar_y = self.target_tree.rect.centery - bar_h // 2
            
            progress = self.chopping_timer / max(1, self.chopping_duration)
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, int(bar_w * progress), bar_h))
            pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1)

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
        self.scale = random.uniform(CLOUD_SCALE_MIN, CLOUD_SCALE_MAX)
        self.speed = random.uniform(CLOUD_SPEED_MIN, CLOUD_SPEED_MAX)
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

def load_assets():
    asset_dir = os.path.join(os.path.dirname(__file__), "assets")
    assets = {}
    
    custom_font_path = os.path.join(asset_dir, "PixelDart.ttf")
    if os.path.exists(custom_font_path):
        assets['font_path'] = custom_font_path
    else:
        assets['font_path'] = None
    
    assets['sprites'] = {}
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

    for icon_name in ["move", "inventory", "build", "exit", "crafting", "buildings"]:
        try:
            img = pygame.image.load(os.path.join(asset_dir, f"{icon_name}.png")).convert_alpha()
            assets[icon_name] = pygame.transform.scale(img, (28, 28))
        except pygame.error:
            assets[icon_name] = create_fallback_icon(icon_name, assets['font_path'])
            
    try:
        assets['pausemenu'] = pygame.image.load(os.path.join(asset_dir, "pausemenu.png")).convert_alpha()
    except pygame.error:
        assets['pausemenu'] = create_fallback_pause_menu_png()

    try:
        craft_img = pygame.image.load(os.path.join(asset_dir, "basiccrafting.png")).convert_alpha()
        assets['basiccrafting'] = craft_img
    except pygame.error:
        assets['basiccrafting'] = create_fallback_basiccrafting_png()
        
    try:
        bag_img = pygame.image.load(os.path.join(asset_dir, "backpack.png")).convert_alpha()
        new_w = max(1, int(bag_img.get_width() * BACKPACK_SCALE))
        new_h = max(1, int(bag_img.get_height() * BACKPACK_SCALE))
        assets['backpack'] = pygame.transform.scale(bag_img, (new_w, new_h))
    except pygame.error:
        fb_img = create_fallback_backpack_png()
        new_w = max(1, int(fb_img.get_width() * BACKPACK_SCALE))
        new_h = max(1, int(fb_img.get_height() * BACKPACK_SCALE))
        assets['backpack'] = pygame.transform.scale(fb_img, (new_w, new_h))

    try:
        cur_img = pygame.image.load(os.path.join(asset_dir, "cursor.png")).convert_alpha()
        assets['cursor'] = pygame.transform.scale(cur_img, (60, 60))
    except pygame.error:
        assets['cursor'] = pygame.transform.scale(create_fallback_cursor_png(), (60, 60))
        
    try:
        sel_img = pygame.image.load(os.path.join(asset_dir, "selecting.png")).convert_alpha()
        assets['selecting'] = pygame.transform.scale(sel_img, (60, 60))
    except pygame.error:
        assets['selecting'] = pygame.transform.scale(create_fallback_selecting_png(), (60, 60))

    try:
        grab_img = pygame.image.load(os.path.join(asset_dir, "grabbing.png")).convert_alpha()
        assets['grabbing'] = pygame.transform.scale(grab_img, (60, 60))
    except pygame.error:
        assets['grabbing'] = pygame.transform.scale(create_fallback_grabbing_png(), (60, 60))

    try:
        bslot_img = pygame.image.load(os.path.join(asset_dir, "backpackslot.png")).convert_alpha()
        assets['backpackslot'] = bslot_img
    except pygame.error:
        assets['backpackslot'] = create_fallback_backpackslot_png()
        
    try:
        tslot_img = pygame.image.load(os.path.join(asset_dir, "toolslot.png")).convert_alpha()
        assets['toolslot'] = tslot_img
    except pygame.error:
        assets['toolslot'] = create_fallback_toolslot_png()

    try:
        peb_img = pygame.image.load(os.path.join(asset_dir, "pebble.png")).convert_alpha()
        assets['pebble'] = pygame.transform.scale(peb_img, (ITEM_BASE_SIZE, ITEM_BASE_SIZE))
    except pygame.error:
        assets['pebble'] = pygame.transform.scale(create_fallback_pebble_png(), (ITEM_BASE_SIZE, ITEM_BASE_SIZE))

    try:
        stick_img = pygame.image.load(os.path.join(asset_dir, "stick.png")).convert_alpha()
        assets['stick'] = pygame.transform.scale(stick_img, (ITEM_BASE_SIZE, ITEM_BASE_SIZE))
    except pygame.error:
        assets['stick'] = pygame.transform.scale(create_fallback_stick_png(), (ITEM_BASE_SIZE, ITEM_BASE_SIZE))

    try:
        vine_img = pygame.image.load(os.path.join(asset_dir, "vine.png")).convert_alpha()
        assets['vine'] = pygame.transform.scale(vine_img, (ITEM_BASE_SIZE, ITEM_BASE_SIZE))
    except pygame.error:
        assets['vine'] = pygame.transform.scale(create_fallback_vine_png(), (ITEM_BASE_SIZE, ITEM_BASE_SIZE))

    try:
        log_img = pygame.image.load(os.path.join(asset_dir, "log.png")).convert_alpha()
        assets['log'] = pygame.transform.scale(log_img, (ITEM_BASE_SIZE, ITEM_BASE_SIZE))
    except pygame.error:
        assets['log'] = pygame.transform.scale(create_fallback_log_png(), (ITEM_BASE_SIZE, ITEM_BASE_SIZE))

    try:
        plank_img = pygame.image.load(os.path.join(asset_dir, "plank.png")).convert_alpha()
        assets['plank'] = pygame.transform.scale(plank_img, (ITEM_BASE_SIZE, ITEM_BASE_SIZE))
    except pygame.error:
        assets['plank'] = pygame.transform.scale(create_fallback_plank_png(), (ITEM_BASE_SIZE, ITEM_BASE_SIZE))

    try:
        boulder_img = pygame.image.load(os.path.join(asset_dir, "boulder.png")).convert_alpha()
        assets['boulder'] = boulder_img
    except pygame.error:
        assets['boulder'] = create_fallback_boulder_png()

    try:
        pick_img = pygame.image.load(os.path.join(asset_dir, "basicpickaxe.png")).convert_alpha()
        assets['basicpickaxe'] = pygame.transform.scale(pick_img, (TOOL_BASE_SIZE, TOOL_BASE_SIZE))
    except pygame.error:
        assets['basicpickaxe'] = pygame.transform.scale(create_fallback_basicpickaxe_png(), (TOOL_BASE_SIZE, TOOL_BASE_SIZE))

    try:
        axe_img = pygame.image.load(os.path.join(asset_dir, "basicaxe.png")).convert_alpha()
        assets['basicaxe'] = pygame.transform.scale(axe_img, (TOOL_BASE_SIZE, TOOL_BASE_SIZE))
    except pygame.error:
        assets['basicaxe'] = pygame.transform.scale(create_fallback_basicaxe_png(), (TOOL_BASE_SIZE, TOOL_BASE_SIZE))

    try:
        movedot_img = pygame.image.load(os.path.join(asset_dir, "movedot.png")).convert_alpha()
        assets['movedot'] = pygame.transform.scale(movedot_img, (8, 8))
    except pygame.error:
        assets['movedot'] = create_fallback_movedot_png()

    try:
        tree_img = pygame.image.load(os.path.join(asset_dir, "tree.png")).convert_alpha()
        assets['tree'] = tree_img
    except pygame.error:
        assets['tree'] = create_fallback_tree_png()

    return assets

# Utility helpers for safe inventory drops
def handle_inventory_close(inventory_menu, dropped_items_list, drop_x, drop_y):
    drops = inventory_menu.close()
    for d in drops:
        dropped_items_list.append(DroppedItem(d['id'], d['type'], d['sprite'], d['count'], drop_x, drop_y))

def handle_inventory_open(inventory_menu, npc, mode, dropped_items_list, drop_x, drop_y):
    drops = inventory_menu.open_for(npc, mode)
    for d in drops:
        dropped_items_list.append(DroppedItem(d['id'], d['type'], d['sprite'], d['count'], drop_x, drop_y))

def main():
    pygame.init()
    
    screen, screen_w, screen_h = setup_transparent_fullscreen()
    clock = pygame.time.Clock()
    
    pygame.mouse.set_visible(False)
    
    pygame.font.init()
    
    assets = load_assets()
    sprites = assets['sprites']
    
    font_path = assets.get('font_path')
    try:
        if font_path:
            debug_font = pygame.font.Font(font_path, 18)
            item_font = pygame.font.Font(font_path, 14)
        else:
            debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
            item_font = pygame.font.SysFont("Courier New", 14, bold=True)
    except:
        debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
        item_font = pygame.font.SysFont("Courier New", 14, bold=True)
        
    debug_mode = False
    game_paused = False 
    
    potential_drag_npc = None
    mouse_down_time = 0
    
    dragging_npc = None
    drag_offset_x = 0
    drag_offset_y = 0
    
    # --- Move Command State ---
    pending_move_command = None

    # --- Item Dragging State ---
    dragging_item = None
    inv_drag_button = None
    inv_drag_active = False
    inv_drag_start_pos = (0, 0)
    inv_dragged_slots = []
    inv_drag_initial_count = 0
    inv_drag_initial_slot_counts = {}
    
    radial_menu = RadialMenu(assets)
    pause_menu = PauseMenu(screen_w, screen_h, assets)
    inventory_menu = InventoryMenu(assets, screen_w) 
    
    num_slots = len(inventory_menu.slots)
    if num_slots == 0:
        print("WARNING: No slots found in backpack. Inventory will be empty.")
    
    custom_cursor = CustomCursor(assets)
    
    adam = Person("Adam", assets['adam'], screen_w, screen_w // 3, num_slots)
    eve = Person("Eve", assets['eve'], screen_w, (screen_w // 3) * 2, num_slots)
    characters = [adam, eve]
    
    normal_indices = [i for i, st in enumerate(inventory_menu.slot_types) if st == "normal"]
    
    if normal_indices:
        adam_avail = list(normal_indices)
        random.shuffle(adam_avail)
        
        for _ in range(min(3, len(adam_avail))):
            idx = adam_avail.pop()
            adam.inventory[idx] = {"id": "pebble", "type": "normal", "sprite": assets['pebble'], "count": 1}
            
        if adam_avail:
            idx = adam_avail.pop()
            adam.inventory[idx] = {"id": "vine", "type": "normal", "sprite": assets['vine'], "count": 2}
            
        eve_avail = list(normal_indices)
        random.shuffle(eve_avail)
        
        for _ in range(min(4, len(eve_avail))):
            idx = eve_avail.pop()
            eve.inventory[idx] = {"id": "stick", "type": "normal", "sprite": assets['stick'], "count": 1}
    
    current_weather = WEATHER_CLOUDY
    weather_timer = 0
    MAX_DEPLETION = FPS * MAX_WATER_DEPLETION_SECONDS 
    WEATHER_CHANGE_TIME = FPS * WEATHER_CHANGE_TIME_SECONDS
    
    water_depletion = 0 
    
    current_wind = 0.0
    target_wind = 0.0
    
    # Environment Setup
    boulders = []
    num_boulders = random.randint(2, 4)
    for _ in range(num_boulders):
        boulders.append(Boulder(screen_w, assets['boulder']))

    trees = []
    num_trees = random.randint(1, 3)
    for _ in range(num_trees):
        trees.append(Tree(screen_w, assets['tree']))

    clouds = []
    for _ in range(6):
        clouds.append(Cloud(screen_w, screen_h, sprites, current_weather, clouds))
        
    raindrops = []
    splashes = []
    dropped_items = []
    ghosts = []

    running = True
    while running:
        current_floor = get_dynamic_floor()
        
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        actual_mouse_pos = (pt.x, pt.y)
        custom_mouse_pos = (int(custom_cursor.x), int(custom_cursor.y))
        
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
                    
            if event.type == pygame.MOUSEMOTION:
                if dragging_npc:
                    dragging_npc.x = custom_mouse_pos[0] + drag_offset_x
                    dragging_npc.y = custom_mouse_pos[1] + drag_offset_y
                    dragging_npc.rect.midbottom = (dragging_npc.x, dragging_npc.y)
                    
                # --- Item Dragging Distribution Logic ---
                if dragging_item and inv_drag_button is not None:
                    if not inv_drag_active:
                        dist = math.hypot(actual_mouse_pos[0] - inv_drag_start_pos[0], actual_mouse_pos[1] - inv_drag_start_pos[1])
                        if dist > DRAG_DROP_THRESHOLD:
                            # Safely prevent wiggles outside the inventory from breaking the item click
                            if inventory_menu.active_npc and inventory_menu.get_hovered_slot_index(actual_mouse_pos) is not None:
                                inv_drag_active = True
                            
                    if inv_drag_active and inventory_menu.active_npc:
                        slot_idx = inventory_menu.get_hovered_slot_index(actual_mouse_pos)
                        
                        if inv_drag_button == 1: 
                            if slot_idx is not None and slot_idx not in inv_dragged_slots:
                                can_place = inventory_menu.can_place_item(slot_idx, dragging_item)
                                target = inventory_menu.get_item(slot_idx)
                                if can_place and (target is None or target['id'] == dragging_item['id']):
                                    inv_drag_initial_slot_counts[slot_idx] = target['count'] if target else 0
                                    inv_dragged_slots.append(slot_idx)
                                    
                            if inv_dragged_slots:
                                for s_idx in inv_dragged_slots:
                                    base = inv_drag_initial_slot_counts[s_idx]
                                    if base == 0:
                                        inventory_menu.set_item(s_idx, None)
                                    else:
                                        inventory_menu.get_item(s_idx)['count'] = base
                                        
                                per_slot = inv_drag_initial_count // len(inv_dragged_slots)
                                current_held = inv_drag_initial_count
                                
                                for s_idx in inv_dragged_slots:
                                    base_count = inv_drag_initial_slot_counts[s_idx]
                                    space = MAX_STACK_SIZE - base_count
                                    add_amt = min(per_slot, space)
                                    
                                    new_count = base_count + add_amt
                                    current_held -= add_amt
                                    
                                    if inventory_menu.get_item(s_idx) is None:
                                        if new_count > 0:
                                            inventory_menu.set_item(s_idx, {
                                                'id': dragging_item['id'], 
                                                'type': dragging_item['type'], 
                                                'sprite': dragging_item['sprite'], 
                                                'count': new_count
                                            })
                                    else:
                                        inventory_menu.get_item(s_idx)['count'] = new_count
                                        
                                dragging_item['count'] = current_held

                        elif inv_drag_button == 3: 
                            if slot_idx is not None and slot_idx not in inv_dragged_slots:
                                can_place = inventory_menu.can_place_item(slot_idx, dragging_item)
                                target = inventory_menu.get_item(slot_idx)
                                if can_place and (target is None or target['id'] == dragging_item['id']):
                                    if dragging_item['count'] > 0 and (target is None or target['count'] < MAX_STACK_SIZE):
                                        dragging_item['count'] -= 1
                                        inv_dragged_slots.append(slot_idx)
                                        if target is None:
                                            inventory_menu.set_item(slot_idx, {
                                                'id': dragging_item['id'], 
                                                'type': dragging_item['type'], 
                                                'sprite': dragging_item['sprite'], 
                                                'count': 1
                                            })
                                        else:
                                            target['count'] += 1
                
            if event.type == pygame.MOUSEBUTTONUP and event.button in [1, 3]:
                if potential_drag_npc and event.button == 1:
                    radial_menu.open_for(potential_drag_npc)
                    potential_drag_npc = None
                    
                if dragging_npc and event.button == 1:
                    dragging_npc.state = "falling"
                    dragging_npc.vy = 0 
                    dragging_npc.is_dragged = False
                    dragging_npc.target_x = None 
                    dragging_npc.target_boulder = None
                    dragging_npc.target_tree = None
                    dragging_npc = None
                    
                # --- ITEM DROPPING LOGIC ---
                if dragging_item and inv_drag_button == event.button:
                    slot_idx = None
                    if inventory_menu.active_npc and inventory_menu.is_hovering(actual_mouse_pos):
                        slot_idx = inventory_menu.get_hovered_slot_index(actual_mouse_pos)
                    
                    clicked_npc = None
                    if slot_idx is None:
                        for char in characters:
                            click_rect = char.rect.copy()
                            click_rect.y -= 40
                            click_rect.height += 40
                            if click_rect.collidepoint(custom_mouse_pos):
                                clicked_npc = char
                                break

                    if not inv_drag_active: 
                        # Single Click execution
                        if slot_idx is not None:
                            can_place = inventory_menu.can_place_item(slot_idx, dragging_item)
                            if can_place:
                                target = inventory_menu.get_item(slot_idx)
                                if inv_drag_button == 1: 
                                    if target is None:
                                        inventory_menu.set_item(slot_idx, dragging_item)
                                        dragging_item = None
                                    elif target['id'] == dragging_item['id']:
                                        total = target['count'] + dragging_item['count']
                                        if total <= MAX_STACK_SIZE:
                                            target['count'] = total
                                            dragging_item = None
                                        else:
                                            target['count'] = MAX_STACK_SIZE
                                            dragging_item['count'] = total - MAX_STACK_SIZE
                                    else:
                                        inventory_menu.set_item(slot_idx, dragging_item)
                                        dragging_item = target
                                elif inv_drag_button == 3: 
                                    if target is None:
                                        inventory_menu.set_item(slot_idx, {
                                            'id': dragging_item['id'], 
                                            'type': dragging_item['type'], 
                                            'sprite': dragging_item['sprite'], 
                                            'count': 1
                                        })
                                        dragging_item['count'] -= 1
                                    elif target['id'] == dragging_item['id'] and target['count'] < MAX_STACK_SIZE:
                                        target['count'] += 1
                                        dragging_item['count'] -= 1
                        
                        elif clicked_npc:
                            for idx, inv_item in enumerate(clicked_npc.inventory):
                                can_place = inventory_menu.can_place_item(idx, dragging_item)
                                if can_place and inv_item and inv_item['id'] == dragging_item['id']:
                                    space = MAX_STACK_SIZE - inv_item['count']
                                    if space > 0:
                                        add_amt = min(space, dragging_item['count'])
                                        inv_item['count'] += add_amt
                                        dragging_item['count'] -= add_amt
                                        if dragging_item['count'] <= 0:
                                            break
                            if dragging_item and dragging_item['count'] > 0:
                                for idx, inv_item in enumerate(clicked_npc.inventory):
                                    can_place = inventory_menu.can_place_item(idx, dragging_item)
                                    if can_place and inv_item is None:
                                        clicked_npc.inventory[idx] = {
                                            'id': dragging_item['id'], 
                                            'type': dragging_item['type'], 
                                            'sprite': dragging_item['sprite'], 
                                            'count': dragging_item['count']
                                        }
                                        dragging_item = None
                                        break
                            radial_menu.close()
                            handle_inventory_close(inventory_menu, dropped_items, actual_mouse_pos[0], actual_mouse_pos[1])
                            
                        else:
                            # Drop entirely to floor
                            drop_x, drop_y = actual_mouse_pos
                            if inv_drag_button == 1 and dragging_item['count'] > 0:
                                dropped_items.append(DroppedItem(dragging_item['id'], dragging_item['type'], dragging_item['sprite'], dragging_item['count'], drop_x, drop_y))
                                dragging_item = None
                            elif inv_drag_button == 3 and dragging_item['count'] > 0:
                                dropped_items.append(DroppedItem(dragging_item['id'], dragging_item['type'], dragging_item['sprite'], 1, drop_x, drop_y))
                                dragging_item['count'] -= 1

                    else:
                        # Drag was active. If released outside, perfectly drop the remainder to floor.
                        if slot_idx is None and not clicked_npc:
                            drop_x, drop_y = actual_mouse_pos
                            if dragging_item['count'] > 0:
                                dropped_items.append(DroppedItem(dragging_item['id'], dragging_item['type'], dragging_item['sprite'], dragging_item['count'], drop_x, drop_y))
                            dragging_item = None

                    inv_drag_button = None
                    inv_drag_active = False
                    inv_dragged_slots = []
                    if dragging_item and dragging_item['count'] <= 0:
                        dragging_item = None
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in [1, 3]:
                if game_paused:
                    action = pause_menu.handle_click(actual_mouse_pos)
                    if action == "Quit Game":
                        running = False
                    elif action:
                        print(f"Pause Menu Clicked: {action}")
                    continue 

                if pending_move_command:
                    if event.button == 1:
                        clicked_boulder = None
                        for b in boulders:
                            if b.rect.collidepoint(actual_mouse_pos):
                                clicked_boulder = b
                                break
                                
                        clicked_tree = None
                        if not clicked_boulder:
                            for t in trees:
                                if t.rect.collidepoint(actual_mouse_pos):
                                    clicked_tree = t
                                    break
                        
                        if clicked_boulder:
                            has_pickaxe = False
                            for idx, item in enumerate(pending_move_command.inventory):
                                if inventory_menu.get_slot_type(idx) == "tool" and item and item['id'] == 'basicpickaxe':
                                    has_pickaxe = True
                                    break
                            
                            if has_pickaxe:
                                pending_move_command.target_boulder = clicked_boulder
                                pending_move_command.target_x = clicked_boulder.x
                                pending_move_command.state = "moving_to_mine"
                                pending_move_command.mining_yield = random.randint(2, 5)
                                pending_move_command.mining_duration = pending_move_command.mining_yield * 60
                                pending_move_command.mining_timer = 0
                                pending_move_command.mining_ghost_ticks = sorted([random.randint(10, pending_move_command.mining_duration - 10) for _ in range(pending_move_command.mining_yield)])
                            else:
                                pending_move_command.target_x = clicked_boulder.x
                                pending_move_command.state = "moving_to_target"
                                
                        elif clicked_tree:
                            has_axe = False
                            for idx, item in enumerate(pending_move_command.inventory):
                                if inventory_menu.get_slot_type(idx) == "tool" and item and item['id'] == 'basicaxe':
                                    has_axe = True
                                    break
                                    
                            if has_axe:
                                pending_move_command.target_tree = clicked_tree
                                pending_move_command.target_x = clicked_tree.x
                                pending_move_command.state = "moving_to_chop"
                            else:
                                pending_move_command.target_x = clicked_tree.x
                                pending_move_command.state = "moving_to_target"
                        else:
                            target_x = max(30, min(screen_w - 30, actual_mouse_pos[0]))
                            pending_move_command.target_x = target_x
                            pending_move_command.state = "moving_to_target"
                            
                        pending_move_command = None
                    elif event.button == 3:
                        pending_move_command = None
                    continue
                
                # --- IF WE ARE ALREADY HOLDING AN ITEM ---
                if dragging_item:
                    inv_drag_button = event.button
                    inv_drag_active = False
                    inv_drag_start_pos = actual_mouse_pos
                    inv_dragged_slots = []
                    inv_drag_initial_count = dragging_item['count']
                    inv_drag_initial_slot_counts = {}
                    
                    if inventory_menu.active_npc:
                        slot_idx = inventory_menu.get_hovered_slot_index(actual_mouse_pos)
                        if slot_idx is not None:
                            can_place = inventory_menu.can_place_item(slot_idx, dragging_item)
                            if can_place:
                                target = inventory_menu.get_item(slot_idx)
                                inv_drag_initial_slot_counts = {slot_idx: target['count'] if target else 0}
                    continue 

                # --- IF WE HAVE AN EMPTY HAND ---
                if inventory_menu.active_npc:
                    slot_idx = inventory_menu.get_hovered_slot_index(actual_mouse_pos)
                    if slot_idx is not None:
                        item = inventory_menu.get_item(slot_idx)
                        if item:
                            if event.button == 1: 
                                dragging_item = item
                                inventory_menu.set_item(slot_idx, None)
                                if slot_idx == inventory_menu.num_base_slots + 9:
                                    inventory_menu.consume_recipe()
                            elif event.button == 3: 
                                if slot_idx == inventory_menu.num_base_slots + 9:
                                    dragging_item = item
                                    inventory_menu.set_item(slot_idx, None)
                                    inventory_menu.consume_recipe()
                                else:
                                    half = math.ceil(item['count'] / 2)
                                    dragging_item = {'id': item['id'], 'type': item['type'], 'sprite': item['sprite'], 'count': half}
                                    item['count'] -= half
                                    if item['count'] == 0:
                                        inventory_menu.set_item(slot_idx, None)
                            continue 
                    elif inventory_menu.is_hovering(actual_mouse_pos):
                        continue 
                    elif event.button == 1:
                        handle_inventory_close(inventory_menu, dropped_items, actual_mouse_pos[0], actual_mouse_pos[1])
                
                if radial_menu.active_npc and event.button == 1:
                    action = radial_menu.handle_click(actual_mouse_pos)
                    if action:
                        if action == "exit":
                            if radial_menu.state == "build":
                                radial_menu.set_state("main")
                            else:
                                radial_menu.close()
                        elif action == "move":
                            pending_move_command = radial_menu.active_npc
                            radial_menu.close()
                        elif action == "build":
                            radial_menu.set_state("build")
                        elif action == "inventory":
                            npc = radial_menu.active_npc
                            radial_menu.close()
                            handle_inventory_open(inventory_menu, npc, "inventory", dropped_items, actual_mouse_pos[0], actual_mouse_pos[1])
                        elif action == "crafting":
                            npc = radial_menu.active_npc
                            radial_menu.close()
                            handle_inventory_open(inventory_menu, npc, "crafting", dropped_items, actual_mouse_pos[0], actual_mouse_pos[1])
                        else:
                            print(f"Clicked {action} - Feature not yet implemented!")
                        continue

                clicked_dropped = None
                for d_item in reversed(dropped_items):
                    if d_item.rect.inflate(15, 15).collidepoint(custom_mouse_pos):
                        clicked_dropped = d_item
                        break
                        
                if clicked_dropped:
                    if event.button == 1:
                        dragging_item = {'id': clicked_dropped.id, 'type': clicked_dropped.type, 'sprite': clicked_dropped.sprite, 'count': clicked_dropped.count}
                        dropped_items.remove(clicked_dropped)
                    elif event.button == 3:
                        half = math.ceil(clicked_dropped.count / 2)
                        dragging_item = {'id': clicked_dropped.id, 'type': clicked_dropped.type, 'sprite': clicked_dropped.sprite, 'count': half}
                        clicked_dropped.count -= half
                        if clicked_dropped.count <= 0:
                            dropped_items.remove(clicked_dropped)
                    continue
                
                if event.button == 1:
                    clicked_npc = None
                    for char in characters:
                        click_rect = char.rect.copy()
                        click_rect.y -= 40
                        click_rect.height += 40
                        if click_rect.collidepoint(custom_mouse_pos):
                            clicked_npc = char
                            break
                            
                    if clicked_npc:
                        potential_drag_npc = clicked_npc
                        mouse_down_time = pygame.time.get_ticks()
                        
                        drag_offset_x = clicked_npc.x - custom_mouse_pos[0]
                        drag_offset_y = clicked_npc.y - custom_mouse_pos[1] 
                        
                        radial_menu.close()
                        handle_inventory_close(inventory_menu, dropped_items, actual_mouse_pos[0], actual_mouse_pos[1])
                        continue
                    
                    for cloud in clouds:
                        if cloud.handle_click(custom_mouse_pos):
                            water_depletion += FPS * 5 
                            if water_depletion > MAX_DEPLETION:
                                water_depletion = MAX_DEPLETION
                            break

        if potential_drag_npc:
            if pygame.time.get_ticks() - mouse_down_time >= DRAG_HOLD_DELAY_MS:
                dragging_npc = potential_drag_npc
                dragging_npc.is_dragged = True
                dragging_npc.target_x = None  
                dragging_npc.target_boulder = None
                dragging_npc.target_tree = None
                dragging_npc.state = "idle"
                potential_drag_npc = None

        is_grabbing_human = dragging_npc is not None
        is_grabbing_item = dragging_item is not None
        custom_cursor.update(characters, game_paused, radial_menu, inventory_menu, pause_menu, is_grabbing_human, is_grabbing_item, pending_move_command)

        if dragging_npc:
            current_cursor_pos = (int(custom_cursor.x), int(custom_cursor.y))
            dragging_npc.x = current_cursor_pos[0] + drag_offset_x
            dragging_npc.y = current_cursor_pos[1] + drag_offset_y
            dragging_npc.rect.midbottom = (dragging_npc.x, dragging_npc.y)

        if not game_paused:
            if inventory_menu.active_npc and inventory_menu.mode == "crafting":
                inventory_menu.check_recipes()

            if water_depletion > 0:
                water_depletion -= 0.5 

            if random.random() < 0.02: 
                if current_weather == WEATHER_STORM:
                    target_wind = random.uniform(-WIND_STORM_RANGE, WIND_STORM_RANGE)
                elif current_weather == WEATHER_RAIN:
                    target_wind = random.uniform(-WIND_RAIN_RANGE, WIND_RAIN_RANGE)
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

            for boulder in boulders:
                boulder.update(current_floor)
                
            for tree in trees:
                tree.update(current_floor)

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

            for ghost in reversed(ghosts):
                if not ghost.update():
                    ghosts.remove(ghost)

            for char in characters:
                char.update(current_floor, dropped_items, boulders, trees, assets, inventory_menu, ghosts)
                
            for d_item in dropped_items:
                d_item.update(current_floor)

        screen.fill(TRANSPARENT_KEY)
        
        # Draw background objects (like boulders) first so they sit behind humans
        for tree in trees:
            tree.draw(screen)
        for boulder in boulders:
            boulder.draw(screen)

        for drop in raindrops:
            drop.draw(screen)
        for splash in splashes:
            splash.draw(screen)
        for cloud in clouds:
            cloud.draw(screen)
            
        for d_item in dropped_items:
            d_item.draw(screen, item_font)
            
        for char in characters:
            if char.target_x is not None and char.state not in ["mining", "chopping"]:
                move_icon = assets['move']
                float_y = char.y - (CHARACTER_TARGET_HEIGHT // 2) + math.sin(pygame.time.get_ticks() * 0.005) * 5
                icon_rect = move_icon.get_rect(center=(char.target_x, float_y))
                screen.blit(move_icon, icon_rect)
                
                start_pos = (char.x, char.y - CHARACTER_TARGET_HEIGHT // 2)
                end_pos = icon_rect.center
                dist = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
                
                dot_spacing = 15
                if dist > dot_spacing:
                    num_dots = int(dist / dot_spacing)
                    for i in range(1, num_dots):
                        t = i / num_dots
                        px = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                        py = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                        dot_rect = assets['movedot'].get_rect(center=(int(px), int(py)))
                        screen.blit(assets['movedot'], dot_rect)
                        
            char.draw(screen, assets)
            
        for ghost in ghosts:
            ghost.draw(screen)
            
        if not game_paused:
            radial_menu.draw(screen, actual_mouse_pos)
            inventory_menu.draw(screen, actual_mouse_pos, item_font) 
            
        if game_paused:
            pause_menu.draw(screen, actual_mouse_pos)
            
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
                
        if dragging_item:
            drag_sprite = pygame.transform.scale(
                dragging_item['sprite'], 
                (int(dragging_item['sprite'].get_width() * ITEM_DRAG_SCALE), 
                 int(dragging_item['sprite'].get_height() * ITEM_DRAG_SCALE))
            )
            drag_rect = drag_sprite.get_rect(center=actual_mouse_pos)
            screen.blit(drag_sprite, drag_rect)
            
            if dragging_item['count'] > 1:
                count_surf = item_font.render(str(dragging_item['count']), True, (255, 255, 255))
                count_rect = count_surf.get_rect(bottomright=(drag_rect.right, drag_rect.bottom))
                for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    outline = item_font.render(str(dragging_item['count']), True, (0,0,0))
                    screen.blit(outline, count_rect.move(ox, oy))
                screen.blit(count_surf, count_rect)
                
        custom_cursor.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()