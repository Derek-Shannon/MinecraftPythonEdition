import enum
import random
import math # Potentially useful for physics, though not extensively used in this basic structure

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
    def __init__(self, block_type: BlockType, x: int, y: int):
        """
        Initializes a new Block.
        :param block_type: The type of the block (e.g., BlockType.DIRT).
        :param x: The x-coordinate of the block in world units.
        :param y: The y-coordinate of the block in world units.
        """
        self.block_type = block_type
        self.x = x
        self.y = y
        self.is_solid = self._get_solidity()
        self.texture_path = self._get_texture_path() # Path to the texture image

    def _get_solidity(self) -> bool:
        """Determines if the block is solid based on its type."""
        return self.block_type not in [BlockType.AIR, BlockType.WATER]

    def _get_texture_path(self) -> str:
        """Returns the texture path for the block type."""
        # In a real game, you'd load actual paths or pre-loaded textures
        texture_map = {
            BlockType.AIR: "assets/textures/air.png",
            BlockType.DIRT: "assets/textures/dirt.png",
            BlockType.GRASS: "assets/textures/grass.png",
            BlockType.STONE: "assets/textures/stone.png",
            BlockType.WOOD: "assets/textures/wood.png",
            BlockType.WATER: "assets/textures/water.png",
            BlockType.COAL_ORE: "assets/textures/coal_ore.png",
            BlockType.IRON_ORE: "assets/textures/iron_ore.png",
            BlockType.DIAMOND_ORE: "assets/textures/diamond_ore.png",
        }
        return texture_map.get(self.block_type, "assets/textures/default.png")

    def get_texture(self) -> str:
        """Public method to get the block's texture path."""
        return self.texture_path

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
        self.texture_path = texture_path
        self.stackable = stackable
        self.max_stack_size = max_stack_size

    def use(self, player: 'Player', world: 'World', target_x: int, target_y: int):
        """
        Abstract method to define what happens when the item is used.
        To be overridden by subclasses.
        :param player: The player using the item.
        :param world: The game world.
        :param target_x: The x-coordinate of the target block (e.g., for placing/mining).
        :param target_y: The y-coordinate of the target block.
        """
        print(f"Using {self.name} (base item)")
        pass # Placeholder for actual item usage logic

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
        """
        Uses the tool. Decreases durability.
        Specific tool actions (e.g., mining a block) would be handled here or by Player.
        """
        if self.durability > 0:
            self.durability -= 1
            print(f"Used {self.name}. Durability remaining: {self.durability}")
            # Example: If it's a pickaxe, try to mine the target block
            # This logic might be better placed in Player's mine_block,
            # which then calls a tool's effectiveness.
        else:
            print(f"{self.name} is broken!")

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
        print(f"Attempting to place {self.name} at ({target_x}, {target_y})")
        world.set_block(target_x, target_y, self.block_type)
        # In a full game, you'd also remove one item from player's inventory

    def __repr__(self) -> str:
        return f"BlockItem(ID:{self.item_id}, Name:'{self.name}', BlockType:{self.block_type.name})"


