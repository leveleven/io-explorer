from sqlalchemy import Column, String, Integer, Float, DateTime
from database import Base
# from datetime import datetime
from dateutil.parser import parse

class Blocks(Base):
    __tablename__ = 'blocks'

    id = Column(Integer, primary_key=True)
    block_id = Column(String(20), unique=True)
    status = Column(String(10))
    time_and_date = Column(DateTime)
    total_block_emission = Column(Float)
    nominated_workers = Column(Integer)
    succeeded = Column(Integer, nullable=True)
    failed = Column(Integer, nullable=True)
    total_workers = Column(Integer, nullable=True)
    verified_cpus = Column(Integer, nullable=True)
    verified_gpus = Column(Integer, nullable=True)

    def __init__(self, **kwargs):
        datetime_string = kwargs["time_and_date"]
        time_and_date = parse(datetime_string)
        # if 'Z' in datetime_string:
        #     time_and_date = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.fZ")
        # else:
        #     time_and_date = datetime.fromisoformat(datetime_string)
            
        block_id_string = kwargs["block_id"]
        block_id = block_id_string.replace("Z", "")

        self.block_id = block_id
        self.status = kwargs["status"]
        self.time_and_date = time_and_date
        self.total_block_emission = kwargs["total_block_emission"]
        self.nominated_workers = kwargs["nominated_workers"]
        self.succeeded = kwargs["succeeded"]
        self.failed = kwargs["failed"]
        self.total_workers = kwargs["total_workers"]
        self.verified_cpus = kwargs["verified_cpus"]
        self.verified_gpus = kwargs["verified_gpus"]

    def __repr__(self) -> str:
        return "<Blocks(id='%s', block_id='%s', status='%s', time_and_date='%s' total_block_emission='%s', nominated_workers='%s', succeeded='%s', failed='%s', total_workers='%s', verified_cpus='%s', verified_gpus='%s')>" % (self.id, self.block_id, self.status, self.time_and_date, self.total_block_emission, self.nominated_workers, self.succeeded, self.failed, self.total_workers, self.verified_cpus, self.verified_gpus)

class BlcokReward(Base):
    __tablename__ = 'blockreward'

    id = Column(Integer, primary_key=True)
    block_id = Column(String(20))
    status = Column(String(10))
    time_and_date = Column(DateTime)
    device_id = Column(String(50))
    connectivity_tier = Column(String(20))
    processor = Column(String(30))
    processor_quantity = Column(Integer)
    pow = Column(String(10))
    potl = Column(String(10))
    uptime_in_minutes = Column(Integer)
    total_score = Column(Float)
    normalized_score = Column(Float)
    rewarded = Column(Float)
    brand_name = Column(String(10))
    brand_id = Column(Integer)
    # pow_success_list = Column(ARRAY(Boolean), default=[])
    # potl_success_list = Column(ARRAY(Boolean), default=[])

    def __init__(self, **kwargs):
        datetime_string = kwargs["time_and_date"]
        time_and_date = parse(datetime_string)
        # if 'Z' in datetime_string:
        #     time_and_date = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.fZ")
        # else:
        #     time_and_date = datetime.fromisoformat(datetime_string)

        block_id_string = kwargs["block_id"]
        block_id = block_id_string.replace("Z", "")

        self.block_id = block_id
        self.status = kwargs["status"]
        self.time_and_date = time_and_date
        self.device_id = kwargs["device_id"]
        self.connectivity_tier = kwargs["connectivity_tier"]
        self.processor = kwargs["processor"]
        self.processor_quantity = kwargs["processor_quantity"]
        self.pow = kwargs["pow"]
        self.potl = kwargs["potl"]
        self.uptime_in_minutes = kwargs["uptime_in_minutes"]
        self.total_score = kwargs["total_score"]
        self.normalized_score = kwargs["normalized_score"]
        self.rewarded = kwargs["rewarded"]
        self.brand_name = kwargs["brand_name"]
        self.brand_id = kwargs["brand_id"]
        self.pow_success_list = kwargs["pow_success_list"]
        self.potl_success_list = kwargs["potl_success_list"]

    def __repr__(self) -> str:
        return "<BlcokReward(id='%s', block_id='%s', status='%s', time_and_date='%s', device_id='%s', connectivity_tier='%s', processor='%s', processor_quantity='%s', pow='%s', potl='%s', uptime_in_minutes='%s', total_score='%s', normalized_score='%s', rewarded='%s', brand_name='%s', brand_id='%s')>" % (self.id, self.block_id, self.status, self.time_and_date, self.device_id, self.connectivity_tier, self.processor, self.processor_quantity, self.pow, self.potl, self.uptime_in_minutes, self.total_score, self.normalized_score, self.rewarded, self.brand_name, self.brand_id)