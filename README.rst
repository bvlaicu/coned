This is a utility package to interact with a ConEdison or Orange and Rockland Utility smart energy meter

The utility returns the latest meter read start time, end time, usage value and unit of measurement.

It requires the [coned.com](coned.com) or [oru.com](oru.com) credentials (email, password, MFA type, MFA secret) and the account uuid and meter number.
MFA type can be either `SECURITY_QUESTION` or `TOTP` (e.g. Google Authenticator).
For MFA Security Question, to set up your MFA secret (answer), log into coned.com (or oru.com), go to your profile and reset your 2FA method. When setting up 2FA again, there will be option to say you do not have texting on your phone. Select this and you should be able to use a security question instead.
For MFA TOTP, choose Google Authenticator, choose a device type and when presented with the QR code, click on "Can't scan?". It should provide you with the MFA secret.
To find the account uuid, log into coned.com (or oru.com) then use the browser developer tools to search for a GET request to `opower.com` with the word `utilityAccounts` that looks like: `https://cned.opower.com/ei/edge/apis/DataBrowser-v1/cws/utilities/cned/utilityAccounts/ACCOUNT_UUID/reads?aggregateType=bill&includeEnhancedBilling=false&includeMultiRegisterData=false`. (note the URL would have the word 'oru' for oru).
The meter number can be found on your utility bill.

Example usage::

    import asyncio
    from coned import Meter

    meter = Meter(
        email="myemail@email.com",
        password="myconedpassword",
        mfa_type=Meter.TOTP,
        mfa_secret="myconedmfasecret",
        account_uuid="cd754d65-5380-11e8-2307-2656615779bf",
        meter_number="703437804",
        site=Meter.CONED)

    event_loop = asyncio.get_event_loop()
    startTime, endTime, value, unit_of_measurement = event_loop.run_until_complete(meter.last_read())

