This is a utility package to interact with an
ConEdison smart energy meter

ConEd calls the API of the ConEdison
smart energy meter to return the current energy usage.

It requires a meter number.
You can find your meter number fon your ConEdison bill.

Example usage::

    from coned import Meter

    meter = Meter("702238804")
    energy_usage_kWh = meter.last_read()

