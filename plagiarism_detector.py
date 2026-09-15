import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticPlagiarismDetector:

    def __init__(self):
        # Pre-trained semantic embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def preprocess(self, text):
        """Clean and normalize the input text."""
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def split_into_sections(self, text):
        """
        Split a document into individual sentences/sections.
        """
        text = self.preprocess(text)

        sections = re.split(r"(?<=[.!?])\s+", text)

        sections = [
            section.strip()
            for section in sections
            if len(section.strip()) > 10
        ]

        return sections

    def create_embeddings(self, sections):
        """
        Convert text sections into semantic embeddings.
        """
        if not sections:
            return np.array([])

        embeddings = self.model.encode(
            sections,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings

    def calculate_similarity(
        self,
        source_sections,
        submitted_sections
    ):
        """
        Calculate cosine similarity between
        submitted and source sections.
        """

        source_embeddings = self.create_embeddings(
            source_sections
        )

        submitted_embeddings = self.create_embeddings(
            submitted_sections
        )

        if (
            len(source_embeddings) == 0
            or len(submitted_embeddings) == 0
        ):
            return np.array([])

        similarity_matrix = cosine_similarity(
            submitted_embeddings,
            source_embeddings
        )

        return similarity_matrix

    def detect_matches(
        self,
        source_sections,
        submitted_sections,
        threshold=0.70
    ):
        """
        Find the best matching source section
        for every submitted section.
        """

        similarity_matrix = self.calculate_similarity(
            source_sections,
            submitted_sections
        )

        matches = []

        if similarity_matrix.size == 0:
            return matches

        for i, submitted_section in enumerate(
            submitted_sections
        ):

            best_source_index = np.argmax(
                similarity_matrix[i]
            )

            best_score = similarity_matrix[
                i,
                best_source_index
            ]

            if best_score >= threshold:

                matches.append({
                    "submitted_section": submitted_section,
                    "source_section": source_sections[
                        best_source_index
                    ],
                    "similarity": float(best_score)
                })

        return matches

    def calculate_overall_similarity(
        self,
        source_sections,
        submitted_sections
    ):
        """
        Calculate the overall semantic similarity
        percentage between two documents.
        """

        similarity_matrix = self.calculate_similarity(
            source_sections,
            submitted_sections
        )

        if similarity_matrix.size == 0:
            return 0.0

        # Find the best source match for each
        # submitted section
        best_scores = np.max(
            similarity_matrix,
            axis=1
        )

        overall_similarity = (
            np.mean(best_scores) * 100
        )

        return float(overall_similarity)

    def generate_report(
        self,
        source_text,
        submitted_text,
        threshold=0.70
    ):
        """
        Complete plagiarism analysis.
        """

        # Split documents into sections
        source_sections = self.split_into_sections(
            source_text
        )

        submitted_sections = self.split_into_sections(
            submitted_text
        )

        # Find matching sections
        matches = self.detect_matches(
            source_sections,
            submitted_sections,
            threshold
        )

        # Calculate overall similarity
        overall_similarity = (
            self.calculate_overall_similarity(
                source_sections,
                submitted_sections
            )
        )

        return {
            "overall_similarity": overall_similarity,
            "matches": matches,
            "source_sections": len(source_sections),
            "submitted_sections": len(submitted_sections)
        }