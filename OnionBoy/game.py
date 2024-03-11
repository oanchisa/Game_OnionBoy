#import libraries
import pygame
import random
import os
from pygame import mixer

#initialise pygame
mixer.init()
pygame.init()

#กำหนดขนาดหน้าต่างเกม
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

#สร้างหน้าต่างเกม
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('onion boy jump')

#โหลดภาพ
icon = pygame.image.load('OnionBoy/onion_boy.png')
pygame.display.set_icon(icon)
bg = pygame.image.load('OnionBoy/bg.png')
jumpy = pygame.image.load('OnionBoy/onion_boy.png')
platform_image = pygame.image.load('OnionBoy/wood2.png')

#กำหนดอัตราเฟรม
clock = pygame.time.Clock()
FPS = 60

#ตัวแปรเกม
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

#โหลดเพลงและเสียง
pygame.mixer.music.load('OnionBoy/music.mp3')
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('OnionBoy/assets_jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('OnionBoy/death.mp3')
death_fx.set_volume(0.5)

if os.path.exists('OnionBoy/score.txt'):
        with open('OnionBoy/score.txt', 'r') as file:
                high_score = int(file.read())

else:
        high_score = 0

#กำหนดสี
WHITE = (255,255,255)
BLACK= (0,0,0)
PANEL = (153, 217, 234)

#กำหนดฟอนต์
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

#ฟังก์ชันสำหรับพิมพ์ข้อความออกบนหน้าจอ
def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

#ฟังก์ชันสำหรับวาดpanel
def draw_panel():
        pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
        pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 3)
        draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

#ฟังก์ชันสำหรับวาดพื้นหลัง
def draw_bg(bg_scroll):
        screen.blit(bg, (0, 0 + bg_scroll))
        screen.blit(bg, (0, -600 + bg_scroll))

#player class
class Player():
        def __init__(self,x,y):
                self.image = pygame.transform.scale(jumpy,(50,50))
                self.width = 25
                self.height = 40
                self.rect = pygame.Rect(0,0,self.width,self.height)
                self.rect.center = (x,y)
                self.vel_y = 0
                self.flip = False

        def move(self):
                
                #reset variables
                scroll = 0
                dx = 0
                dy = 0
                
                #ประมวลผลการกดแป้นคีย์บอร์ด กำหนด Key
                key = pygame.key.get_pressed()
                if key[pygame.K_LEFT]:
                        dx = -10
                        self.flip = True
                if key[pygame.K_a]:
                        dx = -10
                        self.flip = True
                if key[pygame.K_RIGHT]:
                        dx = 10
                        self.flip = False
                if key[pygame.K_d]:
                        dx = 10
                        self.flip = False

                #gravity
                self.vel_y += GRAVITY
                dy += self.vel_y

                #Playerไม่หลุดขอบจอ
                if self.rect.left + dx < 0:
                        dx = -self.rect.left
                if self.rect.right + dx > SCREEN_WIDTH:
                        dx = SCREEN_WIDTH - self.rect.right

                #ตรวจสอบการชนกันของแพลตฟอร์ม
                for platform in platform_group:
                        if platform.rect.colliderect(self.rect.x,self.rect.y + dy, self.width,self.height):
                                if self.rect.bottom < platform.rect.centery:
                                        if self.vel_y > 0:
                                                self.rect.bottom = platform.rect.top
                                                dy  = 0
                                                self.vel_y = -20
                                                jump_fx.play()

                #เช็คPlayerกระโดดขึ้น-ลงบนจอ
                if self.rect.top <= SCROLL_THRESH:
                        if self.vel_y < 0:
                                scroll = -dy
                        
                #อัพเดทตำแหน่งสี่เหลี่ยม
                self.rect.x += dx
                self.rect.y += dy + scroll

                return scroll

        def draw(self):
                screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))
                pygame.draw.rect(screen,WHITE,self.rect,2)

