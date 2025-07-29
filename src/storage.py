import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class DataStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_posts(self, posts: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save posts to JSON file
        
        Args:
            posts: List of post dictionaries
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_posts_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(posts)} posts to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving posts: {e}")
            return ""
    
    def load_posts(self, filename: str) -> List[Dict]:
        """
        Load posts from JSON file
        
        Args:
            filename: Name of the file to load
        
        Returns:
            List of post dictionaries
        """
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                posts = json.load(f)
            
            print(f"Loaded {len(posts)} posts from {filepath}")
            return posts
            
        except Exception as e:
            print(f"Error loading posts from {filepath}: {e}")
            return []
    
    def save_digest(self, digest: str, filename: Optional[str] = None) -> str:
        """
        Save digest to markdown file
        
        Args:
            digest: Digest content as string
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_digest_{timestamp}.md"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(digest)
            
            print(f"Saved digest to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving digest: {e}")
            return ""
    
    def list_saved_files(self) -> Dict[str, List[str]]:
        """
        List all saved files in data directory
        
        Returns:
            Dictionary with file types as keys and lists of filenames as values
        """
        if not os.path.exists(self.data_dir):
            return {"json": [], "md": []}
        
        files = os.listdir(self.data_dir)
        json_files = [f for f in files if f.endswith('.json')]
        md_files = [f for f in files if f.endswith('.md')]
        
        return {
            "json": sorted(json_files, reverse=True),
            "md": sorted(md_files, reverse=True)
        }
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from data directory
        
        Args:
            filename: Name of file to delete
        
        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted {filepath}")
                return True
            else:
                print(f"File not found: {filepath}")
                return False
                
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")
            return False
    
    def get_file_info(self, filename: str) -> Optional[Dict]:
        """
        Get information about a saved file
        
        Args:
            filename: Name of the file
        
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                
                info = {
                    "filename": filename,
                    "filepath": filepath,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add content-specific info for JSON files
                if filename.endswith('.json'):
                    posts = self.load_posts(filename)
                    info["post_count"] = len(posts)
                    if posts:
                        subreddits = set(post.get('subreddit', '') for post in posts)
                        info["subreddits"] = list(subreddits)
                
                return info
            else:
                return None
                
        except Exception as e:
            print(f"Error getting file info for {filename}: {e}")
            return None