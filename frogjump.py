"""
Frog Jump Game
"""
import arcade
import random
import math

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Frog Jump"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5

# Movement speed of player, in pixels per frame
SCROLL_SPEED = 5
# PLAYER_MOVE_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

MIN_BUG_INTERVAL, MAX_BUG_INTERVAL = 2, 6
BUG_HEIGHT_RANGE = 128 * 2
BUG_SPEED = 6
BUG_SPIN_AWAY_SPEED = 15

BACKGROUND_INTERVAL = 520

class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Track our state
        self.jumping = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        self.idle_texture = arcade.load_texture(":resources:images/enemies/frog.png", flipped_horizontally=True)
        self.jump_texture = arcade.load_texture(":resources:images/enemies/frog_move.png", flipped_horizontally=True)
        
        # Set the initial texture
        self.texture = self.idle_texture

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):
        # Jumping animation
        if self.jumping:
            self.texture = self.jump_texture
        else :
            self.texture = self.idle_texture

class BackgroundSprite(arcade.Sprite):
    
    textures = [(arcade.load_texture(":resources:images/tiles/grass_sprout.png"), .5, 0.0),
                (arcade.load_texture(":resources:images/tiles/mushroomRed.png"), .5, 0.0),
                (arcade.load_texture(":resources:images/tiles/rock.png"), .5, 0.0),
                (arcade.load_texture(":resources:images/tiles/bush.png"), 1, 0.0)]
                

    def __init__(self):

        super().__init__()
        self.texture, self.scale,__ = random.choice(BackgroundSprite.textures)
        
class BugSprite(arcade.Sprite):

    """Bug Sprite"""
    def __init__(self, texture : arcade.Texture, value : int):

        # Set up parent class
        super().__init__()

        # Set the initial texture and value provided
        self.texture = texture
        self.value = value

        self.set_hit_box(self.texture.hit_box_points)

        # Position offscreen to the right
        self.left = SCREEN_WIDTH
        self.bottom = 64 + random.randrange(BUG_HEIGHT_RANGE)
        self.change_x = - BUG_SPEED

        # Track our state
        self.alive = True


    def kill_and_spin_away(self):
        self.alive = False
        self.change_angle = random.randint(3,5) * random.choice((-1,1))
        flight_angle = math.radians(random.randint(20,70))
        self.change_x = math.cos(flight_angle) * BUG_SPIN_AWAY_SPEED
        self.change_y = math.sin(flight_angle) * BUG_SPIN_AWAY_SPEED

class FlySprite(BugSprite):

    fly_texture = arcade.load_texture(":resources:images/enemies/fly.png")

    def __init__(self):
        super().__init__(texture = FlySprite.fly_texture, value = 1)


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.bug_list : arcade.SpriteList  = None
        self.dead_bug_list : arcade.SpriteList = None
        self.ground_list : arcade.SpriteList = None
        self.background_list : arcade.SpriteList = None
        self.player_list : arcade.SpriteList = None

        # Separate variable that holds the player sprite
        self.player_sprite : arcade.Sprite = None

        # Our physics engine
        self.physics_engine : arcade.PhysicsEnginePlatformer = None

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit1.wav")

        # Timer for next bug
        self.time_until_next_bug = 0
        self.score = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.bug_list = arcade.SpriteList()
        self.dead_bug_list = arcade.SpriteList()

        self.player_sprite = PlayerCharacter()
        self.player_sprite.left = 128
        self.player_sprite.bottom = 128
        self.player_list.append(self.player_sprite)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, SCREEN_WIDTH + 64, 64):
            ground = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            ground.left = x
            ground.bottom = 0
            self.ground_list.append(ground)

        for i in range(3):
            bg_item = BackgroundSprite()
            bg_item.left = random.randint(0, SCREEN_WIDTH - bg_item.width)
            bg_item.bottom = 64
            self.background_list.append(bg_item)
            print(bg_item.position)


        self.score = 0

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.ground_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        
        # Draw our sprites
        self.background_list.draw()
        self.ground_list.draw()
        self.player_list.draw()
        self.dead_bug_list.draw()
        self.bug_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 , 10 ,
                         arcade.csscolor.WHITE, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.SPACE:
            self.attempt_jump()

    def attempt_jump(self):        
        if self.physics_engine.can_jump():
            arcade.play_sound(self.jump_sound)
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
            # self.player_sprite.change_x = PLAYER_MOVE_SPEED

            for ground in self.ground_list:
                ground.change_x = - SCROLL_SPEED
            for bg in self.background_list:
                bg.change_x = - SCROLL_SPEED
            self.player_sprite.jumping = True


    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()
        self.background_list.update()

        # If was jumping but now landed, stop moving
        if self.player_sprite.jumping and self.physics_engine.can_jump():
            # self.player_sprite.change_x = 0
            for ground in self.ground_list:
                ground.change_x = 0
            for bg in self.background_list:
                bg.change_x = 0

            self.player_sprite.jumping = False


        # Wrap the grounds (ground) around
        for ground in self.ground_list:
            if ground.right < 0:
                ground.left += SCREEN_WIDTH + ground.width
        
        # "wrap" the backgrounds (ground) around
        new_bgs = []
        for bg in self.background_list:
            if bg.right < 0:
                bg.remove_from_sprite_lists()
                bg = BackgroundSprite()
                bg.left = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + BACKGROUND_INTERVAL)
                bg.bottom = 64
                new_bgs.append(bg)
        
        self.background_list.extend(new_bgs)

        # Move bugs, adjust for frog motion
        if self.player_sprite.jumping:
            for bug in self.bug_list:
                bug.change_x -= SCROLL_SPEED 
            for bug in self.dead_bug_list:
                bug.change_x -= SCROLL_SPEED 
        self.bug_list.update()
        self.dead_bug_list.update()

        if self.player_sprite.jumping:
            for bug in self.bug_list:
                bug.change_x += SCROLL_SPEED 
            for bug in self.dead_bug_list:
                bug.change_x += SCROLL_SPEED 

        # Remove if offscreen
        for bug in self.bug_list:
            if bug.right < 0:
                bug.remove_from_sprite_lists()
        for bug in self.dead_bug_list:
            if bug.left > SCREEN_WIDTH or bug.bottom > SCREEN_HEIGHT:
                bug.remove_from_sprite_lists()

        # COLLISION CHECKS
        for bug in arcade.check_for_collision_with_list(self.player_sprite, self.bug_list):
            arcade.play_sound(self.hit_sound)
            self.score += bug.value

            bug.remove_from_sprite_lists()
            self.dead_bug_list.append(bug)
            bug.kill_and_spin_away()


        # Manage bug timer, create bugs and reset timer if time:
        self.time_until_next_bug -= delta_time
        if self.time_until_next_bug <= 0 :
            bug = FlySprite()
            self.bug_list.append(bug)
            self.time_until_next_bug = random.randrange(MIN_BUG_INTERVAL, MAX_BUG_INTERVAL)

        self.player_list.update_animation(delta_time)

def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()