# Brave Search API Setup Guide

## Get Your API Key

1. Visit: **https://brave.com/search/api/**
2. Sign up for a free account
3. Copy your API key

**Free Tier Limits:**
- 2,000 queries per month
- Rate limited to reasonable usage
- No credit card required for free tier

## Configure Environment Variable

### Windows PowerShell (Permanent)

```powershell
# Set for current user (survives restarts)
[System.Environment]::SetEnvironmentVariable('BRAVE_API_KEY', 'YOUR_API_KEY_HERE', 'User')

# Verify it's set
$env:BRAVE_API_KEY
```

### Windows PowerShell (Current Session Only)

```powershell
# Set for current PowerShell session only
$env:BRAVE_API_KEY = "YOUR_API_KEY_HERE"

# Verify
$env:BRAVE_API_KEY
```

### Linux/macOS (Bash/Zsh)

```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
export BRAVE_API_KEY="YOUR_API_KEY_HERE"

# Apply changes
source ~/.bashrc  # or source ~/.zshrc

# Verify
echo $BRAVE_API_KEY
```

## Verify Configuration

After setting the environment variable, test it:

```powershell
cd V3
python -c "import os; print('Brave API Key:', 'Configured' if os.environ.get('BRAVE_API_KEY') else 'NOT SET')"
```

## Testing Web Search

Run the test script to verify Brave API is working:

```powershell
cd V3
python test_web_search.py
```

You should see:
- `Brave API: Found X results` in the logs (Brave is working)
- If you see `DuckDuckGo: Found X results`, it means Brave API key isn't configured and fallback is being used

## Fallback Behavior

**If Brave API fails** (no key, quota exceeded, or error):
- System automatically falls back to DuckDuckGo
- You'll see a warning in logs: `Brave API failed, falling back to DuckDuckGo`
- No disruption to user experience

## What's Changed (Tier 1 & 2 Improvements)

✅ **Brave Search API** (Primary)
- Cleaner results, better snippets
- 7 results instead of 3 (better odds of successful fetches)
- Official API, no rate limiting with your key

✅ **DuckDuckGo Fallback**
- Automatically used if Brave fails
- Same 7 results, graceful degradation

✅ **User-Agent Rotation**
- 10 different browser user agents
- Random selection per request
- Bypasses basic bot detection (reduces 403 errors)

✅ **Always Show Snippets**
- Every search result shows title + URL + snippet
- Full content appended when fetchable
- Status tracked: "fetched" or "snippet_only"

✅ **Better Error Handling**
- Gracefully handles blocked sites (403 errors)
- Continues with available results
- User sees snippets even when full content unavailable

## Expected Behavior

**Before (your error log):**
```
Found 3 results
ERROR: 2/3 blocked (403)
SUCCESS: 1/3 fetched
Result: 1 web source
```

**After (with improvements):**
```
Brave API: Found 7 results
ERROR: 3/7 blocked (403) - but snippets shown
SUCCESS: 4/7 fetched with full content
Result: 7 web sources (4 full + 3 snippet-only)
```

## Troubleshooting

**"BRAVE_API_KEY environment variable not set"**
- Solution: Follow Windows PowerShell steps above, restart terminal

**"Brave API failed, falling back to DuckDuckGo"**
- Possible causes: Invalid API key, quota exceeded, API service down
- Solution: Verify API key, check Brave API dashboard for quota

**Still getting 403 errors on some sites**
- Expected behavior: Some sites (like openai.com) have strong bot protection
- Solution: User-agent rotation helps but won't eliminate all 403s
- Workaround: Snippets always shown, so user still gets context

**"Both search methods failed"**
- Rare case: Both Brave and DuckDuckGo unavailable
- Solution: Check internet connection, try again later
