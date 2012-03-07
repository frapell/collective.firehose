#! /bin/sh

I18NDOMAIN="collective.firehose"

# Synchronise the templates and scripts with the .pot.
# All on one line normally:
i18ndude rebuild-pot --pot collective/firehose/locales/${I18NDOMAIN}.pot \
    --create ${I18NDOMAIN} \
    collective/firehose

# Synchronise the resulting .pot with all .po files
for po in collective/firehose/locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot collective/firehose/locales/${I18NDOMAIN}.pot $po
done
