"""Streamlit frontend for OCR MD Pipeline."""

import streamlit as st
from pathlib import Path
import tempfile
import json
from datetime import datetime
import sys
import os

# Configure OCR cache BEFORE any imports that use it
temp_cache = Path(tempfile.gettempdir()) / "doccomparison_ocr_cache"
temp_cache.mkdir(parents=True, exist_ok=True)
os.environ["RAPIDOCR_HOME"] = str(temp_cache)
os.environ["RAPIDOCR_MODELS_DIR"] = str(temp_cache / "models")
os.environ["HF_HOME"] = str(temp_cache / "huggingface")

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import pipeline functions
from src.app.config import resolve_output, OUTPUT_DIR, get_env
from src.app.converter import convert_to_markdown
from src.app.text_utils import remove_arabic_chars, remove_duplicate_lines
from src.app.compare import compare_files
from src.app.export import markdown_to_json
from src.app.crew_integration import CrewAIProcessor, save_crew_results

# Page config
st.set_page_config(
    page_title="OCR MD Pipeline",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for configuration
st.sidebar.title("⚙️ Configuration")

# API Key input
api_key = st.sidebar.text_input(
    "OpenAI API Key (optional)",
    type="password",
    help="Enter your OpenAI API key for future enhancements"
)

# Processing options
st.sidebar.markdown("---")
st.sidebar.title("🔧 Processing Options")

run_comparison = st.sidebar.checkbox(
    "Run comparison",
    value=True,
    help="Compare the two documents after processing"
)

# Always remove Arabic and deduplicate
remove_arabic = True
deduplicate = True

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Outputs saved to: `{OUTPUT_DIR}`")

# Main content
st.title("📄 OCR → Markdown Pipeline")
st.markdown("Convert documents to markdown, process them, and compare results.")

# Create two columns for file uploads
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Document 1")
    file1 = st.file_uploader(
        "Upload first document",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
        key="file1"
    )

with col2:
    st.subheader("📤 Document 2")
    file2 = st.file_uploader(
        "Upload second document",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
        key="file2"
    )

# Process button
if st.button("🚀 Process Documents", type="primary", use_container_width=True):
    if not file1 or not file2:
        st.error("❌ Please upload both documents")
    else:
        with st.spinner("Processing documents..."):
            try:
                # Create temporary files
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir = Path(tmpdir)
                    
                    # Save uploaded files
                    source1 = tmpdir / "source1.pdf"
                    source2 = tmpdir / "source2.pdf"
                    
                    source1.write_bytes(file1.read())
                    source2.write_bytes(file2.read())
                    
                    # Process document 1
                    st.info("Converting Document 1 to markdown...")
                    md1_path = resolve_output(f"doc1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                    convert_to_markdown(source1, md1_path)
                    
                    if remove_arabic:
                        st.info("Removing Arabic characters from Document 1...")
                        filtered1_path = md1_path.parent / f"{md1_path.stem}_filtered.md"
                        remove_arabic_chars(md1_path, filtered1_path)
                        md1_path = filtered1_path
                    
                    if deduplicate:
                        st.info("Deduplicating lines in Document 1...")
                        unique1_path = md1_path.parent / f"{md1_path.stem}_unique.md"
                        remove_duplicate_lines(md1_path, unique1_path)
                        md1_path = unique1_path
                    
                    # Process document 2
                    st.info("Converting Document 2 to markdown...")
                    md2_path = resolve_output(f"doc2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                    convert_to_markdown(source2, md2_path)
                    
                    if remove_arabic:
                        st.info("Removing Arabic characters from Document 2...")
                        filtered2_path = md2_path.parent / f"{md2_path.stem}_filtered.md"
                        remove_arabic_chars(md2_path, filtered2_path)
                        md2_path = filtered2_path
                    
                    if deduplicate:
                        st.info("Deduplicating lines in Document 2...")
                        unique2_path = md2_path.parent / f"{md2_path.stem}_unique.md"
                        remove_duplicate_lines(md2_path, unique2_path)
                        md2_path = unique2_path
                    
                    # Store in session state
                    st.session_state.md1_path = md1_path
                    st.session_state.md2_path = md2_path
                    
                    st.success("✅ Documents processed successfully!")
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error processing documents: {error_msg}")
                
                # Show additional debugging info
                with st.expander("📋 Detailed Error Information"):
                    st.code(error_msg, language="text")
                    st.info(
                        "**Troubleshooting Tips:**\n"
                        "- Ensure the PDF files are valid and not corrupted\n"
                        "- Try with a smaller or simpler PDF first\n"
                        "- Check that the file format is supported (PDF, PNG, JPG, TIFF, BMP)\n"
                        "- For scanned documents, ensure image quality is good"
                    )

# Display results if available
if "md1_path" in st.session_state and "md2_path" in st.session_state:
    st.markdown("---")
    st.subheader("📊 Results")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Markdown 1", "Markdown 2", "Comparison", "JSON Export", "CrewAI Analysis"])
    
    with tab1:
        md1_content = st.session_state.md1_path.read_text(encoding="utf-8")
        st.markdown("### Document 1 - Markdown")
        st.text_area(
            "Document 1 Content",
            value=md1_content,
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )
        st.download_button(
            "⬇️ Download Markdown 1",
            data=md1_content,
            file_name=st.session_state.md1_path.name,
            mime="text/markdown"
        )
    
    with tab2:
        md2_content = st.session_state.md2_path.read_text(encoding="utf-8")
        st.markdown("### Document 2 - Markdown")
        st.text_area(
            "Document 2 Content",
            value=md2_content,
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )
        st.download_button(
            "⬇️ Download Markdown 2",
            data=md2_content,
            file_name=st.session_state.md2_path.name,
            mime="text/markdown"
        )
    
    with tab3:
        if run_comparison:
            st.markdown("### Document Comparison")
            
            # Exact comparison
            same = compare_files(st.session_state.md1_path, st.session_state.md2_path)
            
            if same:
                st.success("✅ Documents are **IDENTICAL**")
            else:
                st.warning("⚠️ Documents are **DIFFERENT**")
                
                # Show diff stats
                md1_lines = md1_content.splitlines()
                md2_lines = md2_content.splitlines()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Doc 1 Lines", len(md1_lines))
                with col2:
                    st.metric("Doc 2 Lines", len(md2_lines))
                with col3:
                    st.metric("Line Difference", abs(len(md1_lines) - len(md2_lines)))
                
                # Show line-by-line diff
                from difflib import unified_diff
                diff_lines = list(unified_diff(md1_lines, md2_lines, lineterm='', n=1))
                
                if diff_lines:
                    st.markdown("#### Differences:")
                    diff_text = "\n".join(diff_lines[:100])  # Limit to first 100 lines
                    st.code(diff_text, language="diff")
                    
                    if len(diff_lines) > 100:
                        st.info(f"... and {len(diff_lines) - 100} more differences")
        else:
            st.info("Comparison disabled. Enable it in the sidebar to compare documents.")
    
    with tab4:
        st.markdown("### JSON Export")
        
        # Export to JSON
        json1_path = st.session_state.md1_path.parent / f"{st.session_state.md1_path.stem}.json"
        json2_path = st.session_state.md2_path.parent / f"{st.session_state.md2_path.stem}.json"
        
        markdown_to_json(st.session_state.md1_path, json1_path)
        markdown_to_json(st.session_state.md2_path, json2_path)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Document 1 - JSON")
            json1_content = json1_path.read_text(encoding="utf-8")
            st.json(json.loads(json1_content)[:20])  # Show first 20 lines
            st.download_button(
                "⬇️ Download JSON 1",
                data=json1_content,
                file_name=json1_path.name,
                mime="application/json",
                key="json1"
            )
        
        with col2:
            st.markdown("#### Document 2 - JSON")
            json2_content = json2_path.read_text(encoding="utf-8")
            st.json(json.loads(json2_content)[:20])  # Show first 20 lines
            st.download_button(
                "⬇️ Download JSON 2",
                data=json2_content,
                file_name=json2_path.name,
                mime="application/json",
                key="json2"
            )
        
        st.info(f"Full JSON files saved to `{OUTPUT_DIR}`")
    
    with tab5:
        st.markdown("### 🤖 CrewAI Analysis")
        st.markdown("Use AI agents to format documents and analyze compliance differences.")
        
        if not api_key or api_key.strip() == "":
            st.warning("⚠️ Please provide an OpenAI API key in the sidebar to use CrewAI analysis")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("#### Analysis Options")
                run_crew_analysis = st.checkbox(
                    "Run CrewAI Analysis",
                    value=False,
                    help="Format documents with AI and analyze compliance differences"
                )
            
            with col2:
                st.markdown("#### ")
                run_crew_button = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
            
            if run_crew_analysis and run_crew_button:
                with st.spinner("Running CrewAI analysis... This may take a few minutes."):
                    try:
                        # Initialize CrewAI processor
                        processor = CrewAIProcessor(api_key)
                        
                        # Run full pipeline
                        st.info("Step 1: Formatting documents with AI...")
                        results = processor.full_pipeline(
                            st.session_state.md1_path,
                            st.session_state.md2_path
                        )
                        
                        # Save results
                        st.info("Step 2: Saving analysis results...")
                        crew_output_dir = OUTPUT_DIR / "crew_analysis" / datetime.now().strftime('%Y%m%d_%H%M%S')
                        saved_files = save_crew_results(results, crew_output_dir)
                        
                        st.success("✅ CrewAI analysis completed!")
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("#### 📋 Analysis Results")
                        
                        # Document 1 Formatted
                        with st.expander("📄 Document 1 - Formatted JSON", expanded=False):
                            st.json(results.get("document_1_formatted", {}))
                        
                        # Document 2 Formatted
                        with st.expander("📄 Document 2 - Formatted JSON", expanded=False):
                            st.json(results.get("document_2_formatted", {}))
                        
                        # Compliance Report
                        with st.expander("📊 Compliance Analysis Report", expanded=True):
                            report = results.get("compliance_analysis", {})
                            st.markdown(report.get("report", "No report available"))
                        
                        # Download buttons
                        st.markdown("---")
                        st.markdown("#### 📥 Download Results")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            doc1_json_str = json.dumps(results.get("document_1_formatted", {}), indent=2, ensure_ascii=False, default=str)
                            st.download_button(
                                "⬇️ Doc 1 JSON",
                                data=doc1_json_str,
                                file_name="document_1_formatted.json",
                                mime="application/json"
                            )
                        
                        with col2:
                            doc2_json_str = json.dumps(results.get("document_2_formatted", {}), indent=2, ensure_ascii=False, default=str)
                            st.download_button(
                                "⬇️ Doc 2 JSON",
                                data=doc2_json_str,
                                file_name="document_2_formatted.json",
                                mime="application/json"
                            )
                        
                        with col3:
                            report_str = json.dumps(results.get("compliance_analysis", {}), indent=2, ensure_ascii=False, default=str)
                            st.download_button(
                                "⬇️ Report",
                                data=report_str,
                                file_name="compliance_report.json",
                                mime="application/json"
                            )
                        
                        st.info(f"📁 All results saved to: `{crew_output_dir}`")
                        
                    except ValueError as e:
                        st.error(f"❌ Configuration error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error running CrewAI analysis: {str(e)}")
                        st.info("Make sure your OpenAI API key is valid and you have sufficient credits.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    OCR → Markdown Pipeline | Powered by Docling & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
