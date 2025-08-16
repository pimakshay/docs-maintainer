import re
import html
from typing import List, Tuple
from bs4 import BeautifulSoup


class DocumentCleaner:
    """
    Cleans documents by removing artifacts and improving content quality.
    Uses both traditional text processing and limited LLM calls.
    """
    
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        

    def remove_html_tags(self, text: str) -> str:
        """
        Remove HTML tags and entities from text.
        """
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        return text

    def clean_code_artifacts(self, text: str) -> str:
        """Minimal cleanup preserving semantic content"""
        # Only normalize excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # Remove only obvious artifacts like copy-paste line numbers
        text = re.sub(r'^\s*\d+\.\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    def remove_noise_patterns(self, text: str) -> str:
        """Very conservative cleanup preserving semantic content"""

        # Only fix obvious excessive punctuation (maybe)
        text = re.sub(r'[!]{4,}', '!!!', text)  # Only 4+ exclamation marks
        text = re.sub(r'[?]{4,}', '???', text)  # Only 4+ question marks  
        
        # Normalize only extreme whitespace (preserve structure)
        text = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', text)  # 4+ newlines → 3
        
        return text.strip()

    def remove_noise_lines(self, text: str) -> str:
        """
        Remove lines that are likely noise from the document.
        """
        lines = text.split('\n')
        important_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are likely noise
            if self.is_noise_line(line):
                continue

            important_lines.append(line)
            
                
            # NOTE: Not implemented.
            # Keep lines with important content
            # if self.is_important_content(line):
            #     important_lines.append(line)
        
        return '\n'.join(important_lines)

    def is_noise_line(self, line: str) -> bool:
        """
        Determine if a line is noise that should be removed.
        """
        # Lines that are too short and don't contain meaningful content
        if len(line) < 3:
            return True
            
        # Lines that are just punctuation or symbols
        if re.match(r'^[^\w]*$', line):
            return True
            
        # Lines that are just numbers
        if re.match(r'^\d+$', line):
            return True
            
        # Lines that are just repeated characters
        if len(set(line)) <= 2 and len(line) > 5:
            return True
            
        return False

    def clean_document(self, text: str, use_llm: bool = True) -> Tuple[str, dict]:
        """
        Main document cleaning function that combines all techniques.
        
        Args:
            text: Original document text
            use_llm: Whether to use LLM cleaning (default: True)
            
        Returns:
            Tuple of (cleaned_text, cleaning_info)
        """
        original_text = text
        cleaning_info = {
            'original_length': len(original_text),
            'steps_applied': [],
            'llm_used': False
        }
        
        # Step 1: Remove HTML tags
        text = self.remove_html_tags(text)
        cleaning_info['steps_applied'].append('html_removal')
        
        
        # Step 2: Clean code artifacts
        text = self.clean_code_artifacts(text)
        cleaning_info['steps_applied'].append('code_cleaning')
        
        # Step 3: Remove noise patterns
        text = self.remove_noise_patterns(text)
        cleaning_info['steps_applied'].append('noise_removal')
        
        # Step 4: Extract important content
        text = self.remove_noise_lines(text)
        cleaning_info['steps_applied'].append('noise_line_removal')
        
        # Step 6: LLM cleaning (if needed and allowed)
        # NOTE: not implemented
        
        cleaning_info['final_length'] = len(text)
        cleaning_info['reduction_percentage'] = round(
            (cleaning_info['original_length'] - cleaning_info['final_length']) / 
            cleaning_info['original_length'] * 100, 2
        )
        
        return text, cleaning_info

    def batch_clean_documents(self, documents: List[str], use_llm: bool = True) -> List[Tuple[str, dict]]:
        """
        Clean multiple documents efficiently.
        """
        results = []
        for doc in documents:
            result = self.clean_document(doc, use_llm)
            results.append(result)
        return results 