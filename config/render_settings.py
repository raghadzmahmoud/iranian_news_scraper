"""
Render-specific configuration optimizations
"""
import os

# Detect if running on Render
IS_RENDER = os.getenv("RENDER") == "true"

# Render-specific optimizations
if IS_RENDER:
    # Use smaller batch sizes on Render (limited resources)
    X_PLAYWRIGHT_BATCH_SIZE = 5  # Reduced from default
    
    # Longer delays between accounts (avoid rate limiting)
    X_DELAY_BETWEEN_ACCOUNTS = 5  # seconds
    
    # Shorter max scrolls (save resources)
    X_MAX_SCROLLS = 3
    
    # Fewer tweets per account
    X_MAX_TWEETS = 20
    
    # Longer timeouts for slower Render environment
    PLAYWRIGHT_TIMEOUT = 60000  # 60 seconds
    
    # Use single-process mode
    PLAYWRIGHT_SINGLE_PROCESS = True
    
    # Disable GPU (not available on Render)
    PLAYWRIGHT_DISABLE_GPU = True
    
    print("🎯 Running on Render - using optimized settings")
else:
    # Local development defaults
    X_PLAYWRIGHT_BATCH_SIZE = 10
    X_DELAY_BETWEEN_ACCOUNTS = 2
    X_MAX_SCROLLS = 5
    X_MAX_TWEETS = 50
    PLAYWRIGHT_TIMEOUT = 30000
    PLAYWRIGHT_SINGLE_PROCESS = False
    PLAYWRIGHT_DISABLE_GPU = False
