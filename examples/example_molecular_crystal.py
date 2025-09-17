#!/usr/bin/env python3
"""
Example script demonstrating programmatic use of the molecular crystal generator

This script shows how to use the molecular crystal generation functionality
from Python code rather than the command line.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the scripts directory to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "scripts"))

# Now we can import the functions from our script
from generate_molecular_crystal import read_xyz_file, generate_molecular_crystal, write_cif_file

def example_water_crystal():
    """Generate a water crystal programmatically"""
    
    print("Example 1: Water molecule crystal")
    print("-" * 40)
    
    # Path to water XYZ file
    xyz_file = script_dir / "examples" / "molecular_xyz" / "water.xyz"
    
    if not xyz_file.exists():
        print(f"Error: {xyz_file} not found")
        return
    
    try:
        # Read the molecule
        molecule = read_xyz_file(str(xyz_file))
        print(f"Loaded molecule: {molecule.composition}")
        print(f"Number of atoms: {len(molecule.species)}")
        
        # Generate crystal with custom parameters
        crystal = generate_molecular_crystal(
            molecule=molecule,
            num_mols=4,
            factor=1.15,
            space_groups=[1, 2, 14, 15],  # Only try specific space groups
            max_attempts=50,
            verbose=True
        )
        
        if crystal:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cif', delete=False) as f:
                output_file = f.name
            
            write_cif_file(crystal, output_file, verbose=True)
            print(f"\nCrystal saved to: {output_file}")
            
            return output_file
        else:
            print("Failed to generate crystal")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def example_custom_molecule():
    """Create a custom molecule and generate its crystal"""
    
    print("\n\nExample 2: Custom CO2 molecule crystal")
    print("-" * 40)
    
    # Create CO2 molecule programmatically
    import numpy as np
    from pymatgen.core.structure import Molecule
    
    # CO2 coordinates (linear molecule)
    species = ['C', 'O', 'O']
    coords = np.array([
        [0.0, 0.0, 0.0],   # Carbon at center
        [1.16, 0.0, 0.0],  # Oxygen 1
        [-1.16, 0.0, 0.0]  # Oxygen 2
    ])
    
    molecule = Molecule(species, coords)
    print(f"Created molecule: {molecule.composition}")
    
    try:
        # Generate crystal
        crystal = generate_molecular_crystal(
            molecule=molecule,
            num_mols=6,  # Try 6 molecules per unit cell
            factor=1.2,
            space_groups=[1, 14, 19, 62],  # Common space groups for CO2
            max_attempts=30,
            verbose=True
        )
        
        if crystal:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cif', delete=False) as f:
                output_file = f.name
            
            write_cif_file(crystal, output_file, verbose=True)
            print(f"\nCrystal saved to: {output_file}")
            
            return output_file
        else:
            print("Failed to generate crystal")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def example_batch_processing():
    """Process multiple molecules in batch"""
    
    print("\n\nExample 3: Batch processing of molecules")
    print("-" * 40)
    
    # Directory with XYZ files
    xyz_dir = script_dir / "examples" / "molecular_xyz"
    
    if not xyz_dir.exists():
        print(f"Error: {xyz_dir} not found")
        return
    
    xyz_files = list(xyz_dir.glob("*.xyz"))
    print(f"Found {len(xyz_files)} molecules to process")
    
    results = []
    
    for xyz_file in xyz_files:
        molecule_name = xyz_file.stem
        print(f"\nProcessing {molecule_name}...")
        
        try:
            # Read molecule
            molecule = read_xyz_file(str(xyz_file))
            
            # Generate crystal with optimized parameters for batch processing
            crystal = generate_molecular_crystal(
                molecule=molecule,
                num_mols=4,
                factor=1.1,
                space_groups=[1, 2, 14],  # Fast, common space groups only
                max_attempts=10,  # Quick attempts
                verbose=False  # Silent processing
            )
            
            if crystal:
                # Save crystal
                output_file = f"/tmp/{molecule_name}_crystal.cif"
                write_cif_file(crystal, output_file, verbose=False)
                
                results.append({
                    'molecule': molecule_name,
                    'success': True,
                    'space_group': crystal.group.number,
                    'volume': crystal.lattice.volume,
                    'file': output_file
                })
                print(f"  ✓ Success: SG {crystal.group.number}, Vol {crystal.lattice.volume:.1f} Ų")
            else:
                results.append({
                    'molecule': molecule_name,
                    'success': False
                })
                print(f"  ✗ Failed")
                
        except Exception as e:
            results.append({
                'molecule': molecule_name,
                'success': False,
                'error': str(e)
            })
            print(f"  ✗ Error: {e}")
    
    # Summary
    print(f"\nBatch processing summary:")
    print("-" * 25)
    successful = [r for r in results if r['success']]
    print(f"Successful: {len(successful)}/{len(results)}")
    
    for result in successful:
        print(f"  {result['molecule']}: SG {result['space_group']}, {result['volume']:.1f} Ų")
    
    return results

def main():
    """Run all examples"""
    
    print("Molecular Crystal Generator - Programmatic Examples")
    print("=" * 55)
    
    # Change to the PyXtal directory
    os.chdir(script_dir)
    
    # Run examples
    try:
        example_water_crystal()
        example_custom_molecule()
        example_batch_processing()
        
        print("\n" + "=" * 55)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()