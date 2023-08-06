__all__ = [
		'DetaBase',
]

from typing import Union, Optional
from deta import Deta
from dhint.hints import *
from .config import DetaConfig


config = DetaConfig('.env')


class DetaBase:
	
	def __init__(self, table: str, project_key: str = None):
		self.table = table
		self.project_key = project_key
	
	def async_base(self):
		return Deta(self.project_key or config.detabase_project_key).AsyncBase(self.table)
	
	async def put_many(self, items: list[Jsonable], expire_in: ExpireIn = None, expire_at: ExpireAt = None):
		base = self.async_base()
		processed = dict(items=list())
		failed = dict(items=list())
		try:
			loops = (len(items) - (len(items) % 20)) / 20
			gen = (item for item in items)
			while loops > 0:
				result = await base.put_many(items=[next(gen) for _ in range(20)], expire_in=expire_in,
				                             expire_at=expire_at)
				processed['items'].extend(result.get('processed').get('items'))
				failed['items'].extend(result.get('failed').get('items'))
				loops -= 1
			missing = list(gen)
			if len(missing) > 0:
				result = await base.put_many(items=list(gen), expire_in=expire_in, expire_at=expire_at)
				processed['items'].extend(result.get('processed').get('items'))
				failed['items'].extend(result.get('failed').get('items'))
			return {'processed': processed, 'failed': failed}
		except StopIteration:
			pass
		finally:
			await base.close()
			
	async def put(self,
	              data: DetaData,
	              key: DetaKey = None,
	              expire_in: ExpireIn = None,
	              expire_at: ExpireAt = None
	              ) -> Optional[dict]:
		"""
		Save a Json object on table, event if a key already exist.
		:param data: data to be saved, with or without a key
		:param key: the key to be saved, but prefernce for data["key"] if exist
		:param expire_in:
		:param expire_at:
		:return: object saved or raise error
		"""
		base = self.async_base()
		deta_key = data.pop('key', None) or key
		try:
			return await base.put(data=data, key=deta_key, expire_in=expire_in, expire_at=expire_at)
		except BaseException as e:
			raise e
		finally:
			await base.close()
			
	async def update(self,
	                 key: str, sets: Optional[dict] = None,
	                 increments: Optional[dict[str, Union[int, float]]] = None,
	                 appends: Optional[dict[str, Union[JsonPrimitive, list]]] = None,
	                 prepends: Optional[dict[str, Union[JsonPrimitive, list]]] = None,
	                 trims: Optional[list[str]] = None
	                 ):
		base = self.async_base()
		updates = dict()
		if sets:
			for name, value in sets.items():
				updates[name] = value
		if increments:
			for name, value in increments.items():
				updates[name] = base.util.increment(value)
		if appends:
			for name, value in appends.items():
				updates[name] = base.util.append(value)
		if prepends:
			for name, value in prepends.items():
				updates[name] = base.util.prepend(value)
		if trims:
			for name in trims:
				updates[name] = base.util.trim()
		try:
			return await base.update(updates=updates, key=key)
		except BaseException as e:
			raise e
		finally:
			await base.close()
			
	async def delete(self, key: str) -> None:
		"""
		Delete instace from a table if key exist.
		:param key: key of object
		:return: None
		"""
		base = self.async_base()
		try:
			await base.delete(key)
		finally:
			await base.close()
			
	async def fetch_all(self, query: DetaQuery = None) -> list[Optional[dict]]:
		base = self.async_base()
		try:
			response = await base.fetch(query=query)
			all_items = response.items
			while response.last:
				response = await base.fetch(last=response.last, query=query)
				all_items.extend(response.items)
			return all_items
		finally:
			await base.close()
			
	async def fetch(self, query: DetaQuery = None, last: str = None, limit=1000):
		base = self.async_base()
		try:
			return await base.fetch(query=query, last=last, limit=limit)
		finally:
			await base.close()
	
	async def insert(self,
	                 data: DetaData,
	                 key: DetaKey = None,
	                 expire_in: ExpireIn = None,
	                 expire_at: ExpireAt = None
	                 ) -> Optional[dict]:
		"""
		Insert a Json object on table, checking first if key exist, and raising an error if key found.
		:param data: data to be saved, with or without a key
		:param key: the key to be saved, but prefernce for data["key"] if exist
		:param expire_in:
		:param expire_at:
		:return: object saved or raise error if key exist
		"""
		base = self.async_base()
		deta_key = data.pop('key', None) or key
		try:
			return await base.insert(data=data, key=deta_key, expire_in=expire_in, expire_at=expire_at)
		except BaseException as e:
			raise e
		finally:
			await base.close()
			
	async def get(self, key: str) -> Optional[dict]:
		base = self.async_base()
		try:
			return await base.get(key)
		finally:
			await base.close()
			
	async def get_first(self, query: DetaQuery = None) -> Optional[dict]:
		result = await self.fetch(limit=1, query=query)
		data = None
		try:
			data = result.items[0]
		finally:
			return data

	async def get_last(self, query: DetaQuery = None) -> Optional[dict]:
		result = await self.fetch_all(query=query)
		data = None
		try:
			data = result[-1]
		finally:
			return data
		
	async def total_count(self, query: DetaQuery = None) -> int:
		return len(await self.fetch_all(query=query))
	
	async def generate_data_by_attribute(self, attribute: str,  query: DetaQuery = None):
		data = await self.fetch_all(query=query)
		sets = {item[attribute] for item in data}
		gen = ({key: [item for item in data if item[attribute] == key]} for key in sets)
		return gen
	

		
		

		
	
