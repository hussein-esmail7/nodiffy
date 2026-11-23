# nodiffy
An email notifier when the text of a website changes.

Pronounced "no diff eye" (name credit to [@JaydedCompanion](https://github.com/JaydedCompanion/)).
"Difference Notifications" -> "Diff Notify" -> "nodiffy"

## Introduction
The inspiration for this program was a more abstracted version of [rss-parsers](https://github.com/hussein-esmail7/rss-parsers) but eventually transitioned from an RSS feed to email notifications instead.

## Installation
1. `git clone https://github.com/hussein-esmail7/nodiffy`
2. `cd nodiffy `
3. Create your own `urls.yaml` file (see [Creating the `urls.yaml` file](#creating-the-urlsyaml-file)) that will store the URLs you want checked
4. Create your own `secrets.yaml` file (see [Creating the `secrets.yaml` file](#creating-the-secretsyaml-file)) that will store the email credentials this program sends emails from


### Requirements
The following Python libraries are required for this program to run properly.

```
pip install pydefuddle pyyaml yagmail
```

- [Python documentation for pydefuddle (Python implementation of Defuddle - extract and clean web content as Markdown)](https://pypi.org/project/pydefuddle/)
- [Python documentation for pyyaml (YAML parser and emitter for Python)](https://pypi.org/project/pyyaml/)
- [Python documentation for yagmail (Yet Another GMAIL client)](https://pypi.org/project/yagmail/)

### Creating the `urls.yaml` file
Below is the structure to tell the program what URLs to look for, and which email addresses to notify for each email.

```
targets:
  - url: WEBSITE_1_URL
    emails:
      - EMAIL_1@gmail.com

  - url: WEBSITE_2_URL
    emails:
      - EMAIL_1@gmail.com
      - EMAIL_2@gmail.com

  - url: WEBSITE_3_URL
    emails:
      - EMAIL_1@gmail.com
      - EMAIL_3@gmail.com

  - url: WEBSITE_4_URL
    emails:
      - EMAIL_2@gmail.com
```

### Creating the `secrets.yaml` file
Below is the structure to tell the program what the sender email credentials are to notify when a site changes.

The way the program is formatted, it requires an App Password from a Gmail email address. Instructions on how to create one:
1. Sign in to your Gmail Account
    - Open https://myaccount.google.com and log in.
 
2. Enable 2-Step Verification (if not already enabled)
    - Go to Security → 2-Step Verification.
    - Follow the instructions to set it up using your phone or authenticator app.
    - You cannot create an App Password without 2-Step Verification.

3. Create an App Password
    - Go to Security → App Passwords or visit: https://myaccount.google.com/apppasswords
    - You may need to re-enter your password.

4. Select the App and Device
    - Under “Select App” choose Other (Custom name).
    - Enter a descriptive name (ex. "nodiffy")
    - Click Generate.

5. Copy the App Password
    - Google will show a 16-character password.
    - Copy it and paste it into the `EMAIL_ADDRESS_FROM_PASSWORD` field in `secrets.yaml`.

6. Keep it secure
    - Treat the App Password like a secret — don’t share it.
    - You can revoke it anytime in your Google account if it’s no longer needed.

```
EMAIL_ADDRESS_FROM: "SENDER@gmail.com"
EMAIL_APPEARANCE: "What You Want the FROM Name to Show As"
EMAIL_ADDRESS_FROM_PASSWORD: "PASSWORD"
```

## Feedback
Got any feedback/ideas about this? Feel free to send me an email to [contact@husseinesmail.xyz](mailto:contact@husseinesmail.xyz). Would love to hear it!