#platform class
class Platform(pygame.sprite.Sprite):
        def __init__(self,x,y,width, moving):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.transform.scale(platform_image,(width,10))
                self.moving = moving
                self.move_counter = random.randint(0, 50)
                self.direction = random.choice([-1, 1])
                self.speed = random.randint(1, 2)
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y

        def update(self,scroll):

                #ย้ายแท่นไปข้าง ๆ ถ้าเป็นแท่นเคลื่อนที่
                if self.moving == True:
                        self.move_counter += 1
                        self.rect.x += self.direction * self.speed

                #เปลี่ยนทิศทางแท่นถ้าเคลื่อนที่เต็มที่หรือชนกำแพง
                if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                        self.direction *= -1
                        self.move_counter = 0

                #อัพเดทตำแหน่งแนวตั้งของแพลตฟอร์ม
                self.rect.y += scroll

                #เช็คแพลทฟอร์มหลุดหน้าจอ
                if self.rect.top > SCREEN_HEIGHT:
                        self.kill()
                
#ตัวอย่างผู้เล่น
jumpy = Player(SCREEN_WIDTH//2,SCREEN_HEIGHT - 150)

#create sprite groups
platform_group = pygame.sprite.Group()

#สร้างแพลตฟอร์มเริ่มต้น
platform = Platform(SCREEN_WIDTH//2-50,SCREEN_HEIGHT - 50,100, False)
platform_group.add(platform)
        
#game loop
run = True
while run:
        
        clock.tick(FPS)

        if game_over == False:
                scroll = jumpy.move()

                #draw background
                bg_scroll += scroll
                if bg_scroll >= 600:
                        bg_scroll = 0
                draw_bg(bg_scroll)

                #สร้างแพลตฟอร์ม
                if len(platform_group) < MAX_PLATFORMS:
                        p_w = random.randint(40, 60)
                        p_x = random.randint(0, SCREEN_WIDTH - p_w)
                        p_y = platform.rect.y - random.randint(80, 120)
                        p_type = random.randint(1, 2)
                        if p_type == 1 and score > 500:
                                p_moving = True
                        else:
                                p_moving = False
                        platform = Platform(p_x, p_y, p_w, p_moving)
                        platform_group.add(platform)
		
                #update platforms
                platform_group.update(scroll)

                #update score
                if scroll > 0:
                        score += scroll

                #วาดเส้นที่คะแนนสูงสุดครั้งก่อน
                pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH),
                                 (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
                draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

                #draw sprites
                platform_group.draw(screen)
                jumpy.draw()

                #draw panel
                draw_panel()

                #check game over
                if jumpy.rect.top > SCREEN_HEIGHT:
                        game_over = True
                        death_fx.play()

        else:
                if fade_counter < SCREEN_WIDTH:
                        fade_counter += 5
                        for y in range(0, 6, 4):
                                pygame.draw.rect(screen, BLACK, (0, 0, fade_counter,SCREEN_HEIGHT / 2))
                                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, SCREEN_HEIGHT / 2, SCREEN_WIDTH ,SCREEN_HEIGHT / 2))
                else:
                        #แสดงข้อความบนหน้าจอเมื่อจบเกม
                        draw_text('GAME OVER!', font_big, WHITE, 130, 200)
                        draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
                        draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 40, 300)
                        if score > high_score:
                                high_score = score
                                with open('OnionBoy/score.txt', 'w') as file:
                                        file.write(str(high_score))

                key = pygame.key.get_pressed()
                if key[pygame.K_SPACE]:
                        #reset variables
                        game_over = False
                        score = 0
                        scroll = 0
                        fade_counter = 0
                        #เปลี่ยตำเเหน่งjumpy
                        jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                        #reset platforms
                        platform_group.empty()
                        #สร้างแพลตฟอร์มเริ่มต้น
                        platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100,False)
                        platform_group.add(platform)

        #event handler
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        #update high score
                        if score > high_score:
                                high_score = score
                                with open('OnionBoy/score.txt', 'w') as file:
                                        file.write(str(high_score))
                        run = False

        #อัพเดทหน้าต่างแสดงผล
        pygame.display.update()

pygame.quit()
