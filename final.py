import pygame
import sys
import enum
import random
import math
import time

# --- Enums ---

class BlockType(enum.Enum):
    """Defines different types of blocks in the game."""
    AIR = 0
    DIRT = 1
    GRASS = 2
    STONE = 3
    WOOD = 4
    WATER = 5
    COAL_ORE = 6
    IRON_ORE = 7
    DIAMOND_ORE = 8
    # Add more block types as needed

class GameState(enum.Enum):
    """Defines different states of the game."""
    RUNNING = 0
    PAUSED = 1
    MENU = 2
    GAME_OVER = 3

class ToolType(enum.Enum):
    """Defines different types of tools."""
    PICKAXE = 0
    AXE = 1
    SHOVEL = 2
    SWORD = 3

# --- Core Game Classes ---

class Block:
    """
    Represents a single block in the game world.
    Each block has a type, and properties like solidity and texture.
    """
    TEXTURE_CACHE = {}

    def __init__(self, block_type: BlockType, x: int, y: int, tile_size: int):
        """
        Initializes a new Block.
        :param block_type: The type of the block (e.g., BlockType.DIRT).
        :param x: The x-coordinate of the block in world units.
        :param y: The y-coordinate of the block in world units.
        :param tile_size: The pixel size of a single block.
        """
        self.block_type = block_type
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.is_solid = self._get_solidity()
        self.texture = self._load_texture()

    def _get_solidity(self) -> bool:
        """Determines if the block is solid based on its type."""
        return self.block_type not in [BlockType.AIR, BlockType.WATER]

    def _get_texture_path(self) -> str:
        """Returns the texture path for the block type."""
        texture_map = {
            BlockType.DIRT: "assets/dirt.png",
            BlockType.GRASS: "assets/grass.png",
            BlockType.STONE: "assets/stone.png",
            BlockType.WOOD: "assets/wood.png",
            BlockType.WATER: "assets/water.png",
            BlockType.COAL_ORE: "assets/coal_ore.png",
            BlockType.IRON_ORE: "assets/iron_ore.png",
            BlockType.DIAMOND_ORE: "assets/diamond_ore.png",
        }
        return texture_map.get(self.block_type, "assets/default.png")

    def _load_texture(self) -> pygame.Surface | None:
        """Loads and caches the block's texture."""
        if self.block_type == BlockType.AIR:
            return None
        
        path = self._get_texture_path()
        if path not in Block.TEXTURE_CACHE:
            try:
                img = pygame.image.load(path).convert_alpha()
                Block.TEXTURE_CACHE[path] = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            except pygame.error:
                print(f"Warning: Could not load texture from '{path}'. Using placeholder.")
                # Create a simple placeholder surface
                placeholder = pygame.Surface((self.tile_size, self.tile_size))
                placeholder.fill((255, 0, 255)) # Magenta for missing texture
                Block.TEXTURE_CACHE[path] = placeholder
        return Block.TEXTURE_CACHE[path]

    def get_texture(self) -> pygame.Surface | None:
        """Public method to get the block's texture."""
        return self.texture

    def get_properties(self) -> dict:
        """Returns a dictionary of block properties."""
        return {
            "type": self.block_type.name,
            "is_solid": self.is_solid,
            "x": self.x,
            "y": self.y
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Block({self.block_type.name}, x={self.x}, y={self.y})"


class Item:
    """
    Base class for all items in the game.
    Items can be held in inventory and have common properties.
    """
    def __init__(self, item_id: str, name: str, texture_path: str, stackable: bool, max_stack_size: int = 64):
        """
        Initializes a new Item.
        :param item_id: A unique identifier for the item.
        :param name: The display name of the item.
        :param texture_path: Path to the item's texture image.
        :param stackable: True if the item can be stacked in inventory.
        :param max_stack_size: Maximum quantity for a stackable item.
        """
        self.item_id = item_id
        self.name = name
        self.stackable = stackable
        self.max_stack_size = max_stack_size
        self.texture_path = texture_path
        self.texture = None # Will be loaded by the renderer

    def use(self, player: 'Player', world: 'World', target_x: int, target_y: int):
        """
        Abstract method to define what happens when the item is used.
        To be overridden by subclasses.
        """
        pass

    def __repr__(self) -> str:
        return f"Item(ID:{self.item_id}, Name:'{self.name}')"


class Tool(Item):
    """
    Represents a tool used for specific actions like mining or attacking.
    Inherits from Item.
    """
    def __init__(self, item_id: str, name: str, texture_path: str, durability: int, mining_power: int, tool_type: ToolType):
        """
        Initializes a new Tool.
        :param durability: The current durability of the tool.
        :param mining_power: How effective the tool is at mining.
        :param tool_type: The specific type of tool (e.g., ToolType.PICKAXE).
        """
        super().__init__(item_id, name, texture_path, stackable=False, max_stack_size=1)
        self.durability = durability
        self.mining_power = mining_power
        self.tool_type = tool_type

    def use(self, player: 'Player', world: 'World', target_x: int, target_y: int):
        """Uses the tool. Decreases durability."""
        if self.durability > 0:
            self.durability -= 1
        else:
            # Tool is broken, maybe remove from inventory
            pass

    def __repr__(self) -> str:
        return f"Tool(ID:{self.item_id}, Name:'{self.name}', Type:{self.tool_type.name}, Durability:{self.durability})"


class BlockItem(Item):
    """
    Represents an item that is actually a block that can be placed in the world.
    Inherits from Item.
    """
    def __init__(self, item_id: str, name: str, texture_path: str, block_type: BlockType):
        """
        Initializes a new BlockItem.
        :param block_type: The BlockType this item represents when placed.
        """
        super().__init__(item_id, name, texture_path, stackable=True)
        self.block_type = block_type

    def use(self, player: 'Player', world: 'World', target_x: int, target_y: int):
        """
        Uses the block item to place a block in the world.
        """
        world.set_block(target_x, target_y, self.block_type)
        # Player class handles consuming the item from inventory

    def __repr__(self) -> str:
        return f"BlockItem(ID:{self.item_id}, Name:'{self.name}', BlockType:{self.block_type.name})"


class Inventory:
    """
    Manages the player's items, including adding, removing, and querying items.
    """
    def __init__(self, capacity: int = 9):
        """
        Initializes the inventory.
        :param capacity: The total number of item slots in the hotbar.
        """
        self.capacity = capacity
        self.slots = [(None, 0)] * capacity
        self.selected_slot_index = 0

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """Adds an item to the inventory."""
        if quantity <= 0:
            return False

        # Try to stack first
        if item.stackable:
            for i, (existing_item, current_quantity) in enumerate(self.slots):
                if existing_item and existing_item.item_id == item.item_id:
                    space_available = existing_item.max_stack_size - current_quantity
                    if space_available > 0:
                        amount_to_add = min(quantity, space_available)
                        self.slots[i] = (existing_item, current_quantity + amount_to_add)
                        quantity -= amount_to_add
                        if quantity == 0:
                            return True

        # Find an empty slot for the remaining quantity or non-stackable items
        for i, (existing_item, _) in enumerate(self.slots):
            if existing_item is None:
                amount_to_add = min(quantity, item.max_stack_size if item.stackable else 1)
                self.slots[i] = (item, amount_to_add)
                quantity -= amount_to_add
                if quantity == 0:
                    return True
        return False

    def remove_item(self, item: Item, quantity: int = 1) -> bool:
        """Removes a specified quantity of an item from the inventory."""
        if quantity <= 0:
            return False
        
        items_removed = 0
        for i in range(len(self.slots)):
            existing_item, current_quantity = self.slots[i]
            if existing_item and existing_item.item_id == item.item_id:
                amount_to_remove = min(quantity, current_quantity)
                self.slots[i] = (existing_item, current_quantity - amount_to_remove)
                items_removed += amount_to_remove
                quantity -= amount_to_remove
                if self.slots[i][1] <= 0:
                    self.slots[i] = (None, 0)
                if quantity == 0:
                    return True
        return False

    def get_selected_slot_item(self) -> tuple[Item | None, int]:
        """Returns the item and quantity in the currently selected slot."""
        if 0 <= self.selected_slot_index < self.capacity:
            return self.slots[self.selected_slot_index]
        return (None, 0)

    def select_slot(self, index: int):
        """Sets the selected inventory slot."""
        if 0 <= index < self.capacity:
            self.selected_slot_index = index

    def __repr__(self) -> str:
        items_in_inventory = [
            f"{item.name} x{qty}" for item, qty in self.slots if item is not None
        ]
        return f"Inventory(Capacity:{self.capacity}, Items:{items_in_inventory})"


class Player:
    """
    Represents the player character, handling movement, inventory, and interactions.
    """
    def __init__(self, start_x: float, start_y: float, width: float, height: float):
        """Initializes the player."""
        self.pos = pygame.math.Vector2(start_x, start_y)
        self.vel = pygame.math.Vector2(0, 0)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        self.is_grounded = False
        self.inventory = Inventory(capacity=9)
        self.health = 100
        self.max_health = 100
        self.movement_speed = 8.0
        self.jump_strength = 15.0
        self.gravity = 30.0

    def update(self, delta_time: float, world: 'World'):
        """Updates the player's position and handles collisions."""
        # Apply gravity
        self.vel.y -= self.gravity * delta_time

        # Update position
        self.pos.x += self.vel.x * delta_time
        self.pos.y += self.vel.y * delta_time
        self.rect.x = int(self.pos.x * world.tile_size)
        self.rect.y = int(self.pos.y * world.tile_size)

        # Collision detection (simple AABB)
        self.is_grounded = False
        for x in range(int(self.pos.x)-1, int(self.pos.x + self.width) + 1):
            for y in range(int(self.pos.y)-1, int(self.pos.y + self.height) + 1):
                block = world.get_block(x, y)
                if block and block.is_solid:
                    
                    block_rect = pygame.Rect(block.x * world.tile_size, block.y * world.tile_size, world.tile_size, world.tile_size)
                    # if self.rect.colliderect(block_rect):
                    # Collision on the top of character
                    if self.vel.y < 0 and self.rect.bottom <= block_rect.top:
                        self.rect.bottom = block_rect.top
                        self.pos.y = self.rect.y / world.tile_size
                        self.vel.y = 0
                        self.is_grounded = True
                        print("Bottom character Collision")
                    
                    # Collision on the bottom of CHARACTER
                    # if self.vel.y > 0 and self.rect.top >= block_rect.bottom:
                    #     self.rect.top = block_rect.bottom
                    #     self.pos.y = self.rect.y / world.tile_size
                    #     self.vel.y = 0
                    #     print("Top character Collision")
                        
                    # Collision on the right
                    if self.vel.x < 0 and self.rect.right <= block_rect.left:
                        self.rect.right = block_rect.left
                        self.pos.x = self.rect.x / world.tile_size
                        self.vel.x = 0
                        print("right Collision")

                    # Collision on the left
                    if self.vel.x > 0 and self.rect.left >= block_rect.right:
                        self.rect.left = block_rect.right
                        self.pos.x = self.rect.x / world.tile_size
                        self.vel.x = 0
                        print("left Collision")

    def move_left(self):
        """Sets horizontal velocity to move left."""
        self.vel.x = -self.movement_speed

    def move_right(self):
        """Sets horizontal velocity to move right."""
        self.vel.x = self.movement_speed

    def stop_moving_horizontal(self):
        """Stops horizontal movement."""
        self.vel.x = 0

    def jump(self):
        """Makes the player jump if grounded."""
        if self.is_grounded:
            self.vel.y = self.jump_strength
            self.is_grounded = False

    def mine_block(self, world: 'World', target_block_x: int, target_block_y: int) -> bool:
        """Attempts to mine a block at the given coordinates."""
        # Range check: player must be within a certain distance
        distance = math.sqrt((self.pos.x - target_block_x)**2 + (self.pos.y - target_block_y)**2)
        if distance > 5:
            return False

        block_to_mine = world.get_block(target_block_x, target_block_y)
        if block_to_mine and block_to_mine.block_type != BlockType.AIR:
            # Drop an item into the inventory
            item_to_add = BlockItem(
                f"{block_to_mine.block_type.name.lower()}_block_item",
                f"{block_to_mine.block_type.name.capitalize()} Block",
                block_to_mine._get_texture_path(),
                block_to_mine.block_type
            )
            world.set_block(target_block_x, target_block_y, BlockType.AIR)
            self.inventory.add_item(item_to_add, 1)
            return True
        return False

    def place_block(self, world: 'World', target_block_x: int, target_block_y: int) -> bool:
        """Attempts to place a block at the given coordinates."""
        distance = math.sqrt((self.pos.x - target_block_x)**2 + (self.pos.y - target_block_y)**2)
        if distance > 5:
            return False

        selected_item, quantity = self.inventory.get_selected_slot_item()
        if selected_item and isinstance(selected_item, BlockItem) and quantity > 0:
            block_at_target = world.get_block(target_block_x, target_block_y)
            if block_at_target and block_at_target.block_type == BlockType.AIR:
                # Check if the placement location overlaps with the player's bounding box
                player_rect = self.rect.copy()
                block_rect = pygame.Rect(target_block_x * world.tile_size, target_block_y * world.tile_size, world.tile_size, world.tile_size)
                if not player_rect.colliderect(block_rect):
                    selected_item.use(self, world, target_block_x, target_block_y)
                    self.inventory.remove_item(selected_item, 1)
                    return True
        return False
        
    def __repr__(self) -> str:
        return f"Player(pos=({self.pos.x:.2f}, {self.pos.y:.2f}), Health={self.health})"


class World:
    """
    Represents the game world, containing all blocks and managing their states.
    Handles world generation, block retrieval, and modification.
    """
    def __init__(self, width: int, height: int, tile_size: int = 32, seed: int = None):
        """Initializes the game world grid."""
        self.world_width = width
        self.world_height = height
        self.tile_size = tile_size
        self.seed = seed if seed is not None else random.randint(0, 100000)
        self.blocks = [[None for _ in range(self.world_height)] for _ in range(self.world_width)]
        self.generate_world()

    def generate_world(self):
        """Generates a simple 2D world using the seed."""
        random.seed(self.seed)
        ground_level = self.world_height // 2

        for x in range(self.world_width):
            # Simple wavy ground generation
            terrain_height_offset = int(math.sin(x * 0.25) * 3) + random.randint(-1, 1)
            current_ground_level = ground_level + terrain_height_offset

            for y in range(self.world_height):
                block_type = BlockType.AIR
                if y < current_ground_level - 3:
                    block_type = BlockType.STONE
                elif y < current_ground_level:
                    block_type = BlockType.DIRT
                elif y == current_ground_level:
                    block_type = BlockType.GRASS
                
                self.blocks[x][y] = Block(block_type, x, y, self.tile_size)

    def get_block(self, x: int, y: int) -> Block | None:
        """Returns the Block object at the given world coordinates."""
        if self.is_within_bounds(x, y):
            return self.blocks[x][y]
        return None

    def set_block(self, x: int, y: int, block_type: BlockType):
        """Sets the block at the given world coordinates to a new type."""
        if self.is_within_bounds(x, y):
            self.blocks[x][y] = Block(block_type, x, y, self.tile_size)
            # Re-load texture if it's not in cache
            if block_type != BlockType.AIR:
                self.blocks[x][y]._load_texture()

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Checks if the given coordinates are within the world boundaries."""
        return 0 <= x < self.world_width and 0 <= y < self.world_height


class Camera:
    """
    Controls the view of the game world, typically following a target entity like the player.
    Converts world coordinates to screen coordinates.
    """
    def __init__(self, target_entity: Player, screen_size: tuple[int, int], tile_size: int):
        """Initializes the camera."""
        self.target = target_entity
        self.screen_width, self.screen_height = screen_size
        self.tile_size = tile_size
        self.offset = pygame.math.Vector2(0, 0)
        self.update()

    def update(self):
        """Updates the camera's position to follow the target entity."""
        self.offset.x = self.target.pos.x * self.tile_size - self.screen_width // 2
        self.offset.y = self.target.pos.y * self.tile_size - self.screen_height // 2

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[int, int]:
        """Converts world coordinates to screen (pixel) coordinates."""
        screen_x = int(world_x * self.tile_size - self.offset.x)
        screen_y = int(self.screen_height - (world_y * self.tile_size - self.offset.y))
        return screen_x, screen_y

    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple[int, int]:
        """Converts screen (pixel) coordinates to world coordinates (in blocks)."""
        world_x = (screen_x + self.offset.x) // self.tile_size
        world_y = (self.screen_height - screen_y + self.offset.y) // self.tile_size
        return int(world_x), int(world_y)


class Renderer:
    """
    Handles drawing all game elements to the screen using Pygame.
    """
    def __init__(self, screen: pygame.Surface, tile_size: int):
        """Initializes the renderer with the Pygame screen surface."""
        self.screen = screen
        self.tile_size = tile_size
        self.screen_width, self.screen_height = self.screen.get_size()
        self.font = pygame.font.Font(None, 24)
        self.message = ""
        self.message_start_time = 0

    def draw_world(self, world: World, camera: Camera):
        """Draws the visible portion of the game world."""
        # Sky color
        self.screen.fill((135, 206, 235))
        
        # Determine the visible area in world coordinates
        start_x = max(0, int(camera.offset.x // self.tile_size))
        end_x = min(world.world_width, int((camera.offset.x + self.screen_width) // self.tile_size) + 1)
        start_y = max(0, int(camera.offset.y // self.tile_size))
        end_y = min(world.world_height, int((camera.offset.y + self.screen_height) // self.tile_size) + 1)
        
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                block = world.get_block(x, y)
                if block and block.texture:
                    screen_x, screen_y = camera.world_to_screen(block.x, block.y)
                    self.screen.blit(block.texture, (screen_x, screen_y - self.tile_size))

    def draw_player(self, player: Player, camera: Camera):
        """Draws the player character."""
        # Player is a simple rectangle for now
        screen_x, screen_y = camera.world_to_screen(player.pos.x, player.pos.y)
        player_rect = pygame.Rect(screen_x, screen_y - int((player.height+1) * self.tile_size),
                                  int(player.width * self.tile_size), int(player.height * self.tile_size))
        pygame.draw.rect(self.screen, (0, 128, 255), player_rect)
        
    def draw_inventory(self, inventory: Inventory):
        """Draws the player's hotbar inventory UI."""
        # Hotbar background
        hotbar_width = inventory.capacity * (self.tile_size + 5) + 5
        hotbar_height = self.tile_size + 10
        hotbar_x = (self.screen_width - hotbar_width) // 2
        hotbar_y = self.screen_height - hotbar_height - 10
        hotbar_rect = pygame.Rect(hotbar_x, hotbar_y, hotbar_width, hotbar_height)
        pygame.draw.rect(self.screen, (100, 100, 100), hotbar_rect, border_radius=5)
        
        for i, (item, quantity) in enumerate(inventory.slots):
            slot_x = hotbar_x + 5 + i * (self.tile_size + 5)
            slot_y = hotbar_y + 5
            slot_rect = pygame.Rect(slot_x, slot_y, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, (50, 50, 50), slot_rect, border_radius=3)
            
            # Highlight selected slot
            if i == inventory.selected_slot_index:
                pygame.draw.rect(self.screen, (255, 255, 255), slot_rect, 2, border_radius=3)
                
            if item and item.texture:
                self.screen.blit(item.texture, slot_rect.topleft)
                
                # Draw quantity
                if quantity > 1:
                    text_surface = self.font.render(str(quantity), True, (255, 255, 255))
                    text_rect = text_surface.get_rect(bottomright=slot_rect.bottomright)
                    self.screen.blit(text_surface, text_rect)
        
    def draw_ui(self, player: Player, fps: int):
        """Draws other UI elements (FPS, health, messages)."""
        # FPS counter
        fps_text = self.font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))
        
        # Player health
        health_text = self.font.render(f"Health: {player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 40))
        
        # Message box
        if self.message and time.time() - self.message_start_time < 3:
            msg_surface = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surface.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(msg_surface, msg_rect)

    def set_message(self, text: str):
        """Sets a message to be displayed temporarily."""
        self.message = text
        self.message_start_time = time.time()


class InputHandler:
    """
    Processes raw user input (keyboard, mouse) and translates it into game actions.
    """
    def __init__(self, game: 'Game'):
        """Initializes the input handler."""
        self.game = game
        
    def handle_events(self):
        """Processes Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            
            # Keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.player.jump()
                
                # Inventory selection (keys 1-9)
                if pygame.K_1 <= event.key <= pygame.K_9:
                    self.game.player.inventory.select_slot(event.key - pygame.K_1)
                    self.game.renderer.set_message(
                        f"Selected slot {self.game.player.inventory.selected_slot_index + 1}"
                    )
                
            # Mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                world_x, world_y = self.game.camera.screen_to_world(*event.pos)
                if event.button == 1:  # Left click to mine
                    if self.game.player.mine_block(self.game.world, world_x, world_y):
                        self.game.renderer.set_message(f"Mined block at ({world_x}, {world_y})")
                    else:
                        self.game.renderer.set_message("Could not mine block here.")
                elif event.button == 3:  # Right click to place
                    if self.game.player.place_block(self.game.world, world_x, world_y):
                        self.game.renderer.set_message(f"Placed block at ({world_x}, {world_y})")
                    else:
                        self.game.renderer.set_message("Could not place block here.")
            
        # Continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.game.player.move_left()
        elif keys[pygame.K_d]:
            self.game.player.move_right()
        else:
            self.game.player.stop_moving_horizontal()

class Game:
    """
    Manages the overall game loop, state, and coordination between different game components.
    This is the main entry point for the game.
    """
    def __init__(self, screen_width: int = 800, screen_height: int = 600, fps: int = 60):
        """Initializes the game system."""
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps = fps
        self.running = True
        self.game_state = GameState.RUNNING

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("2D Block Game")
        self.clock = pygame.time.Clock()
        
        self.tile_size = 32
        
        # Create dummy assets for the game.
        self._create_dummy_assets()

        self.world = World(width=100, height=50, tile_size=self.tile_size)
        self.player = Player(start_x=self.world.world_width / 2, start_y=self.world.world_height / 2 + 5,
                             width=0.8, height=1.8)
        self.camera = Camera(self.player, (self.screen_width, self.screen_height), self.tile_size)
        self.renderer = Renderer(self.screen, self.tile_size)
        self.input_handler = InputHandler(self)

        self._populate_initial_inventory()
        print("Game initialized. Press '1'-'9' to select inventory slots, 'A'/'D' to move, 'Space' to jump, and mouse clicks to mine/place blocks.")

    def _create_dummy_assets(self):
        """
        Creates simple, colored surfaces to act as block and item textures.
        This avoids needing to ship actual image files with the code.
        """
        assets = {
            "assets/dirt.png": (139, 69, 19),
            "assets/grass.png": (34, 139, 34),
            "assets/stone.png": (128, 128, 128),
            "assets/wood.png": (160, 82, 45),
            "assets/water.png": (0, 191, 255),
            "assets/coal_ore.png": (40, 40, 40),
            "assets/iron_ore.png": (150, 150, 150),
            "assets/diamond_ore.png": (175, 238, 238),
            "assets/default.png": (255, 0, 255),
            "assets/items/dirt_block.png": (139, 69, 19),
            "assets/items/grass_block.png": (34, 139, 34),
            "assets/items/stone_block.png": (128, 128, 128),
            "assets/items/wooden_pickaxe.png": (210, 180, 140),
        }
        
        for path, color in assets.items():
            surface = pygame.Surface((self.tile_size, self.tile_size))
            surface.fill(color)
            
            # Simple details for some textures
            if "ore" in path:
                pygame.draw.circle(surface, (255, 255, 255), (self.tile_size // 2, self.tile_size // 2), 5)
            
            # Save the surface to the cache so other classes can load it
            Block.TEXTURE_CACHE[path] = surface.convert_alpha()
        
    def _populate_initial_inventory(self):
        """Adds some initial items to the player's inventory for testing."""
        grass_item = BlockItem("grass_block_item", "Grass Block", "assets/items/grass_block.png", BlockType.GRASS)
        dirt_item = BlockItem("dirt_block_item", "Dirt Block", "assets/items/dirt_block.png", BlockType.DIRT)
        stone_item = BlockItem("stone_block_item", "Stone Block", "assets/items/stone_block.png", BlockType.STONE)
        pickaxe = Tool("wooden_pickaxe", "Wooden Pickaxe", "assets/items/wooden_pickaxe.png", 50, 5, ToolType.PICKAXE)
        
        self.player.inventory.add_item(grass_item, 5)
        self.player.inventory.add_item(dirt_item, 20)
        self.player.inventory.add_item(stone_item, 15)
        self.player.inventory.add_item(pickaxe, 1)

    def run(self):
        """Starts the main game loop."""
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000.0 # Convert ms to seconds
            
            self.input_handler.handle_events()
            
            if self.game_state == GameState.RUNNING:
                self.update(delta_time)
                self.draw()
            else:
                # Handle paused or menu state drawing
                pass
                
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def update(self, delta_time: float):
        """Updates game logic for all entities."""
        self.player.update(delta_time, self.world)
        self.camera.update()

    def draw(self):
        """Draws all game elements to the screen."""
        self.renderer.draw_world(self.world, self.camera)
        self.renderer.draw_player(self.player, self.camera)
        self.renderer.draw_inventory(self.player.inventory)
        self.renderer.draw_ui(self.player, self.clock.get_fps())

# --- Main entry point ---
if __name__ == "__main__":
    game = Game()
    game.run()
