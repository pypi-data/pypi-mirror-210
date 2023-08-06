from typing import List, Dict

from django.db import IntegrityError
from django.db.models.query import QuerySet

from msb.cipher import Cipher
from msb.dataclasses import Singleton, SearchParameter
from msb.db import constants as _const
from msb.db.models import MsbModel
from msb.exceptions import MsbExceptionHandler
from .exceptions import ApiServiceExceptions


class ApiService(MsbExceptionHandler, metaclass=Singleton):
	db_model: MsbModel = MsbModel
	resource_name: str = None
	exception_class_name: ApiServiceExceptions | None = None

	@property
	def resource_name_value(self) -> str | None:
		try:
			if not self.resource_name:
				import re
				class_name = re.split('(?<=.)(?=[A-Z])', self.__class__.__name__.replace("Service", ""))
				return " ".join(class_name)
			return self.resource_name
		except Exception:
			return None

	@property
	def exception_class(self) -> ApiServiceExceptions:
		if not isinstance(self.exception_class_name, ApiServiceExceptions):
			return ApiServiceExceptions
		return self.exception_class_name

	@property
	def cipher(self) -> Cipher:
		return Cipher

	def get_meta_field_data(self, field_name: str, field_value) -> Dict:
		if hasattr(self.db_model, field_name) and str(field_value).isnumeric():
			return {field_name: field_value}
		return {}

	def __init__(self):
		_class_name = self.db_model.__class__.__name__
		if self.db_model is None:
			raise ApiServiceExceptions.InvalidDatabaseModel(resource=self.resource_name_value)

	def search(self, params: SearchParameter) -> Dict:
		result = dict(count=0, records=[])
		try:
			model_query = params.get_query(self.db_model)
			result['count'] = model_query.count()
			result['records'] = [i.dict() for i in model_query.all()[params.offset:params.offset + params.limit]]
		except Exception as e:
			pass
		return result

	def create(self, *model_data_list, user_id=None) -> bool | MsbModel | List[MsbModel]:
		try:
			if len(model_data_list) == 0:
				raise ApiServiceExceptions.InvalidDataForCreateOperation(resource=self.resource_name_value)

			created_by = self.get_meta_field_data(_const.COLUMN_NAME_CREATED_BY, user_id)

			if len(model_data_list) == 1:
				model_data = model_data_list[0]
				_model = self.db_model(**{**model_data, **created_by})
				_model.save()
				return _model
			else:
				_model_list = [self.db_model({**model_data, **created_by}) for model_data in model_data_list]
				self.db_model.objects.bulk_create(_model_list)
				return _model_list
		except IntegrityError as ie:
			raise ApiServiceExceptions.DuplicateEntry(resource=self.resource_name_value)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.CreateOperationFailed(resource=self.resource_name_value))

	def retrieve(self, pk=None, silent=False):
		try:
			if (pk := self.cipher.decrypt(pk)) is None:
				raise ApiServiceExceptions.InvalidPk(resource=self.resource_name_value)
			return self.db_model.objects.retrieve(pk=pk)
		except self.db_model.DoesNotExist:
			raise ApiServiceExceptions.ResourseDoesNotExists(resource=self.resource_name_value)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.RetrieveOperationFailed(resource=self.resource_name_value), silent)
		return None

	def list(self, limit: int = _const.DEFAULT_QUERY_LIMIT, offset: int = _const.DEFAULT_QUERY_OFFSET) -> QuerySet | None:
		try:
			offset = int(offset) if str(offset).isnumeric() else _const.DEFAULT_QUERY_OFFSET
			limit = int(limit) if str(limit).isnumeric() else _const.DEFAULT_QUERY_LIMIT

			fields = [
				i for i in self.db_model._list_field_names
				if (x := getattr(self.db_model, i, None)) and not isinstance(x, property)
			]
			data_set = self.db_model.objects.only(*fields).all()
			return data_set[offset:(limit + offset)] if len(fields) > 0 else None
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.ListOperationFailed(resource=self.resource_name_value))

	def update(self, pk=None, user_id=None, **model_data) -> bool:
		try:
			if (pk := self.cipher.decrypt(pk)) is None:
				raise ApiServiceExceptions.InvalidPk(resource=self.resource_name_value)

			model_object = self.retrieve(pk=pk)
			model_data.update(self.get_meta_field_data(_const.COLUMN_NAME_UPDATED_BY))

			if not (status := model_object.update(**model_data)):
				raise ApiServiceExceptions.UpdateOperationFailed(resource=self.resource_name_value)
			return bool(status)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.UpdateOperationFailed(resource=self.resource_name_value))

	def delete(self, pk=None, user_id=None) -> bool:
		try:
			if (pk := self.cipher.decrypt(pk)) is None:
				raise ApiServiceExceptions.InvalidPk(resource=self.resource_name_value)
			model_object = self.retrieve(pk=pk)
			delete_kwargs = self.get_meta_field_data(_const.COLUMN_NAME_DELETED_BY, user_id)
			if status := model_object.delete(**delete_kwargs):
				raise ApiServiceExceptions.DeleteOperationFailed(resource=self.resource_name_value)
			return bool(status)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.DeleteOperationFailed(resource=self.resource_name_value))
