#!/usr/bin/env python3

import click
from typing import List, Dict
from datetime import datetime, timedelta
import time

from reddit_client import RedditClient
from summarizer import PostSummarizer
from storage import DataStorage
from config import Config

@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """Reddit Crawler - Fetch and summarize Reddit posts"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config()
    ctx.obj['reddit'] = RedditClient()
    ctx.obj['summarizer'] = PostSummarizer()
    ctx.obj['storage'] = DataStorage()

@cli.command()
@click.argument('subreddit')
@click.option('--limit', '-l', default=10, help='Number of posts to fetch')
@click.option('--sort', '-s', type=click.Choice(['hot', 'new', 'top', 'rising']), default='hot', help='Sort method')
@click.option('--summarize/--no-summarize', default=True, help='Generate summaries')
@click.option('--save/--no-save', default=True, help='Save results to file')
@click.option('--comments/--no-comments', default=False, help='Include comments in summary')
@click.pass_context
def fetch(ctx, subreddit: str, limit: int, sort: str, summarize: bool, save: bool, comments: bool):
    """Fetch posts from a subreddit"""
    reddit = ctx.obj['reddit']
    summarizer = ctx.obj['summarizer']
    storage = ctx.obj['storage']
    
    click.echo(f"Fetching {limit} {sort} posts from r/{subreddit}...")
    
    posts = reddit.get_posts_from_subreddit(subreddit, limit, sort)
    
    if not posts:
        click.echo("No posts found.")
        return
    
    click.echo(f"Found {len(posts)} posts.")
    
    if summarize:
        click.echo("Generating summaries...")
        posts = summarizer.summarize_multiple_posts(posts, comments)
    
    if save:
        filename = f"{subreddit}_{sort}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        storage.save_posts(posts, filename)
    
    # Display results
    for i, post in enumerate(posts, 1):
        click.echo(f"\n{i}. {post['title']}")
        click.echo(f"   Score: {post['score']} | Comments: {post['num_comments']}")
        if 'summary' in post:
            click.echo(f"   Summary: {post['summary']}")
        click.echo(f"   URL: {post['permalink']}")

@cli.command()
@click.argument('query')
@click.option('--subreddit', '-r', help='Search within specific subreddit')
@click.option('--limit', '-l', default=10, help='Number of posts to fetch')
@click.option('--summarize/--no-summarize', default=True, help='Generate summaries')
@click.option('--save/--no-save', default=True, help='Save results to file')
@click.pass_context
def search(ctx, query: str, subreddit: str, limit: int, summarize: bool, save: bool):
    """Search for posts"""
    reddit = ctx.obj['reddit']
    summarizer = ctx.obj['summarizer']
    storage = ctx.obj['storage']
    
    search_location = f"r/{subreddit}" if subreddit else "all of Reddit"
    click.echo(f"Searching for '{query}' in {search_location}...")
    
    posts = reddit.search_posts(query, subreddit, limit)
    
    if not posts:
        click.echo("No posts found.")
        return
    
    click.echo(f"Found {len(posts)} posts.")
    
    if summarize:
        click.echo("Generating summaries...")
        posts = summarizer.summarize_multiple_posts(posts)
    
    if save:
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"search_{safe_query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        storage.save_posts(posts, filename)
    
    # Display results
    for i, post in enumerate(posts, 1):
        click.echo(f"\n{i}. {post['title']}")
        click.echo(f"   Subreddit: r/{post['subreddit']}")
        click.echo(f"   Score: {post['score']} | Comments: {post['num_comments']}")
        if 'summary' in post:
            click.echo(f"   Summary: {post['summary']}")
        click.echo(f"   URL: {post['permalink']}")

@cli.command()
@click.argument('filename')
@click.option('--create-digest/--no-digest', default=True, help='Create overall digest')
@click.pass_context
def digest(ctx, filename: str, create_digest: bool):
    """Create digest from saved posts"""
    storage = ctx.obj['storage']
    summarizer = ctx.obj['summarizer']
    
    posts = storage.load_posts(filename)
    
    if not posts:
        click.echo("No posts found in file.")
        return
    
    if create_digest:
        click.echo("Creating digest...")
        digest_content = summarizer.create_digest(posts)
        
        digest_filename = filename.replace('.json', '_digest.md')
        storage.save_digest(digest_content, digest_filename)
        
        click.echo(f"Digest created: {digest_filename}")
        click.echo("\n" + "="*50)
        click.echo(digest_content)

@cli.command()
@click.pass_context
def list_files(ctx):
    """List saved files"""
    storage = ctx.obj['storage']
    files = storage.list_saved_files()
    
    if files['json']:
        click.echo("Saved post files:")
        for f in files['json']:
            info = storage.get_file_info(f)
            if info:
                click.echo(f"  {f} ({info['post_count']} posts, {info['size_mb']} MB)")
    
    if files['md']:
        click.echo("\nDigest files:")
        for f in files['md']:
            info = storage.get_file_info(f)
            if info:
                click.echo(f"  {f} ({info['size_mb']} MB)")
    
    if not files['json'] and not files['md']:
        click.echo("No saved files found.")

@cli.command()
@click.argument('filename')
@click.pass_context
def file_info(ctx, filename: str):
    """Show information about a saved file"""
    storage = ctx.obj['storage']
    info = storage.get_file_info(filename)
    
    if info:
        click.echo(f"File: {info['filename']}")
        click.echo(f"Size: {info['size_mb']} MB")
        click.echo(f"Created: {info['created']}")
        click.echo(f"Modified: {info['modified']}")
        
        if 'post_count' in info:
            click.echo(f"Posts: {info['post_count']}")
            if 'subreddits' in info:
                click.echo(f"Subreddits: {', '.join(info['subreddits'])}")
    else:
        click.echo("File not found.")

@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    config = ctx.obj['config']
    config.show_config()
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        click.echo("\nConfiguration Issues:")
        for key, error in errors.items():
            click.echo(f"  {key}: {error}")

@cli.command()
@click.option('--key', help='Configuration key to set (e.g., reddit.default_limit)')
@click.option('--value', help='Value to set')
@click.pass_context
def set_config(ctx, key: str, value: str):
    """Set configuration value"""
    if not key or not value:
        click.echo("Both --key and --value are required")
        return
    
    config = ctx.obj['config']
    
    # Try to convert value to appropriate type
    if value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '').isdigit():
        value = float(value)
    
    config.set(key, value)
    click.echo(f"Set {key} = {value}")

if __name__ == '__main__':
    cli()