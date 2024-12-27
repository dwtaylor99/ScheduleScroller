
import pygame


explosions = pygame.image.load('images/fun/explosions.png').convert_alpha()
explosion_anim = []
left_offset = 12
ew = 32
eh = 32

explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

left_offset += 32
explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

left_offset += 32
explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

left_offset += 40
explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

left_offset += 46
explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

left_offset += 46
explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

left_offset += 42
explosions.set_clip((left_offset, 100, ew, eh))
explosion_anim.append(explosions.subsurface(explosions.get_clip()))

hole = pygame.transform.smoothscale_by(pygame.image.load('images/fun/hole_sm.png').convert_alpha(), 0.25)
explosion_anim.append(hole)

shooting = False
exploding = False
explosion_frame = 0
shoot_timing = 0
exp_x = 0
exp_y = 0
