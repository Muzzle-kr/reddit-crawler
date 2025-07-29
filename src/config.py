import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for Reddit Crawler"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "reddit": {
                "default_limit": 10,
                "default_sort": "hot",
                "user_agent": "RedditCrawler/1.0"
            },
            "summarizer": {
                "model": "gemini-2.5-pro",
                "include_comments": False
            },
            "storage": {
                "data_directory": "data",
                "auto_save": True,
                "filename_format": "reddit_posts_%Y%m%d_%H%M%S"
            },
            "filters": {
                "min_score": 0,
                "min_comments": 0,
                "max_age_days": 30,
                "exclude_nsfw": True
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.default_config, config)
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
                return self.default_config.copy()
        else:
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        config_to_save = config or self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'reddit.default_limit')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to config value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def get_reddit_config(self) -> Dict[str, Any]:
        """Get Reddit API configuration"""
        return {
            'client_id': os.getenv('REDDIT_CLIENT_ID'),
            'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'user_agent': os.getenv('REDDIT_USER_AGENT', self.get('reddit.user_agent')),
            'default_limit': self.get('reddit.default_limit'),
            'default_sort': self.get('reddit.default_sort')
        }
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini API configuration"""
        return {
            'api_key': os.getenv('GEMINI_API_KEY'),
            'model': self.get('summarizer.model')
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration"""
        return {
            'data_directory': self.get('storage.data_directory'),
            'auto_save': self.get('storage.auto_save'),
            'filename_format': self.get('storage.filename_format')
        }
    
    def get_filter_config(self) -> Dict[str, Any]:
        """Get filtering configuration"""
        return {
            'min_score': self.get('filters.min_score'),
            'min_comments': self.get('filters.min_comments'),
            'max_age_days': self.get('filters.max_age_days'),
            'exclude_nsfw': self.get('filters.exclude_nsfw')
        }
    
    def validate_config(self) -> Dict[str, str]:
        """
        Validate configuration and return any issues
        
        Returns:
            Dictionary with validation errors (empty if all valid)
        """
        errors = {}
        
        # Check required environment variables
        reddit_config = self.get_reddit_config()
        if not reddit_config['client_id']:
            errors['reddit_client_id'] = "REDDIT_CLIENT_ID environment variable is required"
        if not reddit_config['client_secret']:
            errors['reddit_client_secret'] = "REDDIT_CLIENT_SECRET environment variable is required"
        
        gemini_config = self.get_gemini_config()
        if not gemini_config['api_key']:
            errors['gemini_api_key'] = "GEMINI_API_KEY environment variable is required for summarization"
        
        # Check numeric values
        if not isinstance(self.get('reddit.default_limit'), int) or self.get('reddit.default_limit') <= 0:
            errors['reddit_limit'] = "Reddit default limit must be a positive integer"
        
        
        return errors
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save_config()
        print("Configuration reset to defaults")
    
    def show_config(self):
        """Print current configuration"""
        print("Current Configuration:")
        print(json.dumps(self.config, indent=2))