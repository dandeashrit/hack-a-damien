import random
import time
import pygame
from enum import Enum
import heapq
import os
from gtts import gTTS
import pygame.mixer as mixer

# Initialize Pygame
pygame.init()

# Constants
scrn_wh, scrn_ht = 800, 600
tile_sz = 40
grd_wh , grd_ht = scrn_wh // tile_sz,  scrn_ht // tile_sz
game_time= 300  
fps = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (200, 200, 200)

# Scoring Constants
insn_fllw_bonus = 50
insn_plty_bonus = 10
dlvr_fl_plty = 25

class GameState(Enum):
    lang_slct = 1  # Select langauge
    playing = 2 # Playing
    psd = 3  # Paused
    gm_ovr = 4  # Game Over

class Direction(Enum):
    UP = "back"
    DOWN = "front"
    LEFT = "side"
    RIGHT = "side"

class BuildingType(Enum):
    PIZZERIA = "Pizza"
    APARTMENT = "apartment"
    PARK = "Park"
    BANK = "bank"
    CAFE = "Cafe"

class OrderType(Enum):
    REGULAR = "regular"
    URGENT = "urgent"
    SPECIAL = "special"
    PARTY = "party"

class CustomerInteraction:
    def __init__(self, lang_config):
        self.lang_config = lang_config
    
    def get_greeting(self, ord_tpe):
        greetings = {
            OrderType.REGULAR: {
                "en": "Hello! I'd like to order a pizza.",
                "es": "¡Hola! Quisiera ordenar una pizza.",
                "fr": "Bonjour! Je voudrais commander une pizza.",
                "de": "Hallo! Ich möchte eine Pizza bestellen."
            },
            OrderType.URGENT: {
                "en": "Hi! I'm really hungry, please hurry!",
                "es": "¡Hola! Tengo mucha hambre, ¡por favor apúrate!",
                "fr": "Salut! J'ai très faim, dépêchez-vous s'il vous plaît!",
                "de": "Hi! Ich bin sehr hungrig, bitte beeilen Sie sich!"
            },
            OrderType.SPECIAL: {
                "en": "Good evening! I have dietary requirements.",
                "es": "¡Buenas tardes! Tengo requisitos dietéticos.",
                "fr": "Bonsoir! J'ai des exigences alimentaires.",
                "de": "Guten Abend! Ich habe Ernährungsanforderungen."
            },
            OrderType.PARTY: {
                "en": "Hi there! We're having a party!",
                "es": "¡Hola! ¡Estamos teniendo una fiesta!",
                "fr": "Salut! On fait une fête!",
                "de": "Hallo! Wir haben eine Party!"
            }
        }
        return greetings[ord_tpe][self.lang_config.lng_id]

    def get_special_instructions(self, ord_tpe):
        instructions = {
            OrderType.REGULAR: {
                "en": "Please bring some napkins.",
                "es": "Por favor trae servilletas.",
                "fr": "Apportez des serviettes s'il vous plaît.",
                "de": "Bitte bringen Sie Servietten mit."
            },
            OrderType.URGENT: {
                "en": "Double tip for quick delivery!",
                "es": "¡Doble propina por entrega rápida!",
                "fr": "Double pourboire pour livraison rapide!",
                "de": "Doppeltes Trinkgeld für schnelle Lieferung!"
            },
            OrderType.SPECIAL: {
                "en": "Please ensure it's gluten-free.",
                "es": "Por favor asegúrate que sea sin gluten.",
                "fr": "Assurez-vous que c'est sans gluten.",
                "de": "Bitte stellen Sie sicher, dass es glutenfrei ist."
            },
            OrderType.PARTY: {
                "en": "We need extra plates and cups!",
                "es": "¡Necesitamos platos y vasos extra!",
                "fr": "Nous avons besoin d'assiettes et de verres supplémentaires!",
                "de": "Wir brauchen zusätzliche Teller und Becher!"
            }
        }
        return instructions[ord_tpe][self.lang_config.lng_id]

