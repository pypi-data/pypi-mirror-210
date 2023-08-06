import typing as t

class Tag:
    def __init__(self, name: str, version: t.Optional[str] = None):
        pass
    
    def __str__(self) -> str:
        pass
    
    def __repr__(self) -> str:
        pass
    
    def __eq__(self, other: Tag) -> bool:
        pass
    
    def __lt__(self, other: Tag) -> bool:
        pass
    
    def __hash__(self) -> int:
        pass
    
    @staticmethod
    def from_taglike(taglike: str) -> Tag:
        pass
    
    @staticmethod
    def from_str(tag_str: str) -> Tag:
        pass
    
