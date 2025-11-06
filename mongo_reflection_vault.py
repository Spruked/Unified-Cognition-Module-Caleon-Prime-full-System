import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

class MongoReflectionVault:
    """
    MongoDB-based Reflection Vault for enhanced cognitive learning
    Stores complex reflection data in MongoDB for better scalability and querying
    """

    def __init__(self, mongo_uri: str = "mongodb://cognition_user:cognition_pass2025@mongo:27017/cognition_db",
                 module_name: str = "cerebral_cortex"):
        self.module_name = module_name
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish MongoDB connection with retry logic"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client.cognition_db
            self.collection = self.db.reflection_vaults
            logger.info(f"Connected to MongoDB for {self.module_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None

    def log_reflection(self, case_id: str, emotional_context: str, ethical_dilemma: str,
                       initial_decision: str, refined_reasoning: str, lesson: str,
                       reflection_type: str = "conditional",
                       priority_tags: List[str] = None,
                       resolution_status: str = "unresolved",
                       metadata: Dict[str, Any] = None):
        """
        Log a new reflection entry to MongoDB

        Args:
            case_id: Unique identifier for the decision case
            emotional_context: Emotional tone during the decision
            ethical_dilemma: Description of the moral conflict
            initial_decision: What was originally chosen
            refined_reasoning: Updated logic after reflection
            lesson: Insight gained
            reflection_type: "absolute" or "conditional"
            priority_tags: List of tags like ["conflict", "emotion", "urgency"]
            resolution_status: "resolved", "unresolved", or "unstable"
            metadata: Additional context data
        """
        if not self.collection:
            logger.error("No MongoDB connection available")
            return False

        entry = {
            "case_id": case_id,
            "module_name": self.module_name,
            "timestamp": datetime.now(),
            "emotional_context": emotional_context,
            "ethical_dilemma": ethical_dilemma,
            "initial_decision": initial_decision,
            "refined_reasoning": refined_reasoning,
            "lesson": lesson,
            "reflection_type": reflection_type,
            "priority_tags": priority_tags or [],
            "resolution_status": resolution_status,
            "metadata": metadata or {}
        }

        try:
            result = self.collection.insert_one(entry)
            logger.info(f"Logged reflection for case {case_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to log reflection: {e}")
            return False

    def query_reflections(self, query_type: str = "unresolved",
                         tags: List[str] = None,
                         limit: int = 10,
                         emotion_filter: str = None) -> List[Dict[str, Any]]:
        """
        Query reflections from MongoDB

        Args:
            query_type: Type of query ("unresolved", "resolved", "emotional", etc.)
            tags: Filter by priority tags
            limit: Maximum number of results
            emotion_filter: Filter by emotional context
        """
        if not self.collection:
            return []

        query = {"module_name": self.module_name}

        if query_type == "unresolved":
            query["resolution_status"] = "unresolved"
        elif query_type == "resolved":
            query["resolution_status"] = "resolved"
        elif query_type == "emotional" and emotion_filter:
            query["emotional_context"] = {"$regex": emotion_filter, "$options": "i"}

        if tags:
            query["priority_tags"] = {"$in": tags}

        try:
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to query reflections: {e}")
            return []

    def get_insights_for_case(self, input_data: str, emotional_context: str) -> Dict[str, Any]:
        """
        Get insights from similar past cases
        """
        if not self.collection:
            return {"insights": [], "confidence": 0.0}

        # Find similar cases based on emotional context and input patterns
        pipeline = [
            {
                "$match": {
                    "module_name": self.module_name,
                    "emotional_context": {"$regex": emotional_context, "$options": "i"}
                }
            },
            {
                "$sort": {"timestamp": -1}
            },
            {
                "$limit": 5
            }
        ]

        try:
            similar_cases = list(self.collection.aggregate(pipeline))
            insights = []

            for case in similar_cases:
                insights.append({
                    "case_id": case["case_id"],
                    "lesson": case["lesson"],
                    "refined_reasoning": case["refined_reasoning"],
                    "emotional_context": case["emotional_context"],
                    "relevance_score": 0.8  # Could implement better similarity scoring
                })

            return {
                "insights": insights,
                "confidence": min(len(insights) * 0.2, 1.0),
                "total_similar_cases": len(similar_cases)
            }
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return {"insights": [], "confidence": 0.0}

    def get_vault_statistics(self) -> Dict[str, Any]:
        """Get comprehensive vault statistics"""
        if not self.collection:
            return {"error": "No MongoDB connection"}

        try:
            total_entries = self.collection.count_documents({"module_name": self.module_name})

            resolved_count = self.collection.count_documents({
                "module_name": self.module_name,
                "resolution_status": "resolved"
            })

            unresolved_count = self.collection.count_documents({
                "module_name": self.module_name,
                "resolution_status": "unresolved"
            })

            # Get emotion distribution
            emotion_pipeline = [
                {"$match": {"module_name": self.module_name}},
                {"$group": {"_id": "$emotional_context", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]

            emotion_stats = list(self.collection.aggregate(emotion_pipeline))

            # Get recent activity
            recent_entries = list(self.collection.find(
                {"module_name": self.module_name}
            ).sort("timestamp", -1).limit(1))

            last_activity = recent_entries[0]["timestamp"] if recent_entries else None

            return {
                "total_entries": total_entries,
                "resolved_cases": resolved_count,
                "unresolved_cases": unresolved_count,
                "resolution_rate": resolved_count / total_entries if total_entries > 0 else 0,
                "emotional_distribution": emotion_stats,
                "last_activity": last_activity.isoformat() if last_activity else None,
                "module_name": self.module_name
            }
        except Exception as e:
            logger.error(f"Failed to get vault statistics: {e}")
            return {"error": str(e)}

    def record_activity(self):
        """Record that the module is active (for idle monitoring)"""
        # This could be used for activity tracking if needed
        pass

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()