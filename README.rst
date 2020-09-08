This is a utility package to interact with an ConEdison smart energy meter

Coned calls the APIs of the ConEdison smart energy meter to return the latest meter read value and unit of measurement.

It requires the coned.com credentials (email, password, MFA answer) and the account id and meter number.
To set up your MFA aswer, log ingto coned.com, go to your profile and reset your 2FA method. When setting up 2FA again, there will be option to say you do not have texting on your phone. Select this and you should be able to use a security question instead.
The account id and meter number can be found on your ConEdison bill.

Example usage::

    meter = Meter(
        email="myemail@email.com",
        password="myconedpassword",
        mfa_answer="myconedmfaanswer",
        account_id="cd754d65-5380-11e8-2307-2656615779bf",
        meter_id="703437804")

    value, unit_of_measurement = event_loop.run_until_complete(meter.last_read())

