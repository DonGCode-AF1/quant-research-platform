def generate_targets(context, parameters):
    symbols = list(context.prices.columns)
    cash_buffer = float(parameters.get("cash_buffer", 0.0))
    weight = (1.0 - cash_buffer) / len(symbols)
    return {symbol: weight for symbol in symbols}
