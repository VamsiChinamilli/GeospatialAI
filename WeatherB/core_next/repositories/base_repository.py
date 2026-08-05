# core_next/repositories/base_repository.py

from django.db import transaction


class BaseRepository:
    """
    Base repository providing common database utilities.
    """

    @staticmethod
    def atomic():
        return transaction.atomic()