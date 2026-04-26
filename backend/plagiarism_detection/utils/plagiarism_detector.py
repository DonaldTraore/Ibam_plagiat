"""
Module pour la détection de plagiat.
Utilise TF-IDF et cosine similarity pour détecter les similitudes.
"""
import os
import re
from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from difflib import SequenceMatcher

from plagiarism_detection.reports.models import Report, ReportChapter, PlagiarismResult
from plagiarism_detection.documents.models import ReferenceDocument
from .file_processor import FileProcessor


class PlagiarismDetector:
    """
    Détecteur de plagiat utilisant TF-IDF et cosine similarity.
    """
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.threshold = 0.25  # Seuil de 25%
    
    def analyze_report(
        self,
        report: Report,
        type_detection: str = 'PAR_CHAPITRE',
        chapitres_specifiques: Optional[List[int]] = None,
        teste_par=None
    ) -> PlagiarismResult:
        """
        Analyse un rapport pour détecter le plagiat.
        
        Args:
            report: Le rapport à analyser
            type_detection: 'PAR_CHAPITRE' ou 'GLOBAL'
            chapitres_specifiques: Liste des chapitres à tester (optionnel)
            teste_par: Utilisateur qui lance le test
        
        Returns:
            PlagiarismResult avec les résultats de l'analyse
        """
        # Extraire le contenu du fichier
        if not report.fichier:
            raise ValueError("Le rapport n'a pas de fichier associé")
        
        file_result = self.file_processor.process_file(report.fichier.path)
        content = file_result['content']
        
        # Extraire ou récupérer les chapitres
        if type_detection == 'PAR_CHAPITRE':
            chapters = self._get_or_create_chapters(report, content)
            
            # Filtrer les chapitres si spécifié
            if chapitres_specifiques:
                chapters = [c for c in chapters if c.numero_chapitre in chapitres_specifiques]
            
            # Analyser chaque chapitre
            chapter_scores = {}
            all_similitudes = []
            total_weighted_score = 0
            total_words = 0
            
            for chapter in chapters:
                score, similitudes = self._analyze_chapter(chapter)
                chapter_scores[chapter.numero_chapitre] = {
                    'score': score,
                    'titre': chapter.titre_chapitre,
                    'nombre_mots': chapter.nombre_mots
                }
                all_similitudes.extend(similitudes)
                
                # Pondération par le nombre de mots
                total_weighted_score += score * chapter.nombre_mots
                total_words += chapter.nombre_mots
                
                # Mettre à jour le chapitre
                chapter.score_plagiat = score
                chapter.passages_plagies = similitudes
                chapter.save()
            
            # Calculer le score global pondéré
            score_global = (total_weighted_score / total_words) if total_words > 0 else 0
        else:
            # Analyse globale
            score_global, all_similitudes = self._analyze_text(content)
            chapter_scores = {'global': {'score': score_global}}
        
        # Créer le résultat
        result = PlagiarismResult.objects.create(
            report=report,
            type_detection=type_detection,
            score_global=round(score_global, 2),
            score_par_chapitre=chapter_scores,
            similitudes_trouvees=all_similitudes,
            teste_par=teste_par
        )
        
        # Ajouter les documents de référence utilisés
        reference_docs = ReferenceDocument.objects.filter(
            est_actif=True,
            departement=report.departement
        )
        result.documents_reference.set(reference_docs)
        
        return result
    
    def _get_or_create_chapters(self, report: Report, content: str) -> List[ReportChapter]:
        """Récupère ou crée les chapitres d'un rapport."""
        # Vérifier si des chapitres existent déjà
        existing_chapters = list(report.chapters.all().order_by('numero_chapitre'))
        
        if existing_chapters:
            return existing_chapters
        
        # Extraire les chapitres du contenu
        chapters_data = self.file_processor.extract_chapters(content)
        
        chapters = []
        for ch_data in chapters_data:
            chapter = ReportChapter.objects.create(
                report=report,
                numero_chapitre=ch_data['numero'],
                titre_chapitre=ch_data['titre'][:255],
                contenu=ch_data['contenu'],
                nombre_mots=ch_data['nombre_mots']
            )
            chapters.append(chapter)
        
        return chapters
    
    def _analyze_chapter(self, chapter: ReportChapter) -> Tuple[float, List[Dict]]:
        """
        Analyse un chapitre pour détecter le plagiat.
        
        Returns:
            Tuple (score_de_plagiat, liste_des_similitudes)
        """
        return self._analyze_text(chapter.contenu)
    
    def _analyze_text(self, text: str) -> Tuple[float, List[Dict]]:
        """
        Analyse un texte pour détecter le plagiat.
        
        Returns:
            Tuple (score_de_plagiat, liste_des_similitudes)
        """
        similitudes = []
        max_similarity = 0.0
        
        # Récupérer les documents de référence
        reference_docs = ReferenceDocument.objects.filter(est_actif=True)
        
        if not reference_docs.exists():
            # Si pas de documents de référence, retourner 0%
            return 0.0, []
        
        # Extraire les phrases du texte
        sentences = self.file_processor.extract_sentences(text)
        
        # Analyser chaque phrase
        for i, sentence in enumerate(sentences):
            if len(sentence) < 20:  # Ignorer les phrases trop courtes
                continue
            
            # Comparer avec les documents de référence
            for doc in reference_docs:
                if not doc.contenu_extrait:
                    continue
                
                similarity = self._calculate_similarity(sentence, doc.contenu_extrait)
                
                if similarity > self.threshold:
                    similitudes.append({
                        'passage_teste': sentence[:200],
                        'passage_source': self._find_matching_text(sentence, doc.contenu_extrait)[:200],
                        'similarite': round(similarity * 100, 2),
                        'document_source': {
                            'id': doc.id,
                            'titre': doc.titre,
                            'auteur': doc.auteur,
                            'type': doc.get_type_document_display()
                        },
                        'position': i
                    })
                    
                    max_similarity = max(max_similarity, similarity)
        
        # Calculer le score global basé sur les similitudes trouvées
        if similitudes:
            # Moyenne pondérée des similitudes
            total_similarity = sum(s['similarite'] for s in similitudes)
            score = min((total_similarity / len(similitudes)) * (len(similitudes) / len(sentences)) * 10, 100)
        else:
            score = 0.0
        
        return round(score, 2), similitudes
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes.
        Utilise TF-IDF et cosine similarity.
        """
        try:
            # Utiliser TF-IDF pour les textes plus longs
            if len(text1) > 100 and len(text2) > 100:
                vectorizer = TfidfVectorizer(
                    analyzer='word',
                    stop_words='english',
                    ngram_range=(1, 2),
                    max_features=5000
                )
                
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            else:
                # Utiliser SequenceMatcher pour les textes courts
                return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        except Exception as e:
            print(f"Erreur lors du calcul de similarité: {e}")
            return 0.0
    
    def _find_matching_text(self, query: str, source: str, window: int = 200) -> str:
        """
        Trouve le texte correspondant dans la source.
        """
        best_match = ""
        best_ratio = 0.0
        
        # Rechercher dans une fenêtre glissante
        query_len = len(query)
        for i in range(0, len(source) - query_len, 50):
            window_text = source[i:i + query_len + window]
            ratio = SequenceMatcher(None, query.lower(), window_text.lower()).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = window_text
        
        return best_match[:300] if best_match else "Texte non trouvé"
    
    def compare_two_documents(self, doc1_content: str, doc2_content: str) -> Dict:
        """
        Compare deux documents entre eux.
        """
        similarity = self._calculate_similarity(doc1_content, doc2_content)
        
        return {
            'similarite_globale': round(similarity * 100, 2),
            'est_plagiat': similarity > self.threshold,
            'seuil': self.threshold * 100
        }
