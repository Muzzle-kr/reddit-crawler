# Reddit Crawler

A Python tool to crawl Reddit posts and summarize them using AI.

## Features

- Fetch posts from specific subreddits
- Search posts across Reddit
- Generate AI-powered summaries using OpenAI
- Save and manage crawled data
- Create digest reports
- Configurable filtering and sorting
- Command-line interface

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables by copying `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your API credentials:
   - **Reddit API**: Get credentials from https://www.reddit.com/prefs/apps
   - **OpenAI API**: Get key from https://platform.openai.com/api-keys

## Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down your `client_id` (under the app name) and `client_secret`

## Usage

### Basic Commands

Fetch posts from a subreddit:
```bash
python src/main.py fetch python --limit 20 --sort hot
```

Search for posts:
```bash
python src/main.py search "machine learning" --subreddit MachineLearning --limit 15
```

Create digest from saved posts:
```bash
python src/main.py digest python_hot_20231128_143022.json
```

List saved files:
```bash
python src/main.py list-files
```

Show file information:
```bash
python src/main.py file-info python_hot_20231128_143022.json
```

### Configuration

View current configuration:
```bash
python src/main.py config
```

Update configuration:
```bash
python src/main.py set-config --key reddit.default_limit --value 25
python src/main.py set-config --key summarizer.model --value gpt-4
```

### Command Options

#### Fetch Command
- `--limit, -l`: Number of posts to fetch (default: 10)
- `--sort, -s`: Sort method (hot, new, top, rising)
- `--summarize/--no-summarize`: Generate summaries (default: yes)
- `--save/--no-save`: Save results to file (default: yes)
- `--comments/--no-comments`: Include comments in summary (default: no)

#### Search Command
- `--subreddit, -r`: Search within specific subreddit
- `--limit, -l`: Number of posts to fetch (default: 10)
- `--summarize/--no-summarize`: Generate summaries (default: yes)
- `--save/--no-save`: Save results to file (default: yes)

## Project Structure

```
reddit-crawler/
├── src/
│   ├── main.py           # CLI interface
│   ├── reddit_client.py  # Reddit API client
│   ├── summarizer.py     # AI summarization
│   ├── storage.py        # Data storage management
│   └── config.py         # Configuration management
├── data/                 # Saved posts and digests
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── config.json          # Configuration file (auto-created)
└── README.md           # This file
```

## Configuration Options

The tool creates a `config.json` file with the following options:

- **reddit.default_limit**: Default number of posts to fetch
- **reddit.default_sort**: Default sort method
- **summarizer.model**: OpenAI model to use for summaries
- **summarizer.max_tokens**: Maximum tokens for summaries
- **storage.data_directory**: Directory to save files
- **filters.min_score**: Minimum post score
- **filters.exclude_nsfw**: Exclude NSFW content

## Examples

### Fetch and summarize top posts from r/technology:
```bash
python src/main.py fetch technology --limit 10 --sort top --summarize
```

### Search for AI-related posts across all of Reddit:
```bash
python src/main.py search "artificial intelligence" --limit 20
```

### Create a digest from previously saved posts:
```bash
python src/main.py digest technology_top_20231128_143022.json
```

### Update configuration to use GPT-4:
```bash
python src/main.py set-config --key summarizer.model --value gpt-4
```

## API Costs

- Reddit API is free but has rate limits
- OpenAI API costs vary by model:
  - GPT-3.5-turbo: ~$0.002 per 1K tokens
  - GPT-4: ~$0.03 per 1K tokens

## Rate Limits

- Reddit API: 60 requests per minute
- OpenAI API: Varies by tier (usually 3-200 RPM)

The tool automatically handles basic rate limiting for Reddit API.

## Troubleshooting

1. **"PRAW" authentication error**: Check your Reddit API credentials in `.env`
2. **OpenAI API error**: Verify your OpenAI API key and check your billing status
3. **No posts found**: Try different search terms or check if the subreddit exists
4. **Permission denied**: Make sure the `data/` directory is writable

## License

MIT License - see LICENSE file for details.