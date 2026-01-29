"""Document clarity checking service.

Analyzes uploaded identity document images to determine
if they are clear enough for identification purposes.
Checks: file size, dimensions, blur detection, brightness.
"""

import os
from pathlib import Path
from typing import Tuple


def check_document_clarity(file_path: str) -> Tuple[str, str]:
    """Check if an uploaded document image is clear.

    Returns a tuple of (status, notes):
        status: 'clear', 'unclear', or 'pending'
        notes: human-readable description of the check results
    """
    full_path = Path(file_path.lstrip("/"))

    if not full_path.exists():
        return "pending", "File not found for clarity check"

    file_size = full_path.stat().st_size
    notes_parts = []

    # Check 1: File size (too small = likely low quality)
    if file_size < 50 * 1024:  # Less than 50KB
        notes_parts.append("Image file is very small (under 50KB), may be low quality")

    # Try to use PIL for advanced checks
    try:
        from PIL import Image
        import math

        img = Image.open(full_path)
        width, height = img.size

        # Check 2: Resolution
        if width < 400 or height < 300:
            notes_parts.append(f"Low resolution ({width}x{height}px). Minimum recommended: 400x300px")
        elif width >= 800 and height >= 600:
            notes_parts.append(f"Good resolution ({width}x{height}px)")
        else:
            notes_parts.append(f"Acceptable resolution ({width}x{height}px)")

        # Check 3: Brightness analysis
        if img.mode != "L":
            grayscale = img.convert("L")
        else:
            grayscale = img

        pixels = list(grayscale.getdata())
        avg_brightness = sum(pixels) / len(pixels) if pixels else 128

        if avg_brightness < 50:
            notes_parts.append(f"Image appears too dark (brightness: {avg_brightness:.0f}/255)")
        elif avg_brightness > 230:
            notes_parts.append(f"Image appears overexposed (brightness: {avg_brightness:.0f}/255)")
        else:
            notes_parts.append(f"Brightness is acceptable ({avg_brightness:.0f}/255)")

        # Check 4: Variance (blur detection - low variance = blurry)
        mean = avg_brightness
        variance = sum((p - mean) ** 2 for p in pixels) / len(pixels) if pixels else 0
        std_dev = math.sqrt(variance)

        if std_dev < 20:
            notes_parts.append(f"Image may be blurry or uniform (contrast: {std_dev:.1f})")
        elif std_dev < 40:
            notes_parts.append(f"Image contrast is acceptable ({std_dev:.1f})")
        else:
            notes_parts.append(f"Good image contrast ({std_dev:.1f})")

        img.close()

        # Determine overall status
        has_critical_issue = (
            (width < 400 or height < 300) or
            avg_brightness < 50 or
            avg_brightness > 230 or
            std_dev < 20
        )

        if has_critical_issue:
            status = "unclear"
        else:
            status = "clear"

    except ImportError:
        # PIL not available, do basic file size check only
        if file_size < 50 * 1024:
            status = "unclear"
            notes_parts.append("Image quality could not be fully verified (Pillow not installed)")
        elif file_size > 100 * 1024:
            status = "clear"
            notes_parts.append("File size suggests adequate quality. Install Pillow for detailed analysis")
        else:
            status = "pending"
            notes_parts.append("Install Pillow package for full image quality analysis")

    except Exception as e:
        status = "pending"
        notes_parts.append(f"Could not analyze image: {str(e)}")

    notes = ". ".join(notes_parts)
    return status, notes
