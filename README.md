# VA Medication Refill Identifier (MedsToOrder)

A small Windows app that reads a medication list downloaded from VA.gov / My HealtheVet and finds the prescriptions that actually need to be reordered: active, 0 refills left, not already being processed, and excluding non-VA items.

## Disclaimer

This is an independent personal project. It is **not** created, operated, endorsed by, or affiliated with the U.S. Department of Veterans Affairs (VA), My HealtheVet, or any government agency.

It is provided "as is," with no warranty of any kind, and is not a substitute for your official VA medication records or your VA provider's/pharmacist's guidance. Always confirm medications and refill status directly through VA.gov, My HealtheVet, or your VA pharmacy before making any medical decisions. Use at your own risk. The full disclaimer is also in the user guide.

## What's in this repo

- `MedsToOrder_GUI.py` — the app's source code (Python + tkinter)
- `MedsToOrder_App_UserGuide.docx` — a plain-language user guide: one-time install, step-by-step usage, troubleshooting
- `Distribute/` — the ready-to-run package for end users:
  - `Install_MedsToOrder.bat` — one-click installer (creates a `VAMEDS` folder, copies the app in, adds a Desktop shortcut)
  - `MedsToOrder.exe` — the compiled, standalone app (no Python required to run it)

## Installing (for end users)

See `MedsToOrder_App_UserGuide.docx` for the full walkthrough. Short version: download the `Distribute` folder, double-click `Install_MedsToOrder.bat`, and it sets everything up automatically.

## Building from source

Requires Python 3 with tkinter. To rebuild the standalone `.exe` after changing `MedsToOrder_GUI.py`:

```
pip install pyinstaller
pyinstaller --onefile --noconsole --name "MedsToOrder" MedsToOrder_GUI.py
```

## Privacy

This app runs entirely on your own computer. It reads the medication file you download yourself and never sends any data anywhere. No medication data, results, or logs are stored in this repository — see `.gitignore`.
