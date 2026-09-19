"""Verify that all Gemini 2.0 references have been removed"""
import re
import os

def check_file(filepath):
    """Check if file contains Gemini 2.0 references"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for gemini-2.0 or 2.0-flash patterns
            patterns = [
                r'gemini-2\.0',
                r'2\.0-flash',
                r'gemini.*2\.0'
            ]
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content, re.IGNORECASE)
                if found:
                    matches.extend(found)
            return matches
    except Exception as e:
        return None

# Check key files
files_to_check = [
    'resume_parser.py',
    'gemini_rate_limiter.py',
    'debug_gemini.py'
]

print("="*70)
print("Verifying Gemini 2.0 Removal")
print("="*70)
print()

all_clean = True
for filepath in files_to_check:
    if os.path.exists(filepath):
        matches = check_file(filepath)
        if matches is None:
            print(f"[WARN] {filepath}: Could not read file")
        elif matches:
            print(f"[FAIL] {filepath}: Found {len(matches)} Gemini 2.0 reference(s)")
            for match in set(matches):
                print(f"   - {match}")
            all_clean = False
        else:
            print(f"[OK] {filepath}: No Gemini 2.0 references found")
    else:
        print(f"[WARN] {filepath}: File not found")

print()
print("="*70)
if all_clean:
    print("[SUCCESS] All Gemini 2.0 references have been removed!")
    print("   The system is now using Gemini 3.0")
else:
    print("[WARNING] Some Gemini 2.0 references still exist")
print("="*70)

