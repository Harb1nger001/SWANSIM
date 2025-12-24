from dataclasses import dataclass

@dataclass
class ExogenousShock:
    type: str
    severity: float
    duration: int
    start_step: int

class ShockManager:
    def __init__(self):
        self.active_shocks = []
        
    def inject(self, shock: ExogenousShock):
        self.active_shocks.append(shock)
        
    def step(self, current_step):
        # Update active shocks, remove expired ones
        self.active_shocks = [s for s in self.active_shocks if current_step < s.start_step + s.duration]
        
    def apply_to_state(self, global_state):
        for shock in self.active_shocks:
            # Modify global state based on shock type and severity
            pass
