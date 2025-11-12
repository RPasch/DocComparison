"""
CrewAI agents for document processing and compliance analysis.
"""
from crewai import Agent, Task, Crew
import json
from pathlib import Path
from typing import Optional


class DocumentFormatAgent:
    """Agent that formats OCR markdown output into structured JSON with key-value pairs."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the document formatting agent."""
        return Agent(
            role="Document Formatter",
            goal="Convert OCR markdown output into accurate, structured JSON with correct key-value pairs. "
                 "Extract all relevant information without making up any values.",
            backstory="You are an expert document analyst with years of experience in data extraction. "
                     "You understand various document formats and can accurately identify and structure information. "
                     "You are meticulous and never invent data - if information is unclear, you mark it as uncertain.",
            verbose=True,
            allow_delegation=False,
            model="gpt-4-turbo"
        )
    
    def format_document(self, markdown_content: str) -> dict:
        """
        Format markdown content into structured JSON.
        
        Args:
            markdown_content: The OCR markdown output
            
        Returns:
            Structured JSON as dictionary
        """
        task = Task(
            description=f"""Analyze the following OCR markdown output and convert it into a well-structured JSON object with accurate key-value pairs.

Markdown Content:
{markdown_content}

Requirements:
1. Extract all identifiable information (names, numbers, dates, addresses, etc.)
2. Organize information hierarchically (e.g., personal info, business info, dates, etc.)
3. Do NOT make up or invent any values
4. If a value is unclear or partially visible, mark it as "uncertain" or "partial"
5. Preserve all tables as structured data
6. Return ONLY valid JSON, no additional text

Return the JSON object directly.""",
            agent=self.agent,
            expected_output="A valid JSON object with extracted and structured information from the document"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Parse the result to JSON
        try:
            # Handle CrewOutput object
            result_str = str(result)
            
            # Find JSON in the result
            import re
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return json.loads(result_str)
        except (json.JSONDecodeError, ValueError) as e:
            return {"raw_output": str(result), "error": f"Could not parse JSON: {str(e)}"}


class ComplianceAnalysisAgent:
    """Agent that analyzes differences between two documents for compliance and accuracy."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the compliance analysis agent."""
        return Agent(
            role="Account Maintenance & Compliance Officer",
            goal="Analyze differences between two documents, identify discrepancies, and provide a comprehensive "
                 "compliance report highlighting any issues that need attention.",
            backstory="You are an experienced account maintenance officer at a digital bank with deep compliance expertise. "
                     "You understand KYC (Know Your Customer) requirements, AML (Anti-Money Laundering) regulations, and "
                     "account verification procedures. You are detail-oriented and can identify suspicious patterns or "
                     "inconsistencies that may indicate fraud or compliance issues.",
            verbose=True,
            allow_delegation=False,
            model="gpt-4-turbo"
        )
    
    def analyze_differences(self, doc1_json: dict, doc2_json: dict, comparison_result: Optional[dict] = None) -> dict:
        """
        Analyze differences between two documents and generate compliance report.
        
        Args:
            doc1_json: Structured JSON from first document
            doc2_json: Structured JSON from second document
            comparison_result: Optional comparison result from the app
            
        Returns:
            Compliance analysis report as dictionary
        """
        task = Task(
            description=f"""You are reviewing two account documents for compliance and accuracy. Analyze the differences between them and provide a detailed report.

Document 1 (JSON):
{json.dumps(doc1_json, indent=2)}

Document 2 (JSON):
{json.dumps(doc2_json, indent=2)}

{f'Comparison Results: {json.dumps(comparison_result, indent=2)}' if comparison_result else ''}

Please provide:
1. **Key Differences**: List all significant differences between the documents
2. **Compliance Concerns**: Identify any potential compliance issues or red flags
3. **Discrepancy Analysis**: Explain why these differences might exist
4. **Risk Assessment**: Rate the risk level (Low/Medium/High) based on the differences
5. **Recommendations**: Suggest actions to resolve discrepancies
6. **Summary**: A brief executive summary of findings

Format your response as a structured report.""",
            agent=self.agent,
            expected_output="A comprehensive compliance analysis report in structured format"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Convert CrewOutput to string properly
        report_text = str(result) if result else "No report generated"
        
        return {
            "report": report_text,
            "timestamp": str(Path.cwd()),
            "documents_analyzed": 2
        }


def create_agents(api_key: str) -> tuple:
    """
    Factory function to create both agents.
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        Tuple of (DocumentFormatAgent, ComplianceAnalysisAgent)
    """
    return DocumentFormatAgent(api_key), ComplianceAnalysisAgent(api_key)
