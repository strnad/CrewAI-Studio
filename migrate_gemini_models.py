#!/usr/bin/env python3
"""
Database migration script to update legacy Gemini model formats.
This script updates existing agents in the database to use the new Gemini model format.
"""

import json
import os
import sys
from sqlalchemy import create_engine, text

# Database setup (copied from db_utils.py to avoid import issues)
DEFAULT_SQLITE_URL = 'sqlite:///crewai.db'
DB_URL = os.getenv('DB_URL', DEFAULT_SQLITE_URL)
engine = create_engine(DB_URL, echo=False)

def get_db_connection():
    return engine.connect()

def migrate_gemini_models():
    """
    Migrate legacy Gemini model names to new format with gemini/ prefix
    """
    legacy_to_new_mapping = {
        "Google Gemini: gemini-2.5-flash": "Google Gemini: gemini/gemini-2.5-flash",
        "Google Gemini: gemini-2.5-pro": "Google Gemini: gemini/gemini-2.5-pro", 
        "Google Gemini: gemini-2.0-flash": "Google Gemini: gemini/gemini-2.0-flash",
        "Google Gemini: gemini-1.5-flash": "Google Gemini: gemini/gemini-1.5-flash",
        "Google Gemini: gemini-1.5-pro": "Google Gemini: gemini/gemini-1.5-pro",
        # Handle the mysterious "models/" prefix as well
        "Google Gemini: models/gemini-2.5-flash": "Google Gemini: gemini/gemini-2.5-flash",
        "Google Gemini: models/gemini-2.5-pro": "Google Gemini: gemini/gemini-2.5-pro",
        "Google Gemini: models/gemini-2.0-flash": "Google Gemini: gemini/gemini-2.0-flash",
        "Google Gemini: models/gemini-1.5-flash": "Google Gemini: gemini/gemini-1.5-flash",
        "Google Gemini: models/gemini-1.5-pro": "Google Gemini: gemini/gemini-1.5-pro",
    }
    
    updated_count = 0
    
    with get_db_connection() as conn:
        # Get all agent entities
        result = conn.execute(text("SELECT id, data FROM entities WHERE entity_type = 'agent'"))
        agents = result.fetchall()
        
        print(f"Found {len(agents)} agents in database")
        
        for agent_row in agents:
            agent_id = agent_row[0]
            agent_data = json.loads(agent_row[1])
            
            current_llm_model = agent_data.get('llm_provider_model', '')
            
            if current_llm_model in legacy_to_new_mapping:
                new_llm_model = legacy_to_new_mapping[current_llm_model]
                agent_data['llm_provider_model'] = new_llm_model
                
                # Update the database
                update_sql = text("""
                    UPDATE entities 
                    SET data = :data 
                    WHERE id = :id AND entity_type = 'agent'
                """)
                
                conn.execute(update_sql, {
                    'data': json.dumps(agent_data),
                    'id': agent_id
                })
                
                print(f"Updated agent {agent_id}: {current_llm_model} → {new_llm_model}")
                updated_count += 1
            elif current_llm_model.startswith("Google Gemini:"):
                print(f"Agent {agent_id} has Gemini model but no mapping: {current_llm_model}")
        
        conn.commit()
    
    print(f"\nMigration complete! Updated {updated_count} agents.")
    return updated_count

def check_gemini_agents():
    """
    Check current state of Gemini agents in database
    """
    with get_db_connection() as conn:
        result = conn.execute(text("SELECT id, data FROM entities WHERE entity_type = 'agent'"))
        agents = result.fetchall()
        
        print("Current Gemini agents in database:")
        print("=" * 50)
        
        gemini_count = 0
        for agent_row in agents:
            agent_id = agent_row[0]
            agent_data = json.loads(agent_row[1])
            
            llm_model = agent_data.get('llm_provider_model', '')
            if 'Gemini' in llm_model:
                role = agent_data.get('role', 'Unknown')
                print(f"Agent: {role[:30]:<30} | Model: {llm_model}")
                gemini_count += 1
        
        if gemini_count == 0:
            print("No Gemini agents found")
        else:
            print(f"\nTotal Gemini agents: {gemini_count}")

if __name__ == "__main__":
    print("Gemini Model Migration Script")
    print("=" * 40)
    
    print("\n1. Checking current state...")
    check_gemini_agents()
    
    print("\n2. Starting migration...")
    updated = migrate_gemini_models()
    
    if updated > 0:
        print("\n3. Verifying migration...")
        check_gemini_agents()
    
    print("\nDone!")