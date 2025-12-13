# Fiber Maintenance Analytics - Mobile App

A React Native mobile application for accessing fiber maintenance analytics on Android and iOS.

## 📱 Features

- **Dashboard** - Overview of key metrics and performance
- **KPIs** - Interactive charts showing trends and engineer performance
- **Ticket Search** - Search tickets by number or customer name
- **Settings** - User profile, preferences, and logout

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+**: https://nodejs.org/
- **Expo CLI**: `npm install -g expo-cli`
- **EAS CLI** (for building): `npm install -g eas-cli`
- **Android Studio** (for Android development)
- **Xcode** (for iOS development, macOS only)

### Development

```bash
# Navigate to mobile app folder
cd mobile_app

# Install dependencies
npm install

# Start Expo development server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios
```

## 📦 Building APK for Android

### Option 1: Using EAS Build (Recommended)

EAS Build runs in the cloud - no local Android SDK needed!

```bash
# Login to Expo
npx eas-cli login

# Configure your project (first time only)
npx eas-cli build:configure

# Build APK for distribution
npm run build:apk
```

The APK will be available for download from Expo's servers.

### Option 2: Local Build

Requires Android Studio and SDK installed.

```bash
# Build Android bundle
npx expo prebuild --platform android

# Navigate to android folder
cd android

# Build APK
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk
```

## 🍎 Building for iOS

Requires macOS with Xcode installed.

```bash
# Build using EAS (cloud)
npx eas-cli build --platform ios

# Or local build
npx expo prebuild --platform ios
cd ios
xcodebuild -workspace FiberAnalytics.xcworkspace -scheme FiberAnalytics archive
```

## 🔧 Configuration

### API Server URL

Edit `src/config.js`:

```javascript
export const API_URL = 'http://100.83.80.26:8000';
```

### App Information

Edit `app.json`:

```json
{
  "expo": {
    "name": "Fiber Analytics",
    "version": "1.0.0",
    "android": {
      "package": "com.fireside.fiberanalytics"
    },
    "ios": {
      "bundleIdentifier": "com.fireside.fiberanalytics"
    }
  }
}
```

## 📁 Project Structure

```
mobile_app/
├── App.js                 # Main app entry point
├── app.json               # Expo configuration
├── package.json           # Dependencies
├── eas.json               # EAS Build configuration
│
├── src/
│   ├── api.js             # API client
│   └── config.js          # App configuration
│
├── screens/
│   ├── LoginScreen.js     # Login page
│   ├── HomeScreen.js      # Dashboard home
│   ├── KPIScreen.js       # KPI charts
│   ├── SearchScreen.js    # Ticket search
│   └── SettingsScreen.js  # Settings & profile
│
├── components/
│   ├── MetricCard.js      # Metric display card
│   └── GradeCard.js       # Grade display card
│
└── assets/
    ├── icon.png           # App icon (1024x1024)
    ├── splash.png         # Splash screen
    └── adaptive-icon.png  # Android adaptive icon
```

## 🎨 Theme

The app uses a dark theme matching the desktop application:

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#0f172a` | Main background |
| Card | `#1e293b` | Card backgrounds |
| Primary Orange | `#f97316` | Accents, buttons |
| Primary Purple | `#a855f7` | Gradients |
| Text Primary | `#ffffff` | Main text |
| Text Secondary | `#94a3b8` | Labels, hints |

## 🔄 Updating the App

### Over-the-Air Updates (Expo Updates)

For JavaScript-only changes, use OTA updates:

```bash
npx expo publish
```

Users will get the update on next app launch.

### Full App Update

For native changes (icons, permissions, etc.):

1. Update version in `app.json`
2. Rebuild using EAS Build
3. Distribute new APK/IPA

## 📲 Distribution

### Android

1. Build the APK: `npm run build:apk`
2. Download from Expo dashboard
3. Share APK directly or upload to:
   - Google Play Store
   - Firebase App Distribution
   - Direct download link

### iOS

1. Build the IPA: `npx eas-cli build --platform ios`
2. Distribute via:
   - TestFlight (for testing)
   - App Store (for production)
   - Ad-hoc distribution (Enterprise)

## 🐛 Troubleshooting

### "Network request failed"

1. Check API server is running
2. Verify API_URL in `src/config.js`
3. Ensure device/emulator can reach the server

### "Expo Go not working"

Some features require a development build:
```bash
npx eas-cli build --profile development --platform android
```

### Build fails on EAS

1. Check `eas.json` configuration
2. Verify Expo account credentials
3. Check build logs on expo.dev dashboard

## 📄 License

MIT License - Fireside Communications Kenya Ltd

## 👨‍💻 Author

**Joseph Nderitu**
- Email: josephnderito16@gmail.com
- GitHub: [@josephndex](https://github.com/josephndex)
