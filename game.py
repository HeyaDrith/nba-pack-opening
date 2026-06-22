import pygame
import time
import random
import os

# Initialize pygame before creating the display or mixer
pygame.init()
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NBA Card Opening")

RARITY = {
    "common": 30,
    "rare": 25,
    "epic": 25,
    "legendary": 20
}

cards_rarity = {
    "common": [],
    "rare": [],
    "epic": [],
    "legendary": []
}

# Initialize mixer after pygame.init() and attempt to load/play music
try:
    pygame.mixer.init()
except Exception:
    # If mixer can't initialize, continue without crashing
    pass
music_file = os.path.join("assets", "heavenp4.mp3")
if os.path.exists(music_file):
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.025)
        pygame.mixer.music.play(-1)  # Loop the music
        # Debug: report whether music playback started
        try:
            print("mixer init:", bool(pygame.mixer.get_init()))
            print("music busy:", pygame.mixer.music.get_busy())
        except Exception:
            pass
    except Exception:
        print("Failed to load or play music:", music_file)
else:
    print("Music file not found:", music_file)

open_sound = pygame.mixer.Sound('assets/openingsound.mp3')


clock = pygame.time.Clock()
FPS = 60

#GAME STATES
STATE_IDLE = "idle"
STATE_SHAKING = "shaking"
STATE_REVEALED = "revealed"
current_state = STATE_IDLE

#ANIMATION
shake_timer = 0
shake_duration = 120
shake_intensity = 5


