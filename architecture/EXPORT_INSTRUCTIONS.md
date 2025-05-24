# 🎨 How to Export Your Professional AWS Architecture Diagrams

## 📋 Steps to Export High-Quality Diagrams

### Method 1: Using draw.io Desktop

1. **Download draw.io Desktop**:
   - Visit: https://github.com/jgraph/drawio-desktop/releases
   - Download the version for macOS

2. **Open your diagram files**:
   - `/Users/rohitsurya/erasmus-aws-1/architecture/erasmus-aws-architecture.drawio`
   - `/Users/rohitsurya/erasmus-aws-1/architecture/erasmus-dataflow-diagram.drawio`

3. **Export as PNG**:
   - File → Export As → PNG...
   - Set resolution to 300 DPI
   - Enable "Transparent Background"
   - Set "Zoom" to 100%
   - Click "Export"
   - Save as:
     - `erasmus-aws-architecture-professional.png`
     - `erasmus-dataflow-professional.png`

4. **Export as SVG** (for web documentation):
   - File → Export As → SVG...
   - Enable "Transparent Background"
   - Enable "Include a copy of my diagram"
   - Click "Export"
   - Save as:
     - `erasmus-aws-architecture-professional.svg`
     - `erasmus-dataflow-professional.svg`

### Method 2: Using Online draw.io

1. **Go to** https://app.diagrams.net/

2. **Open your diagram files**:
   - File → Open From → Device
   - Select each .drawio file

3. **Export following the same steps as Method 1**

## 🖼️ Where to Use These Diagrams

Once exported, update the following files with links to your new professional diagrams:

1. **README.md**: Replace the architecture diagram reference
2. **README_FINAL.md**: Replace the architecture diagram reference
3. **ARCHITECTURE_DETAILED.md**: Add the new professional diagrams
4. **ARCHITECTURE_VISUAL.md**: Add the new professional diagrams

## 📊 Diagram Explanation

### Main Architecture Diagram (`erasmus-aws-architecture-professional.png`)

This professional diagram shows:
- Official AWS service icons for all components
- Clear data flow between services
- Color-coded components by function
- Proper service naming and descriptions

### Data Flow Diagram (`erasmus-dataflow-professional.png`)

This diagram illustrates:
- Step-by-step processing of SBOMs
- Complete flow from upload to analysis results
- Integration with external APIs
- Monitoring and alerting flow

## 💡 Tips for Further Customization

- **Adjust Colors**: Modify the color scheme to match your branding
- **Add More Services**: Easily add additional AWS services using the AWS icon library
- **Update Flows**: Modify data flows as your architecture evolves
- **Add Security Layers**: Highlight IAM roles, encryption, and security groups

## 🔄 Keeping Diagrams Updated

As you enhance the Erasmus SBOM Risk Analyzer:
1. Open the original .drawio files
2. Make your changes
3. Re-export following the steps above
4. Update documentation links

---

These professional AWS architecture diagrams will greatly enhance your project documentation, providing clear visualization of your sophisticated SBOM risk analysis platform.
