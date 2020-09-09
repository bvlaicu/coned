This is a utility package to interact with an ConEdison smart energy meter

Coned calls the APIs of the ConEdison smart energy meter to return the latest meter read value and unit of measurement.

It requires the coned.com credentials (email, password, MFA type, MFA secret) and the account id and meter number.
MFA type can be either Security Question or TOTP (e.g. Google Authenticator).
For MFA Security Question, to set up your MFA secret (answer), log ingto coned.com, go to your profile and reset your 2FA method. When setting up 2FA again, there will be option to say you do not have texting on your phone. Select this and you should be able to use a security question instead.
For MFA TOTP, choose Google Authenticator, choose a device type and when presented with the QR code, click on "Can't scan?". It should provide you with the MFA secret.
The account id and meter number can be found on your Coned Utility bill.

Example usage::

    meter = Meter(
        email="myemail@email.com",
        password="myconedpassword",
        mfa_type="TOTP",
        mfa_secret="myconedmfasecret",
        account_id="cd754d65-5380-11e8-2307-2656615779bf",
        meter_id="703437804")

    value, unit_of_measurement = event_loop.run_until_complete(meter.last_read())

