#!/bin/sh

# read in .env file config.env
set -a
source config.env
set +a

# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg

# Copy the app bundle to the dmg folder.
cp -r "dist/$APP_NAME.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/dmg/$APP_NAME.dmg" && rm "dist/dmg/$APP_NAME.dmg"
create-dmg \
  --volname "$APP_NAME" \
  --volicon "assets/dmg_logo.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "$APP_NAME.app" 175 120 \
  --hide-extension "$APP_NAME.app" \
  --app-drop-link 425 120 \
  "dist/dmg/$APP_NAME.dmg" \
  "dist/dmg/"