"""Terminal-bell sound effects."""
import sys


class Sound:
    def __init__(self, enabled: bool = True, volume: int = 1, output=sys.stdout):
        self.enabled = enabled
        self.volume = max(0, min(3, volume))
        self.output = output

    def _bell(self, n: int) -> None:
        if not self.enabled or self.volume <= 0:
            return
        self.output.write("\a" * n * self.volume)
        self.output.flush()

    def click(self) -> None:    self._bell(1)
    def hint(self) -> None:     self._bell(1)
    def undo(self) -> None:     self._bell(1)
    def reset(self) -> None:    self._bell(2)
    def capture(self) -> None:  self._bell(2)
    def extra(self) -> None:    self._bell(1)
    def win(self) -> None:      self._bell(4)
    def lose(self) -> None:     self._bell(2)
    def menu(self) -> None:     self._bell(1)
