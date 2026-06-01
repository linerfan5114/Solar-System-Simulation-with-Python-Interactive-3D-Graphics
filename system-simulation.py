import pygame
import math
import sys
import random
from pygame import gfxdraw

pygame.init()
pygame.mixer.init()

# Fullscreen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Solar System Explorer - Ultimate Edition")

clock = pygame.time.Clock()

# Colors
DARK_SPACE = (2, 1, 15)
WHITE = (255, 255, 255)
SUN_COLOR = (255, 235, 100)
BLACK = (0, 0, 0)

# Fonts
font_large = pygame.font.Font(None, 52)
font_medium = pygame.font.Font(None, 34)
font_small = pygame.font.Font(None, 26)
font_tiny = pygame.font.Font(None, 20)
font_huge = pygame.font.Font(None, 80)

# Sound generation (simple sine waves for space ambiance)
def generate_click_sound():
    sample_rate = 22050
    duration = 0.1
    samples = int(sample_rate * duration)
    wave = [int(127 * math.sin(2 * math.pi * 440 * t / sample_rate) * (1 - t / samples)) 
            for t in range(samples)]
    # Convert to unsigned bytes (0-255)
    unsigned_wave = [(w + 128) for w in wave]
    sound = pygame.mixer.Sound(buffer=bytes(unsigned_wave))
    sound.set_volume(0.3)
    return sound

def generate_ambient_sound():
    sample_rate = 22050
    duration = 2.0
    samples = int(sample_rate * duration)
    wave = []
    for t in range(samples):
        val = (math.sin(2 * math.pi * 110 * t / sample_rate) * 0.3 +
               math.sin(2 * math.pi * 165 * t / sample_rate) * 0.2 +
               math.sin(2 * math.pi * 220 * t / sample_rate) * 0.1)
        wave.append(int(127 * val))
    # Convert to unsigned bytes (0-255)
    unsigned_wave = [(w + 128) for w in wave]
    sound = pygame.mixer.Sound(buffer=bytes(unsigned_wave))
    sound.set_volume(0.1)
    return sound

click_sound = generate_click_sound()
ambient_sound = generate_ambient_sound()

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2.5)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.speed_y = random.uniform(-0.3, 0.3)
        self.alpha = random.randint(50, 200)
        self.twinkle_speed = random.uniform(0.02, 0.05)
        self.twinkle_offset = random.uniform(0, math.tau)
        
    def update(self, mouse_x, mouse_y):
        # Move towards mouse slightly
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = max(1, math.hypot(dx, dy))
        self.x += self.speed_x + dx * 0.0001
        self.y += self.speed_y + dy * 0.0001
        
        # Wrap around screen
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0
        
        # Twinkle effect
        self.alpha = 100 + int(80 * math.sin(pygame.time.get_ticks() * self.twinkle_speed + self.twinkle_offset))
        
    def draw(self, screen):
        color = (200, 220, 255, self.alpha)
        try:
            pygame.draw.circle(screen, color[:3], (int(self.x), int(self.y)), int(self.size))
        except:
            pass

class SolarFlare:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.flares = []
        self.particles = []
        self.generate_flares()
        
    def generate_flares(self):
        for _ in range(3):
            angle = random.uniform(0, math.tau)
            length = random.uniform(1.3, 2.0) * self.base_radius
            self.flares.append({
                'angle': angle,
                'length': length,
                'speed': random.uniform(0.01, 0.03),
                'life': random.uniform(0.5, 1.0),
                'offset': random.uniform(0, math.tau)
            })
            
    def update(self):
        for flare in self.flares:
            flare['life'] -= 0.001
            if flare['life'] < 0:
                flare['life'] = random.uniform(0.5, 1.0)
                flare['angle'] = random.uniform(0, math.tau)
                
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 0.02
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                
        # Add new particles
        if random.random() < 0.1:
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': self.x + math.cos(angle) * self.base_radius,
                'y': self.y + math.sin(angle) * self.base_radius,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': random.choice([(255, 200, 50), (255, 150, 30), (255, 100, 20)])
            })
            
    def draw(self, screen, zoom):
        for flare in self.flares:
            angle = flare['angle'] + math.sin(pygame.time.get_ticks() * 0.001 * flare['speed']) * 0.5
            length = flare['length'] * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003 + flare['offset']))
            end_x = self.x + math.cos(angle) * length
            end_y = self.y + math.sin(angle) * length
            
            # Draw flame-like curve
            points = []
            for i in range(10):
                t = i / 9.0
                px = self.x + (end_x - self.x) * t
                py = self.y + (end_y - self.y) * t
                offset = math.sin(t * math.pi) * 5 * zoom
                px += math.cos(angle + math.pi/2) * offset
                py += math.sin(angle + math.pi/2) * offset
                points.append((int(px), int(py)))
                
            if len(points) > 1:
                alpha = int(200 * flare['life'])
                color = (255, 150 + int(50 * flare['life']), 20, alpha)
                try:
                    pygame.draw.lines(screen, color[:3], False, points, max(1, int(2 * zoom)))
                except:
                    pass
                    
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            radius = max(1, int(2 * particle['life'] * zoom))
            try:
                pygame.draw.circle(screen, color[:3], (int(particle['x']), int(particle['y'])), radius)
            except:
                pass

