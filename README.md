# Uncluttered

> *Cooking, clarified.*

AI-powered recipe extraction for the terminal. Type a search query, get clean ingredients and steps. No ads, no life stories, no scrolling.

## Install

```bash
pip install uncluttered
```

Or install from source:

```bash
git clone https://github.com/brendaninnis/uncluttered-cli.git
cd uncluttered-cli
pip install -e .
```

## Setup

You'll need API keys from two services (both have free tiers):

1. **Gemini** (AI extraction): https://aistudio.google.com/apikey
2. **Tavily** (recipe search): https://tavily.com

Create a `.env` file in your working directory:
```shell
cp .env.example .env
```

Then use a text editor to update the file with your keys:
```
GEMINI_API_KEY=your-gemini-key
TAVILY_API_KEY=your-tavily-key
```

## Usage

### Search for recipes

```bash
uncluttered search "chocolate chip cookies"
```

This searches for recipes, extracts them using AI, saves them locally, and displays the top results ranked by trust score.

Options:
- `--fetch N` / `-f N`: Number of recipes to fetch (default: 5)
- `--display N` / `-d N`: Number of results to display (default: 3)

### View a saved recipe

```bash
uncluttered show classic-chocolate-chip-cookies
```

### List saved recipes

```bash
uncluttered list "chocolate chip cookies"
```

### Delete recipes

```bash
# Delete a single recipe by slug
uncluttered delete classic-chocolate-chip-cookies

# Delete all recipes for a search term
uncluttered delete --search-term "chocolate chip cookies"

# Delete all saved recipes
uncluttered delete --all
```

## Trust Scores

Each recipe gets a trust score (0-100) based on:

- **+20**: Exact measurements (grams, cups with precise amounts)
- **+10**: Known culinary source (Serious Eats, NYT Cooking, etc.)
- **+10**: Clear, detailed instructions with timing cues
- **+5**: Includes prep and cook times
- **+5**: Specifies exact yield/servings

Deductions for vague measurements, unclear instructions, or missing information.

Recipes are sorted by trust score, so the best ones appear first.

## Data Storage

Recipes are saved locally in `uncluttered.db` (SQLite) in your working directory.

## License

MIT
