# This is a practical test script for the pygame-manager library.

import sys
import os
from manager.path import (
    create_path,
    get_projects_path,
    get_path,
    valid_project,
    _validate_name
)

# Test only the core path for now

try:
    print("[1] Testing get_projects_path...")
    projects_path = get_projects_path()
    assert os.path.exists(projects_path)
    print(f"    ✓ Projects path: {projects_path}")

    print("\n[2] Testing _validate_name with valid names...")
    _validate_name("my_project")
    _validate_name("test123")
    _validate_name("valid-name")
    print("    ✓ Valid names accepted")

    print("\n[3] Testing _validate_name with invalid names...")
    invalid_names = [
        ("", "empty string"),
        (".", "dot"),
        ("..", "double dot"),
        (".hidden", "starts with dot"),
        ("path/to/project", "contains slash"),
        ("path\\to\\project", "contains backslash"),
        (" spacey ", "has whitespace"),
    ]
    for name, reason in invalid_names:
        try:
            _validate_name(name)
            print(f"    ✗ Should have rejected: {reason}")
            sys.exit(1)
        except ValueError:
            pass
    print("    ✓ Invalid names rejected")

    print("\n[4] Testing get_path...")
    test_path = get_path("test_project")
    assert "test_project" in test_path
    assert not os.path.exists(test_path)
    print(f"    ✓ Got path: {test_path}")

    print("\n[5] Testing create_path...")
    created_path = create_path("test_project_created")
    assert os.path.exists(created_path)
    print(f"    ✓ Created path: {created_path}")

    print("\n[6] Testing valid_project on non-existent project...")
    assert not valid_project("nonexistent_project")
    print("    ✓ Non-existent project is invalid")

    print("\n[7] Testing valid_project on incomplete project...")
    assert not valid_project("test_project_created")
    print("    ✓ Incomplete project is invalid")

    print("\n[8] Cleaning up test directory...")
    import shutil
    if os.path.exists(created_path):
        shutil.rmtree(created_path)
    print("    ✓ Cleaned up")

    print("\n[PASS] All path tests completed successfully. No errors detected.")
    sys.exit(0)

except Exception as e:
    print(f"\n[FAIL] Test failed with exception: {e}")
    sys.exit(1)
