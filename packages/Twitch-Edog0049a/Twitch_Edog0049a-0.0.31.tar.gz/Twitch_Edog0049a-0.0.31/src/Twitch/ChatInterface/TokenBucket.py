from datetime import timedelta,datetime
from typing import Optional
class TokenBucket:
    def __init__(self, maxToken: Optional[int] = 20, timePeriod: Optional[int] = 30) -> None:
        self._maxToken: int = maxToken
        self._timePeriod: int = timePeriod
        self._nextFill = datetime.now()
        self._bucket = 0
        
    @property
    def usetoken(self) -> bool:
        self._fill_Bucket()
        if self._isfull:
            self._nextFill = datetime.now() + timedelta(seconds=self._timePeriod)
        if self._bucket > 0:
            self._bucket -= 1
            return True
        return False

    @property
    def maxToken(self) -> int:
        return self._maxToken
    
    @maxToken.setter
    def maxToken(self, tokens: int) -> None:
        self._maxToken = tokens

    @property
    def timePeriod(self)-> int:
        return self._timePeriod
    
    @timePeriod.setter
    def timePeriod(self, seconds: int) -> None:
        self._timePeriod = seconds

    @property
    def _isfull(self) -> bool:
        return self._bucket == self.maxToken
    
    @property
    def isEmpty(self) -> bool:
        self._fill_Bucket()
        return self._bucket == 0
    
    def _fill_Bucket(self) -> None:
        if datetime.now() > self._nextFill:
            self._bucket = self.maxToken
        
        

