"""
Image Similarity Service
Detect duplicate verification photos for fraud prevention
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
import hashlib
from io import BytesIO

logger = logging.getLogger(__name__)

# Try importing image processing libraries
try:
    from PIL import Image
    import numpy as np
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False

try:
    import imagehash
    HASH_AVAILABLE = True
except ImportError:
    HASH_AVAILABLE = False


@dataclass
class ImageFingerprint:
    """Image fingerprint for similarity matching."""
    image_id: str
    project_id: int
    user_id: str
    perceptual_hash: str
    color_hash: str
    average_hash: str
    file_hash: str
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class SimilarityMatch:
    """Similarity match result."""
    image_id: str
    similarity_score: float
    match_type: str  # exact, near, partial
    original_project_id: int
    original_user_id: str
    distance: int


class ImageSimilarityService:
    """
    Image similarity detection for fraud prevention.
    
    Detects:
    - Exact duplicates (file hash match)
    - Perceptually similar images (pHash)
    - Color-similar images
    - Cropped/resized versions
    
    Uses perceptual hashing which is robust to:
    - Minor edits
    - Compression
    - Resizing
    - Color adjustments
    """
    
    # Thresholds for similarity detection
    EXACT_THRESHOLD = 0  # Hash distance for exact match
    NEAR_THRESHOLD = 5   # Hash distance for near match
    PARTIAL_THRESHOLD = 12  # Hash distance for partial match
    
    def __init__(self):
        self._fingerprint_db: Dict[str, ImageFingerprint] = {}
        self._hash_index: Dict[str, List[str]] = {}  # Hash prefix -> image_ids
    
    async def generate_fingerprint(
        self,
        image_data: bytes,
        image_id: str,
        project_id: int,
        user_id: str
    ) -> ImageFingerprint:
        """Generate fingerprint for an image."""
        # Calculate file hash first
        file_hash = hashlib.sha256(image_data).hexdigest()
        
        # Calculate perceptual hashes if available
        if IMAGING_AVAILABLE and HASH_AVAILABLE:
            img = Image.open(BytesIO(image_data))
            
            # Multiple hash types for robustness
            p_hash = str(imagehash.phash(img))
            a_hash = str(imagehash.average_hash(img))
            c_hash = str(imagehash.colorhash(img))
            
            metadata = {
                "size": img.size,
                "format": img.format,
                "mode": img.mode
            }
        else:
            # Fallback to file hash only
            p_hash = file_hash[:16]
            a_hash = file_hash[16:32]
            c_hash = file_hash[32:48]
            metadata = {}
        
        fingerprint = ImageFingerprint(
            image_id=image_id,
            project_id=project_id,
            user_id=user_id,
            perceptual_hash=p_hash,
            average_hash=a_hash,
            color_hash=c_hash,
            file_hash=file_hash,
            created_at=datetime.utcnow(),
            metadata=metadata
        )
        
        # Store fingerprint
        self._fingerprint_db[image_id] = fingerprint
        
        # Index by hash prefix for fast lookup
        hash_prefix = p_hash[:4]
        if hash_prefix not in self._hash_index:
            self._hash_index[hash_prefix] = []
        self._hash_index[hash_prefix].append(image_id)
        
        return fingerprint
    
    async def find_similar(
        self,
        image_data: bytes,
        exclude_project_id: Optional[int] = None,
        exclude_user_id: Optional[str] = None
    ) -> List[SimilarityMatch]:
        """
        Find similar images in the database.
        """
        matches = []
        
        # Generate temporary fingerprint for comparison
        file_hash = hashlib.sha256(image_data).hexdigest()
        
        # Check for exact file match first
        for img_id, fp in self._fingerprint_db.items():
            if fp.file_hash == file_hash:
                if exclude_project_id and fp.project_id == exclude_project_id:
                    continue
                matches.append(SimilarityMatch(
                    image_id=img_id,
                    similarity_score=1.0,
                    match_type="exact",
                    original_project_id=fp.project_id,
                    original_user_id=fp.user_id,
                    distance=0
                ))
        
        # If exact match found, return immediately
        if matches:
            return matches
        
        # Check perceptual similarity if libraries available
        if IMAGING_AVAILABLE and HASH_AVAILABLE:
            img = Image.open(BytesIO(image_data))
            query_hash = imagehash.phash(img)
            
            for img_id, fp in self._fingerprint_db.items():
                if exclude_project_id and fp.project_id == exclude_project_id:
                    continue
                if exclude_user_id and fp.user_id == exclude_user_id:
                    continue
                
                try:
                    stored_hash = imagehash.hex_to_hash(fp.perceptual_hash)
                    distance = query_hash - stored_hash
                    
                    if distance <= self.PARTIAL_THRESHOLD:
                        if distance == self.EXACT_THRESHOLD:
                            match_type = "exact"
                            score = 1.0
                        elif distance <= self.NEAR_THRESHOLD:
                            match_type = "near"
                            score = 1 - (distance / 16)
                        else:
                            match_type = "partial"
                            score = 1 - (distance / 32)
                        
                        matches.append(SimilarityMatch(
                            image_id=img_id,
                            similarity_score=score,
                            match_type=match_type,
                            original_project_id=fp.project_id,
                            original_user_id=fp.user_id,
                            distance=distance
                        ))
                        
                except Exception as e:
                    logger.error(f"Hash comparison failed: {e}")
        
        # Sort by similarity score
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        
        return matches[:10]  # Return top 10 matches
    
    async def check_for_fraud(
        self,
        image_data: bytes,
        project_id: int,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Check if verification photo might be fraudulent.
        Returns fraud risk assessment.
        """
        matches = await self.find_similar(
            image_data,
            exclude_project_id=project_id,
            exclude_user_id=user_id
        )
        
        if not matches:
            return {
                "risk_level": "low",
                "risk_score": 0.0,
                "is_duplicate": False,
                "matches": [],
                "recommendation": "proceed"
            }
        
        # Analyze matches
        exact_matches = [m for m in matches if m.match_type == "exact"]
        near_matches = [m for m in matches if m.match_type == "near"]
        
        if exact_matches:
            return {
                "risk_level": "critical",
                "risk_score": 1.0,
                "is_duplicate": True,
                "matches": [
                    {
                        "project_id": m.original_project_id,
                        "user_id": m.original_user_id,
                        "similarity": f"{m.similarity_score:.0%}",
                        "match_type": m.match_type
                    }
                    for m in exact_matches
                ],
                "recommendation": "reject"
            }
        
        if near_matches:
            best_match = max(near_matches, key=lambda m: m.similarity_score)
            
            return {
                "risk_level": "high",
                "risk_score": best_match.similarity_score,
                "is_duplicate": best_match.similarity_score > 0.9,
                "matches": [
                    {
                        "project_id": m.original_project_id,
                        "user_id": m.original_user_id,
                        "similarity": f"{m.similarity_score:.0%}",
                        "match_type": m.match_type
                    }
                    for m in near_matches[:3]
                ],
                "recommendation": "manual_review"
            }
        
        # Partial matches
        best_match = matches[0]
        return {
            "risk_level": "medium" if best_match.similarity_score > 0.6 else "low",
            "risk_score": best_match.similarity_score,
            "is_duplicate": False,
            "matches": [
                {
                    "project_id": m.original_project_id,
                    "similarity": f"{m.similarity_score:.0%}",
                    "match_type": m.match_type
                }
                for m in matches[:3]
            ],
            "recommendation": "proceed" if best_match.similarity_score < 0.6 else "flag"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "total_fingerprints": len(self._fingerprint_db),
            "unique_projects": len(set(fp.project_id for fp in self._fingerprint_db.values())),
            "index_size": len(self._hash_index)
        }


# Singleton
_similarity_service: Optional[ImageSimilarityService] = None

def get_similarity_service() -> ImageSimilarityService:
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = ImageSimilarityService()
    return _similarity_service
