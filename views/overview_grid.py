from PySide6.QtWidgets import QWidget, QLabel

from views.flow_layout import FlowLayout
from views.grid_item import GridItem


class GridWidget(QWidget):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []

        # Grid settings
        self.grid_spacing = 10
        self.item_size = 100

        # Create layout
        self.layout = FlowLayout(self)
        self.layout.setSpacing(self.grid_spacing)

        # Populate grid
        self.populate_grid()

    def populate_grid(self):
        """Generate grid from list of strings"""
        # Clear existing widgets
        self.clear_grid()

        # Add widgets to the flow layout (will wrap automatically)
        for text in self.items:
            item_widget = GridItem(text, self.item_size)
            self.layout.addWidget(item_widget)

        # If no sounds are in the list
        if len(self.items) == 0:
            self.layout.addWidget(QLabel("No sounds found!"))

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

