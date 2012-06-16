import pyglet
from pyglet import clock
import time
import bulletml
import bulletml.bulletyaml
from bulletml.collision import collides_all
from pprint import pprint
import os, glob

pyglet.options['debug_gl'] = False

class BulletTest(pyglet.window.Window):
    is_event_handler = True
    def __init__(self, *args, **kwargs):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        template = pyglet.gl.Config(double_buffer=True)
        config = screen.get_best_config(template)
        context = config.create_context(None)
        pyglet.window.Window.__init__(self, resizable=True, width=800, height=600, caption="Bullets OMG:" , context=context)
        self.mouse_pos = (0, 0)
        self.new_file = False
        self.target = bulletml.Bullet()
        self.paused = False
        self.filenames = []
        self.active = None
        self.doc = None
        for myfile in glob.glob(os.path.join('patterns/', "*.xml")):
            self.filenames.append(myfile)

    def on_key_press(self, symbol, modifier):
        if symbol == pyglet.window.key.SPACE:
            print "You pressed space"
            self.paused ^= True
        elif symbol == pyglet.window.key.LEFT:
            self.file_idx -= 1
            self.new_file = True
        elif symbol == pyglet.window.key.RIGHT:
            self.file_idx += 1
            self.new_file = True
        elif symbol == pyglet.window.key.ESCAPE:
            self.has_exit = True

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)
    
    def on_mouse_release(self, x, y, button, modifiers):
        source = bulletml.Bullet.FromDocument(self.doc, x=x/2, y=y/2, target=self.target, rank=0.5)
        source.vanished = True
        self.active.add(source)
        print "Trying to add a new bullet source"


    def main(self):
        self.file_idx = 0
        while not self.has_exit:
            filename = self.filenames[self.file_idx % len(self.filenames)]
            print "Processing: " + filename
            self.doc = bulletml.BulletML.FromDocument(open(filename, "rU"))
            source = bulletml.Bullet.FromDocument(self.doc, x=200, y=200, target=self.target, rank=0.5)
            self.active = set([source])
            source.vanished = True
            self.new_file = False
            total = 0
            frames = 0
            blue = (0, 0, 1, 1)
            black = (0, 0, 0 , 1)
            while self.active and not self.new_file:
                self.dispatch_events()
                self.target.x, self.target.y = self.mouse_pos
                self.target.x /= 2
                self.target.y /= 2
                #target.y = 300 - target.y
                self.target.px = self.target.x
                self.target.py = self.target.y
                collides = False
                if not self.paused:
                    lactive = list(self.active)
                    start = time.time()
                    count = len(self.active)
                    for obj in lactive:
                        new = obj.step()
                        total += len(new)
                        self.active.update(new)
                        if (obj.finished
                            or not (-50 < obj.x < 650)
                            or not (-50 < obj.y < 650)):
                            self.active.remove(obj)
                    if lactive:
                        collides = collides_all(self.target, lactive)
                    elapsed = time.time() - start
    
                    frames += 1
                    if frames % 100 == 0:
                        print "  Processing: %04d: %d bullets, %d active." % (
                            frames, total, count)
                        if elapsed:
                            seconds_per_bullet = elapsed / count
                            bullets_per_second = count / elapsed
                            print "  %g seconds per bullet (120Hz max: %g)." % (
                                seconds_per_bullet, bullets_per_second / 120)
                if collides:
                    pyglet.gl.glClearColor(*blue)
                else:
                    pyglet.gl.glClearColor(*black)
                self.clear()
                vert_list = []
                for obj in self.active:
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
                            vert_list.append((x, y))
                pyglet.gl.glBegin(pyglet.gl.GL_POINTS)
                for x, y in vert_list:
                    pyglet.gl.gl.glVertex2f( x, y )
                pyglet.gl.glEnd()
                self.flip()
                
            print "  Finished: %04d: %d bullets." % (frames, total)
            self.file_idx += 1

if __name__ == "__main__":
    b = BulletTest()
    b.main()