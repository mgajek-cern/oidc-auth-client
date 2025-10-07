from abc import ABC, abstractmethod

class AuthStrategy(ABC):
    """Base class for authentication strategies"""
    
    @abstractmethod
    def login(self, page, username, password):
        """
        Execute login flow
        
        Args:
            page: Playwright page object
            username: User username
            password: User password
            
        Returns:
            None (page should be at redirect URL after login)
        """
        pass