class Inventory:
    """
    Manages the player's items, including adding, removing, and querying items.
    """
    def __init__(self, capacity: int = 36):
        """
        Initializes the inventory.
        :param capacity: The total number of item slots in the inventory.
        """
        self.capacity = capacity
        # slots is a list of tuples: (item_object, quantity)
        # Using None to represent empty slots
        self.slots = [(None, 0)] * capacity
        self.selected_slot_index = 0 # Index of the currently selected item slot

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Adds an item to the inventory.
        Handles stacking if the item is stackable and a slot with the same item exists.
        :param item: The Item object to add.
        :param quantity: The quantity of the item to add.
        :return: True if the item was successfully added, False otherwise.
        """
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
                            print(f"Added {amount_to_add} {item.name}(s) to existing stack.")
                            return True
            # If still quantity left, try to find an empty slot
            if quantity > 0:
                print(f"Added {item.name}(s) to new stack(s). Remaining quantity: {quantity}")

        # Find an empty slot for the remaining quantity or non-stackable items
        for i, (existing_item, _) in enumerate(self.slots):
            if existing_item is None:
                amount_to_add = min(quantity, item.max_stack_size if item.stackable else 1)
                self.slots[i] = (item, amount_to_add)
                quantity -= amount_to_add
                print(f"Placed {amount_to_add} {item.name}(s) in new slot {i}.")
                if quantity == 0:
                    return True
        print(f"Could not add all {item.name}(s). Inventory full or no suitable stack found. Remaining: {quantity}")
        return False # Not all items could be added

    def remove_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Removes a specified quantity of an item from the inventory.
        :param item: The Item object to remove.
        :param quantity: The quantity to remove.
        :return: True if items were successfully removed, False otherwise.
        """
        if quantity <= 0:
            return False

        items_removed = 0
        for i in range(len(self.slots) - 1, -1, -1): # Iterate backwards to handle empty slots better
            existing_item, current_quantity = self.slots[i]
            if existing_item and existing_item.item_id == item.item_id:
                amount_to_remove = min(quantity, current_quantity)
                self.slots[i] = (existing_item, current_quantity - amount_to_remove)
                items_removed += amount_to_remove
                quantity -= amount_to_remove
                if self.slots[i][1] <= 0: # If slot is empty, clear it
                    self.slots[i] = (None, 0)
                if quantity == 0:
                    print(f"Removed {items_removed} {item.name}(s).")
                    return True
        print(f"Could not remove all {item.name}(s). Only removed {items_removed}.")
        return False

    def has_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Checks if the inventory contains at least the specified quantity of an item.
        :return: True if the item(s) are present in sufficient quantity, False otherwise.
        """
        count = self.get_item_count(item)
        return count >= quantity

    def get_item_count(self, item: Item) -> int:
        """Returns the total count of a specific item across all slots."""
        total_count = 0
        for existing_item, quantity in self.slots:
            if existing_item and existing_item.item_id == item.item_id:
                total_count += quantity
        return total_count

    def get_selected_slot_item(self) -> tuple[Item | None, int]:
        """Returns the item and quantity in the currently selected slot."""
        if 0 <= self.selected_slot_index < self.capacity:
            return self.slots[self.selected_slot_index]
        return (None, 0)

    def select_slot(self, index: int):
        """Sets the selected inventory slot."""
        if 0 <= index < self.capacity:
            self.selected_slot_index = index
        else:
            print(f"Invalid slot index: {index}")

    def __repr__(self) -> str:
        items_in_inventory = [
            f"{item.name} x{qty}" for item, qty in self.slots if item is not None
        ]
        return f"Inventory(Capacity:{self.capacity}, Items:{items_in_inventory})"


class Player:
    """
    Represents the player character, handling movement, inventory, and interactions.
    """
    def __init__(self, start_x: float, start_y: float, width: float = 0.8, height: float = 1.8):
        """
        Initializes the player.
        :param start_x: Starting x-coordinate in world units.
        :param start_y: Starting y-coordinate in world units.
        :param width: Width of the player collision box.
        :param height: Height of the player collision box.
        """
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_grounded = False
        self.inventory = Inventory(capacity=36)
        self.health = 100
        self.max_health = 100
        self.movement_speed = 5.0 # Units per second
        self.jump_strength = 10.0 # Initial upward velocity for jump
        self.gravity = 20.0 # Acceleration due to gravity

    def update(self, delta_time: float, world: 'World'):
        """
        Updates the player's position, applies gravity and collision detection.
        :param delta_time: Time elapsed since last update (in seconds).
        :param world: The game world object for collision checks.
        """
        # Apply gravity
        self.velocity_y -= self.gravity * delta_time

        # Update position based on velocity
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        # Basic collision detection (very rudimentary, needs refinement for a real game)
        # Check collision with blocks below for grounding
        block_below_x = int(self.x + self.width / 2)
        block_below_y = int(self.y - 0.1) # Check slightly below player
        block_below = world.get_block(block_below_x, block_below_y)

        if block_below and block_below.is_solid:
            if self.velocity_y < 0 and self.y <= block_below.y + 1: # If falling and hit block
                self.y = block_below.y + 1.0 # Snap to top of block
                self.velocity_y = 0
                self.is_grounded = True
        else:
            self.is_grounded = False

        # Reset horizontal velocity if not moving
        if abs(self.velocity_x) < 0.1: # Small threshold to prevent floating point issues
            self.velocity_x = 0


    def move_left(self):
        """Sets horizontal velocity to move left."""
        self.velocity_x = -self.movement_speed

    def move_right(self):
        """Sets horizontal velocity to move right."""
        self.velocity_x = self.movement_speed

    def stop_moving_horizontal(self):
        """Stops horizontal movement."""
        self.velocity_x = 0

    def jump(self):
        """Makes the player jump if grounded."""
        if self.is_grounded:
            self.velocity_y = self.jump_strength
            self.is_grounded = False
            print("Player jumped!")

    def mine_block(self, world: 'World', target_block_x: int, target_block_y: int):
        """
        Attempts to mine a block at the given coordinates.
        Requires a tool in hand or can be done by hand for certain blocks.
        :param world: The game world.
        :param target_block_x: X-coordinate of the block to mine.
        :param target_block_y: Y-coordinate of the block to mine.
        """
        print(f"Attempting to mine block at ({target_block_x}, {target_block_y})")
        block_to_mine = world.get_block(target_block_x, target_block_y)

        if block_to_mine and block_to_mine.block_type != BlockType.AIR:
            # Example: Check distance, tool, etc.
            distance = math.sqrt((self.x - target_block_x)**2 + (self.y - target_block_y)**2)
            if distance < 3: # Simple range check
                print(f"Mining {block_to_mine.block_type.name} at ({target_block_x}, {target_block_y})")
                world.set_block(target_block_x, target_block_y, BlockType.AIR) # Remove block
                # Add block item to inventory (if applicable)
                # For demonstration, always add a dirt block item
                dirt_item = BlockItem("dirt_block_item", "Dirt Block", "assets/items/dirt_block.png", BlockType.DIRT)
                self.inventory.add_item(dirt_item, 1)
            else:
                print("Block too far to mine.")
        else:
            print("No solid block to mine at this location.")

    def place_block(self, world: 'World', target_block_x: int, target_block_y: int):
        """
        Attempts to place a block at the given coordinates using the selected item.
        :param world: The game world.
        :param target_block_x: X-coordinate for placing the block.
        :param target_block_y: Y-coordinate for placing the block.
        """
        print(f"Attempting to place block at ({target_block_x}, {target_block_y})")
        selected_item, quantity = self.inventory.get_selected_slot_item()

        if selected_item and isinstance(selected_item, BlockItem) and quantity > 0:
            block_at_target = world.get_block(target_block_x, target_block_y)
            if block_at_target and block_at_target.block_type == BlockType.AIR:
                # Ensure player is not placing block on themselves
                if not (int(self.x) <= target_block_x < int(self.x + self.width) and \
                        int(self.y) <= target_block_y < int(self.y + self.height)):
                    selected_item.use(self, world, target_block_x, target_block_y)
                    self.inventory.remove_item(selected_item, 1) # Consume one item
                else:
                    print("Cannot place block inside player.")
            else:
                print("Cannot place block here, space is occupied.")
        else:
            print("No block item selected or not enough blocks to place.")


    def take_damage(self, amount: int):
        """Reduces player health."""
        self.health -= amount
        if self.health < 0:
            self.health = 0
            print("Player has died!")
            # Trigger game over state
        print(f"Player took {amount} damage. Health: {self.health}")

    def add_to_inventory(self, item: Item, quantity: int = 1):
        """Wrapper for inventory's add_item."""
        self.inventory.add_item(item, quantity)

    def remove_from_inventory(self, item: Item, quantity: int = 1):
        """Wrapper for inventory's remove_item."""
        self.inventory.remove_item(item, quantity)

    def __repr__(self) -> str:
        return f"Player(x={self.x:.2f}, y={self.y:.2f}, Health={self.health})"


