from typing import Callable

class _BaseCounter:
    Event_OnCountChange = None # type: Callable[[int, int],None]
    '''user defined event callback, args: (oldCount, newCount)'''

    def __init__(self):
        self.count = 0

    def _Event_OnCountChange(self, oldCount:int, newCount: int):
        self.count = newCount
        if(self.Event_OnCountChange is not None):
            self.Event_OnCountChange(oldCount, newCount)

    def increment(self, count=1):
        self._Event_OnCountChange(self.count, self.count + count)
    
    def Update(self, newCount:int):
        self._Event_OnCountChange(self.count, newCount)


class CheckpointCounter(_BaseCounter):
    Event_OnCheckpointReached = None  # type: Callable[[int],None]
    def __init__(self, checkpointAmount: int):
        super().__init__()
        self._checkpointAmount = checkpointAmount
        self._nextCheckpoint = self._calculateNextCheckpoint()
        self._reachedCheckpoint = False

    def _Event_OnCountChange(self, oldCount: int, newCount: int):
        super()._Event_OnCountChange(oldCount, newCount)
        self._CheckpointControl()

    def _calculateNextCheckpoint(self):
        countLeftToNextCheckpoint = self._checkpointAmount - (self.count % self._checkpointAmount)
        return self.count + countLeftToNextCheckpoint

    def _CheckpointControl(self):
        if(self._nextCheckpoint <= self.count):
            self._reachedCheckpoint = True
            self._nextCheckpoint = self._calculateNextCheckpoint()
            if(self.Event_OnCheckpointReached is not None):
                self.Event_OnCheckpointReached(self.count)
        return

    def HasCheckpoint(self):
        if(self._reachedCheckpoint):
            self._reachedCheckpoint = False
            return True
        return False