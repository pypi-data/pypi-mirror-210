import pyrosex 

def dice(ctx, message):
    return hasattr(message, 'dice') and message.dice
pyrosex.filters.dice = dice
