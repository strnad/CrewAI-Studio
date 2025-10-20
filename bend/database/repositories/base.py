"""
Base Repository
Generic repository with common CRUD operations
"""
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        """
        Create new record

        Args:
            **kwargs: Model attributes

        Returns:
            Created model instance

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, id: str) -> Optional[ModelType]:
        """
        Get record by ID

        Args:
            id: Record ID

        Returns:
            Model instance or None
        """
        # Determine primary key column name
        pk_name = list(self.model.__table__.primary_key.columns.keys())[0]
        return self.db.query(self.model).filter(
            getattr(self.model, pk_name) == id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        """
        Update record by ID

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance or None

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete(self, id: str) -> bool:
        """
        Delete record by ID

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False

            self.db.delete(instance)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def count(self) -> int:
        """
        Count total records

        Returns:
            Total number of records
        """
        return self.db.query(self.model).count()

    def exists(self, id: str) -> bool:
        """
        Check if record exists

        Args:
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        return self.get_by_id(id) is not None
