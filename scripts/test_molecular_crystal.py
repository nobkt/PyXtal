#!/usr/bin/env python3
"""
Test script for the molecular crystal generator

This script tests the generate_molecular_crystal.py script with various
example molecules to ensure it works correctly.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_molecule(xyz_file, output_dir, verbose=False):
    """Test crystal generation for a single molecule"""
    molecule_name = Path(xyz_file).stem
    output_file = os.path.join(output_dir, f"{molecule_name}_crystal.cif")
    
    cmd = [
        sys.executable, 
        "scripts/generate_molecular_crystal.py",
        xyz_file,
        "-o", output_file,
        "--max-attempts", "20"
    ]
    
    if verbose:
        cmd.append("--verbose")
    
    print(f"\n{'='*50}")
    print(f"Testing {molecule_name}...")
    print(f"Input: {xyz_file}")
    print(f"Output: {output_file}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {molecule_name} crystal generated")
            if verbose:
                print("STDOUT:", result.stdout)
            return True
        else:
            print(f"✗ FAILED: {molecule_name}")
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ TIMEOUT: {molecule_name} (>120s)")
        return False
    except Exception as e:
        print(f"✗ ERROR: {molecule_name} - {e}")
        return False

def main():
    """Main test function"""
    
    # Change to the PyXtal directory
    script_dir = Path(__file__).parent
    pyxtal_dir = script_dir.parent
    os.chdir(pyxtal_dir)
    
    print("Molecular Crystal Generator Test Suite")
    print("=====================================")
    
    # Find all XYZ files in examples/molecular_xyz
    xyz_dir = Path("examples/molecular_xyz")
    if not xyz_dir.exists():
        print(f"Error: {xyz_dir} directory not found")
        sys.exit(1)
    
    xyz_files = list(xyz_dir.glob("*.xyz"))
    if not xyz_files:
        print(f"Error: No XYZ files found in {xyz_dir}")
        sys.exit(1)
    
    print(f"Found {len(xyz_files)} molecules to test:")
    for xyz_file in xyz_files:
        print(f"  - {xyz_file.stem}")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as output_dir:
        print(f"\nOutput directory: {output_dir}")
        
        success_count = 0
        total_count = len(xyz_files)
        
        # Test each molecule
        for xyz_file in xyz_files:
            if test_molecule(str(xyz_file), output_dir, verbose=False):
                success_count += 1
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*50}")
        print(f"Total molecules tested: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Success rate: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print(f"\n❌ {total_count - success_count} test(s) failed")
            sys.exit(1)

if __name__ == "__main__":
    main()