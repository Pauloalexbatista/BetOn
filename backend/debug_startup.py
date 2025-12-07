import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting imports...")
try:
    from api.routes import analysis
    print("Analysis imported")
    from api.routes import bankroll
    print("Bankroll imported")
    from api.routes import strategies_routes
    print("Strategies Routes imported")
    from api.routes import signals
    print("Signals imported")
    from api.routes import matches
    print("Matches imported")
    from api.routes import bets
    print("Bets imported")
    from api.routes import system
    print("System imported")
    print("ALL IMPORTS SUCCESSFUL")
except Exception as e:
    print("IMPORT FAILED")
    traceback.print_exc()
