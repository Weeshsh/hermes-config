#!/usr/bin/env python3
"""
Rendering helpers for Mermaid and SVG diagrams.
Used by mermaid-maker and svg-maker subagents.
"""

import subprocess
import tempfile
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional

VIZ_DIR = Path.cwd() / "viz"

def render_mermaid(source: str, output_name: str = "diagram") -> Tuple[bool, str, Optional[str]]:
    """
    Render Mermaid source to PNG using mmdc (Mermaid CLI).
    
    Args:
        source: Mermaid diagram source code
        output_name: Short name for the file (slug)
    
    Returns:
        (success, message, output_path)
    """
    VIZ_DIR.mkdir(exist_ok=True)
    
    if not output_name:
        output_name = "diagram"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = VIZ_DIR / f"viz-{output_name}-{timestamp}.png"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(source)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['mmdc', '-i', temp_file, '-o', str(output_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return False, f"mmdc error: {result.stderr}", None
        
        if not output_file.exists():
            return False, "Output file was not created", None
        
        return True, "Rendered successfully", str(output_file)
    
    except FileNotFoundError:
        return False, "mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli", None
    except subprocess.TimeoutExpired:
        return False, "Rendering timed out", None
    finally:
        os.unlink(temp_file)

def render_svg(source: str, output_name: str = "diagram") -> Tuple[bool, str, Optional[str]]:
    """
    Render SVG source to PNG using rsvg-convert or ImageMagick.
    
    Args:
        source: SVG source code
        output_name: Short name for the file (slug)
    
    Returns:
        (success, message, output_path)
    """
    VIZ_DIR.mkdir(exist_ok=True)
    
    if not output_name:
        output_name = "diagram"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = VIZ_DIR / f"viz-{output_name}-{timestamp}.png"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
        f.write(source)
        temp_file = f.name
    
    try:
        # Try rsvg-convert first (preferred)
        result = subprocess.run(
            ['rsvg-convert', '-o', str(output_file), temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and output_file.exists():
            return True, "Rendered successfully", str(output_file)
        
        # Fallback to ImageMagick convert
        result = subprocess.run(
            ['convert', temp_file, str(output_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return False, f"Rendering error: {result.stderr}", None
        
        if not output_file.exists():
            return False, "Output file was not created", None
        
        return True, "Rendered successfully", str(output_file)
    
    except FileNotFoundError:
        return False, "No rendering tool found. Install rsvg-convert or ImageMagick.", None
    except subprocess.TimeoutExpired:
        return False, "Rendering timed out", None
    finally:
        os.unlink(temp_file)

def validate_mermaid(source: str) -> Tuple[bool, str]:
    """
    Validate Mermaid syntax without rendering.
    
    Args:
        source: Mermaid diagram source code
    
    Returns:
        (is_valid, message)
    """
    if not source.strip():
        return False, "Empty source"
    
    # Basic checks
    if not any(source.startswith(prefix) for prefix in ['graph', 'sequenceDiagram', 'stateDiagram', 'erDiagram', 'mindmap', 'timeline', 'flowchart']):
        return False, "Unknown diagram type. Start with: graph, sequenceDiagram, stateDiagram, erDiagram, mindmap, timeline, or flowchart"
    
    return True, "Valid"

def validate_svg(source: str) -> Tuple[bool, str]:
    """
    Validate SVG syntax without rendering.
    
    Args:
        source: SVG source code
    
    Returns:
        (is_valid, message)
    """
    if not source.strip().startswith('<svg'):
        return False, "SVG must start with <svg>"
    
    if not source.strip().endswith('</svg>'):
        return False, "SVG must end with </svg>"
    
    return True, "Valid"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: render_helpers.py [mermaid|svg] <source_file> [output_name]")
        sys.exit(1)
    
    mode = sys.argv[1]
    source_file = sys.argv[2]
    output_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    with open(source_file, 'r') as f:
        source = f.read()
    
    if mode == "mermaid":
        valid, msg = validate_mermaid(source)
        if not valid:
            print(json.dumps({"error": msg}))
            sys.exit(1)
        success, msg, path = render_mermaid(source, output_name)
    elif mode == "svg":
        valid, msg = validate_svg(source)
        if not valid:
            print(json.dumps({"error": msg}))
            sys.exit(1)
        success, msg, path = render_svg(source, output_name)
    else:
        print(json.dumps({"error": f"Unknown mode: {mode}"}))
        sys.exit(1)
    
    if success:
        print(json.dumps({
            "success": True,
            "message": msg,
            "output": path,
            "filename": Path(path).name
        }))
    else:
        print(json.dumps({"error": msg}))
        sys.exit(1)
