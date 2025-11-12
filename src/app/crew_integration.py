"""
Integration module for CrewAI agents with the document processing pipeline.
"""
import json
import os
from pathlib import Path
from typing import Optional, Tuple
from .crew_agents import DocumentFormatAgent, ComplianceAnalysisAgent


class CrewAIProcessor:
    """Main processor that orchestrates CrewAI agents for document analysis."""
    
    def __init__(self, api_key: str):
        """
        Initialize the CrewAI processor.
        
        Args:
            api_key: OpenAI API key for GPT-4 access
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("API key is required for CrewAI agents")
        
        # Set the API key in environment for CrewAI
        os.environ["OPENAI_API_KEY"] = api_key
        
        self.api_key = api_key
        self.format_agent = DocumentFormatAgent(api_key)
        self.compliance_agent = ComplianceAnalysisAgent(api_key)
    
    def process_document(self, markdown_content: str, doc_name: str = "document") -> dict:
        """
        Process a single document through the formatting agent.
        
        Args:
            markdown_content: Markdown content as string
            doc_name: Name of the document for logging
            
        Returns:
            Structured JSON output from the formatting agent
        """
        print(f"Processing document: {doc_name}")
        formatted_json = self.format_agent.format_document(markdown_content)
        
        return formatted_json
    
    def process_both_documents(self, markdown_content1: str, markdown_content2: str) -> Tuple[dict, dict]:
        """
        Process both documents through the formatting agent.
        
        Args:
            markdown_content1: First markdown content as string
            markdown_content2: Second markdown content as string
            
        Returns:
            Tuple of (doc1_json, doc2_json)
        """
        doc1_json = self.process_document(markdown_content1, "document_1")
        doc2_json = self.process_document(markdown_content2, "document_2")
        
        return doc1_json, doc2_json
    
    def analyze_compliance(self, doc1_json: dict, doc2_json: dict, comparison_result: Optional[dict] = None) -> dict:
        """
        Analyze differences between documents for compliance.
        
        Args:
            doc1_json: Structured JSON from first document
            doc2_json: Structured JSON from second document
            comparison_result: Optional comparison result from the app
            
        Returns:
            Compliance analysis report
        """
        print("Running compliance analysis...")
        report = self.compliance_agent.analyze_differences(doc1_json, doc2_json, comparison_result)
        
        return report
    
    def full_pipeline(self, markdown_content1: str, markdown_content2: str, 
                     comparison_result: Optional[dict] = None) -> dict:
        """
        Run the full pipeline: format both documents and analyze compliance.
        
        Args:
            markdown_content1: First markdown content as string
            markdown_content2: Second markdown content as string
            comparison_result: Optional comparison result
            
        Returns:
            Complete analysis result with formatted JSONs and compliance report
        """
        print("Starting full CrewAI pipeline...")
        
        # Step 1: Format both documents
        doc1_json, doc2_json = self.process_both_documents(markdown_content1, markdown_content2)
        
        # Step 2: Analyze compliance
        compliance_report = self.analyze_compliance(doc1_json, doc2_json, comparison_result)
        
        return {
            "document_1_formatted": doc1_json,
            "document_2_formatted": doc2_json,
            "compliance_analysis": compliance_report,
            "status": "completed"
        }


def save_crew_results(results: dict, output_dir: Path) -> dict:
    """
    Save CrewAI results to files.
    
    Args:
        results: Results from CrewAI pipeline
        output_dir: Directory to save results
        
    Returns:
        Dictionary with file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save formatted JSONs
    doc1_path = output_dir / "document_1_formatted.json"
    doc1_data = results.get("document_1_formatted", {})
    doc1_path.write_text(
        json.dumps(doc1_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )
    saved_files["document_1_formatted"] = str(doc1_path)
    
    doc2_path = output_dir / "document_2_formatted.json"
    doc2_data = results.get("document_2_formatted", {})
    doc2_path.write_text(
        json.dumps(doc2_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )
    saved_files["document_2_formatted"] = str(doc2_path)
    
    # Save compliance report
    report_path = output_dir / "compliance_report.json"
    report_data = results.get("compliance_analysis", {})
    report_path.write_text(
        json.dumps(report_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )
    saved_files["compliance_report"] = str(report_path)
    
    return saved_files
