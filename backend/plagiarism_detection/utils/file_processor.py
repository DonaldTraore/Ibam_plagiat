"""
Module pour le traitement des fichiers (PDF, DOCX, TXT).
"""
import os
import re
from typing import Dict, List, Optional
import PyPDF2
from docx import Document


class FileProcessor:
    """
    Processeur de fichiers pour extraire le contenu textuel.
    """
    
    def process_file(self, file_path: str) -> Dict:
        """
        Traite un fichier et extrait son contenu.
        
        Returns:
            Dict avec 'content', 'word_count', 'page_count'
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._process_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self._process_docx(file_path)
        elif ext == '.txt':
            return self._process_txt(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {ext}")
    
    def _process_pdf(self, file_path: str) -> Dict:
        """Extrait le contenu d'un fichier PDF."""
        content = ""
        page_count = 0
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        except Exception as e:
            print(f"Erreur lors de l'extraction PDF: {e}")
        
        # Nettoyer le contenu
        content = self._clean_text(content)
        word_count = len(content.split())
        
        return {
            'content': content,
            'word_count': word_count,
            'page_count': page_count
        }
    
    def _process_docx(self, file_path: str) -> Dict:
        """Extrait le contenu d'un fichier DOCX."""
        content = ""
        
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
        except Exception as e:
            print(f"Erreur lors de l'extraction DOCX: {e}")
        
        # Nettoyer le contenu
        content = self._clean_text(content)
        word_count = len(content.split())
        
        # Estimation du nombre de pages (environ 500 mots par page)
        page_count = max(1, word_count // 500)
        
        return {
            'content': content,
            'word_count': word_count,
            'page_count': page_count
        }
    
    def _process_txt(self, file_path: str) -> Dict:
        """Lit le contenu d'un fichier TXT."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            # Essayer avec un autre encodage
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        
        # Nettoyer le contenu
        content = self._clean_text(content)
        word_count = len(content.split())
        
        # Estimation du nombre de pages
        page_count = max(1, word_count // 500)
        
        return {
            'content': content,
            'word_count': word_count,
            'page_count': page_count
        }
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte extrait."""
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les retours à la ligne multiples
        text = re.sub(r'\n+', '\n', text)
        # Supprimer les caractères spéciaux inutiles
        text = re.sub(r'[^\w\s\n.,;:!?()\'-]', '', text)
        return text.strip()
    
    def extract_chapters(self, content: str) -> List[Dict]:
        """
        Extrait les chapitres du contenu.
        Recherche des patterns comme "Chapitre 1", "CHAPITRE I", "1.", etc.
        """
        chapters = []
        
        # Patterns pour détecter les chapitres
        patterns = [
            r'(?:Chapitre|CHAPITRE|Chapter|CHAPTER)\s+(\d+|[IVX]+)[\.:\s]',
            r'^(\d+)\.[\s]+',
            r'CHAP\s+(\d+)',
        ]
        
        # Diviser le contenu en sections potentielles
        lines = content.split('\n')
        current_chapter = None
        current_content = []
        chapter_num = 0
        
        for line in lines:
            is_chapter_start = False
            chapter_title = ""
            
            for pattern in patterns:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    is_chapter_start = True
                    chapter_num += 1
                    chapter_title = line.strip()
                    break
            
            if is_chapter_start:
                # Sauvegarder le chapitre précédent
                if current_chapter is not None:
                    chapter_content = '\n'.join(current_content)
                    chapters.append({
                        'numero': current_chapter,
                        'titre': chapter_title,
                        'contenu': chapter_content,
                        'nombre_mots': len(chapter_content.split())
                    })
                
                current_chapter = chapter_num
                current_content = [line]
            else:
                current_content.append(line)
        
        # Ajouter le dernier chapitre
        if current_chapter is not None and current_content:
            chapter_content = '\n'.join(current_content)
            chapters.append({
                'numero': current_chapter,
                'titre': chapter_title,
                'contenu': chapter_content,
                'nombre_mots': len(chapter_content.split())
            })
        
        # Si aucun chapitre détecté, créer un seul chapitre avec tout le contenu
        if not chapters:
            chapters.append({
                'numero': 1,
                'titre': 'Document complet',
                'contenu': content,
                'nombre_mots': len(content.split())
            })
        
        return chapters
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extrait les phrases d'un texte."""
        # Pattern pour détecter les phrases
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def get_word_frequencies(self, text: str) -> Dict[str, int]:
        """Calcule la fréquence des mots dans un texte."""
        words = re.findall(r'\b\w+\b', text.lower())
        frequencies = {}
        for word in words:
            if len(word) > 3:  # Ignorer les mots courts
                frequencies[word] = frequencies.get(word, 0) + 1
        return frequencies
