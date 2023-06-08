
import sge
from sge import gfx
import objects
import evolution
import time
import pygame
from pygame.time import Clock
import invaders

# Deklarasi Variable Setting
# Resolusi Layar
RESX = 960
RESY = 540

# Posisi Object
PLAYER_YOFFSET = 50
PLAYER_SPEED = 4
WALL_YOFFSET = 70
WALL_HEIGHT = 2

# Jumlah waktu untuk membuat generasi, yang akan berkurang setiap generasinya hingga mencapai limit
GENERATION_TIME = 5000
MIN_GEN_TIME = 2000

# Warna Dasar untuk menandai mating
CITIUS_COLOR = sge.gfx.Color('#EF7D10')
IMMUNIT_COLOR = sge.gfx.Color('#15AFF0')

#Jumlah minimal Kraken dalam permainan
MIN_NINV = 4

#Jumlah maksimal Kraken dalam permainan dan sebagai penanda game over
MAX_NINV = 100

#Setting awal score dan upgrade
SCORES = 0
UPGRADE = False
DOUBLE_SHOOT = False

#Membaca highscore terakhir
HSSCORE = 'HighScore.txt'
with open(HSSCORE) as file:
    HIGHSCORE = int(file.read())

pygame.init()

class InvadersGame(sge.dsp.Game):
    """
    Kelas utama untuk permainan. Ini mengatur tindakan global yang mempengaruhi semua
    objek dalam permainan.
    """

    def __init__(self):
        # Menginisialisasi InvadersGame baru, dengan semua parameter diatur
        super(InvadersGame, self).__init__(width=RESX, height=RESY, fps=120, collision_events_enabled=False,
                                           window_text="Kraken Lore")
        self.gensprite = sge.gfx.Sprite(width=RESX, height=RESY, origin_x=0, origin_y=0)
        self.scoresprite = sge.gfx.Sprite(width=320, height=120, origin_x=100, origin_y=100)

        self.hud_font = sge.gfx.Font('INVASION2000.ttf', size=20)
        self.pairs = None
        self.score = 0
        self.anim_sleep = None
        self.last_gen = 0
        self.game_over = False
        self.clock = Clock()

    #Fungsi untuk menampilkan text atau hud selama permainan
    def show_hud(self):
        self.clock.tick()
        # Menampilkan Score yang didapat dan banyaknya Kraken yang bermunculan
        hud_string = 'HIGHSCORE: {0:03d}  KRAKEN: {1:03d}\nSCORE: {2:03d}'
        num_invaders = sum(1 for o in self.current_room.objects if isinstance(o, objects.Invader))

        self.project_text(self.hud_font, hud_string.format(HIGHSCORE, num_invaders, SCORES), 5, 5, anti_alias=False)

        #Jika gameover, maka menampilkan tampilan layar gameover
        if self.game_over:
            sge.game.mouse.visible = True
            mouse = pygame.mouse.get_pos()
            quit_hover = False
            retry_hover = False
            # update highscore
            if SCORES >= HIGHSCORE:
                with open('HighScore.txt', 'w') as f:
                    f.write(str(SCORES))

            self.project_text(sge.gfx.Font('INVASION2000.ttf', size=70), 'Game\nOver', RESX/2, RESY/2 - 140, halign='center', valign='center')
            self.project_text(sge.gfx.Font('INVASION2000.ttf', size=30), 'SCORE: ' + str(SCORES), RESX / 2, RESY / 2 + 100,
                              halign='center', valign='center')
           
            self.project_text(sge.gfx.Font('INVASION2000.ttf', size=30), 'HIGH SCORE: ' + str(HIGHSCORE), RESX / 2, RESY / 2 + 150,
                              halign='center', valign='center')


            if 685 > mouse[0] > 615 and 500 > mouse[1] > 484:
                color_pause_quit = gfx.Color("gray")
                quit_hover = True
            else:
                color_pause_quit = gfx.Color("white")
            if 320 > mouse[0] > 256 and 505 > mouse[1] > 484:
                color_pause_retry = gfx.Color("gray")
                retry_hover = True
            else:
                color_pause_retry= gfx.Color("white")

            self.project_text(self.hud_font, "Retry", 256, 480,
                              anti_alias=False, color=color_pause_retry)
            self.project_text(self.hud_font, "Exit", 614, 480,
                              anti_alias=False , color=color_pause_quit)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and retry_hover == True:
                    invaders.retry = True
                    invaders.run_game()
                    self.end()

                elif event.type == pygame.MOUSEBUTTONUP and quit_hover == True:
                    self.end()
                quit_hover = False
                retry_hover = False
            self.anim_sleep = None
            self.clock = Clock()

    # fungsi menciptakan generasi baru
    def new_generation(self):
        # Menghasilkan Invaders baru dan mengurangi waktu generasi yang menjadi tantangan player
        global GENERATION_TIME
        inv = {o for o in self.current_room.objects if isinstance(o, objects.Invader)}
        # The number of new individuals is determined by a box-cox
        # transformation with lambda=0.6.
        newinv = int(((len(inv)**0.6)-1)/0.6)
        # memanggil fungsi mating pada class evolution
        pairs = evolution.mating_pool_tournament(inv, newinv)
        if pairs:
            #Menandai mana yang mating
            self.pairs = pairs
            self.pause(sprite=self.gensprite)
            # Waktu untuk bergenerasi akan selalu berukurang hingga mencapai batas
            if GENERATION_TIME > MIN_GEN_TIME:
                GENERATION_TIME -= 150

    # Membuat tampilan Main Menu ketika gamenya dirun
    def show_main_menu(self):
        sge.game.mouse.visible = True
        mouse = pygame.mouse.get_pos()
        # print(mouse)
        start_hover = False
        exit_hover = False
        self.project_text(sge.gfx.Font('INVASION2000.ttf', size=70), 'Kraken Lore', RESX / 2, RESY / 2 - 140,
                          halign='center', valign='center')

        if 507 > mouse[0] > 452 and 312 > mouse[1] > 300:
            color_start = gfx.Color("gray")
            start_hover = True
        else:
            color_start = gfx.Color("white")
        if 496 > mouse[0] > 456 and 392 > mouse[1] > 370:
            color_exit = gfx.Color("gray")
            exit_hover = True
        else:
            color_exit = gfx.Color("white")

        self.project_text(self.hud_font, "Start", 445, 290, anti_alias=False, color=color_start)
        self.project_text(self.hud_font, "Exit", 455, 365, anti_alias=False, color=color_exit)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and start_hover:
                invaders.menu = False
                invaders.run_game()
            elif event.type == pygame.MOUSEBUTTONUP and exit_hover:
                self.end()
            start_hover = False
            exit_hover = False

    # fungsi selama game berjalan
    def event_step(self, time_passed, delta_mult):

        if invaders.menu == True:
            self.show_main_menu()
        elif invaders.menu == False:
            sge.game.mouse.visible = False

            # Jika kondisi terpenuhi maka tembakan pelurunya akan terupdate
            # Program peluru diupdate ada di object.py
            # Menampilkan informasi teks ketika ada upgrade
            if SCORES % 10 == 0 and SCORES != 0:
                if SCORES == 50:
                    self.project_text(self.hud_font, "Got Upgrade Double Bullet!!", 5, 65,
                                      anti_alias=False)
                elif SCORES < 70:
                    self.project_text(self.hud_font, "Got Upgrade!!", 5, 65,
                                  anti_alias=False)
                elif SCORES == 100:
                    self.project_text(self.hud_font, "Got Upgrade!!", 5, 65,
                                      anti_alias=False)

            num_invaders = sum(1 for o in
                       self.current_room.objects if isinstance(o, objects.Invader))
            self.show_hud()

            # Game akan selesai jika jumlah Kraken melebihi batas maksimal Kraken (dibatasi 100)
            self.game_over = num_invaders >= MAX_NINV
            if not self.game_over:
                self.last_gen += time_passed

            # jika sudah melewati ambang batas, saatnya berkembang biak lagi
            if self.last_gen >= GENERATION_TIME:
                self.new_generation()

            # Kondisi ketika jumlah Kraken saat ini dibawah batas minimal Kraken (batas min = 4)
            # Kita tidak bisa menunggu mereka sampai selesai berkembang biak
            elif num_invaders <= MIN_NINV:
                for inv in (o for o in self.current_room.objects
                                                if isinstance(o, objects.Invader)):
                    self.project_circle(inv.x+inv.bbox_width/2,
                                        inv.y+inv.bbox_height/2,
                                        inv.bbox_width, outline=IMMUNIT_COLOR,
                                        outline_thickness=2)

    #fungsi untuk menerima inputan keyboard dari user
    def event_key_press(self, key, char):
        # Key untuk melakukan Fullscreen
        if key == 'f11':
            self.fullscreen = not self.fullscreen
        elif self.fullscreen and key == 'f11':
            self.fullscreen = self.fullscreen
        # Key untuk keluar dari permainan
        elif key == 'escape':
            self.event_close()
        # Key untuk melakukan pause game
        elif not self.game_over and key in ('p', 'enter'):
            self.pause()

    def event_close(self):
        self.end()

    #Fungsi yang akan berjalan selama pause sementara
    def event_paused_step(self, time_passed, delta_mult):
        self.show_hud()
        if self.pairs:
            # Menggambar bagaimana operasi crossover terjadi
            # Operasi Crossover / perkawinan akan berhenti selama 5 detik
            i1, i2 = self.pairs.pop()
            self.gensprite.draw_clear()
            self.gensprite.draw_circle(i1.x+i1.bbox_width/2,
                                       i1.y+i1.bbox_height/2,
                                       i1.bbox_width, outline=CITIUS_COLOR)
            self.gensprite.draw_circle(i2.x+i2.bbox_width/2,
                                       i2.y+i2.bbox_height/2,
                                       i2.bbox_width, outline=CITIUS_COLOR)
            self.gensprite.draw_line(i1.x+i1.bbox_width/2,
                                     i1.y+i1.bbox_height/2,
                                     i2.x+i2.bbox_width/2,
                                     i2.y+i2.bbox_height/2,
                                     CITIUS_COLOR, thickness=2)

            children_genes = evolution.recombinate([(i1, i2)],
                                                 objects.Invader.gene_props)[0]
            # Menambah individu childeren_genes yang tadi dilakukan dari hasil perkawinan
            desc = objects.Invader(**children_genes)
            desc.x, desc.y = (i1.x + i2.x)/2, (i1.y+i2.y)/2
            self.current_room.add(desc)
            # Perlambat penggambaran untuk meningkatkan animasi secara visual
            if self.anim_sleep is None:
                # Waktu animasi disesuaikan dengan jumlah individu baru tadi.
                self.anim_sleep = (1.0 if len(self.pairs) == 0
                                       else 0 if len(self.pairs) > 50
                                           else min(1.0, 3.0/len(self.pairs)))
                if self.score > 4:
                    self.anim_sleep = 0
            else:
                time.sleep(self.anim_sleep)
        elif self.pairs is not None:
            # Crossover selesai, game dapat berjalan kembali
            time.sleep(self.anim_sleep)
            self.pairs = self.anim_sleep = None
            self.score += 1
            self.last_gen = 0
            self.unpause()
        else:
            quit_hover = False
            continue_hover = False
            sge.game.mouse.visible = True
            mouse = pygame.mouse.get_pos()

            if 512 > mouse[0] > 468 and 413 > mouse[1] > 395:
                color_pause_quit = gfx.Color("gray")
                quit_hover = True
            else:
                color_pause_quit = gfx.Color("white")
            if 541 > mouse[0] > 439 and 363 > mouse[1] > 345:
                color_pause_continue = gfx.Color("gray")
                continue_hover = True
            else:
                color_pause_continue = gfx.Color("white")

            self.project_text(self.hud_font, "Continue", 437, 340,
                              anti_alias=False, color=color_pause_continue)
            self.project_text(self.hud_font, "Exit", 467, 390,
                              anti_alias=False , color=color_pause_quit)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and continue_hover == True:
                    self.unpause()
                elif event.type == pygame.MOUSEBUTTONUP and quit_hover == True:
                    self.end()
                quit_hover = False
                continue_hover = False


class GameRoom(sge.dsp.Room):
    def event_step(self, time_passed, delta_mult):
        pass