#ASSETS
bg = pygame.image.load("assets/bg.jpg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

packimg = pygame.image.load("assets/pack.png")
packimg = pygame.transform.scale(packimg, (200, 300))
# Use a rect sized to the image and keep an original position to avoid drifting
pack_rect = packimg.get_rect(topleft=(400, 325))
pack_orig_pos = pack_rect.topleft

card_img = None
card_rect = pygame.Rect(0, 0, 0, 0)

# Rarity state + reveal effect
current_rarity = None
reveal_effect_timer = 0
reveal_effect_duration = 60
RARITY_COLORS = {
    'common': (140, 140, 140),
    'rare': (0, 150, 255),
    'epic': (170, 0, 255),
    'legendary': (255, 200, 50)
}

def get_card_files():
    # Return image files in assets (including subdirectories) that can be used as cards
    global cards_rarity
    exts = ('.png', '.jpg', '.jpeg')
    exclusions = {'bg.jpg', 'pack.png'}
    files = []
    try:
        # Reset cards_rarity mapping
        cards_rarity = {k: [] for k in cards_rarity}
        for root, _, filenames in os.walk('assets'):
            for f in filenames:
                if f.lower() in exclusions:
                    continue
                if f.lower().endswith(exts):
                    path = os.path.join(root, f)
                    files.append(path)
                    # Determine rarity from immediate subfolder under assets, if present
                    # Example: assets/common/card1.png -> rarity 'common'
                    try:
                        rel = os.path.normpath(os.path.relpath(root, 'assets'))
                        parts = rel.split(os.sep)
                        if parts and parts[0] in cards_rarity:
                            cards_rarity[parts[0]].append(path)
                    except Exception:
                        # If anything goes wrong, skip categorization
                        pass
    except Exception:
        pass
    return files




def load_random_card():
    global card_img, card_rect, current_rarity, reveal_effect_timer
    files = get_card_files()
    if not files:
        print('No card images found in assets; using fallback if available')
        fallback = os.path.join('assets', 'wcfwemby.jpg')
        if os.path.exists(fallback):
            files = [fallback]
        else:
            card_img = None
            return
    # Choose a rarity based on weights in RARITY (values treated as weights)
    rarities = list(RARITY.keys())
    weights = [RARITY[r] for r in rarities]
    try:
        chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
    except Exception:
        # Fallback if weights are invalid
        chosen_rarity = random.choice(rarities)

    # Try to pick a file from the chosen rarity; if empty, fall back to any available file
    candidate_list = cards_rarity.get(chosen_rarity, [])
    if not candidate_list:
        # find first non-empty rarity list
        for rlist in cards_rarity.values():
            if rlist:
                candidate_list = rlist
                break
    # Final fallback to all files
    if not candidate_list:
        candidate_list = files

    choice = random.choice(candidate_list)
    print(f"Chosen rarity: {chosen_rarity} -> {choice}")

    # Record current rarity and start reveal effect
    current_rarity = chosen_rarity
    reveal_effect_timer = reveal_effect_duration

    try:
        img = pygame.image.load(choice)
        img = pygame.transform.scale(img, (240, 360))
        card_img = img
        card_rect = card_img.get_rect(center=(WIDTH//2, HEIGHT//2))
    except Exception as e:
        print('Failed to load card image:', choice, e)
        card_img = None

def draw():
    # draw should not advance timers or mutate logical positions
    WIN.blit(bg, (0, 0))

    if current_state == STATE_IDLE:
        WIN.blit(packimg, pack_rect)

    elif current_state == STATE_SHAKING:
        # Apply shaking effect to the pack visually without mutating pack_rect
        if shake_timer < shake_duration:
            offset_x = random.randint(-shake_intensity, shake_intensity)
            offset_y = random.randint(-shake_intensity, shake_intensity)
        else:
            offset_x = 0
            offset_y = 0
        draw_pos = (pack_orig_pos[0] + offset_x, pack_orig_pos[1] + offset_y)
        WIN.blit(packimg, draw_pos)

    elif current_state == STATE_REVEALED:
        if card_img:
            # Draw rarity-colored glow behind the card while the reveal effect timer is active
            if 'reveal_effect_timer' in globals() and reveal_effect_timer > 0 and current_rarity:
                try:
                    glow_w = card_rect.width + 40
                    glow_h = card_rect.height + 40
                    glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                    color = RARITY_COLORS.get(current_rarity, (255, 255, 255))
                    alpha = int(180 * (reveal_effect_timer / float(reveal_effect_duration)))
                    glow_surf.fill((color[0], color[1], color[2], alpha))
                    glow_pos = (card_rect.centerx - glow_w // 2, card_rect.centery - glow_h // 2)
                    WIN.blit(glow_surf, glow_pos)
                except Exception:
                    pass
            WIN.blit(card_img, card_rect)

    pygame.display.update()


def main():
    global current_state, shake_timer, reveal_effect_timer, current_rarity
    running = True
    while running:
        clock.tick(FPS)

        # Advance shake timer only in main loop
        if current_state == STATE_SHAKING:
            shake_timer += 1
            if shake_timer >= shake_duration:
                # Load a random card when shaking finishes
                load_random_card()
                current_state = STATE_REVEALED
                # Ensure pack rect returns to original position when revealed
                pack_rect.topleft = pack_orig_pos
                shake_timer = 0

        # Advance reveal effect timer when revealed
        if current_state == STATE_REVEALED and reveal_effect_timer > 0:
            reveal_effect_timer -= 1


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                else:
                    continue
                
                if current_state == STATE_IDLE and pack_rect.collidepoint(mouse_pos):
                    current_state = STATE_SHAKING
                    shake_timer = 0
                    print("Shaking Started")
                    open_sound.play()
                    

                elif current_state == STATE_REVEALED and card_rect.collidepoint(mouse_pos):
                    # Clicking the revealed card should return to idle and reset pack
                    current_state = STATE_IDLE
                    pack_rect.topleft = pack_orig_pos
                    # reset rarity and reveal effect
                    current_rarity = None
                    reveal_effect_timer = 0
                    print("Revealed card clicked; pack reset")
                    



        draw()

    # Stop music (if playing) and quit when exiting main loop
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass
    pygame.quit()

if __name__ == "__main__":
    main()