# utils/colors.py
# Predefined colors for UI elements
COLORS = {
    "primary": "#4CAF50",     # Green
    "secondary": "#2196F3",   # Blue
    "danger": "#F44336",      # Red
    "warning": "#FFC107",     # Amber
    "info": "#00BCD4",        # Cyan
    "light": "#F5F5F5",       # Light grey background
    "dark": "#212121",        # Dark text / background
    "white": "#FFFFFF",
    "black": "#000000",
}

# Gradient colors for class cards
CLASS_COLORS = [
    ("#6A11CB", "#2575FC"),   # Purple → Blue
    ("#FF512F", "#DD2476"),   # Red → Pink
    ("#11998E", "#38EF7D"),   # Teal → Green
    ("#FC466B", "#3F5EFB"),   # Pink → Blue
    ("#FDBB2D", "#22C1C3"),   # Yellow → Cyan
]

def get_class_color(index: int):
    """Return a gradient tuple for class card based on index."""
    return CLASS_COLORS[index % len(CLASS_COLORS)]
