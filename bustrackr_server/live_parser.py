from bustrackr_server.models_redis import VehicleLive
from bustrackr_server import redis_client
import concurrent.futures as cf
from threading import Thread
from queue import Queue
import bs4
from datetime import datetime

MAX_WORKERS = 8

def parse_live_chunk(buffer):
    soup = bs4.BeautifulSoup(''.join(buffer), 'xml')
    vehicle_live = VehicleLive(
        service_journey_id=int(soup.find('DatedVehicleJourneyRef').text.split(':')[-1]),
        vehicle_id=int(soup.find('VehicleRef').text),
        bearing=float(soup.find('Bearing').text),
        velocity=int(soup.find('Velocity').text),
        latitude=float(soup.find('Latitude').text),
        longitude=float(soup.find('Longitude').text),
        timestamp=datetime.fromisoformat(soup.find('RecordedAtTime').text)
    )

    return vehicle_live

def write_to_redis(queue):
    vehicles = []
    while True:
        vehicle_live = queue.get()
        if vehicle_live is None:
            break
        vehicles.append(vehicle_live)
    with redis_client.pipeline() as pipe:
        for vehicle_live in vehicles:
            vehicle_live.save(pipeline=pipe)
            vehicle_live.expire(15, pipeline=pipe)
        pipe.execute()

def process_data(data: str, writer_queue: Queue):
    buffer = []
    inside_target_tag = False
    start_tag_pattern = '<VehicleActivity>'  # Match the start tag
    end_tag_pattern = '</VehicleActivity>'  # Match the end tag

    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for line in data.splitlines():
            line = line.strip()

            if line == start_tag_pattern:
                inside_target_tag = True
                buffer = [line]
                continue

            if inside_target_tag:
                buffer.append(line)
                if line == end_tag_pattern:
                    parsed_chunk = parse_live_chunk(buffer)
                    writer_queue.put(parsed_chunk)
                    inside_target_tag = False
                    buffer = []

            if len(futures) >= MAX_WORKERS * 2:
                for future in cf.as_completed(futures[:MAX_WORKERS]):
                    future.result()
                futures = futures[MAX_WORKERS:]

        for future in cf.as_completed(futures):
            future.result() 

def process_live_data(data: str):
    writer_queue = Queue()
    writer_thread = Thread(target=write_to_redis, args=(writer_queue,))
    writer_thread.start()
    process_data(data, writer_queue)
    writer_queue.put(None)
    writer_thread.join()