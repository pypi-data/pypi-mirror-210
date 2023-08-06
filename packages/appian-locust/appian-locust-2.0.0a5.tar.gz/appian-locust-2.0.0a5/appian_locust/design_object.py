class DesignObject:
    """
    Class representing an Design Object
    """

    def __init__(self, name: str, opaque_id: str):
        self.name = name
        self.opaque_id = opaque_id

    def __str__(self) -> str:
        return f"DesignObject(name={self.name}, opaque_id={self.opaque_id})"

    def __repr__(self) -> str:
        return self.__str__()
