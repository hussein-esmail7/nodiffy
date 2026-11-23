# nodiffy
An email notifier when the text of a website changes.

Pronounced "no diff eye" (name credit to [@JaydedCompanion](https://github.com/JaydedCompanion/)).
"Difference Notifications" -> "Diff Notify" -> "nodiffy"

## Introduction
The inspiration for this program was a more abstracted version of [rss-parsers](https://github.com/hussein-esmail7/rss-parsers) but eventually transitioned from an RSS feed to email notifications instead.

## Requirements
```pip install pydefuddle pyyaml yagmail
```

## Creating the `urls.yaml` file
Below is the structure to tell the program what URLs to look for, and which email addresses to notify for each email.

```targets:
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

## Creating the `secrets.yaml` file
Below is the structure to tell the program what the sender email credentials are to notify when a site changes.

```EMAIL_ADDRESS_FROM: "SENDER@gmail.com"
EMAIL_APPEARANCE: "What You Want the FROM Name to Show As"
EMAIL_ADDRESS_FROM_PASSWORD: "PASSWORD"
```