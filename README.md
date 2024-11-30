# Python-ADB-OCR

A tool for connecting to Android devices via ADB and performing screen capture and OCR text recognition.        
This tool can also be used as an automation tool for Android phones, providing basic functions such as tapping and swiping.

## Features

- Connect to an Android device over ADB.
- Capture the device screen.
- Perform OCR (Optical Character Recognition) on the screen capture (Using PaddleOcr).
- Execute touch and swipe actions on the device screen.
- Retrieve device information such as screen size and density.

## Prerequisites

- Python 3.7 or higher.
- Ensure that `adb` is installed and configured on your phone or emulator.
- Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Use Cases
```python
async def example():
    await adb_ocr.load(port=5555, host="localhost")
    await adb_ocr.set_screen_size(1080, 1920)
    await adb_ocr.set_screen_density(420)
    await adb_ocr.click(500, 500)
    await adb_ocr.swipe(100, 100, 500, 500, 200)
    await adb_ocr.go_back()
    ocr_results = await adb_ocr.get_screen_text()
    if ocr_results:
        for res in ocr_results:
            print(f"Text: {res.text}, Position: ({res.x}, {res.y})")

if __name__ == "__main__":
    asyncio.run(example())
```

## Keywords
Android ADB, screen capture, OCR, text recognition, touch actions, swipe actions, device information, screen size, screen density, Python, PaddleOCR, adb_shell, asyncio, OpenCV, numpy, psutil, loguru