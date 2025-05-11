import logging
from db.database import Database


class FeatureManager:

    def __init__(self, db: Database, root_logger: logging.Logger):
        self.db = db
        self.root_logger = root_logger
 
    def feature(self, name: str) -> bool:
        try:
            feature = self.db.select_feature(name)
            if feature is None:
                access = input(f"Feature '{name}' not found in the database. Do you want to enable it? (y/n): ")
                if access.lower() == 'y':
                    self.db.insert_feature(name=name, enabled=True)
                    return True
                else:
                    self.db.insert_feature(name=name, enabled=False)
                    return False
            else:
                return feature
        except Exception as e:
            self.root_logger.error(f"Error in is_enabled: {e}")
            return False