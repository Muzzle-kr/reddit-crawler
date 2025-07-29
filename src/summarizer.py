import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class PostSummarizer:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def summarize_post(self, post: Dict, include_comments: bool = False, comments: List[Dict] = None) -> Dict:
        """
        Summarize a single Reddit post
        
        Args:
            post: Post dictionary from Reddit API
            include_comments: Whether to include comments in summary
            comments: List of comments if include_comments is True
        
        Returns:
            Dictionary with original post data plus summary
        """
        try:
            # Prepare content for summarization
            content_to_summarize = f"Title: {post['title']}\n"
            
            if post['content']:
                content_to_summarize += f"Content: {post['content']}\n"
            
            if include_comments and comments:
                content_to_summarize += "\nTop Comments:\n"
                for i, comment in enumerate(comments[:5], 1):
                    content_to_summarize += f"{i}. {comment['body'][:200]}...\n"
            
            # Create summary prompt
            prompt = f"""
            Please provide a concise summary of this Reddit post. Include:
            1. Main topic/subject
            2. Key points discussed
            3. Overall sentiment/tone
            4. Any important details or conclusions
            
            Post content:
            {content_to_summarize}
            
            Provide a summary in 2-3 sentences.
            """
            
            system_prompt = "You are a helpful assistant that summarizes Reddit posts concisely and accurately."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(full_prompt)
            summary = response.text.strip()
            
            # Add summary to post data
            post_with_summary = post.copy()
            post_with_summary['summary'] = summary
            post_with_summary['summarized_at'] = self._get_current_timestamp()
            
            return post_with_summary
            
        except Exception as e:
            print(f"Error summarizing post {post['id']}: {e}")
            post_with_summary = post.copy()
            post_with_summary['summary'] = "Error: Could not generate summary"
            return post_with_summary
    
    def summarize_multiple_posts(self, posts: List[Dict], include_comments: bool = False) -> List[Dict]:
        """
        Summarize multiple Reddit posts
        
        Args:
            posts: List of post dictionaries
            include_comments: Whether to include comments in summaries
        
        Returns:
            List of posts with summaries added
        """
        summarized_posts = []
        
        for post in posts:
            print(f"Summarizing post: {post['title'][:50]}...")
            
            comments = None
            if include_comments:
                # Note: You would need to fetch comments separately using RedditClient
                # This is left as a placeholder for integration
                comments = []
            
            summarized_post = self.summarize_post(post, include_comments, comments)
            summarized_posts.append(summarized_post)
        
        return summarized_posts
    
    def create_digest(self, posts: List[Dict]) -> str:
        """
        Create a digest summary of multiple posts
        
        Args:
            posts: List of summarized posts
        
        Returns:
            String containing the digest
        """
        try:
            if not posts:
                return "No posts to summarize."
            
            # Prepare content for digest
            digest_content = "Reddit Posts Summary:\n\n"
            
            for i, post in enumerate(posts[:10], 1):  # Limit to top 10 posts
                digest_content += f"{i}. **{post['title']}**\n"
                digest_content += f"   Subreddit: r/{post['subreddit']}\n"
                digest_content += f"   Score: {post['score']} | Comments: {post['num_comments']}\n"
                
                if 'summary' in post:
                    digest_content += f"   Summary: {post['summary']}\n"
                
                digest_content += f"   Link: {post['permalink']}\n\n"
            
            # Create overall summary
            prompt = f"""
            Based on these Reddit posts, provide an overall summary highlighting:
            1. Main themes or topics discussed
            2. Notable trends or patterns
            3. Most engaging or controversial posts
            4. Key insights or takeaways
            
            Posts data:
            {digest_content}
            
            Provide a comprehensive but concise summary in 3-4 paragraphs.
            """
            
            system_prompt = "You are a helpful assistant that creates insightful summaries of Reddit discussions."
            full_digest_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(full_digest_prompt)
            overall_summary = response.text.strip()
            
            final_digest = f"# Reddit Posts Digest\n\n"
            final_digest += f"**Generated on:** {self._get_current_timestamp()}\n\n"
            final_digest += f"## Overall Summary\n{overall_summary}\n\n"
            final_digest += f"## Individual Posts\n{digest_content}"
            
            return final_digest
            
        except Exception as e:
            print(f"Error creating digest: {e}")
            return f"Error creating digest: {e}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")