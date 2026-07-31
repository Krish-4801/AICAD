import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------
# Colors & Typography
# ---------------------------------------------------------
COLOR_BG = RGBColor(15, 23, 42)        # Slate-900 (Deep background)
COLOR_CARD = RGBColor(30, 41, 59)      # Slate-800 (Card background)
COLOR_TEXT_MAIN = RGBColor(248, 250, 252) # Slate-50 (Heading/Body)
COLOR_TEXT_MUTED = RGBColor(148, 163, 184) # Slate-400 (Secondary text)
COLOR_ACCENT_PURPLE = RGBColor(168, 85, 247) # Purple-500 (Primary accent)
COLOR_ACCENT_TEAL = RGBColor(20, 184, 166)   # Teal-500 (Secondary accent)

FONT_HEADING = "Outfit"
FONT_BODY = "Inter"

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG

def add_header(slide, title, category="AICAD PIPELINE"):
    # Add category header (top tiny text)
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    cat_tf = cat_box.text_frame
    cat_tf.word_wrap = True
    cat_tf.margin_left = cat_tf.margin_top = cat_tf.margin_right = cat_tf.margin_bottom = 0
    p0 = cat_tf.paragraphs[0]
    p0.text = category.upper()
    p0.font.name = FONT_BODY
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ACCENT_TEAL
    
    # Add slide title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    title_tf = title_box.text_frame
    title_tf.word_wrap = True
    title_tf.margin_left = title_tf.margin_top = title_tf.margin_right = title_tf.margin_bottom = 0
    p1 = title_tf.paragraphs[0]
    p1.text = title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN

