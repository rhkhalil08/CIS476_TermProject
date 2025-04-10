#MORE UI COMPONENT HANDLING W/ MEDIATOR (used briefly in car listing)
class Mediator:
    def __init__(self):
        self.components = []

    def register(self, component):
        """Register a UI component to listen for updates."""
        self.components.append(component)

    def notify(self, sender, action, data=None):
        """Notify all registered components about an action."""
        for component in self.components:
            if component != sender:
                component.update(sender, action, data)
