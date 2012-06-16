import pyglet
from pyglet import clock
import time
import bulletml
import bulletml.bulletyaml
from bulletml.collision import collides_all
from pprint import pprint
my_image = pyglet.image.load('bullet.png')
b = pyglet.sprite.Sprite(my_image)
target = bulletml.Bullet()
win = pyglet.window.Window(1024, 768)
mouse_pos = (0, 0)
#pyglet.clock.set_fps_limit(60)

filename = "test1.xml"
doc = bulletml.BulletML.FromDocument(open(filename, "rU"))
source = bulletml.Bullet.FromDocument(doc, x=150, y=150, target=target, rank=0.5)
active = set([source])
source.vanished = True
print filename
print "  Loaded %d top-level actions." % len(source.actions)
my_batch = pyglet.graphics.Batch()

@win.event
def on_mouse_motion(x, y, dx, dy):
    global mouse_pos
    mouse_pos = (x, y)
    
def update(dt):
    global target
    global mouse_pos
    target.x, target.y = mouse_pos
    target.x /= 2
    target.y /= 2
    target.y = 300 - target.y
    target.px = target.x
    target.py = target.y
    collides = False
    global active
    lactive = list(active)
    for obj in lactive:
        new = obj.step()
        active.update(new)
        if (obj.finished
            or not (-50 < obj.x < 350)
            or not (-50 < obj.y < 350)):
            active.remove(obj)
    if lactive:
        collides = collides_all(target, lactive)

    for obj in active:
        try:
            x, y = obj.x, obj.y
        except AttributeError:
            pass
        else:
            if not obj.vanished:
                x *= 2
                y *= 2
                x -= 1
                y -= 1
                global b
                global my_batch
                global my_image
                pyglet.sprite.Sprite(my_image, x=x, y=y, batch=my_batch).draw()
                #sprite.draw()

pyglet.clock.schedule(update)
fps_display = pyglet.clock.ClockDisplay()
@win.event
def on_draw():
    win.clear()
    fps_display.draw()
    my_batch.draw()
    pyglet.clock.tick(60)

pyglet.app.run()