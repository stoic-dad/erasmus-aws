#!/bin/bash

# Export draw.io diagrams to PNG and SVG with high quality
# This script provides instructions for exporting using draw.io desktop application

echo "🎨 Erasmus AWS Architecture Diagrams Export Guide"
echo "=================================================="
echo ""
echo "⚠️ Automated CLI export is not working. Please use the draw.io desktop application instead."
echo ""
echo "📥 Download draw.io desktop:"
echo "   https://www.diagrams.net/blog/diagrams-offline"
echo ""
echo "📋 Instructions:"

# Create export directory if it doesn't exist
EXPORT_DIR="architecture/exports"
mkdir -p "$EXPORT_DIR"

echo "1. Open draw.io desktop application"
echo "2. Open each diagram file:"
echo "   - architecture/erasmus-aws-architecture.drawio"
echo "   - architecture/erasmus-dataflow-diagram.drawio"
echo ""
echo "3. For each diagram, export as PNG:"
echo "   - File → Export As → PNG..."
echo "   - Enable 'Transparent Background'"
echo "   - Set 'Scale' to 2.0 or 300 DPI"
echo "   - Save to: $EXPORT_DIR/erasmus-aws-architecture-professional.png"
echo "   - Save to: $EXPORT_DIR/erasmus-dataflow-professional.png"
echo ""
echo "4. For each diagram, export as SVG:"
echo "   - File → Export As → SVG..."
echo "   - Enable 'Transparent Background'"
echo "   - Save to: $EXPORT_DIR/erasmus-aws-architecture-professional.svg"
echo "   - Save to: $EXPORT_DIR/erasmus-dataflow-professional.svg"
echo ""

echo "5. Verify exports exist in the $EXPORT_DIR directory"
echo ""
echo "✅ After export, update your documentation to reference these files:"
echo "   - README.md"
echo "   - README_FINAL.md"
echo "   - ARCHITECTURE_DETAILED.md"
echo "   - ARCHITECTURE_VISUAL.md"
echo ""
echo "📝 Example markdown to include diagrams:"
echo '```markdown'
echo '## Architecture'
echo '![AWS Architecture](architecture/exports/erasmus-aws-architecture-professional.png)'
echo ''
echo '## Data Flow'
echo '![Data Flow Diagram](architecture/exports/erasmus-dataflow-professional.png)'
echo '```'
echo ""
echo "🔍 For more details, see the architecture/EXPORT_INSTRUCTIONS.md file"