class World:
    """
    Represents the game world, containing all blocks and managing their states.
    Handles world generation, block retrieval, and modification.
    """
    def __init__(self, width: int, height: int, tile_size: int = 32, seed: int = None):
        """
        Initializes the game world grid.
        :param width: Width of the world in blocks.
        :param height: Height of the world in blocks.
        :param tile_size: The pixel size of a single block (for rendering context).
        :param seed: Seed for world generation, None for random.
        """
        self.world_width = width
        self.world_height = height
        self.tile_size = tile_size
        self.seed = seed if seed is not None else random.randint(0, 100000)
        self.blocks = [[None for _ in range(self.world_height)] for _ in range(self.world_width)]
        self.generate_world()

    def generate_world(self):
        """
        Generates a simple 2D world using the seed.
        For a more complex game, this would involve Perlin noise, biomes, etc.
        """
        print(f"Generating world with seed: {self.seed}")
        random.seed(self.seed)

        ground_level = self.world_height // 2 # Simple flat ground level

        for x in range(self.world_width):
            # Simple wavy ground
            # This can be replaced with Perlin noise for more realistic terrain
            terrain_height_offset = int(math.sin(x * 0.5) * 5) # Example wave
            current_ground_level = ground_level + terrain_height_offset

            for y in range(self.world_height):
                if y < current_ground_level - 1:
                    self.blocks[x][y] = Block(BlockType.STONE, x, y)
                elif y == current_ground_level - 1:
                    self.blocks[x][y] = Block(BlockType.DIRT, x, y)
                elif y == current_ground_level:
                    self.blocks[x][y] = Block(BlockType.GRASS, x, y)
                else:
                    self.blocks[x][y] = Block(BlockType.AIR, x, y)

        print("World generation complete.")

    def get_block(self, x: int, y: int) -> Block | None:
        """
        Returns the Block object at the given world coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :return: Block object or None if out of bounds.
        """
        if self.is_within_bounds(x, y):
            return self.blocks[x][y]
        return None

    def set_block(self, x: int, y: int, block_type: BlockType):
        """
        Sets the block at the given world coordinates to a new type.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :param block_type: The new BlockType to set.
        """
        if self.is_within_bounds(x, y):
            self.blocks[x][y] = Block(block_type, x, y)
        else:
            print(f"Warning: Attempted to set block out of bounds at ({x}, {y})")

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Checks if the given coordinates are within the world boundaries."""
        return 0 <= x < self.world_width and 0 <= y < self.world_height

    def save_world(self, file_path: str):
        """Saves the current state of the world to a file."""
        print(f"Saving world to {file_path} (Not implemented)")
        # This would involve serializing the block data to JSON or a custom format
        pass

    def load_world(self, file_path: str):
        """Loads a world from a file."""
        print(f"Loading world from {file_path} (Not implemented)")
        # This would involve deserializing the block data
        pass

    def __repr__(self) -> str:
        return f"World(Width={self.world_width}, Height={self.world_height}, Seed={self.seed})"


class Camera:
    """
    Controls the view of the game world, typically following a target entity like the player.
    Converts world coordinates to screen coordinates.
    """
    def __init__(self, target_entity: Player, screen_width: int, screen_height: int, tile_size: int):
        """
        Initializes the camera.
        :param target_entity: The entity the camera should follow (e.g., Player object).
        :param screen_width: The width of the game screen in pixels.
        :param screen_height: The height of the game screen in pixels.
        :param tile_size: The pixel size of a single block.
        """
        self.target = target_entity
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        self.x = 0.0 # Camera's top-left world x-coordinate
        self.y = 0.0 # Camera's top-left world y-coordinate
        self.offset_x = 0.0 # Offset to center target
        self.offset_y = 0.0 # Offset to center target

        self._calculate_offsets()

    def _calculate_offsets(self):
        """Calculates offsets to try and center the target on screen."""
        self.offset_x = (self.screen_width / 2) / self.tile_size - (self.target.width / 2)
        self.offset_y = (self.screen_height / 2) / self.tile_size - (self.target.height / 2)

    def update(self):
        """
        Updates the camera's position to follow the target entity.
        The camera's (x, y) represents the world coordinate of the top-left corner
        of the visible screen area.
        """
        # Calculate the desired camera position to center the player
        target_center_x = self.target.x + (self.target.width / 2)
        target_center_y = self.target.y + (self.target.height / 2)

        # Camera x, y should be the top-left of the viewable area in world coordinates
        self.x = target_center_x - (self.screen_width / (2 * self.tile_size))
        self.y = target_center_y - (self.screen_height / (2 * self.tile_size))

        # Clamp camera to world boundaries if necessary (optional for infinite worlds)
        # For this basic example, we'll let it move freely for now.

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[int, int]:
        """
        Converts world coordinates to screen (pixel) coordinates.
        :param world_x: X-coordinate in world units.
        :param world_y: Y-coordinate in world units.
        :return: Tuple of (screen_x, screen_y) in pixels.
        """
        screen_x = int((world_x - self.x) * self.tile_size)
        screen_y = int(self.screen_height - (world_y - self.y) * self.tile_size)
        return screen_x, screen_y

    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple[float, float]:
        """
        Converts screen (pixel) coordinates to world coordinates.
        Useful for mouse interactions.
        :param screen_x: X-coordinate in pixels.
        :param screen_y: Y-coordinate in pixels.
        :return: Tuple of (world_x, world_y) in world units.
        """
        world_x = (screen_x / self.tile_size) + self.x
        world_y = (self.screen_height - screen_y) / self.tile_size + self.y
        return world_x, world_y


class Renderer:
    """
    Handles drawing all game elements to the screen.
    This class would typically interact with a graphics library (e.g., Pygame, Arcade).
    """
    def __init__(self, screen_width: int, screen_height: int, tile_size: int):
        """
        Initializes the renderer.
        :param screen_width: Width of the game screen in pixels.
        :param screen_height: Height of the game screen in pixels.
        :param tile_size: The pixel size of a single block.
        """
        # In a real Pygame app, 'screen' would be a pygame.Surface object.
        # Here, it's a placeholder.
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        print(f"Renderer initialized with screen size {screen_width}x{screen_height} and tile size {tile_size}")
        self._loaded_textures = {} # Cache for loaded textures

    def load_texture(self, path: str):
        """
        Loads and caches a texture.
        In a real game, this would use a graphics library's image loading function.
        For this example, it just prints a message.
        """
        if path not in self._loaded_textures:
            print(f"Loading texture: {path}")
            # Simulate loading, in reality: self._loaded_textures[path] = pygame.image.load(path)
            self._loaded_textures[path] = f"Texture for {path}" # Placeholder
        return self._loaded_textures[path]

    def draw_world(self, world: World, camera: Camera):
        """
        Draws the visible portion of the game world.
        :param world: The World object to draw.
        :param camera: The Camera object to determine the view.
        """
        # Calculate which blocks are visible on screen
        start_col = max(0, int(camera.x))
        end_col = min(world.world_width, int(camera.x + self.screen_width / camera.tile_size) + 2) # +2 for buffer
        start_row = max(0, int(camera.y))
        end_row = min(world.world_height, int(camera.y + self.screen_height / camera.tile_size) + 2) # +2 for buffer

        # Optimized loop to draw only visible blocks
        for x in range(start_col, end_col):
            for y in range(start_row, end_row):
                block = world.get_block(x, y)
                if block and block.block_type != BlockType.AIR:
                    screen_x, screen_y = camera.world_to_screen(block.x, block.y + 1) # +1 because y is bottom-left of block
                    # Simulate drawing a block
                    texture = self.load_texture(block.get_texture())
                    # In Pygame: self.screen.blit(texture, (screen_x, screen_y - self.tile_size))
                    print(f"  Drawing block {block.block_type.name} at screen ({screen_x}, {screen_y - self.tile_size})")

    def draw_player(self, player: Player, camera: Camera):
        """
        Draws the player character.
        :param player: The Player object to draw.
        :param camera: The Camera object for coordinate conversion.
        """
        screen_x, screen_y = camera.world_to_screen(player.x, player.y + player.height) # +height because y is player's base
        # In Pygame: pygame.draw.rect(self.screen, (255, 0, 0), (screen_x, screen_y - int(player.height * self.tile_size),
        #                                                     int(player.width * self.tile_size), int(player.height * self.tile_size)))
        print(f"  Drawing player at screen ({screen_x}, {screen_y - int(player.height * self.tile_size)})")

    def draw_inventory(self, inventory: Inventory):
        """
        Draws the player's inventory UI.
        :param inventory: The Inventory object to draw.
        """
        print("  Drawing Inventory UI:")
        for i, (item, quantity) in enumerate(inventory.slots):
            is_selected = " (SELECTED)" if i == inventory.selected_slot_index else ""
            if item:
                print(f"    Slot {i}{is_selected}: {item.name} x{quantity} (Texture: {item.texture_path})")
            else:
                print(f"    Slot {i}{is_selected}: Empty")

    def draw_ui(self, player: Player):
        """
        Draws other UI elements (health bar, etc.).
        :param player: The Player object to get health info.
        """
        print(f"  Drawing UI: Health: {player.health}/{player.max_health}")
        # In Pygame: draw health bar, crosshair, etc.

    def update_display(self):
        """
        Updates the actual display. In Pygame, this would be pygame.display.flip().
        For this example, it's just a message.
        """
        print("Display Updated!")
        print("-" * 50) # Separator for visual clarity in console output


class InputHandler:
    """
    Processes raw user input (keyboard, mouse) and translates it into game actions.
    This would typically interact with a library like Pygame's event system.
    """
    def __init__(self):
        """Initializes the input handler."""
        self._keys_pressed = set()
        self._mouse_buttons_pressed = set()
        self._mouse_pos = (0, 0)
        print("InputHandler initialized.")

    def handle_events(self, game_instance: 'Game'):
        """
        Processes events from the input system.
        In a real Pygame loop, this would iterate through pygame.event.get().
        For this example, it simulates some events.
        :param game_instance: The Game object to interact with.
        """
        # Simulate some input events for demonstration
        # In a real Pygame app, this would be:
        # for event in pygame.event.get():
        #   if event.type == pygame.KEYDOWN: self._keys_pressed.add(event.key)
        #   etc.

        # Example: Simulate pressing 'A' to move left, 'D' to move right
        if self.is_key_pressed("a"):
            game_instance.player.move_left()
        elif self.is_key_pressed("d"):
            game_instance.player.move_right()
        else:
            game_instance.player.stop_moving_horizontal()

        if self.is_key_pressed("space"):
            game_instance.player.jump()

        if self.is_mouse_button_pressed("left_click"):
            # Simulate a mouse click at a specific world coordinate
            # In a real game, you'd convert mouse_pos to world_pos
            world_x, world_y = game_instance.camera.screen_to_world(self._mouse_pos[0], self._mouse_pos[1])
            game_instance.player.mine_block(game_instance.world, int(world_x), int(world_y))
            # Reset mouse click to avoid continuous action
            self._mouse_buttons_pressed.discard("left_click")

        if self.is_mouse_button_pressed("right_click"):
            world_x, world_y = game_instance.camera.screen_to_world(self._mouse_pos[0], self._mouse_pos[1])
            game_instance.player.place_block(game_instance.world, int(world_x), int(world_y))
            # Reset mouse click
            self._mouse_buttons_pressed.discard("right_click")

        # Simulate inventory selection with numbers 1-9
        for i in range(1, 10):
            if self.is_key_pressed(str(i)):
                game_instance.player.inventory.select_slot(i - 1)
                self._keys_pressed.discard(str(i)) # "Release" the key immediately


    def set_key_state(self, key: str, pressed: bool):
        """Simulates key presses/releases for demonstration."""
        if pressed:
            self._keys_pressed.add(key.lower())
        else:
            self._keys_pressed.discard(key.lower())

    def set_mouse_button_state(self, button: str, pressed: bool):
        """Simulates mouse button presses/releases."""
        if pressed:
            self._mouse_buttons_pressed.add(button.lower())
        else:
            self._mouse_buttons_pressed.discard(button.lower())

    def set_mouse_position(self, x: int, y: int):
        """Sets the simulated mouse position."""
        self._mouse_pos = (x, y)

    def is_key_pressed(self, key_code: str) -> bool:
        """Checks if a specific key is currently pressed."""
        return key_code.lower() in self._keys_pressed

    def get_mouse_position(self) -> tuple[int, int]:
        """Returns the current mouse position."""
        return self._mouse_pos

    def is_mouse_button_pressed(self, button_code: str) -> bool:
        """Checks if a specific mouse button is pressed (e.g., 'left_click', 'right_click')."""
        return button_code.lower() in self._mouse_buttons_pressed


class Game:
    """
    Manages the overall game loop, state, and coordination between different game components.
    This is the main entry point for the game.
    """
    def __init__(self, screen_width: int = 800, screen_height: int = 600, fps: int = 60):
        """
        Initializes the game system.
        :param screen_width: Width of the game window in pixels.
        :param screen_height: Height of the game window in pixels.
        :param fps: Desired frames per second.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps = fps
        self.running = True
        self.game_state = GameState.RUNNING

        self.tile_size = 32 # Assuming blocks are 32x32 pixels

        self.world = World(width=100, height=50, tile_size=self.tile_size)
        self.player = Player(start_x=self.world.world_width / 2, start_y=self.world.world_height / 2 + 5)
        self.renderer = Renderer(screen_width, screen_height, self.tile_size)
        self.camera = Camera(self.player, screen_width, screen_height, self.tile_size)
        self.input_handler = InputHandler()

        self._populate_initial_inventory()
        print("Game initialized.")

    def _populate_initial_inventory(self):
        """Adds some initial items to the player's inventory for testing."""
        self.player.add_to_inventory(BlockItem("grass_block_item", "Grass Block", "assets/items/grass_block.png", BlockType.GRASS), 10)
        self.player.add_to_inventory(BlockItem("dirt_block_item", "Dirt Block", "assets/items/dirt_block.png", BlockType.DIRT), 20)
        self.player.add_to_inventory(BlockItem("stone_block_item", "Stone Block", "assets/items/stone_block.png", BlockType.STONE), 5)
        self.player.add_to_inventory(Tool("wooden_pickaxe", "Wooden Pickaxe", "assets/items/wooden_pickaxe.png", 50, 5, ToolType.PICKAXE), 1)
        self.player.add_to_inventory(Tool("wooden_axe", "Wooden Axe", "assets/items/wooden_axe.png", 50, 5, ToolType.AXE), 1)

    def run(self):
        """
        Starts the main game loop.
        In a real game, this would contain a while loop and a clock for timing.
        Here, we simulate a few frames for demonstration.
        """
        print("\n--- Starting Game Loop ---")
        # Simulate a few frames of the game loop
        last_time = 0 # Placeholder for actual time tracking
        frame_duration = 1.0 / self.fps # Time per frame if running at target FPS

        for frame_num in range(5): # Simulate 5 frames
            print(f"\n--- Frame {frame_num + 1} ---")
            delta_time = frame_duration # For simulation, assume consistent delta_time

            self.handle_input()
            if self.game_state == GameState.RUNNING:
                self.update(delta_time)
                self.draw()
            else:
                print(f"Game is {self.game_state.name}. Skipping update/draw.")

            # In a real game loop, you'd delay here to match FPS
            # time.sleep(max(0, frame_duration - (time.time() - last_time)))
            # last_time = time.time()

        print("\n--- Game Loop Finished ---")
        print(f"Final Player State: {self.player}")
        print(f"Final Inventory: {self.player.inventory}")

    def update(self, delta_time: float):
        """
        Updates game logic for all entities.
        :param delta_time: Time elapsed since the last update in seconds.
        """
        # print(f"Updating game logic (delta_time: {delta_time:.3f}s)")
        self.player.update(delta_time, self.world)
        self.camera.update()
        # Other entities' update logic would go here

    def draw(self):
        """Draws all game elements to the screen."""
        # print("Drawing game elements...")
        self.renderer.draw_world(self.world, self.camera)
        self.renderer.draw_player(self.player, self.camera)
        self.renderer.draw_inventory(self.player.inventory)
        self.renderer.draw_ui(self.player)
        self.renderer.update_display()

    def handle_input(self):
        """Handles user input based on the current game state."""
        # print("Handling input...")
        self.input_handler.handle_events(self) # Pass self to allow InputHandler to interact with Game/Player/World

    def set_game_state(self, new_state: GameState):
        """Changes the current game state."""
        print(f"Changing game state from {self.game_state.name} to {new_state.name}")
        self.game_state = new_state