def create_card(slide, left, top, width, height, title, points, accent_color=None):
    # Create card rectangle shape
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_CARD
    shape.line.color.rgb = accent_color if accent_color else COLOR_CARD
    shape.line.width = Pt(1.5) if accent_color else Pt(0)
    
    # Add content textbox inside shape margins
    tb = slide.shapes.add_textbox(left + Inches(0.3), top + Inches(0.3), width - Inches(0.6), height - Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if title:
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = accent_color if accent_color else COLOR_TEXT_MAIN
        p.space_after = Pt(14)
        
    for i, pt_text in enumerate(points):
        if not title and i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = "• " + pt_text
        p.font.name = FONT_BODY
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(8)

# ---------------------------------------------------------
# Presentation Initialization
# ---------------------------------------------------------
def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Use blank slide layout
    blank_layout = prs.slide_layouts[6]
    
    # ---------------------------------------------------------
    # Slide 1: Title Slide (Sleek Gradient & Big Title)
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    
    # Add a beautiful glowing colored background accent line
    accent_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.15), Inches(7.5)
    )
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_ACCENT_PURPLE
    accent_bar.line.fill.background()
    
    # Title & Subtitle box
    tb = slide.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.5), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = "AICAD"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(64)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(6)
    
    p2 = tf.add_paragraph()
    p2.text = "Natural Language 3D CAD Generation"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_ACCENT_TEAL
    p2.space_after = Pt(20)
    
    p3 = tf.add_paragraph()
    p3.text = "Bridging generative AI and parametric boundary-representation modeling workflows. Speak in prose, engineer in solid code models, compile watertight STEP assets."
    p3.font.name = FONT_BODY
    p3.font.size = Pt(16)
    p3.font.color.rgb = COLOR_TEXT_MUTED
    
    # ---------------------------------------------------------
    # Slide 2: The Problem & Opportunity (Two-Column Cards)
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, "The Problem & Opportunity")
    
    # Column 1: The Problem
    create_card(
        slide, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        title="The Limitations Today",
        points=[
            "High Learning Curve: Traditional CAD programs require deep GUI modeling and coordinates training.",
            "Static AI Output: Existing AI 3D model generators export triangulated polygonal meshes (STL/OBJ).",
            "Non-Parametric: Meshes cannot be cleanly edited, resized, hollowed, or fitted with holes in professional engineering workflows.",
            "Industrial Mismatch: CNC, injection molding, and aerospace tooling require mathematically precise CAD formats (STEP/IGES)."
        ],
        accent_color=COLOR_ACCENT_PURPLE
    )
    
    # Column 2: The Opportunity
    create_card(
        slide, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        title="The AICAD Solution",
        points=[
            "Prose-to-CAD: Express structural intent in natural language description phrases.",
            "Deterministic Code: Translation of description into build123d Python script models rather than directly guessing vertices.",
            "Watertight Solid Compilation: Real-time compiling of standard geometries using OpenCascade CAD kernel.",
            "Direct B-Rep Exports: Produces standard STEP files as primary source of truth, retaining editable curves, faces, and design history."
        ],
        accent_color=COLOR_ACCENT_TEAL
    )

    # ---------------------------------------------------------
    # Slide 3: Architecture & Workflow (Process Flow Grid)
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, "System Architecture & Pipeline Flow")
    
    # Workflow card blocks
    blocks = [
        ("1. Input", ["User describes part via terminal or the interactive Web UI.", "Prompts can specify dimensions, holes, fillets, and constraints."], COLOR_ACCENT_TEAL),
        ("2. Translate", ["Gemini CLI Agent wakes up and parses the prompt.", "Generates verified Python script using the build123d library syntax."], COLOR_ACCENT_PURPLE),
        ("3. Compile", ["Subprocess runner calls OCP (OpenCascade) to build the solids.", "Validates volume and face watertight status, writing STEP."], COLOR_TEXT_MAIN),
        ("4. Export", ["Converts parent STEP to STL (3D Printing mesh), 3MF (metadata slicer), or DXF (2D Laser CNC).", "Loads details to Web UI."], COLOR_ACCENT_TEAL)
    ]
    
    width = Inches(2.7)
    height = Inches(4.5)
    y_pos = Inches(2.0)
    for i, (title, points, color) in enumerate(blocks):
        x_pos = Inches(0.8) + i * Inches(2.95)
        create_card(slide, x_pos, y_pos, width, height, title, points, color)

    # ---------------------------------------------------------
    # Slide 4: Core CAD Engine: build123d
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, "Under the Hood: build123d & OpenCascade")
    
    # Card 1: OpenCascade & OCP
    create_card(
        slide, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        title="OpenCascade Technology (OCP)",
        points=[
            "Industrial standard B-Rep (Boundary Representation) geometric kernel.",
            "Calculates exact curves, arcs, splines, and boolean cuts programmatically.",
            "Provides solid geometry structures with high tolerances and precision.",
            "Guarantees that files export cleanly to SolidWorks, Fusion 360, and CNC tooling."
        ],
        accent_color=COLOR_ACCENT_PURPLE
    )
    
    # Card 2: build123d API Strengths
    create_card(
        slide, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        title="Why build123d?",
        points=[
            "High-level Python wrapper with clear, readable CAD modeling semantics.",
            "Supports algebraic operators (extrude, revolve, loft, sweep, sweep_path).",
            "Coordinate system helper frames allow easy hole alignments and relative offsets.",
            "Ideal for AI code generation due to consistent structures, object-oriented APIs, and descriptive docstrings."
        ],
        accent_color=COLOR_ACCENT_TEAL
    )

    # ---------------------------------------------------------
    # Slide 5: Interactive Web User Interface
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, "Interactive Web User Interface")
    
    # Features text card on the left
    create_card(
        slide, Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.8),
        title="A Modern Browser Experience",
        points=[
            "Live Progress Tracker: Real-time visibility into agent states (Queued -> Coding -> Compiling -> Rendering -> Completed).",
            "Interactive WebGL Viewer: Three.js integration displays converted STL models directly in the viewport. Drag to rotate, scroll to zoom, right-click to pan.",
            "Code & Render Side-by-Side: View the compiled python source code and the rendered rasterized snapshot side-by-side.",
            "Direct Artifact Downloads: Single-click download links for industrial-grade STEP files, STL meshes, and raw python builders.",
            "Status Log Streaming: Raw compilation stderr/stdout output streams for instant developers debugging."
        ],
        accent_color=COLOR_ACCENT_TEAL
    )
    
    # Visual container on the right (Placeholder / Image)
    # Try to load engine cylinder image or request screenshot if available
    img_path = None
    for p in ["engine_cylinder_20260605T101149Z.png", "requests/req_1783352682/snapshot_20260706T155103Z.png"]:
        if os.path.exists(p):
            img_path = p
            break
            
    if img_path:
        # Create card backing for image
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.8), Inches(5.3), Inches(4.8)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_CARD
        shape.line.fill.background()
        # Add actual image inside card bounds
        slide.shapes.add_picture(img_path, Inches(7.35), Inches(2.2), Inches(5.0), Inches(4.0))
    else:
        create_card(
            slide, Inches(7.2), Inches(1.8), Inches(5.3), Inches(4.8),
            title="UI Visualization Engine",
            points=[
                "[Screenshot Unavailable]",
                "Responsive front-end written in Vanilla HTML, CSS, and JS.",
                "Integrates with lightweight HTTP service server.py API endpoints.",
                "Uses Prism.js for syntax highlighted Python previews."
            ],
            accent_color=COLOR_ACCENT_PURPLE
        )

    # ---------------------------------------------------------
    # Slide 6: Case Studies & Examples (Show real outputs)
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, "Case Studies & Compiled Examples")
    
    # Left Card: Example List
    create_card(
        slide, Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.8),
        title="Parametric Models Produced",
        points=[
            "Engine Cylinder (Complex Parametric solid):\n- A central piston cylinder chamber with radial cooling fins.\n- Bolt circle attachment mounting flanges.",
            "L-Bracket (Structural attachment):\n- 50mm leg lengths, 4mm thick solid face.\n- Auto-positioned M4 countersunk holes.",
            "M5 Hex Nut (Mechanical standard):\n- Exact 10mm flat-to-flat distance hex profile.\n- Inner clearance cylinder with thread tolerancing."
        ],
        accent_color=COLOR_ACCENT_PURPLE
    )
    
    # Right Column: Multi-Image visual display if available
    img_nut = "requests/req_1783352075/snapshot_20260706T153605Z.png"
    img_bracket = "requests/req_1783352682/snapshot_20260706T155103Z.png"
    
    if os.path.exists(img_nut) and os.path.exists(img_bracket):
        # Nut Image Card
        shape_nut = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.8), Inches(2.55), Inches(4.8)
        )
        shape_nut.fill.solid()
        shape_nut.fill.fore_color.rgb = COLOR_CARD
        shape_nut.line.fill.background()
        
        slide.shapes.add_picture(img_nut, Inches(7.3), Inches(2.3), Inches(2.35), Inches(2.35))
        
        tb_nut = slide.shapes.add_textbox(Inches(7.2), Inches(4.8), Inches(2.55), Inches(1.5))
        tf_nut = tb_nut.text_frame
        tf_nut.word_wrap = True
        p_nut = tf_nut.paragraphs[0]
        p_nut.alignment = PP_ALIGN.CENTER
        p_nut.text = "Generated M5 Hex Nut"
        p_nut.font.name = FONT_HEADING
        p_nut.font.size = Pt(13)
        p_nut.font.bold = True
        p_nut.font.color.rgb = COLOR_ACCENT_TEAL
        
        # Bracket Image Card
        shape_brac = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.95), Inches(1.8), Inches(2.55), Inches(4.8)
        )
        shape_brac.fill.solid()
        shape_brac.fill.fore_color.rgb = COLOR_CARD
        shape_brac.line.fill.background()
        
        slide.shapes.add_picture(img_bracket, Inches(10.05), Inches(2.3), Inches(2.35), Inches(2.35))
        
        tb_brac = slide.shapes.add_textbox(Inches(9.95), Inches(4.8), Inches(2.55), Inches(1.5))
        tf_brac = tb_brac.text_frame
        tf_brac.word_wrap = True
        p_brac = tf_brac.paragraphs[0]
        p_brac.alignment = PP_ALIGN.CENTER
        p_brac.text = "Generated L-Bracket"
        p_brac.font.name = FONT_HEADING
        p_brac.font.size = Pt(13)
        p_brac.font.bold = True
        p_brac.font.color.rgb = COLOR_ACCENT_PURPLE
        
    elif img_path:
        # Fallback to single image
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.8), Inches(5.3), Inches(4.8)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_CARD
        shape.line.fill.background()
        slide.shapes.add_picture(img_path, Inches(7.35), Inches(2.2), Inches(5.0), Inches(4.0))
    else:
        create_card(
            slide, Inches(7.2), Inches(1.8), Inches(5.3), Inches(4.8),
            title="Generated Samples",
            points=[
                "Models are fully parsed by step/inspect tool scripts.",
                "Geometric features verified programmatically.",
                "Exported STL structures loaded directly to Three.js viewer."
            ],
            accent_color=COLOR_ACCENT_TEAL
        )

    # ---------------------------------------------------------
    # Slide 7: Future Vision & Roadmap
    # ---------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, "Conclusion & Future Roadmap")
    
    # Left Column: Key Achievements
    create_card(
        slide, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        title="Project Achievements",
        points=[
            "Prototyped a complete Text-to-CAD translation pipeline combining LLMs with build123d.",
            "Established automated execution, inspection, and format conversion workflows.",
            "Designed and implemented a responsive, real-time web interface.",
            "Created a zero-install local environment powered by uv package manager."
        ],
        accent_color=COLOR_ACCENT_PURPLE
    )
    
    # Right Column: Roadmap
    create_card(
        slide, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        title="The Road Ahead",
        points=[
            "Constraint-Based Assemblies: Move from individual solid parts to complex mechanical assemblies with mated joints.",
            "Fine-Tuned Modeling Agents: Train specialized models on standard libraries and engineering handbook databases.",
            "Automated Technical Blueprints: Generate standard 2D technical drawings with automatic dimension callouts in DXF.",
            "CAD Integrations: Directly plug output scripts into professional CAD platforms (FreeCAD, Fusion 360, Onshape)."
        ],
        accent_color=COLOR_ACCENT_TEAL
    )
    
    # Save the presentation to workspace root and web folder
    filename = "presentation.pptx"
    prs.save(filename)
    print(f"Presentation successfully saved to {filename}")
    
    web_filename = os.path.join("web", "presentation.pptx")
    prs.save(web_filename)
    print(f"Presentation copy saved to {web_filename}")

if __name__ == "__main__":
    main()