class LanguageConfig:
    TRANSLATIONS = {
        "en": {  # English
            "menu": {
                "title": "Select Language",
                "start": "Press SPACE to Start",
                "selected": "Selected"
            },
            "game": {
                "title": "Pizza Delivery Game",
                "time": "Time: {}s",
                "score": "Score: {}",
                "controls": "Arrow keys to move, ESC to pause",
                "dlvr_tm": "Delivery Time: {}s",
                "psd": "PAUSED - Press ESC to resume",
                "gm_ovr": "Game Over!",
                "fnl_scr": "Final Score: {}",
                "play_again": "Press SPACE to play again",
                "quit": "Press ESC to quit",
                "dlvr_fl": "Delivery Failed!",
                "dlvr_sc": "Delivery Success!",
                "ord_tpe": "Order Type: {}",
                "time_left": "Time Left: {}s",
                "bonus_pts": "Bonus: +{}"
            },
            "directions": {
                "right": "Go Right",
                "left": "Go Left",
                "down": "Go Down",
                "up": "Go Up",
                "blocks": "blocks"
            }
        },
        "es": {  # Spanish
            "menu": {
                "title": "Seleccionar Idioma",
                "start": "Presiona ESPACIO para Comenzar",
                "selected": "Seleccionado"
            },
            "game": {
                "title": "Juego de Entrega de Pizza",
                "time": "Tiempo: {}s",
                "score": "Puntuación: {}",
                "controls": "Flechas para mover, ESC para pausar",
                "dlvr_tm": "Tiempo de Entrega: {}s",
                "psd": "PAUSADO - Presiona ESC para continuar",
                "gm_ovr": "¡Juego Terminado!",
                "fnl_scr": "Puntuación Final: {}",
                "play_again": "Presiona ESPACIO para jugar de nuevo",
                "quit": "Presiona ESC para salir",
                "dlvr_fl": "¡Entrega Fallida!",
                "dlvr_sc": "¡Entrega Exitosa!",
                "ord_tpe": "Tipo de Orden: {}",
                "time_left": "Tiempo Restante: {}s",
                "bonus_pts": "Bono: +{}"
            },
            "directions": {
                "right": "Ve a la Derecha",
                "left": "Ve a la Izquierda",
                "down": "Ve Abajo",
                "up": "Ve Arriba",
                "blocks": "cuadras"
            }
        },
        "fr": {  # French
            "menu": {
                "title": "Choisir la Langue",
                "start": "Appuyez sur ESPACE pour Commencer",
                "selected": "Sélectionné"
            },
            "game": {
                "title": "Jeu de Livraison de Pizza",
                "time": "Temps: {}s",
                "score": "Score: {}",
                "controls": "Flèches pour bouger, ESC pour pause",
                "dlvr_tm": "Temps de Livraison: {}s",
                "psd": "PAUSE - Appuyez sur ESC pour continuer",
                "gm_ovr": "Partie Terminée!",
                "fnl_scr": "Score Final: {}",
                "play_again": "Appuyez sur ESPACE pour rejouer",
                "quit": "Appuyez sur ESC pour quitter",
                "dlvr_fl": "Livraison Échouée!",
                "dlvr_sc": "Livraison Réussie!",
                "ord_tpe": "Type de Commande: {}",
                "time_left": "Temps Restant: {}s",
                "bonus_pts": "Bonus: +{}"
            },
            "directions": {
                "right": "Allez à Droite",
                "left": "Allez à Gauche",
                "down": "Allez en Bas",
                "up": "Allez en Haut",
                "blocks": "blocs"
            }
        },
        "de": {  # German
            "menu": {
                "title": "Sprache Auswählen",
                "start": "LEERTASTE drücken zum Starten",
                "selected": "Ausgewählt"
            },
            "game": {
                "title": "Pizza-Lieferungsspiel",
                "time": "Zeit: {}s",
                "score": "Punktzahl: {}",
                "controls": "Pfeiltasten zum Bewegen, ESC für Pause",
                "dlvr_tm": "Lieferzeit: {}s",
                "psd": "PAUSE - ESC drücken zum Fortsetzen",
                "gm_ovr": "Spiel Vorbei!",
                "fnl_scr": "Endpunktzahl: {}",
                "play_again": "LEERTASTE drücken für neues Spiel",
                "quit": "ESC drücken zum Beenden",
                "dlvr_fl": "Lieferung Fehlgeschlagen!",
                "dlvr_sc": "Lieferung Erfolgreich!",
                "ord_tpe": "Bestelltyp: {}",
                "time_left": "Verbleibende Zeit: {}s",
                "bonus_pts": "Bonus: +{}"
            },
            "directions": {
                "right": "Gehen Sie Rechts",
                "left": "Gehen Sie Links",
                "down": "Gehen Sie Runter",
                "up": "Gehen Sie Hoch",
                "blocks": "Blöcke"
            }
        }
    }

    def __init__(self, lng_id="en"):
        self.lng_id = lng_id

    def get_text(self, category, key, *args):
        try:
            text = self.TRANSLATIONS[self.lng_id][category][key]
            if args:
                return text.format(*args)
            return text
        except KeyError:
            try:
                text = self.TRANSLATIONS["en"][category][key]
                if args:
                    return text.format(*args)
                return text
            except KeyError:
                return f"Missing translation: {category}.{key}"