# --- Example Usage (Run this to see basic class interactions) ---
if __name__ == "__main__":
    # Create a Game instance
    game = Game(screen_width=800, screen_height=600, fps=60)

    # Simulate some initial actions
    print("\n--- Simulating Player Actions (before game loop) ---")
    game.input_handler.set_key_state("d", True) # Player starts moving right
    game.input_handler.set_mouse_position(400, 300) # Mouse in center of screen

    # Simulate a key press for inventory slot 2
    game.input_handler.set_key_state("2", True)
    game.handle_input() # Process the selection
    game.input_handler.set_key_state("2", False) # Release the key

    # Simulate a few steps for the player to move
    for _ in range(2):
        game.player.update(0.1, game.world) # Small delta time
        game.camera.update() # Update camera with player movement
        print(f"Player current position: ({game.player.x:.2f}, {game.player.y:.2f})")

    # Simulate mining a block (e.g., at a fixed coordinate relative to player)
    # Target 1 block to the right and slightly down from player center
    target_mine_world_x = int(game.player.x + game.player.width / 2 + 1)
    target_mine_world_y = int(game.player.y) # Roughly at player's y level

    print("\n--- Simulating Mining and Placing ---")
    game.input_handler.set_mouse_position(
        *game.camera.world_to_screen(target_mine_world_x, target_mine_world_y)
    )
    game.input_handler.set_mouse_button_state("left_click", True)
    game.handle_input()
    game.input_handler.set_mouse_button_state("left_click", False)
    print(f"Inventory after mining: {game.player.inventory}")

    # Simulate placing a block (e.g., 1 block to the right of the mined spot)
    target_place_world_x = target_mine_world_x + 1
    target_place_world_y = target_mine_world_y

    # Select the dirt block item if available (assuming it was added)
    dirt_item_in_inventory = False
    for i, (item, _) in enumerate(game.player.inventory.slots):
        if item and item.item_id == "dirt_block_item":
            game.player.inventory.select_slot(i)
            dirt_item_in_inventory = True
            break
    if not dirt_item_in_inventory:
        print("Dirt block item not found in inventory for placing simulation.")

    if dirt_item_in_inventory:
        game.input_handler.set_mouse_position(
            *game.camera.world_to_screen(target_place_world_x, target_place_world_y)
        )
        game.input_handler.set_mouse_button_state("right_click", True)
        game.handle_input()
        game.input_handler.set_mouse_button_state("right_click", False)
        print(f"Inventory after placing: {game.player.inventory}")

    # Start the main game loop simulation
    game.run()

    print("\n--- End of Program ---")
