// MongoDB initialization script for Unified Cognition Module
db = db.getSiblingDB('cognition_db');

// Create collections with indexes
db.createCollection('reflection_vaults');
db.createCollection('cognitive_patterns');
db.createCollection('learning_experiences');
db.createCollection('emotional_contexts');
db.createCollection('decision_history');

// Create indexes for better query performance
db.reflection_vaults.createIndex({ "module_name": 1, "timestamp": -1 });
db.reflection_vaults.createIndex({ "emotional_context": 1 });
db.reflection_vaults.createIndex({ "priority_tags": 1 });

db.cognitive_patterns.createIndex({ "pattern_key": 1 }, { unique: true });
db.cognitive_patterns.createIndex({ "confidence_score": -1 });
db.cognitive_patterns.createIndex({ "last_used": -1 });

db.learning_experiences.createIndex({ "input_data": "text" });
db.learning_experiences.createIndex({ "outcome_score": -1 });
db.learning_experiences.createIndex({ "timestamp": -1 });

db.emotional_contexts.createIndex({ "emotion_type": 1 });
db.emotional_contexts.createIndex({ "intensity": -1 });

db.decision_history.createIndex({ "case_id": 1 }, { unique: true });
db.decision_history.createIndex({ "timestamp": -1 });

// Create user for application access
db.createUser({
  user: 'cognition_user',
  pwd: 'cognition_pass2025',
  roles: [
    {
      role: 'readWrite',
      db: 'cognition_db'
    }
  ]
});

print("MongoDB initialization completed for Unified Cognition Module");