class AuroraEffect:
    def __init__(self):
        self.waves = []
        for _ in range(5):
            self.waves.append({
                'offset': random.uniform(0, math.tau),
                'speed': random.uniform(0.02, 0.04),
                'amplitude': random.uniform(0.3, 0.6),
                'color': random.choice([(100, 200, 255), (150, 255, 200), (200, 150, 255)])
            })
            
    def draw(self, screen, x, y, radius, zoom):
        if zoom < 0.5:
            return
            
        for wave in self.waves:
            points = []
            wave_length = radius * 1.8
            for i in range(50):
                angle = (i / 49.0) * math.pi - math.pi/2
                r = radius * 1.1 + math.sin(i * 0.3 + pygame.time.get_ticks() * 0.001 * wave['speed'] + wave['offset']) * radius * wave['amplitude']
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                points.append((int(px), int(py)))
                
            if len(points) > 1:
                alpha = int(80 + 40 * math.sin(pygame.time.get_ticks() * 0.002 + wave['offset']))
                color = (*wave['color'], alpha)
                try:
                    pygame.draw.lines(screen, color[:3], False, points, max(1, int(3 * zoom)))
                except:
                    pass

class CelestialBody:
    def __init__(self, name, color, radius, orbit_radius, speed, info, has_ring=False, has_aurora=False):
        self.name = name
        self.color = color
        self.radius = radius
        self.orbit_radius = orbit_radius
        self.speed = speed
        self.angle = random.uniform(0, math.tau)
        self.info = info
        self.has_ring = has_ring
        self.has_aurora = has_aurora
        self.trail = []
        self.x = 0
        self.y = 0
        self.moons = []
        self.aurora = AuroraEffect() if has_aurora else None
        self.discovery_level = 0
        self.facts = []
        self.generate_facts()
        
    def generate_facts(self):
        facts_dict = {
            "Earth": ["Only known planet with liquid water on surface", "Has 1 natural satellite: the Moon", "Magnetic field protects from solar wind"],
            "Jupiter": ["Great Red Spot is a storm larger than Earth", "Has 79 known moons", "Strongest magnetic field of all planets"],
            "Mars": ["Has the largest volcano in Solar System: Olympus Mons", "Evidence of ancient rivers and lakes", "Has 2 moons: Phobos and Deimos"],
            "Venus": ["Rotates backwards compared to other planets", "Day is longer than its year", "Surface temperature: 462°C"],
            "Saturn": ["Rings are made mostly of ice particles", "Least dense planet - could float in water", "Has 82 known moons"]
        }
        self.facts = facts_dict.get(self.name, [f"Distance from Sun: {self.orbit_radius:.0f} AU (scaled)", 
                                                  f"Temperature: {random.randint(-200, 500)}°C",
                                                  f"Discovered in ancient times"])

    def update(self, center_x, center_y, time_scale):
        self.angle += self.speed * time_scale
        self.x = center_x + math.cos(self.angle) * self.orbit_radius
        self.y = center_y + math.sin(self.angle) * self.orbit_radius
        self.trail.append((self.x, self.y))
        if len(self.trail) > 600:
            self.trail.pop(0)

    def draw(self, screen, camera_x, camera_y, zoom, sun_x, sun_y):
        sx = (self.x - camera_x) * zoom + WIDTH//2
        sy = (self.y - camera_y) * zoom + HEIGHT//2
        r = int(self.radius * zoom)
        
        # Dynamic lighting based on sun position
        if (self.x, self.y) != (sun_x, sun_y):  # Not the sun
            sun_angle = math.atan2(sun_y - self.y, sun_x - self.x)
            
            # Shadow gradient overlay
            for angle in range(360):
                rad = math.radians(angle)
                shadow_strength = (math.cos(rad - sun_angle) + 1) / 2  # 0 to 1
                shadow_color = tuple(int(c * (0.4 + 0.6 * shadow_strength)) for c in self.color)
                px = sx + math.cos(rad) * r
                py = sy + math.sin(rad) * r
                try:
                    pygame.draw.circle(screen, shadow_color, (int(px), int(py)), max(1, int(2 * zoom)))
                except:
                    pass

        # Strong Glow
        for i in range(4):
            alpha = 60 - i*12
            glow_r = int(r * (1.6 + i*0.3))
            if glow_r > 0:
                color_glow = (*[int(c * 0.6) for c in self.color], alpha)
                try:
                    pygame.draw.circle(screen, color_glow, (int(sx), int(sy)), glow_r)
                except:
                    pass

        # Main Body
        pygame.draw.circle(screen, self.color, (int(sx), int(sy)), max(1, r))

        # Aurora effect for Earth and Jupiter
        if self.has_aurora and self.aurora:
            self.aurora.draw(screen, sx, sy, r, zoom)

        # Saturn Ring
        if self.has_ring:
            pygame.draw.ellipse(screen, (220, 210, 180), 
                              (sx - r*2.2, sy - r*0.35, r*4.4, r*0.7), max(1, int(zoom*2)))

        # Name Label
        if zoom > 0.3:
            label = font_tiny.render(self.name.upper(), True, (255, 255, 255))
            screen.blit(label, (sx - label.get_width()//2, sy - r - 22))

# ================== BODIES ==================
bodies = [
    CelestialBody("Sun", SUN_COLOR, 38, 0, 0, "Our Star • 99.8% of Solar System mass", False, False),
    CelestialBody("Mercury", (200, 200, 200), 6, 110, 0.038, "Closest planet to Sun • Extreme temperature swings", False, False),
    CelestialBody("Venus", (240, 200, 120), 11, 165, 0.015, "Hottest planet • Thick toxic atmosphere", False, False),
    CelestialBody("Earth", (80, 140, 255), 12, 230, 0.0095, "Only known planet with life • 71% covered by water", False, True),
    CelestialBody("Mars", (220, 100, 80), 9, 300, 0.0075, "Red Planet • Evidence of ancient rivers", False, False),
    CelestialBody("Jupiter", (220, 170, 110), 22, 420, 0.002, "Largest planet • Great Red Spot storm", False, True),
    CelestialBody("Saturn", (230, 210, 170), 18, 540, 0.0012, "Most spectacular ring system", True, False),
    CelestialBody("Uranus", (170, 230, 230), 15, 650, 0.00085, "Ice giant • Rotates sideways", True, False),
    CelestialBody("Neptune", (80, 120, 255), 15, 760, 0.0006, "Strongest winds in the Solar System", True, False),
]

# Extra Famous Systems
extra_systems = [
    ("TRAPPIST-1", (180, 100, 255), "Ultra-cool red dwarf with 7 Earth-sized planets"),
    ("Kepler-186f", (100, 200, 150), "First Earth-sized planet in habitable zone"),
    ("Sirius A & B", (240, 240, 255), "Brightest star system • White dwarf companion"),
    ("Proxima Centauri", (200, 120, 255), "Closest star to Sun • Has Proxima b exoplanet"),
]

# Game State
current_index = 0
camera_x = camera_y = 0
target_camera_x = target_camera_y = 0
zoom = 1.0
time_scale = 1.0
show_info = True
selected_body = None
mode = "solar"
fullscreen = True
show_timeline = False
timeline_year = 2024
show_size_comparison = False
show_moons = False
random_fact = None
random_fact_timer = 0
aurora_effects = []
particles = [Particle() for _ in range(200)]
show_radial_menu = False
free_flight_mode = False
flight_speed = 5
supernova_triggered = False
supernova_particles = []
pluto_unlocked = False
pluto_message = ""
pluto_message_timer = 0
keystrokes = ""
asteroids = []
mission_active = False
mission_target = None
mission_progress = 0
dragging = False
drag_start = (0, 0)
show_eclipse = False
eclipse_progress = 0

# Initialize solar flares
solar_flare = SolarFlare(WIDTH//2, HEIGHT//2, 38)

# Generate asteroids
for _ in range(20):
    asteroids.append({
        'angle': random.uniform(0, math.tau),
        'orbit': random.uniform(350, 390),
        'speed': random.uniform(0.003, 0.006),
        'size': random.uniform(1, 4),
        'color': (150, 150, 150)
    })

running = True

print("ULTIMATE Solar System Explorer")
print("F11 = Fullscreen | ENTER = Next | Click planets | Scroll = Zoom")
print("WASD = Free Flight | Right Click = Menu | T = Time Warp")
print("Type 'pluto' = Easter Egg | I = Info | M = Moons | C = Compare Sizes")

# Play ambient sound loop
ambient_sound.play(-1)

while running:
    dt = clock.get_time() / 1000.0
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEWHEEL:
            old_zoom = zoom
            zoom *= 1.1 ** event.y
            zoom = max(0.1, min(10, zoom))
            # Zoom towards mouse position
            if zoom != old_zoom:
                mouse_world_x = (mouse_x - WIDTH//2) / old_zoom + camera_x
                mouse_world_y = (mouse_y - HEIGHT//2) / old_zoom + camera_y
                camera_x = mouse_world_x - (mouse_x - WIDTH//2) / zoom
                camera_y = mouse_world_y - (mouse_y - HEIGHT//2) / zoom
            click_sound.play()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((1280, 800))
                WIDTH, HEIGHT = screen.get_size()
                
            elif event.key == pygame.K_ESCAPE:
                if show_radial_menu:
                    show_radial_menu = False
                elif free_flight_mode:
                    free_flight_mode = False
                else:
                    running = False
                    
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                current_index += 1
                if mode == "solar" and current_index >= len(bodies):
                    mode = "extra"
                    current_index = 0
                elif mode == "extra" and current_index >= len(extra_systems):
                    mode = "solar"
                    current_index = 0
                    
                if mode == "solar":
                    target_camera_x = bodies[current_index].x
                    target_camera_y = bodies[current_index].y
                selected_body = None
                click_sound.play()
                
            elif event.key == pygame.K_t:
                time_scale = 5 if time_scale == 1 else 1
                show_timeline = not show_timeline
                
            elif event.key == pygame.K_i:
                show_info = not show_info
                
            elif event.key == pygame.K_m:
                show_moons = not show_moons
                click_sound.play()
                
            elif event.key == pygame.K_c:
                show_size_comparison = not show_size_comparison
                click_sound.play()
                
            elif event.key == pygame.K_f:
                free_flight_mode = not free_flight_mode
                click_sound.play()
                
            # Collect keystrokes for easter egg
            elif event.unicode.isalpha():
                keystrokes += event.unicode.lower()
                if len(keystrokes) > 10:
                    keystrokes = keystrokes[-10:]
                if "pluto" in keystrokes and not pluto_unlocked:
                    pluto_unlocked = True
                    pluto_message = "PLUTO: I'm still a planet in our hearts! 💫"
                    pluto_message_timer = 300
                    bodies.append(CelestialBody("Pluto", (200, 180, 150), 5, 850, 0.0004, 
                                               "Dwarf planet • Still beloved by millions", False, False))
                    click_sound.play()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if show_radial_menu:
                    # Check radial menu items
                    cx, cy = WIDTH//2, HEIGHT//2
                    for i, body in enumerate(bodies if mode == "solar" else []):
                        angle = (math.tau / len(bodies)) * i - math.pi/2
                        item_x = cx + math.cos(angle) * 200
                        item_y = cy + math.sin(angle) * 200
                        if math.hypot(item_x - mouse_x, item_y - mouse_y) < 25:
                            if mode == "solar":
                                target_camera_x = body.x
                                target_camera_y = body.y
                                selected_body = body
                            show_radial_menu = False
                            click_sound.play()
                            break
                elif mode == "solar":
                    # Check planet clicks
                    clicked = False
                    for body in bodies:
                        sx = (body.x - camera_x) * zoom + WIDTH//2
                        sy = (body.y - camera_y) * zoom + HEIGHT//2
                        dist = math.hypot(sx - mouse_x, sy - mouse_y)
                        if dist < max(10, body.radius * zoom * 2):
                            selected_body = body
                            target_camera_x = body.x
                            target_camera_y = body.y
                            clicked = True
                            click_sound.play()
                            
                            # Supernova easter egg
                            if body.name == "Sun" and mode == "solar":
                                body.discovery_level += 1
                                if body.discovery_level >= 10 and not supernova_triggered:
                                    supernova_triggered = True
                                    for _ in range(100):
                                        supernova_particles.append({
                                            'x': body.x,
                                            'y': body.y,
                                            'vx': random.uniform(-5, 5),
                                            'vy': random.uniform(-5, 5),
                                            'life': 1.0,
                                            'color': random.choice([(255, 200, 50), (255, 100, 30), (255, 50, 20)])
                                        })
                            break
                            
                    if not clicked and not free_flight_mode:
                        dragging = True
                        drag_start = (mouse_x, mouse_y)
                        
            elif event.button == 3:  # Right click
                show_radial_menu = not show_radial_menu
                click_sound.play()
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                
        elif event.type == pygame.MOUSEMOTION and dragging:
            dx = (mouse_x - drag_start[0]) / zoom
            dy = (mouse_y - drag_start[1]) / zoom
            camera_x -= dx
            camera_y -= dy
            target_camera_x = camera_x
            target_camera_y = camera_y
            drag_start = (mouse_x, mouse_y)
            
    # Handle free flight mode
    keys = pygame.key.get_pressed()
    if free_flight_mode:
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            camera_y -= flight_speed / zoom
            target_camera_y = camera_y
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            camera_y += flight_speed / zoom
            target_camera_y = camera_y
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            camera_x -= flight_speed / zoom
            target_camera_x = camera_x
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            camera_x += flight_speed / zoom
            target_camera_x = camera_x
            
    # Update particles
    for particle in particles:
        particle.update(mouse_x, mouse_y)
        
    # Update solar flare
    solar_flare.x = WIDTH//2 - camera_x * zoom + WIDTH//2
    solar_flare.y = HEIGHT//2 - camera_y * zoom + HEIGHT//2
    solar_flare.update()
    
    # Update supernova
    if supernova_triggered:
        for particle in supernova_particles[:]:
            particle['life'] -= 0.005
            if particle['life'] <= 0:
                supernova_particles.remove(particle)
            else:
                particle['x'] += particle['vx'] * dt * 60
                particle['y'] += particle['vy'] * dt * 60
                particle['vx'] *= 0.98
                particle['vy'] *= 0.98
                
    # Update pluto message
    if pluto_message_timer > 0:
        pluto_message_timer -= 1
        
    # Random fact display
    if random_fact_timer <= 0 and mode == "solar" and selected_body:
        random_fact = random.choice(selected_body.facts)
        random_fact_timer = 300
    random_fact_timer -= 1
    
    # Eclipse detection
    if mode == "solar" and not show_eclipse:
        for body1 in bodies:
            for body2 in bodies:
                if body1 != body2 and body1.name != "Sun" and body2.name != "Sun":
                    dist = math.hypot(body1.x - body2.x, body1.y - body2.y)
                    if dist < 30:
                        show_eclipse = True
                        eclipse_progress = 180
                        
    if show_eclipse:
        eclipse_progress -= 1
        if eclipse_progress <= 0:
            show_eclipse = False
        
    screen.fill(DARK_SPACE)
    
    # Draw background stars
    for _ in range(350):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        b = random.randint(160, 255)
        pygame.draw.circle(screen, (b, b, 255), (x, y), random.randint(1, 2))
        
    # Draw particles
    for particle in particles:
        particle.draw(screen)
        
    if mode == "solar":
        cx = WIDTH // 2
        cy = HEIGHT // 2
        sun_x, sun_y = 0, 0
        
        # Find sun position
        for body in bodies:
            if body.name == "Sun":
                body.update(cx / zoom, cy / zoom, time_scale * 0.65)
                sun_x, sun_y = body.x, body.y
                
        for body in bodies:
            if body.name != "Sun":
                body.update(cx / zoom, cy / zoom, time_scale * 0.65)
            body.draw(screen, camera_x, camera_y, zoom, sun_x, sun_y)
            
        # Draw asteroid belt
        for asteroid in asteroids:
            asteroid['angle'] += asteroid['speed'] * time_scale * 0.65
            ax = sun_x + math.cos(asteroid['angle']) * asteroid['orbit']
            ay = sun_y + math.sin(asteroid['angle']) * asteroid['orbit']
            sax = (ax - camera_x) * zoom + WIDTH//2
            say = (ay - camera_y) * zoom + HEIGHT//2
            if 0 <= sax <= WIDTH and 0 <= say <= HEIGHT:
                pygame.draw.circle(screen, asteroid['color'], (int(sax), int(say)), max(1, int(asteroid['size'] * zoom)))
                
        # Draw supernova particles
        for particle in supernova_particles:
            sx = (particle['x'] - camera_x) * zoom + WIDTH//2
            sy = (particle['y'] - camera_y) * zoom + HEIGHT//2
            if 0 <= sx <= WIDTH and 0 <= sy <= HEIGHT:
                alpha = int(255 * particle['life'])
                color = (*particle['color'], alpha)
                radius = max(1, int(3 * particle['life'] * zoom))
                try:
                    pygame.draw.circle(screen, color[:3], (int(sx), int(sy)), radius)
                except:
                    pass
                    
        # Smooth camera
        camera_x = camera_x * 0.88 + target_camera_x * 0.12
        camera_y = camera_y * 0.88 + target_camera_y * 0.12
        
    else:
        # Extra Systems Display
        sx, sy = WIDTH//2, HEIGHT//2
        name, color, info = extra_systems[current_index]
        pygame.draw.circle(screen, color, (sx, sy), 50)
        pygame.draw.circle(screen, (255,255,255), (sx, sy), 68, 5)
        title = font_large.render(name, True, WHITE)
        screen.blit(title, (sx - title.get_width()//2, sy - 140))
        
    # Draw eclipse effect
    if show_eclipse:
        alpha = int(abs(120 * math.sin(eclipse_progress * 0.05)))
        eclipse_surf = pygame.Surface((WIDTH, HEIGHT))
        eclipse_surf.set_alpha(alpha)
        eclipse_surf.fill((20, 20, 40))
        screen.blit(eclipse_surf, (0, 0))
        eclipse_text = font_medium.render("ECLIPSE!", True, (200, 200, 255))
        screen.blit(eclipse_text, (WIDTH//2 - eclipse_text.get_width()//2, 50))
        
    # Draw timeline
    if show_timeline:
        timeline_y = HEIGHT - 80
        pygame.draw.rect(screen, (0, 0, 40, 200), (50, timeline_y, WIDTH-100, 40), border_radius=10)
        pygame.draw.rect(screen, (80, 220, 255), (50, timeline_y, WIDTH-100, 40), 2, border_radius=10)
        year_text = font_small.render(f"Year: {int(timeline_year)}", True, WHITE)
        screen.blit(year_text, (WIDTH//2 - year_text.get_width()//2, timeline_y - 30))
        
        # Timeline slider
        slider_x = 100 + (timeline_year % 100) * (WIDTH-200) / 100
        pygame.draw.circle(screen, (255, 200, 50), (int(slider_x), timeline_y + 20), 10)
        
    # Draw size comparison
    if show_size_comparison and mode == "solar":
        comp_y = HEIGHT - 150
        sorted_bodies = sorted(bodies, key=lambda b: b.radius, reverse=True)
        total_width = sum(b.radius * 2 for b in sorted_bodies[:5])
        start_x = (WIDTH - total_width) // 2
        
        for i, body in enumerate(sorted_bodies[:5]):
            x = start_x + sum(b.radius * 2 for b in sorted_bodies[:i]) + body.radius
            pygame.draw.circle(screen, body.color, (int(x), comp_y), min(30, body.radius))
            label = font_tiny.render(body.name, True, WHITE)
            screen.blit(label, (x - label.get_width()//2, comp_y + 35))
            
    # Draw moons (simplified)
    if show_moons and mode == "solar" and selected_body and selected_body.name in ["Earth", "Jupiter", "Mars", "Saturn"]:
        moon_count = {"Earth": 1, "Mars": 2, "Jupiter": 4, "Saturn": 5}
        count = moon_count.get(selected_body.name, 0)
        body_sx = (selected_body.x - camera_x) * zoom + WIDTH//2
        body_sy = (selected_body.y - camera_y) * zoom + HEIGHT//2
        
        for i in range(count):
            angle = pygame.time.get_ticks() * 0.001 * (i+1) + i * math.tau / count
            moon_x = body_sx + math.cos(angle) * selected_body.radius * 2 * zoom
            moon_y = body_sy + math.sin(angle) * selected_body.radius * 2 * zoom
            pygame.draw.circle(screen, (200, 200, 200), (int(moon_x), int(moon_y)), max(1, int(3 * zoom)))
            
    # Draw pluto message
    if pluto_message_timer > 0:
        alpha = min(255, pluto_message_timer * 2)
        msg_surf = font_medium.render(pluto_message, True, (200, 180, 150))
        msg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT - 100))
        screen.blit(msg_surf, msg_rect)
        
    # Draw free flight indicator
    if free_flight_mode:
        flight_text = font_small.render("FREE FLIGHT MODE - WASD to navigate", True, (100, 255, 100))
        screen.blit(flight_text, (WIDTH//2 - flight_text.get_width()//2, HEIGHT - 30))
        
    # Info Panel
    if show_info:
        panel_rect = pygame.Rect(20, 20, 480, 340)
        pygame.draw.rect(screen, (0, 0, 40, 220), panel_rect, border_radius=18)
        pygame.draw.rect(screen, (80, 220, 255), panel_rect, 4, border_radius=18)
        
        if selected_body and mode == "solar":
            b = selected_body
            lines = [
                (f"★ {b.name}", (255, 240, 100), font_medium),
                (b.info, WHITE, font_small),
                (f"Size: {b.radius*2:.0f} (scaled)", WHITE, font_small),
                (f"Orbit: {b.orbit_radius:.0f} AU (scaled)", WHITE, font_small),
                (f"Discovery Level: {'⭐' * b.discovery_level}", (255, 200, 50), font_small),
            ]
            
            # Show random fact
            if random_fact and random_fact_timer > 0:
                lines.append((f"Fact: {random_fact}", (200, 200, 255), font_small))
                
        elif mode == "solar":
            b = bodies[current_index]
            lines = [
                (f"Current: {b.name}", (255, 240, 100), font_medium),
                (b.info, WHITE, font_small),
            ]
        else:
            name, color, info = extra_systems[current_index]
            lines = [
                (f"System: {name}", (255, 240, 100), font_medium),
                (info, WHITE, font_small),
            ]
            
        y = 50
        for text, color, fnt in lines:
            surf = fnt.render(text, True, color)
            screen.blit(surf, (45, y))
            y += 42
            
    # Radial Menu
    if show_radial_menu and mode == "solar":
        cx, cy = WIDTH//2, HEIGHT//2
        for i, body in enumerate(bodies):
            angle = (math.tau / len(bodies)) * i - math.pi/2
            item_x = cx + math.cos(angle) * 200
            item_y = cy + math.sin(angle) * 200
            pygame.draw.circle(screen, body.color, (int(item_x), int(item_y)), 20)
            pygame.draw.circle(screen, WHITE, (int(item_x), int(item_y)), 22, 2)
            name = font_tiny.render(body.name, True, WHITE)
            screen.blit(name, (item_x - name.get_width()//2, item_y + 25))
            
    # Update display
    pygame.display.flip()
    clock.tick(65)

# Cleanup
ambient_sound.stop()
pygame.mixer.quit()
pygame.quit()
sys.exit()
