import pygame
import sqlite3
import random
import json
import os
from datetime import datetime

# Initialize database
def init_db():
    conn = sqlite3.connect('beaver_game.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS high_scores
                 (id INTEGER PRIMARY KEY, score INTEGER, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def get_high_score():
    conn = sqlite3.connect('beaver_game.db')
    c = conn.cursor()
    c.execute('SELECT MAX(score) FROM high_scores')
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

def get_all_scores():
    conn = sqlite3.connect('beaver_game.db')
    c = conn.cursor()
    c.execute('SELECT score, timestamp FROM high_scores ORDER BY score DESC LIMIT 10')
    results = c.fetchall()
    conn.close()
    return results

def save_score(score):
    conn = sqlite3.connect('beaver_game.db')
    c = conn.cursor()
    c.execute('INSERT INTO high_scores (score, timestamp) VALUES (?, ?)', 
              (score, datetime.now()))
    conn.commit()
    conn.close()

# Load questions from JSON file 
def load_questions(filename="questions.json"):
    with open(filename, "r") as file:
        return json.load(file)

# Utility function to wrap long text
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 800
TOPIC_DIR = "topics"
FPS = 120
GRAVITY = 0.8
JUMP_STRENGTH = -15

class Beaver(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT - 50))
        self.velocity = 0

    def update(self, keys):
        if keys[pygame.K_SPACE] and self.rect.bottom >= SCREEN_HEIGHT:
            self.velocity = JUMP_STRENGTH
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity = 0

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, random.randint(20, 100)))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - self.rect.height

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

def advanced_topic_menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Select a Topic")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)

    topic_files = sorted([f for f in os.listdir(TOPIC_DIR) if f.endswith(".json")])
    topics = [f.replace(".json", "").replace("_", " ").title() for f in topic_files]
    selected_index = 0

    running = True
    while running:
        screen.fill((135, 206, 235))
        title = font.render("Select a Topic", True, (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        instructions = small_font.render("Use ↑/↓ to navigate, Enter to select, B to go back", True, (50, 50, 50))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 160))

        for i, topic in enumerate(topics):
            color = (255, 255, 255) if i == selected_index else (0, 0, 0)
            bg_color = (0, 0, 0) if i == selected_index else None
            text_surface = font.render(topic, True, color)
            x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
            y = 220 + i * 60
            if bg_color:
                pygame.draw.rect(screen, bg_color, (x - 10, y - 5, text_surface.get_width() + 20, text_surface.get_height() + 10))
            screen.blit(text_surface, (x, y))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(topics)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(topics)
                elif event.key == pygame.K_RETURN:
                    return os.path.join(TOPIC_DIR, topic_files[selected_index])
                elif event.key == pygame.K_b:
                    return None            

def menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Beaver Jumper - Menu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    background = pygame.image.load("beaver.png").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    running = True

    while running:
        screen.blit(background, (0, 0))
        title = font.render("Beaver Jumper", True, (0, 0, 0))
        start = font.render("Press S to Start Game", True, (0, 0, 0))
        view_scores = font.render("Press H to View Highscores", True, (0, 0, 0))
        quit_game = font.render("Press Q to Quit", True, (0, 0, 0))

        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 300))
        screen.blit(view_scores, (SCREEN_WIDTH//2 - view_scores.get_width()//2, 360))
        screen.blit(quit_game, (SCREEN_WIDTH//2 - quit_game.get_width()//2, 420))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    topic_file = advanced_topic_menu()
                    if topic_file:
                        main(topic_file)
                        return
                elif event.key == pygame.K_h:
                    show_high_scores(screen, background, font)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return

def show_high_scores(screen, background, font):
    scores = get_all_scores()
    running = True
    while running:
        screen.blit(background, (0, 0))
        title = font.render("High Scores", True, (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        for i, (score, timestamp) in enumerate(scores):
            text = font.render(f"{i+1}. {score} - {timestamp}", True, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 180 + i * 40))

        prompt = font.render("Press B to go back", True, (0, 0, 0))
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 650))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    running = False            

def main(question_file):
    pygame.init()
    questions_data = load_questions(question_file)["questions"]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Beaver Jumper")
    clock = pygame.time.Clock()

    background = pygame.image.load("beaver.png").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    beaver = Beaver()
    all_sprites.add(beaver)

    score = 0
    high_score = get_high_score()
    running = True
    game_over = False

    OBSTACLE_SPAWN = pygame.USEREVENT + 1
    pygame.time.set_timer(OBSTACLE_SPAWN, 1500)

    question_phase = False
    current_question = None
    current_obstacle = None
    selected_answer = None
    font_question = pygame.font.SysFont(None, 40)
    font_option = pygame.font.SysFont(None, 32)
    font_instruction = pygame.font.SysFont(None, 28)
    font = pygame.font.SysFont(None, 36)

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == OBSTACLE_SPAWN and not game_over and not question_phase:
                obstacle = Obstacle()
                obstacles.add(obstacle)
                all_sprites.add(obstacle)

            if event.type == pygame.KEYDOWN:
                if question_phase and event.key in [pygame.K_a, pygame.K_b, pygame.K_c]:
                    selected_answer = chr(event.key - pygame.K_a + ord('A'))

                if game_over:
                    if event.key == pygame.K_r:
                        main(question_file)
                        return
                    elif event.key == pygame.K_m:
                        menu()  # ✅ FIX: explicitly call menu
                        return

        if question_phase:
            if selected_answer:
                if selected_answer == current_question['answer']:
                    current_obstacle.kill()
                    question_phase = False
                    current_question = None
                    current_obstacle = None
                    selected_answer = None
                    pygame.time.set_timer(OBSTACLE_SPAWN, 1500)
                else:
                    game_over = True
                    if score > high_score:
                        save_score(score)
                    high_score = max(high_score, score)

        if not game_over and not question_phase:
            beaver.update(keys)
            obstacles.update()

            collided = pygame.sprite.spritecollideany(beaver, obstacles)
            if collided:
                question_phase = True
                current_obstacle = collided
                current_question = random.choice(questions_data)
                selected_answer = None
                pygame.time.set_timer(OBSTACLE_SPAWN, 0)

            score += 1

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        obstacles.draw(screen)

        if question_phase:
            box_rect = pygame.Rect(300, 300, 600, 250)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), box_rect, 2, border_radius=10)

            wrapped_lines = wrap_text(current_question['question'], font_question, 560)
            for i, line in enumerate(wrapped_lines):
                q_text = font_question.render(line, True, (0, 0, 0))
                screen.blit(q_text, (320, 320 + i * 40))

            offset_y = 320 + len(wrapped_lines) * 40 + 10
            for i, option in enumerate(current_question['options']):
                is_selected = selected_answer == chr(ord('A') + i)
                color = (0, 128, 0) if is_selected else (0, 0, 0)
                opt_text = font_option.render(option, True, color)
                screen.blit(opt_text, (340, offset_y + i * 40))

            instr = font_instruction.render("Press A, B, or C to answer", True, (100, 100, 100))
            screen.blit(instr, (320, offset_y + 140))

        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if game_over:
            screen.blit(background, (0, 0))
            game_over_text = font.render("GAME OVER! Press R to restart or M to return to the main menu", True, (255, 0, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2))
            high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
            screen.blit(high_score_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    init_db()
    while True:
        pygame.init()
        if not menu():
            break  # Exit the loop if menu() returns None (indicating Q was pressed)
        pygame.quit()
