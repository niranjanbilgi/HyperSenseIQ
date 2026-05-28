# HyperSenseIQ PTA/RTA Pipeline - Complete Integration
# End-to-end workflow: Import → Validate → Analyze → Report
# Production-ready for OIL India well data

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class HyperSenseIQPipeline:
    """Complete PTA/RTA analysis pipeline for well diagnostics"""
    
    def __init__(self, well_name, q=100, B=1.0, mu=1.0, h=50, phi=0.2, ct=1e-5, rw=0.3):
        self.well_name = well_name
        self.q = q
        self.B = B
        self.mu = mu
        self.h = h
        self.phi = phi
        self.ct = ct
        self.rw = rw
        
        self.time = None
        self.pressure = None
        self.permeability = None
        self.skin_factor = None
        self.validation = None
        self.analysis_complete = False
    
    # ========== STAGE 1: IMPORT & VALIDATE ==========
    def import_and_validate(self, csv_file):
        """Import pressure test data and validate quality"""
        print(f"\n{'='*70}")
        print(f"STAGE 1: DATA IMPORT & VALIDATION")
        print(f"{'='*70}")
        
        try:
            df = pd.read_csv(csv_file)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                print(f"✗ Error: Need 2+ numeric columns, found {len(numeric_cols)}")
                return False
            
            self.time = df[numeric_cols[0]].values
            self.pressure = df[numeric_cols[1]].values
            
            # Validate
            self.validation = self._validate_data()
            
            if not self.validation['is_valid']:
                print(f"✗ Data validation failed:")
                for issue in self.validation['issues']:
                    print(f"  - {issue}")
                return False
            
            print(f"✓ Data imported: {len(self.time)} data points")
            print(f"  Time range: {self.time[0]:.2f} to {self.time[-1]:.2f} hours")
            print(f"  Pressure range: {self.pressure.min():.2f} to {self.pressure.max():.2f} psi")
            print(f"  Quality score: {self.validation['quality_score']:.0f}%")
            
            return True
            
        except Exception as e:
            print(f"✗ Import error: {e}")
            return False
    
    def _validate_data(self):
        """Data quality validation"""
        issues = []
        quality_score = 100
        
        if np.any(self.time < 0):
            issues.append("Negative time values")
            quality_score -= 15
        
        if np.any(self.pressure < 0):
            issues.append("Negative pressure values")
            quality_score -= 15
        
        if not np.all(np.diff(self.time) > 0):
            issues.append("Non-monotonic time")
            quality_score -= 20
        
        if len(self.time) < 5:
            issues.append("Insufficient data points")
            quality_score -= 25
        
        pressure_diff = np.abs(np.diff(self.pressure))
        if len(pressure_diff) > 0 and np.max(pressure_diff) > 5 * np.mean(pressure_diff):
            issues.append("Potential outliers")
            quality_score -= 10
        
        return {
            'is_valid': quality_score >= 60,
            'quality_score': max(0, quality_score),
            'issues': issues
        }
    
    # ========== STAGE 2: HORNER ANALYSIS ==========
    def run_horner_analysis(self):
        """Execute Horner plot analysis"""
        print(f"\n{'='*70}")
        print(f"STAGE 2: HORNER PLOT ANALYSIS")
        print(f"{'='*70}")
        
        if self.time is None or self.pressure is None:
            print("✗ No data loaded. Run import_and_validate() first")
            return False
        
        # Stabilized pressure (last 3 points average)
        p_ws = np.mean(self.pressure[-3:])
        
        # Production time assumption (buildup test)
        tp = self.time[-1] * 10
        
        # Horner function
        delta_t = self.time - self.time[0]
        horner_x = np.log((tp + delta_t) / delta_t)
        horner_y = p_ws - self.pressure
        
        # Remove invalid values
        valid_idx = np.isfinite(horner_x) & np.isfinite(horner_y)
        horner_x = horner_x[valid_idx]
        horner_y = horner_y[valid_idx]
        
        if len(horner_x) < 2:
            print("✗ Insufficient valid data for analysis")
            return False
        
        # Linear regression
        coeffs = np.polyfit(horner_x, horner_y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Permeability calculation
        if slope != 0:
            self.permeability = (162.6 * self.q * self.B * self.mu) / (abs(slope) * self.h)
        else:
            self.permeability = 0
        
        # Skin factor calculation
        if self.permeability > 0 and slope != 0:
            self.skin_factor = 1.151 * (slope * np.log(self.permeability / (self.phi * self.mu * self.ct * self.rw**2)) - np.log(intercept / slope))
        else:
            self.skin_factor = 0
        
        # Store for plotting
        self.horner_x = horner_x
        self.horner_y = horner_y
        self.slope = slope
        self.intercept = intercept
        
        print(f"✓ Horner analysis complete:")
        print(f"  Permeability (k): {self.permeability:.2f} mD")
        print(f"  Skin Factor (s): {self.skin_factor:.2f}")
        print(f"  Slope: {slope:.4f}")
        print(f"  Intercept: {intercept:.4f}")
        
        self.analysis_complete = True
        return True
    
    # ========== STAGE 3: VISUALIZATION ==========
    def generate_horner_plot(self, output_file=None):
        """Generate professional Horner plot"""
        print(f"\n{'='*70}")
        print(f"STAGE 3: VISUALIZATION")
        print(f"{'='*70}")
        
        if not self.analysis_complete:
            print("✗ Run horner analysis first")
            return False
        
        if output_file is None:
            output_file = f"horner_plot_{self.well_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.figure(figsize=(13, 8))
        
        # Plot measured data
        plt.plot(self.horner_x, self.horner_y, 'bo', linewidth=2.5, markersize=11, 
                label='Measured Buildup Data', zorder=3)
        
        # Linear fit
        fit_line = self.slope * self.horner_x + self.intercept
        plt.plot(self.horner_x, fit_line, 'r--', linewidth=3, label='Horner Straight Line Fit', zorder=2)
        
        # Labels and formatting
        plt.xlabel('log[(tp + Δt)/Δt]', fontsize=14, fontweight='bold')
        plt.ylabel('p* - p (psi)', fontsize=14, fontweight='bold')
        plt.title(f'Horner Plot Analysis - {self.well_name}\nPermeability: {self.permeability:.2f} mD | Skin Factor: {self.skin_factor:.2f}', 
                 fontsize=15, fontweight='bold')
        
        plt.grid(True, alpha=0.4, linestyle='--', linewidth=1)
        plt.legend(fontsize=12, loc='best', framealpha=0.95)
        plt.tight_layout()
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Horner plot saved: {output_file}")
        
        plt.show()
        return True
    
    # ========== STAGE 4: REPORT GENERATION ==========
    def generate_report(self, output_file=None):
        """Generate comprehensive analysis report"""
        print(f"\n{'='*70}")
        print(f"STAGE 4: REPORT GENERATION")
        print(f"{'='*70}")
        
        if not self.analysis_complete:
            print("✗ Run analysis first")
            return False
        
        if output_file is None:
            output_file = f"PTA_Report_{self.well_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("HYPERSENSEIQ - PRESSURE TRANSIENT ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"WELL: {self.well_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("DATA QUALITY\n")
            f.write("-"*80 + "\n")
            f.write(f"Data Points: {len(self.time)}\n")
            f.write(f"Time Range: {self.time[0]:.2f} to {self.time[-1]:.2f} hours\n")
            f.write(f"Pressure Range: {self.pressure.min():.2f} to {self.pressure.max():.2f} psi\n")
            f.write(f"Quality Score: {self.validation['quality_score']:.0f}%\n\n")
            
            f.write("-"*80 + "\n")
            f.write("ANALYSIS RESULTS\n")
            f.write("-"*80 + "\n")
            f.write(f"Permeability (k): {self.permeability:.2f} mD\n")
            f.write(f"Skin Factor (s): {self.skin_factor:.2f}\n")
            f.write(f"Horner Slope: {self.slope:.4f}\n")
            f.write(f"Horner Intercept: {self.intercept:.4f}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("WELL PARAMETERS\n")
            f.write("-"*80 + "\n")
            f.write(f"Production Rate (q): {self.q} bbl/d\n")
            f.write(f"Formation Volume (B): {self.B}\n")
            f.write(f"Viscosity (μ): {self.mu} cp\n")
            f.write(f"Pay Thickness (h): {self.h} ft\n")
            f.write(f"Porosity (φ): {self.phi}\n")
            f.write(f"Wellbore Radius (rw): {self.rw} ft\n\n")
            
            f.write("-"*80 + "\n")
            f.write("INTERPRETATION\n")
            f.write("-"*80 + "\n")
            
            if self.permeability < 10:
                perm_interp = "Low permeability - tight formation, requires enhanced recovery"
            elif self.permeability < 50:
                perm_interp = "Moderate permeability - good production potential"
            else:
                perm_interp = "High permeability - excellent flow characteristics"
            
            f.write(f"Permeability: {perm_interp}\n\n")
            
            if self.skin_factor < -2:
                skin_interp = "Positive skin effect - well stimulated or has natural high-permeability zone"
            elif self.skin_factor < 0:
                skin_interp = "Slightly improved well performance from completion design"
            elif self.skin_factor < 5:
                skin_interp = "Minor formation damage - acceptable performance"
            else:
                skin_interp = "Significant formation damage - intervention recommended"
            
            f.write(f"Skin Factor: {skin_interp}\n\n")
            
            f.write("="*80 + "\n")
            f.write("HyperSenseIQ - See Beyond the Surface\n")
            f.write("="*80 + "\n")
        
        print(f"✓ Report generated: {output_file}")
        return True
    
    # ========== EXECUTIVE SUMMARY ==========
    def print_summary(self):
        """Print executive summary to console"""
        print(f"\n{'='*70}")
        print(f"EXECUTIVE SUMMARY - {self.well_name}")
        print(f"{'='*70}")
        print(f"Permeability:    {self.permeability:.2f} mD")
        print(f"Skin Factor:     {self.skin_factor:.2f}")
        print(f"Data Quality:    {self.validation['quality_score']:.0f}%")
        print(f"Data Points:     {len(self.time)}")
        print(f"Analysis Status: {'✓ COMPLETE' if self.analysis_complete else '✗ PENDING'}")
        print(f"{'='*70}\n")

# ========== MAIN PIPELINE ==========
if __name__ == "__main__":
    print("\n" + "="*70)
    print("HYPERSENSEIQ PTA/RTA PIPELINE - PRODUCTION DEPLOYMENT")
    print("="*70)
    
    # Initialize pipeline
    pipeline = HyperSenseIQPipeline(
        well_name="Assam-Tipam-Well-001",
        q=150,
        B=1.0,
        mu=0.8,
        h=45,
        phi=0.22,
        ct=5e-5,
        rw=0.35
    )
    
    # Stage 1: Import & Validate
    if pipeline.import_and_validate('sample_pressure_test.csv'):
        
        # Stage 2: Horner Analysis
        if pipeline.run_horner_analysis():
            
            # Stage 3: Visualization
            pipeline.generate_horner_plot()
            
            # Stage 4: Report
            pipeline.generate_report()
            
            # Summary
            pipeline.print_summary()
            
            print("✓ PIPELINE COMPLETE - Ready for OIL India deployment")
        else:
            print("✗ Analysis failed")
    else:
        print("✗ Import failed")