"""
Module pour la détection de similarité entre thèmes.
"""
from typing import Dict, List
from difflib import SequenceMatcher
from plagiarism_detection.themes.models import Theme


class ThemeSimilarityChecker:
    """
    Vérifie la similarité entre thèmes pour éviter les doublons.
    """
    
    def __init__(self):
        self.threshold = 0.25  # Seuil de 25%
    
    def check_similarity(self, theme: Theme) -> Dict:
        """
        Vérifie la similarité d'un thème avec les thèmes existants.
        
        Returns:
            Dict avec le score global et les thèmes similaires
        """
        similar_themes = []
        max_similarity = 0.0
        
        # Récupérer les thèmes existants (non brouillons, non tests privés)
        existing_themes = Theme.objects.filter(
            est_test_prive=False,
            statut__in=['VALIDE', 'SOUMIS', 'EN_REVUE_CHEF', 'EN_REVUE_DA']
        ).exclude(id=theme.id)
        
        # Comparer avec chaque thème existant
        for existing_theme in existing_themes:
            similarity = self._calculate_theme_similarity(theme, existing_theme)
            
            if similarity > 0.1:  # Au moins 10% de similarité
                similar_themes.append({
                    'theme_id': existing_theme.id,
                    'titre': existing_theme.titre,
                    'etudiant': existing_theme.etudiant.get_full_name(),
                    'similarite': round(similarity * 100, 2),
                    'departement': existing_theme.departement,
                    'statut': existing_theme.get_statut_display()
                })
                
                max_similarity = max(max_similarity, similarity)
        
        # Trier par similarité décroissante
        similar_themes.sort(key=lambda x: x['similarite'], reverse=True)
        
        return {
            'score_global': round(max_similarity * 100, 2),
            'themes_similaires': similar_themes[:10],  # Top 10
            'total_similaires': len(similar_themes),
            'seuil': self.threshold * 100
        }
    
    def _calculate_theme_similarity(self, theme1: Theme, theme2: Theme) -> float:
        """
        Calcule la similarité entre deux thèmes.
        """
        scores = []
        
        # 1. Similarité du titre (poids: 40%)
        title_similarity = self._text_similarity(theme1.titre, theme2.titre)
        scores.append((title_similarity, 0.4))
        
        # 2. Similarité de la description (poids: 35%)
        if theme1.description and theme2.description:
            desc_similarity = self._text_similarity(theme1.description, theme2.description)
            scores.append((desc_similarity, 0.35))
        
        # 3. Similarité des mots-clés (poids: 25%)
        if theme1.mots_cles and theme2.mots_cles:
            keywords_similarity = self._keywords_similarity(theme1.mots_cles, theme2.mots_cles)
            scores.append((keywords_similarity, 0.25))
        
        # Calculer la moyenne pondérée
        if scores:
            total_weight = sum(weight for _, weight in scores)
            weighted_sum = sum(score * weight for score, weight in scores)
            return weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return 0.0
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes (méthode publique).
        """
        return self._text_similarity(text1, text2)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes.
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _keywords_similarity(self, keywords1: str, keywords2: str) -> float:
        """
        Calcule la similarité entre deux listes de mots-clés.
        """
        # Normaliser et séparer les mots-clés
        set1 = set(k.strip().lower() for k in keywords1.split(','))
        set2 = set(k.strip().lower() for k in keywords2.split(','))
        
        # Calculer l'intersection
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        # Coefficient de Jaccard
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
