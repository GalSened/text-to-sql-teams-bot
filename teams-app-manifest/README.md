# Teams App Manifest

## Required Icons

You need to add two icon files to this directory:

1. **color.png** - 192x192 pixels
2. **outline.png** - 32x32 pixels

You can create these using:
- https://www.canva.com (free)
- Microsoft Paint
- Any image editor

### Suggested Icons:
- Use a database icon with SQL symbol
- Colors: Blue (#0078D4) for color icon
- Transparent background for outline icon

## How to Package for Teams

1. Add your icon files (color.png and outline.png) to this directory
2. Update `manifest.json` with your bot ID (or leave as-is for local dev)
3. Zip all three files:
   ```bash
   # In this directory
   zip -r TextToSQL.zip manifest.json color.png outline.png
   ```
4. In Teams, go to Apps → Manage your apps → Upload a custom app
5. Upload the TextToSQL.zip file

## Local Development (No Bot ID needed)

For local development with Bot Framework Emulator:
- You don't need a Microsoft App ID
- Just leave it blank in the code
- Use the emulator to test directly
