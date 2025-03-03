class FileModel:
    """Model representing a file in the system."""
    
    def __init__(self, file_id=None, original_name=None, stored_path=None, 
                 file_type=None, file_size=None, upload_date=None, 
                 last_modified=None, content=None, metadata=None):
        self.id = file_id
        self.original_name = original_name
        self.stored_path = stored_path
        self.file_type = file_type
        self.file_size = file_size
        self.upload_date = upload_date
        self.last_modified = last_modified
        self.content = content
        self.metadata = metadata
    
    @staticmethod
    def format_size(size):
        """Format file size to human-readable format."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.2f} KB"
        else:
            return f"{size/(1024*1024):.2f} MB"
