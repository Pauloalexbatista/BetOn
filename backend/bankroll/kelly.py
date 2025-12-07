def calculate_kelly_stake(
    bankroll: float,
    odds: float,
    probability: float,
    fraction: float = 0.5, # Default to Half-Kelly (safer)
    max_stake_percent: float = 0.05 # Never bet more than 5% of bank
) -> float:
    """
    Calculate optimal stake using the Kelly Criterion.
    
    Formula: f = (bp - q) / b
    where:
    - b = net odds (odds - 1)
    - p = probability of winning (0.0 to 1.0)
    - q = probability of losing (1 - p)
    
    Args:
        bankroll: Total current bankroll
        odds: Decimal odds (e.g. 2.0)
        probability: Estimated probability (e.g. 0.55 for 55%)
        fraction: Fraction of Kelly to use (e.g. 0.5 for Half Kelly)
        max_stake_percent: Hard cap on stake size (default 5%)
        
    Returns:
        Recommended stake amount (currency)
    """
    if odds <= 1:
        return 0.0
        
    b = odds - 1
    p = probability
    q = 1 - p
    
    # Kelly fraction
    f = (b * p - q) / b
    
    if f <= 0:
        return 0.0
        
    # Apply fractional Kelly (Safety)
    adjusted_f = f * fraction
    
    # Apply bankroll cap
    final_f = min(adjusted_f, max_stake_percent)
    
    # Calculate amount
    stake = bankroll * final_f
    
    return round(stake, 2)
