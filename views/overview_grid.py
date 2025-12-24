from PySide6.QtWidgets import QWidget, QLabel

from service.sounds_service import SoundsService
from views.flow_layout import FlowLayout
from views.grid_item import GridItem
from service.signal_service import signals

class GridWidget(QWidget):
    def __init__(self, sound_service: SoundsService, parent=None):
        super().__init__(parent)
        self.items = sound_service.sounds_list
        signals.sounds_list_changed.connect(self.populate_grid)

        # Grid settings
        self.grid_spacing = 10
        self.item_size = 100

        # Create layout
        self.layout = FlowLayout(self)
        self.layout.setSpacing(self.grid_spacing)

        # Populate grid
        self.populate_grid()

    def populate_grid(self):
        """Generate a grid from a list of sound effect objects"""
        # Clear existing widgets
        self.clear_grid()

        # Add widgets to the flow layout (will wrap automatically)
        for sound_effect_obj in self.items:
            item_widget = GridItem(sound_effect_obj, self.item_size)
            self.layout.addWidget(item_widget)

        # If no sounds are in the list
        if len(self.items) == 0:
            self.layout.addWidget(QLabel("No sounds found! Add some in the Sounds tab."))

    def clear_grid(self):
        """Remove all widgets from the grid"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

    def set_items(self, items):
        """Update the grid with new items"""
        self.items = items
        self.populate_grid()

