import os
import glob
import numpy as np

class LandsatThermalEngine:
    def __init__(self):
        # USGS Collection 2 Scale Factors for Surface Temperature
        self.scale_factor = 0.00341802
        self.add_offset = 149.0
        
    def raw_dn_to_lst(self, thermal_patch, mask_patch):
        """
        Decodes pre-scaled Landsat 8 Collection 2 Surface Temperature data 
        and refines it using localized emissivity corrections from your U-Net mask.
        """
        # Step 1: Decode the raw values into absolute Kelvin temperature
        # Filter out clear background/zero fill values first
        kelvin_grid = np.where(thermal_patch > 0, (thermal_patch * self.scale_factor) + self.add_offset, np.nan)

        # Step 2: Extract Emissivity (ε) dynamically based on your U-Net Mask layout
        # Class 0: Bare/Built-Up (ε ≈ 0.970), Class 1: Water (ε ≈ 0.991), Class 2: Veg (ε ≈ 0.985)
        emissivity = np.where(mask_patch == 1, 0.991, 
                     np.where(mask_patch == 2, 0.985, 0.970))

        # Step 3: Apply the physical Emissivity Correction to the surface layer
        # This adjusts the coarse top-of-atmosphere reading down to the true ground material properties
        lambda_val = 10.89  # Wavelength of Band 10
        rho = 14388         # h * c / σ constant
        
        corrected_lst_k = kelvin_grid / (1.0 + ((lambda_val * kelvin_grid / rho) * np.log(emissivity)))
        
        # Step 4: Convert to local Celsius scale
        lst_celsius = corrected_lst_k - 273.15
        
        return lst_celsius

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    thermal_dir = os.path.join(project_root, "data", "processed", "patches", "thermal")
    mask_dir = os.path.join(project_root, "data", "processed", "patches", "masks")
    
    thermal_patches = sorted(glob.glob(os.path.join(thermal_dir, "*.npy")))
    mask_patches = sorted(glob.glob(os.path.join(mask_dir, "*.npy")))
    
    if thermal_patches and mask_patches:
        engine = LandsatThermalEngine()
        
        sample_thermal = np.load(thermal_patches[0])
        sample_mask = np.load(mask_patches[0])
        
        celsius_grid = engine.raw_dn_to_lst(sample_thermal, sample_mask)
        
        print("\n✅ Thermal Calibration Engine Updated Successfully!")
        print(f"🌡️ Decoded Surface Temp range: {np.nanmin(celsius_grid):.1f}°C to {np.nanmax(celsius_grid):.1f}°C")
        print(f"📊 Mean Calculated Temperature: {np.nanmean(celsius_grid):.1f}°C\n")
    else:
        print("❌ Thermal or Mask patch folders appear empty.")