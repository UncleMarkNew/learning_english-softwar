import sqlite3
from datetime import datetime

class DBManager:
    def __init__(self, db_path='file_system.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create files table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            original_name TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            upload_date TEXT,
            last_modified TEXT,
            content TEXT,
            metadata TEXT
        )
        ''')
        
        self.conn.commit()
    
    def insert_file(self, file_id, original_name, stored_path, file_type, file_size, content, metadata):
        """Insert a new file record into the database."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO files (id, original_name, stored_path, file_type, file_size, upload_date, last_modified, content, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_id, original_name, stored_path, file_type, file_size, current_time, current_time, content, metadata))
        
        self.conn.commit()
    
    def update_file(self, file_id, content, metadata):
        """Update content and metadata for existing file."""
        last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE files
        SET content = ?, metadata = ?, last_modified = ?
        WHERE id = ?
        ''', (content, metadata, last_modified, file_id))
        
        self.conn.commit()
    
    def get_all_files(self):
        """Get information about all files."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, file_type, file_size, upload_date, last_modified
        FROM files
        ''')
        
        return cursor.fetchall()
    
    def search_files(self, name_search, type_search):
        """Search files by name and type."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, file_type, file_size, upload_date, last_modified
        FROM files
        WHERE original_name LIKE ? AND file_type LIKE ?
        ''', (f"%{name_search}%", f"%{type_search}%"))
        
        return cursor.fetchall()
    
    def get_file_content(self, file_id):
        """Get file content."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT content
        FROM files
        WHERE id = ?
        ''', (file_id,))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_file_for_edit(self, file_id):
        """Get file information for editing."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT original_name, content, metadata
        FROM files
        WHERE id = ?
        ''', (file_id,))
        
        return cursor.fetchone()
    
    def get_file_for_query(self, file_id):
        """Get complete file information for querying and future LLM interaction."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, stored_path, file_type, file_size, upload_date, last_modified, content, metadata
        FROM files
        WHERE id = ?
        ''', (file_id,))
        
        result = cursor.fetchone()
        if result:
            # 将结果转换为字典，便于扩展
            file_info = {
                "id": result[0],
                "original_name": result[1],
                "stored_path": result[2],
                "file_type": result[3],
                "file_size": result[4],
                "upload_date": result[5],
                "last_modified": result[6],
                "content": result[7],
                "metadata": result[8]
            }
            return file_info
        else:
            return None
    
    def get_files_for_selection(self):
        """Get file information for selection dialog."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, file_type, upload_date
        FROM files
        ''')
        
        return cursor.fetchall()
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
