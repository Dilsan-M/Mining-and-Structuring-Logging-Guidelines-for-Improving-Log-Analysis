# Hiring Test App - Project Documentation

## Project Overview

The **Hiring Test App** is a high-fidelity Flutter application developed as part of a technical assessment. It replicates a modern UI design for a stadium/sports facility booking platform, featuring a rich, responsive interface with advanced state management and clean architecture principles.

---

## Technical Stack

- **Framework**: [Flutter](https://flutter.dev/) (SDK ^3.10.4)
- **State Management**: [Flutter Bloc](https://pub.dev/packages/flutter_bloc) for predictable state transitions and separation of business logic from UI.
- **Navigation**: [GoRouter](https://pub.dev/packages/go_router) for declarative routing and deep linking support.
- **Networking**: [Dio](https://pub.dev/packages/dio) for optimized HTTP requests (infrastructure ready).
- **Dependency Injection**: [GetIt](https://pub.dev/packages/get_it) & [Injectable](https://pub.dev/packages/injectable) (infrastructure ready).
- **Data Modeling**: [Freezed](https://pub.dev/packages/freezed) & [JsonSerializable](https://pub.dev/packages/json_serializable) for immutable models and type-safe JSON parsing.
- **Typography**: [Google Fonts](https://pub.dev/packages/google_fonts) (Poppins).
- **Tooling**: [Build Runner](https://pub.dev/packages/build_runner) for code generation.

---

## Architecture

The project follow a **Clean Architecture** approach with a **Feature-First** structure. Each feature is self-contained, promoting maintainability and scalability.

### Directory Structure

```
lib/
├── core/                  # App-wide configurations and utilities
│   ├── extensions/        # BuildContext and other extensions
│   ├── logger/            # Structured logging implementation
│   ├── resources/         # Asset and constant managers
│   ├── routes/            # GoRouter configuration
│   └── theme/             # Theme tokens and ColorManager
├── features/              # Feature modules
│   ├── details/           # Stadium Details screen
│   │   ├── cubit/         # Bloc logic for details
│   │   ├── widgets/       # Feature-specific reusable widgets
│   │   └── details_page.dart
│   └── home/              # Home screen with stadium listings
│       ├── cubit/         # Bloc logic for home
│       ├── models/        # Data models (StadiumModel)
│       ├── widgets/       # Feature-specific reusable widgets
│       └── home_page.dart
├── shared/                # Global widgets used across features
└── main.dart              # Application entry point
```

---

## Core Features

### 1. Home Feed

- **Dynamic Header**: personalized greeting and search bar.
- **Hero Banner**: High-impact promotional section.
- **City Filtering**: Filter stadiums based on location using `HomeCubit`.
- **Stadium Listings**: Vertical list of stadiums with rating, distance, and price tags.

### 2. Stadium Details

- **Interactive Header**: Visual section with back navigation.
- **Sport Category Selection**: Ability to filter available sports at the venue.
- **Facility Info**: Detailed description and pricing.
- **Booking CTA**: Prominent "Book Now" action.

---

## Technical Highlights

### Structured Logging

The app uses a custom `AppLogger` based on the `logger` package, supporting tagged logs (e.g., `[BLOC]`, `[NETWORK]`) and pretty pricing in development.

### Responsive Design

Usage of `context.width`/`context.height` extensions ensures the UI scales correctly across different screen sizes.

### Immutability

All models are generated using `Freezed`, ensuring thread safety and easy state copying patterns (`state.copyWith`).

---

## Getting Started

### Prerequisites

- Flutter SDK installed.
- Android Studio / VS Code with Flutter extensions.

### Installation

1. Clone the repository.
2. Run `flutter pub get` to install dependencies.
3. Run `dart run build_runner build --delete-conflicting-outputs` to generate necessary files.
4. Launch the app using `flutter run`.

---

## Testing

Unit tests are located in the `test/` directory.
Example: `test/features/details/cubit/details_cubit_test.dart` verifies state transitions for the details screen.

Run tests using:

```bash
flutter test
```

---

## Submission Details

- **Screens Replicated**: Home and Details.
- **APK Path**: `build/app/outputs/flutter-apk/app-release.apk`