class Building:
    def __init__(self, x, y, bldg_typ):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * tile_sz, y * tile_sz, tile_sz, tile_sz)
        self.type = bldg_typ
        try:
            self.image = pygame.image.load(os.path.join("assets", f"{bldg_typ.value}.png"))
            self.image = pygame.transform.scale(self.image, (tile_sz, tile_sz))
        except pygame.error:
            self.image = pygame.Surface((tile_sz, tile_sz))
            self.image.fill(GRAY)
        self.has_order = False
        self.is_destination = False
        self.ord_tpe = None
        self.customer_message = None
        self.special_instruction = None
        self.vocab = []
        self.ord_tm_bnss = 0

    def set_order(self, ord_tpe, cst_intrn):
        self.ord_tpe = ord_tpe
        self.has_order = True
        self.is_destination = True
        
        self.customer_message = cst_intrn.get_greeting(ord_tpe)
        self.special_instruction = cst_intrn.get_special_instructions(ord_tpe)
        
        if ord_tpe == OrderType.URGENT:
            self.ord_tm_bnss = 100
            self.vocab = ["hurry", "quick", "fast", "hungry"]
        elif ord_tpe == OrderType.SPECIAL:
            self.ord_tm_bnss = 75
            self.vocab = ["dietary", "requirements", "allergy", "gluten-free"]
        elif ord_tpe == OrderType.PARTY:
            self.ord_tm_bnss = 150
            self.vocab = ["party", "celebration", "plates", "drinks"]
        else:  # REGULAR
            self.ord_tm_bnss = 50
            self.vocab = ["please", "thank you", "delivery", "napkins"]

    def clear_order(self):
        self.has_order = False
        self.is_destination = False
        self.ord_tpe = None
        self.customer_message = None
        self.special_instruction = None
        self.vocab = []
        self.ord_tm_bnss = 0

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * tile_sz, y * tile_sz, tile_sz, tile_sz)
        self.has_pizza = False
        self.direction = Direction.DOWN
        self.speed = 1
        
        self.sprites = {}
        sprite_files = {
            Direction.UP: "subaru_back.png",
            Direction.DOWN: "subaru_front.png",
            Direction.LEFT: "subaru_side.png",
            Direction.RIGHT: "subaru_side.png"
        }
        
        for direction, filename in sprite_files.items():
            try:
                sprite = pygame.image.load(os.path.join("assets", filename))
                if direction == Direction.RIGHT:
                    sprite = pygame.transform.flip(sprite, True, False)
                self.sprites[direction] = pygame.transform.scale(sprite, (tile_sz, tile_sz))
            except pygame.error:
                surface = pygame.Surface((tile_sz, tile_sz))
                surface.fill(RED)
                self.sprites[direction] = surface

    def move(self, dx, dy, game_map, buildings):
        new_x = self.x + (dx * self.speed)
        new_y = self.y + (dy * self.speed)
        
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP

        if 0 <= new_x < grd_wh and 0 <= new_y < grd_ht:
            can_move = True
            for building in buildings:
                if building.x == new_x and building.y == new_y:
                    if not (building.is_destination or building.type == BuildingType.PIZZERIA):
                        can_move = False
                        break
            
            if game_map[int(new_y)][int(new_x)] == 0 or can_move:
                self.x = new_x
                self.y = new_y
                self.rect.x = self.x * tile_sz
                self.rect.y = self.y * tile_sz

    def draw(self, screen):
        screen.blit(self.sprites[self.direction], self.rect)
        if self.has_pizza:
            pygame.draw.circle(screen, RED, 
                             (self.rect.x + tile_sz//2, self.rect.y - 5), 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((scrn_wh, scrn_ht))
        pygame.display.set_caption("Pizza Delivery Language Learning Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        self.state = GameState.lang_slct
        self.language_menu = LanguageMenu(self.screen)
        self.lang_config = None
        
        self.volume = 1.0
        mixer.init()
        
        # Add delivery time constant
        self.dlvr_tm = 60  # Time in seconds for each delivery
        
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.game_start_time = time.time()
        self.current_order = None
        self.order_start_time = None
        self.current_instruction_index = 0
        self.last_move_pos = None
        
        self.map = self.generate_map()
        self.buildings = self.generate_buildings()
        self.pizzeria = self.get_or_create_pizzeria()
        self.player = Player(self.pizzeria.x, self.pizzeria.y)
        self.path = []
        self.instructions = []
    
    def generate_map(self):
        map_height = scrn_ht // tile_sz
        map_width = scrn_wh // tile_sz
        return [[1 if (i % 2 == 0 and j % 2 == 0) else 0 
                 for j in range(map_width)] 
                for i in range(map_height)]

    def generate_buildings(self):
        buildings = []
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == 1:
                    if (x, y) != (1, 1):
                        bldg_typ = random.choice([
                            BuildingType.APARTMENT,
                            BuildingType.BANK,
                            BuildingType.PARK,
                            BuildingType.CAFE
                        ])
                        buildings.append(Building(x, y, bldg_typ))
        
        buildings.append(Building(1, 1, BuildingType.PIZZERIA))
        return buildings

    def get_or_create_pizzeria(self):
        pizzeria = next((b for b in self.buildings 
                         if b.type == BuildingType.PIZZERIA), None)
        if not pizzeria:
            pizzeria = Building(1, 1, BuildingType.PIZZERIA)
            self.buildings.append(pizzeria)
        return pizzeria

    def generate_new_order(self):
        residential_buildings = [b for b in self.buildings 
                               if b.type == BuildingType.APARTMENT]
        if residential_buildings:
            for building in self.buildings:
                building.clear_order()
            
            destination = random.choice(residential_buildings)
            ord_tpe = random.choice(list(OrderType))
            cst_intrn = CustomerInteraction(self.lang_config)
            destination.set_order(ord_tpe, cst_intrn)
            self.current_order = destination
            self.order_start_time = time.time()
            self.current_order = destination
            self.order_start_time = time.time()
            
            # Show new order popup
            self.show_new_order_popup()
            return True
        return False

    def show_new_order_popup(self):
        if not self.current_order:
            return

        # Create popup surface
        popup_width = 500
        popup_height = 200
        popup = pygame.Surface((popup_width, popup_height))
        popup.fill(WHITE)
        pygame.draw.rect(popup, BLACK, popup.get_rect(), 2)

        # Render order information
        title_font = pygame.font.Font(None, 36)
        text_font = pygame.font.Font(None, 24)

        # Title
        title = title_font.render(
            f"New {self.current_order.ord_tpe.value.title()} Order!",
            True, BLACK
        )
        popup.blit(title, (20, 20))

        # Customer message
        msg_text = text_font.render(
            self.current_order.customer_message,
            True, BLACK
        )
        popup.blit(msg_text, (20, 70))

        # Special instruction
        if self.current_order.special_instruction:
            inst_text = text_font.render(
                self.current_order.special_instruction,
                True, BLUE
            )
            popup.blit(inst_text, (20, 100))

        # Bonus information
        bonus_text = text_font.render(
            f"Delivery Bonus: +{self.current_order.ord_tm_bnss} points",
            True, GREEN
        )
        popup.blit(bonus_text, (20, 130))

        # Continue prompt
        prompt_text = text_font.render(
            "Press any key to continue",
            True, BLACK
        )
        popup.blit(prompt_text, (20, 160))

        # Display popup in center of screen
        popup_x = (scrn_wh - popup_width) // 2
        popup_y = (scrn_ht - popup_height) // 2
        self.screen.blit(popup, (popup_x, popup_y))
        pygame.display.flip()

        # Wait for keypress
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    waiting = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    return

    def check_delivery(self):
        for building in self.buildings:
            if (self.player.x == building.x and self.player.y == building.y):
                if building.type == BuildingType.PIZZERIA and not self.player.has_pizza:
                    self.player.has_pizza = True
                    if not self.current_order:
                        self.generate_new_order()
                    self.update_path_and_instructions()
                elif building.has_order and self.player.has_pizza:
                    dlvr_tm = time.time() - self.order_start_time
                    time_bonus = building.ord_tm_bnss if dlvr_tm <= self.dlvr_tm else 0
                    
                    if dlvr_tm <= self.dlvr_tm:
                        # Base score + time bonus + instruction following bonus
                        points = max(1, int((self.dlvr_tm - dlvr_tm) / 10))
                        points += time_bonus
                        self.score += points
                        
                        success_text = self.lang_config.get_text("game", "dlvr_sc")
                        bonus_text = f"+{points} points! ({time_bonus} bonus)"
                        self.show_popup_message(f"{success_text}\n{bonus_text}", GREEN)
                    else:
                        # Apply penalty for failed delivery
                        self.score = max(0, self.score - dlvr_fl_plty)
                        fail_text = self.lang_config.get_text("game", "dlvr_fl")
                        penalty_text = f"-{dlvr_fl_plty} points!"
                        self.show_popup_message(f"{fail_text}\n{penalty_text}", RED)
                    
                    self.player.has_pizza = False
                    building.clear_order()
                    self.current_order = None
                    self.order_start_time = None
                    self.generate_new_order()
                    self.update_path_and_instructions()

    def show_warning_message(self):
        if self.current_order and self.order_start_time:
            time_left = max(0, self.dlvr_tm - int(time.time() - self.order_start_time))
            
            # Show warning message when 15 seconds or less remain
            if 10 < time_left <= 15:
                warning_text = "Hurry up! Time is running out!"
                warning_color = YELLOW
            elif 0 < time_left <= 10:
                warning_text = "Warning! Delivery about to fail!"
                warning_color = RED
            else:
                return
            
            # Create warning text
            warning_font = pygame.font.Font(None, 36)
            warning_surface = warning_font.render(warning_text, True, warning_color)
            warning_rect = warning_surface.get_rect(center=(scrn_wh//2, 30))
            
            # Add a semi-transparent background for better visibility
            bg_surface = pygame.Surface((warning_surface.get_width() + 20, warning_surface.get_height() + 10))
            bg_surface.fill(WHITE)
            bg_surface.set_alpha(200)
            bg_rect = bg_surface.get_rect(center=(scrn_wh//2, 30))
            
            # Draw warning
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(warning_surface, warning_rect)

    def show_popup_message(self, message, color, duration=2.0):
        start_time = time.time()
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(scrn_wh/2, scrn_ht/2))
        
        while time.time() - start_time < duration:
            self.draw_game()
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            self.clock.tick(60)

    def update_path_and_instructions(self):
        if self.current_order:
            start = (self.player.x, self.player.y)
            goal = (self.current_order.x, self.current_order.y)
            
            path = self.a_star_search(start, goal)
            
            if path:
                self.path = path
                self.instructions = self.path_to_instructions(path)
                self.current_instruction_index = 0
                self.speak_instructions()
            else:
                print("No valid path found!")
                self.path = []
                self.instructions = []
        else:
            self.path = []
            self.instructions = []

    def speak_instructions(self):
        if self.instructions and self.current_instruction_index < len(self.instructions):
            try:
                instruction = self.instructions[self.current_instruction_index]
                tts = gTTS(text=instruction, lang=self.lang_config.lng_id, slow=False)
                tts.save("instruction.mp3")
                
                mixer.music.load("instruction.mp3")
                mixer.music.play()
                
                while mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                os.remove("instruction.mp3")
            except Exception as e:
                print(f"Text-to-speech failed: {e}")

    def path_to_instructions(self, path):
        if not path or len(path) < 2:
            return []

        instructions = []
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            dx = next_pos[0] - current[0]
            dy = next_pos[1] - current[1]
            
            direction = ""
            if dx > 0:
                direction = self.lang_config.get_text("directions", "right")
            elif dx < 0:
                direction = self.lang_config.get_text("directions", "left")
            elif dy > 0:
                direction = self.lang_config.get_text("directions", "down")
            elif dy < 0:
                direction = self.lang_config.get_text("directions", "up")
            
            blocks = "1"
            direction_text = f"{direction} {blocks} {self.lang_config.get_text('directions', 'blocks')}"
            instructions.append(direction_text)

        return instructions

    def a_star_search(self, start, goal):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < grd_wh and 0 <= new_y < grd_ht and
                    (self.map[new_y][new_x] == 0 or (new_x == goal[0] and new_y == goal[1]))):
                    neighbors.append((new_x, new_y))
            return neighbors

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break

            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        if goal not in came_from:
            return None

        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def draw_hud(self):
        # Create a semi-transparent HUD background on the right side
        hud_width = 200
        hud_height = 180
        hud_x = scrn_wh - hud_width - 10  # Position from right edge
        hud_y = 10
        
        hud_surface = pygame.Surface((hud_width, hud_height))
        hud_surface.fill(WHITE)
        hud_surface.set_alpha(230)
        self.screen.blit(hud_surface, (hud_x, hud_y))
        
        # Draw time and score
        elapsed_time = int(game_time- (time.time() - self.game_start_time))
        if elapsed_time < 0:
            elapsed_time = 0
        
        time_text = self.font.render(
            self.lang_config.get_text("game", "time", elapsed_time),
            True, BLACK
        )
        score_text = self.font.render(
            self.lang_config.get_text("game", "score", self.score),
            True, BLACK
        )
        self.screen.blit(time_text, (hud_x + 10, hud_y + 10))
        self.screen.blit(score_text, (hud_x + 10, hud_y + 40))

        # Draw current order information
        if self.current_order:
            ord_tpe_color = {
                OrderType.REGULAR: BLACK,
                OrderType.URGENT: RED,
                OrderType.SPECIAL: BLUE,
                OrderType.PARTY: PURPLE
            }.get(self.current_order.ord_tpe, BLACK)

            order_text = self.font.render(
                self.lang_config.get_text("game", "ord_tpe", 
                    self.current_order.ord_tpe.value.title()),
                True, ord_tpe_color
            )
            self.screen.blit(order_text, (hud_x + 10, hud_y + 70))

            if self.order_start_time:
                time_left = max(0, self.dlvr_tm - 
                              int(time.time() - self.order_start_time))
                time_color = GREEN if time_left > 30 else (YELLOW if time_left > 15 else RED)
                time_text = self.font.render(
                    self.lang_config.get_text("game", "time_left", time_left),
                    True, time_color
                )
                self.screen.blit(time_text, (hud_x + 10, hud_y + 100))

                bonus_text = self.font.render(
                    self.lang_config.get_text("game", "bonus_pts", 
                        self.current_order.ord_tm_bnss),
                    True, GREEN
                )
                self.screen.blit(bonus_text, (hud_x + 10, hud_y + 130))

    def draw_customer_message(self):
        if self.current_order and self.current_order.customer_message:
            # Create message box at the bottom of the screen
            message_height = 80
            message_surface = pygame.Surface((scrn_wh - 20, message_height))
            message_surface.fill(WHITE)
            pygame.draw.rect(message_surface, BLACK, message_surface.get_rect(), 2)

            # Draw customer message
            message_font = pygame.font.Font(None, 24)
            message_text = message_font.render(
                self.current_order.customer_message,
                True, BLACK
            )
            message_surface.blit(message_text, (10, 10))

            # Draw special instruction
            if self.current_order.special_instruction:
                instruction_text = message_font.render(
                    self.current_order.special_instruction,
                    True, BLUE
                )
                message_surface.blit(instruction_text, (10, 35))

            # Draw vocab
            vocab_text = message_font.render(
                "Learn: " + ", ".join(self.current_order.vocab),
                True, GREEN
            )
            message_surface.blit(vocab_text, (10, 60))

            # Position at bottom of screen
            self.screen.blit(message_surface, (10, scrn_ht - message_height - 10))

    def draw_building_indicator(self, building):
        if building.has_order:
            indicator_color = {
                OrderType.REGULAR: BLACK,
                OrderType.URGENT: RED,
                OrderType.SPECIAL: BLUE,
                OrderType.PARTY: PURPLE
            }.get(building.ord_tpe, RED)
            
            pygame.draw.circle(
                self.screen, 
                indicator_color,
                (building.rect.x + tile_sz//2, building.rect.y - 5),
                5
            )

            if building.ord_tpe == OrderType.URGENT:
                pygame.draw.line(self.screen, RED,
                               (building.rect.x + tile_sz//2, building.rect.y - 15),
                               (building.rect.x + tile_sz//2, building.rect.y - 10), 2)
                pygame.draw.circle(self.screen, RED,
                                 (building.rect.x + tile_sz//2, building.rect.y - 8), 1)

    def draw_map_and_buildings(self):
        for building in self.buildings:
            building.rect.x = building.x * tile_sz
            building.rect.y = building.y * tile_sz
            self.screen.blit(building.image, building.rect)
            
            if building.has_order:
                self.draw_building_indicator(building)

    def draw_game(self):
        self.screen.fill(WHITE)
        self.draw_map_and_buildings()
        self.player.draw(self.screen)
        self.draw_hud()
        self.draw_customer_message()
        
        # Draw current instruction
        if self.instructions and self.current_instruction_index < len(self.instructions):
            instruction_text = self.font.render(
                self.instructions[self.current_instruction_index], True, BLUE)
            instruction_pos = (10, scrn_ht - self.font.get_height() - 90)
            self.screen.blit(instruction_text, instruction_pos)

        self.show_warning_message()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.handle_keydown(event):
                        running = False

            if self.state == GameState.playing:
                self.check_delivery()
                
                if time.time() - self.game_start_time >= game_time:
                    self.state = GameState.gm_ovr

            self.draw()
            pygame.display.flip()
            self.clock.tick(fps)

    def handle_keydown(self, event):
        if self.state == GameState.lang_slct:
            selected_language = self.language_menu.handle_input(event)
            if selected_language:
                self.lang_config = LanguageConfig(selected_language)
                self.state = GameState.playing
                self.reset_game()
        elif self.state == GameState.playing:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.psd
            else:
                old_pos = (self.player.x, self.player.y)
                if event.key == pygame.K_LEFT:
                    self.player.move(-1, 0, self.map, self.buildings)
                elif event.key == pygame.K_RIGHT:
                    self.player.move(1, 0, self.map, self.buildings)
                elif event.key == pygame.K_UP:
                    self.player.move(0, -1, self.map, self.buildings)
                elif event.key == pygame.K_DOWN:
                    self.player.move(0, 1, self.map, self.buildings)
                
                if (self.player.x, self.player.y) != old_pos:
                    self.last_move_pos = old_pos
                    self.check_instruction_follow()
                self.update_path_and_instructions()
        elif self.state == GameState.psd:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.playing
        elif self.state == GameState.gm_ovr:
            if event.key == pygame.K_SPACE:
                self.state = GameState.playing
                self.reset_game()
            elif event.key == pygame.K_ESCAPE:
                return True
        return False

    def check_instruction_follow(self):
        if not self.instructions or not self.last_move_pos:
            return

        current_pos = (self.player.x, self.player.y)
        expected_direction = None
        actual_direction = None

        dx = current_pos[0] - self.last_move_pos[0]
        dy = current_pos[1] - self.last_move_pos[1]

        # Determine actual movement direction
        if dx > 0: actual_direction = "right"
        elif dx < 0: actual_direction = "left"
        elif dy > 0: actual_direction = "down"
        elif dy < 0: actual_direction = "up"

        # Get expected direction from current instruction
        if self.current_instruction_index < len(self.instructions):
            current_instruction = self.instructions[self.current_instruction_index]
            for direction in ["right", "left", "up", "down"]:
                if self.lang_config.get_text("directions", direction) in current_instruction:
                    expected_direction = direction
                    break

            if actual_direction and expected_direction:
                if actual_direction == expected_direction:
                    self.score += insn_fllw_bonus
                    self.show_popup_message(f"Correct direction! +{insn_fllw_bonus}", GREEN, 1.0)
                    self.current_instruction_index += 1
                    if self.current_instruction_index < len(self.instructions):
                        self.speak_instructions()
                else:
                    self.score = max(0, self.score - insn_plty_bonus)
                    self.show_popup_message(f"Wrong direction! -{insn_plty_bonus}", RED, 1.0)

    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == GameState.lang_slct:
            self.language_menu.draw()
        elif self.state == GameState.playing:
            self.draw_game()
        elif self.state == GameState.psd:
            self.draw_pause_screen()
        elif self.state == GameState.gm_ovr:
            self.draw_gm_ovr_screen()
        
        pygame.display.flip()

    def draw_pause_screen(self):
        # Draw the game state in the background
        self.draw_game()
        
        # Add semi-transparent overlay
        overlay = pygame.Surface((scrn_wh, scrn_ht))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause message
        pause_text = self.font.render(
            self.lang_config.get_text("game", "psd"),
            True, WHITE
        )
        text_rect = pause_text.get_rect(center=(scrn_wh/2, scrn_ht/2))
        self.screen.blit(pause_text, text_rect)

    def draw_gm_ovr_screen(self):
        self.screen.fill(WHITE)
        
        # Game over text
        gm_ovr_text = self.font.render(
            self.lang_config.get_text("game", "gm_ovr"),
            True, BLACK
        )
        score_text = self.font.render(
            self.lang_config.get_text("game", "fnl_scr", self.score),
            True, BLACK
        )
        play_again_text = self.font.render(
            self.lang_config.get_text("game", "play_again"),
            True, BLACK
        )
        quit_text = self.font.render(
            self.lang_config.get_text("game", "quit"),
            True, BLACK
        )
        
        center_y = scrn_ht // 2
        self.screen.blit(gm_ovr_text,
            gm_ovr_text.get_rect(center=(scrn_wh/2, center_y - 60)))
        self.screen.blit(score_text,
            score_text.get_rect(center=(scrn_wh/2, center_y)))
        self.screen.blit(play_again_text,
            play_again_text.get_rect(center=(scrn_wh/2, center_y + 40)))
        self.screen.blit(quit_text,
            quit_text.get_rect(center=(scrn_wh/2, center_y + 80)))

# class LanguageMenu:
class LanguageMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.languages = {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch"
        }
        self.selected_index = 0
        self.button_height = 50
        self.button_width = 200
        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = []
        start_y = scrn_ht // 3
        for i, (code, name) in enumerate(self.languages.items()):
            rect = pygame.Rect(
                (scrn_wh - self.button_width) // 2,
                start_y + i * (self.button_height + 10),
                self.button_width,
                self.button_height
            )
            buttons.append({"rect": rect, "code": code, "name": name})
        return buttons

    def draw(self):
        self.screen.fill(WHITE)
        title = self.font.render("Select Language / Seleccionar Idioma", True, BLACK)
        title_rect = title.get_rect(center=(scrn_wh // 2, scrn_ht // 4))
        self.screen.blit(title, title_rect)

        for i, button in enumerate(self.buttons):
            color = BLUE if i == self.selected_index else BLACK
            pygame.draw.rect(self.screen, color, button["rect"], 2)
            text = self.font.render(button["name"], True, color)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
            elif event.key == pygame.K_RETURN:
                return self.buttons[self.selected_index]["code"]
        return None
    
if __name__ == "__main__":
    game = Game()
    game.run()