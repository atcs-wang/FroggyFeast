"""
Frog Jump Game
"""
import arcade
import random

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

MIN_BUG_INTERVAL, MAX_BUG_INTERVAL = 3, 8
BUG_HEIGHT_RANGE = 128 * 2
BUG_SPEED = 4

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
        self.ground_list : arcade.SpriteList = None
        self.player_list : arcade.SpriteList = None

        # Separate variable that holds the player sprite
        self.player_sprite : arcade.Sprite = None

        # Our physics engine
        self.physics_engine : arcade.PhysicsEnginePlatformer = None

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit1.wav")

        # Timer for next bug
        self.time_until_next_bug = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()
        self.bug_list = arcade.SpriteList()

        self.player_sprite = PlayerCharacter()
        self.player_sprite.left = 128
        self.player_sprite.bottom = 128
        self.player_list.append(self.player_sprite)


        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            ground = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            ground.center_x = x
            ground.center_y = 32
            self.ground_list.append(ground)


        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.ground_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        
        # Draw our sprites
        self.ground_list.draw()
        self.player_list.draw()
        self.bug_list.draw()


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

            for bug in self.bug_list:
                bug.change_x = - BUG_SPEED - SCROLL_SPEED 
            self.player_sprite.jumping = True


    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()

        # If was jumping but now landed, stop moving
        if self.player_sprite.jumping and self.physics_engine.can_jump():
            # self.player_sprite.change_x = 0
            for ground in self.ground_list:
                ground.change_x = 0
            for bug in self.bug_list:
                bug.change_x = - BUG_SPEED
            self.player_sprite.jumping = False


        # Wrap the grounds (ground) around
        for ground in self.ground_list:
            if ground.right < 0:
                ground.left += SCREEN_WIDTH + ground.width
        
        for bug in self.bug_list:
            if bug.right < 0:
                bug.remove_from_sprite_lists()

        # Manage bugs

        # Move bugs, check collisions
        self.bug_list.update()
        for bug in arcade.check_for_collision_with_list(self.player_sprite, self.bug_list):
            arcade.play_sound(self.hit_sound)
            bug.remove_from_sprite_lists()

        # Manage bug timer, create bugs and reset timer if time:
        self.time_until_next_bug -= delta_time
        if self.time_until_next_bug <= 0 :
            bug = arcade.Sprite(":resources:images/enemies/fly.png")
            bug.left = SCREEN_WIDTH
            bug.bottom = 64 + random.randrange(BUG_HEIGHT_RANGE)
            bug.change_x = - BUG_SPEED
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