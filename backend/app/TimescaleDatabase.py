import psycopg2
from app.models import Image, Station, InferenceRequest, User


from abc import ABC, abstractmethod
from typing import List

class FileStorageRepository(ABC):
    @abstractmethod
    def insert_inference_request(self, request: InferenceRequest) -> None:
        pass

    @abstractmethod
    def fetch_one_inference_request(self, request_id: int) -> InferenceRequest:
        pass

    @abstractmethod
    def fetch_all_inference_requests(self) -> List[InferenceRequest]:
        pass

    @abstractmethod
    def fetch_last_10_inference_requests(self) -> List[InferenceRequest]:
        pass

    @abstractmethod
    def delete_inference_request(self, request_id: int) -> None:
        pass

    @abstractmethod
    def update_inference_request_status(self, request_id: int, status_id: int) -> None:
        pass

    @abstractmethod
    def insert_station(self, station: Station) -> None:
        pass

    @abstractmethod
    def fetch_one_station(self, station_id: int) -> Station:
        pass

    @abstractmethod
    def fetch_all_stations(self) -> List[Station]:
        pass

    @abstractmethod
    def delete_station(self, station_id: int) -> None:
        pass

    @abstractmethod
    def update_station_status(self, station_id: int, station_status_id: int) -> None:
        pass

    @abstractmethod
    def insert_image(self, image: Image) -> None:
        pass

    @abstractmethod
    def fetch_one_image(self, image_id: int) -> Image:
        pass

    @abstractmethod
    def fetch_all_images(self) -> List[Image]:
        pass

    @abstractmethod
    def delete_image(self, image_id: int) -> None:
        pass

    @abstractmethod
    def insert_user(self, user: User) -> None:
        pass

    @abstractmethod
    def fetch_one_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def fetch_all_users(self) -> List[User]:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    def update_user_password(self, user_id: int, password: str) -> None:
        pass

class TimescaleDBRepository(FileStorageRepository):
    def __init__(self, db_url: str):
        self.conn = psycopg2.connect(db_url)
        self.cursor = self.conn.cursor()

    def insert_inference_request(self, request: InferenceRequest) -> None:
        query = """
        INSERT INTO InferenceRequest (station_id, initial_image_id, inferred_image_id, request_creation, answer_time, status_id, confidence_level, pallet_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (request.station_id, request.initial_image_id, request.inferred_image_id, request.request_creation, request.answer_time, request.status_id, request.confidence_level, request.pallet_type))
        self.conn.commit()

    def fetch_one_inference_request(self, request_id: int) -> InferenceRequest:
        query = "SELECT * FROM InferenceRequest WHERE request_id = %s"
        self.cursor.execute(query, (request_id,))
        return self.cursor.fetchone()

    def fetch_all_inference_requests(self) -> List[InferenceRequest]:
        query = "SELECT * FROM InferenceRequest"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_last_10_inference_requests(self) -> List[InferenceRequest]:
        query = "SELECT * FROM InferenceRequest ORDER BY request_creation DESC LIMIT 10"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_inference_request(self, request_id: int) -> None:
        query = "DELETE FROM InferenceRequest WHERE request_id = %s"
        self.cursor.execute(query, (request_id,))
        self.conn.commit()

    def update_inference_request_status(self, request_id: int, status_id: int) -> None:
        query = "UPDATE InferenceRequest SET status_id = %s WHERE request_id = %s"
        self.cursor.execute(query, (status_id, request_id))
        self.conn.commit()

    def insert_station(self, station: Station) -> None:
        query = "INSERT INTO Station (name, location, station_status_id) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (station.name, station.location, station.station_status_id))
        self.conn.commit()

    def fetch_one_station(self, station_id: int) -> Station:
        query = "SELECT * FROM Station WHERE id = %s"
        self.cursor.execute(query, (station_id,))
        return self.cursor.fetchone()

    def fetch_all_stations(self) -> List[Station]:
        query = "SELECT * FROM Station"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_station(self, station_id: int) -> None:
        query = "DELETE FROM Station WHERE id = %s"
        self.cursor.execute(query, (station_id,))
        self.conn.commit()

    def update_station_status(self, station_id: int, station_status_id: int) -> None:
        query = "UPDATE Station SET station_status_id = %s WHERE id = %s"
        self.cursor.execute(query, (station_status_id, station_id))
        self.conn.commit()

    def insert_image(self, image: Image) -> None:
        query = "INSERT INTO Image (path) VALUES (%s)"
        self.cursor.execute(query, (image.path,))
        self.conn.commit()

    def fetch_one_image(self, image_id: int) -> Image:
        query = "SELECT * FROM Image WHERE id = %s"
        self.cursor.execute(query, (image_id,))
        return self.cursor.fetchone()

    def fetch_all_images(self) -> List[Image]:
        query = "SELECT * FROM Image"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_image(self, image_id: int) -> None:
        query = "DELETE FROM Image WHERE id = %s"
        self.cursor.execute(query, (image_id,))
        self.conn.commit()

    def insert_user(self, user: User) -> None:
        query = "INSERT INTO User (username, password) VALUES (%s, %s)"
        self.cursor.execute(query, (user.username, user.password))
        self.conn.commit()

    def fetch_one_user(self, user_id: int) -> User:
        query = "SELECT * FROM User WHERE id = %s"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchone()

    def fetch_all_users(self) -> List[User]:
        query = "SELECT * FROM User"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_user(self, user_id: int) -> None:
        query = "DELETE FROM User WHERE id = %s"
        self.cursor.execute(query, (user_id,))
        self.conn.commit()

    def update_user_password(self, user_id: int, password: str) -> None:
        query = "UPDATE User SET password = %s WHERE id = %s"
        self.cursor.execute(query, (password, user_id))
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

