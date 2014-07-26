"""Debugging image display.

This is a simple module, that shows images on screen using PyGame.
It is not used anywhere in the standard UI, serves only for debugging.
"""

try:
    import pygame
except ImportError, msg:
    import sys
    print >>sys.stderr, msg
    sys.exit(1)

def show(image, caption='', name=None):
    """Initialize PyGame and show the *image*."""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    pygame.init()
    if caption:
        caption = "Imago: " + caption
    else:
        caption = "Imago"
    pygame.display.set_caption(caption)
    pygame.display.set_mode(image.size)
    main_surface = pygame.display.get_surface()
    picture = pygame.image.frombuffer(image.tostring(), image.size, image.mode)
    main_surface.blit(picture, (0, 0))
    pygame.display.update()
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                return
