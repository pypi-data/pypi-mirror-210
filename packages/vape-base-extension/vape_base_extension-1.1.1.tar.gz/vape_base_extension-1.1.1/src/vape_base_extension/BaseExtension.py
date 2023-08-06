from abc import ABC, abstractmethod
from typing import Any

class BaseExtension(ABC):
    def __init__(self, debug_mode: bool = False):
        # Note we set a debug mode for the class rather than as an 
        # argument/parameter for each method/function because that 
        # way it's less for extension authors to worry about
        self.debug_mode = debug_mode
    
    @abstractmethod
    def run(self) -> Any:
        """Runs the extension

        This is where the actual processing for the extension should be done

        Returns:
            Any: The output of the extension
        """

        pass

    @abstractmethod
    def finalize(self):
        """Finalizes the extension
        
        This is where any cleanup the extension needs to do, should be done
        """
        pass
    
    @classmethod
    @abstractmethod
    def create_from_user_input(cls, debug_mode: bool = False):
        """Creates an instance of the extension class from user input

        This is intended to provide a hook into the instantiation process, when/if needed.
        Rather than assuming parameters for a constructor, which should give extension authors more flexibility when needed.

        Args:
            debug_mode (bool, optional): If in debug mode (should show debugging messages, etc...). Defaults to False.
        """

        pass