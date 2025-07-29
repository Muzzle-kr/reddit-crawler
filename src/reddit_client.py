import praw
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class RedditClient:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'RedditCrawler/1.0 by /u/ZorbaHan')
        )
    
    def get_posts_from_subreddit(self, subreddit_name: str, limit: int = 10, sort_by: str = 'hot') -> List[Dict]:
        """
        Fetch posts from a specific subreddit
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Number of posts to fetch
            sort_by: Sort method ('hot', 'new', 'top', 'rising')
        
        Returns:
            List of post dictionaries
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            if sort_by == 'hot':
                posts = subreddit.hot(limit=limit)
            elif sort_by == 'new':
                posts = subreddit.new(limit=limit)
            elif sort_by == 'top':
                posts = subreddit.top(limit=limit)
            elif sort_by == 'rising':
                posts = subreddit.rising(limit=limit)
            else:
                posts = subreddit.hot(limit=limit)
            
            post_list = []
            for post in posts:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.selftext,
                    'url': post.url,
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'author': str(post.author) if post.author else '[deleted]',
                    'permalink': f"https://reddit.com{post.permalink}",
                    'subreddit': subreddit_name
                }
                post_list.append(post_data)
            
            return post_list
            
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def search_posts(self, query: str, subreddit_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search for posts across Reddit or within a specific subreddit
        
        Args:
            query: Search query
            subreddit_name: Optional subreddit to search within
            limit: Number of posts to fetch
        
        Returns:
            List of post dictionaries
        """
        try:
            if subreddit_name:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.search(query, limit=limit)
            else:
                posts = self.reddit.subreddit('all').search(query, limit=limit)
            
            post_list = []
            for post in posts:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.selftext,
                    'url': post.url,
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'author': str(post.author) if post.author else '[deleted]',
                    'permalink': f"https://reddit.com{post.permalink}",
                    'subreddit': post.subreddit.display_name
                }
                post_list.append(post_data)
            
            return post_list
            
        except Exception as e:
            print(f"Error searching posts: {e}")
            return []
    
    def get_post_comments(self, post_id: str, limit: int = 10) -> List[Dict]:
        """
        Get comments for a specific post
        
        Args:
            post_id: Reddit post ID
            limit: Number of top comments to fetch
        
        Returns:
            List of comment dictionaries
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body'):
                    comment_data = {
                        'id': comment.id,
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'author': str(comment.author) if comment.author else '[deleted]'
                    }
                    comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            return []